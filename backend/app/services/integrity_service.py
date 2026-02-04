"""
Herodotus Integrity Verifier service for L2 proof verification

Verifies STARK proofs on Starknet L2 via the Integrity Verifier contract.
This provides always-on verification for every proof.
"""
import logging
import json
import subprocess
import time
from typing import Optional, Sequence
from dataclasses import dataclass
from pathlib import Path

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.client_models import Call, ResourceBounds, ResourceBoundsMapping, SierraContractClass
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.selector import get_selector_from_name

from app.config import get_settings
from app.utils.rpc import get_rpc_urls, with_rpc_fallback

logger = logging.getLogger(__name__)
settings = get_settings()

# Integrity Verifier contract addresses
# Option 1: Public FactRegistry (has verifiers registered) - RECOMMENDED
# This is the public FactRegistry with all verifiers pre-registered.
# Use this for production and testing to avoid "verifier not registered" errors.
INTEGRITY_VERIFIER_SEPOLIA = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
# Option 2: Your own deployed FactRegistry (needs verifiers registered)
# Custom FactRegistry: 0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64
# Only use if you've registered verifiers in your own FactRegistry.
# Mocked FactRegistry (no proof verification; for demo fallbacks) - DISABLED
MOCKED_FACT_REGISTRY_SEPOLIA = 0x02c0364efde25a53ef446352347e525c0bef3496e6463d6aa7453783d16322c0
INTEGRITY_VERIFIER_MAINNET = 0xcc63a1e8e7824642b89fa6baf996b8ed21fa4707be90ef7605570ca8e4f00b

# Manual resource bounds for Integrity proof verification invokes.
# L1 data gas price increased to handle current network conditions (actual price can be ~21 trillion)
INTEGRITY_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=200000, max_price_per_unit=100000000000000),
    l1_data_gas=ResourceBounds(max_amount=200000, max_price_per_unit=150000000000000),  # 150 trillion - Sepolia L1 data gas can exceed 50T (error 55: resource bounds not satisfied)
    l2_gas=ResourceBounds(max_amount=300000000, max_price_per_unit=20000000000),
)

_INTEGRITY_ABI: Optional[list] = None
_MOCKED_FACT_REGISTRY_ABI: Optional[list] = None


def _load_integrity_abi() -> list:
    global _INTEGRITY_ABI
    if _INTEGRITY_ABI is not None:
        return _INTEGRITY_ABI

    repo_root = Path(__file__).resolve().parents[3]
    abi_path = repo_root / "integrity" / "target" / "dev" / "integrity_FactRegistry.contract_class.json"
    if not abi_path.exists():
        raise FileNotFoundError(f"Integrity FactRegistry ABI not found at {abi_path}")

    payload = json.loads(abi_path.read_text())
    _INTEGRITY_ABI = payload.get("abi", [])
    return _INTEGRITY_ABI


def _load_mocked_fact_registry_abi() -> list:
    global _MOCKED_FACT_REGISTRY_ABI
    if _MOCKED_FACT_REGISTRY_ABI is not None:
        return _MOCKED_FACT_REGISTRY_ABI

    repo_root = Path(__file__).resolve().parents[3]
    abi_path = repo_root / "contracts" / "target" / "dev" / "obsqra_contracts_MockIsValidRegistry.contract_class.json"
    if not abi_path.exists():
        raise FileNotFoundError(f"Mocked FactRegistry ABI not found at {abi_path}")

    payload = json.loads(abi_path.read_text())
    _MOCKED_FACT_REGISTRY_ABI = payload.get("abi", [])
    return _MOCKED_FACT_REGISTRY_ABI


class IntegrityService:
    """L2 proof verification via Herodotus Integrity Verifier"""
    
    def __init__(self, rpc_url: str, network: str = "sepolia"):
        """
        Initialize Integrity Service
        
        Args:
            rpc_url: Starknet RPC URL
            network: Network name ('sepolia' or 'mainnet')
        """
        fallback_urls = get_rpc_urls()
        if rpc_url:
            self.rpc_urls = [rpc_url] + [url for url in fallback_urls if url != rpc_url]
        else:
            self.rpc_urls = fallback_urls
        self.rpc_client = FullNodeClient(node_url=self.rpc_urls[0])
        self.network = network.lower()
        self.verifier_address = (
            INTEGRITY_VERIFIER_SEPOLIA if self.network == "sepolia" 
            else INTEGRITY_VERIFIER_MAINNET
        )
        # Mocked registry disabled in strict mode (Stone-only path).
        self.mocked_registry_address = None
        self.chain_id = StarknetChainId.SEPOLIA if self.network == "sepolia" else StarknetChainId.MAINNET
        logger.info(f"Integrity Service initialized for {network} (address: {hex(self.verifier_address)})")

    async def _init_backend_account(self, client: FullNodeClient) -> Account:
        key_pair = KeyPair.from_private_key(int(settings.BACKEND_WALLET_PRIVATE_KEY, 16))
        account = Account(
            address=int(settings.BACKEND_WALLET_ADDRESS, 16),
            client=client,
            key_pair=key_pair,
            chain=self.chain_id,
        )
        try:
            contract_class = await client.get_class_at(
                contract_address=account.address,
                block_number="latest",
            )
            account._cairo_version = 1 if isinstance(contract_class, SierraContractClass) else 0
        except Exception as err:
            account._cairo_version = 1
            logger.warning("⚠️ Could not resolve account Cairo version; defaulting to Cairo 1: %s", err)
        return account

    @staticmethod
    def _bytes_to_felts(data: bytes, chunk_size: int = 31) -> list[int]:
        """
        Convert an arbitrary byte blob to an array of felts (Cairo-friendly).
        Chunks in 31-byte segments to stay within field limits.
        """
        return [
            int.from_bytes(data[i:i+chunk_size], "big")
            for i in range(0, len(data), chunk_size)
        ]

    @staticmethod
    def _validate_verifier_config(config: dict) -> bool:
        """Validate that verifier_config has required fields for Integrity"""
        if not isinstance(config, dict):
            return False
        required_fields = ["layout", "hasher", "stone_version", "memory_verification"]
        return all(field in config for field in required_fields)
    
    @staticmethod
    def _validate_stark_proof(proof: dict) -> bool:
        """Validate that stark_proof has required fields for Integrity"""
        if not isinstance(proof, dict):
            return False
        # StarkProofWithSerde requires: config, public_input, unsent_commitment, witness
        required_fields = ["config", "public_input", "unsent_commitment", "witness"]
        return all(field in proof for field in required_fields)

    async def verify_proof_full_and_register_fact(
        self,
        verifier_config,
        stark_proof
    ) -> bool:
        """
        Pragmatic verification using Integrity's full proof entrypoint.
        Accepts either ABI-shaped dicts (preferred) or raw byte blobs (chunked to felts).
        
        Returns:
            True if verification succeeded, False otherwise
        """
        try:
            # Step 1: Normalize inputs to dicts
            local_verifier = verifier_config
            local_proof = stark_proof
            
            if isinstance(local_verifier, str):
                try:
                    local_verifier = json.loads(local_verifier)
                except Exception as e:
                    logger.warning(f"Could not parse verifier_config JSON string: {e}")
                    local_verifier = None
            
            if isinstance(local_proof, str):
                try:
                    local_proof = json.loads(local_proof)
                except Exception as e:
                    logger.warning(f"Could not parse stark_proof JSON string: {e}")
                    local_proof = None
            
            # Step 2: Validate structured proofs
            if isinstance(local_verifier, dict) and isinstance(local_proof, dict):
                verifier_valid = self._validate_verifier_config(local_verifier)
                proof_valid = self._validate_stark_proof(local_proof)
                
                if not verifier_valid or not proof_valid:
                    logger.warning(
                        f"Proof structure validation failed. "
                        f"verifier_config valid={verifier_valid}, stark_proof valid={proof_valid}"
                    )
                    if not verifier_valid:
                        logger.warning(
                            f"Expected verifier_config to have keys: layout, hasher, stone_version, memory_verification. "
                            f"Got: {list(local_verifier.keys()) if local_verifier else 'None'}"
                        )
                    if not proof_valid:
                        logger.warning(
                            f"Expected stark_proof to have keys: config, public_input, unsent_commitment, witness. "
                            f"Got: {list(local_proof.keys()) if local_proof else 'None'}"
                        )
                    # Continue anyway - fallback will handle it
                else:
                    # Valid structures - try direct contract call
                    logger.info("Proof structures valid, calling Integrity verify_proof_full_and_register_fact")
                    
                    async def _call_structured(client: FullNodeClient, _rpc_url: str):
                        account = await self._init_backend_account(client)
                        abi = _load_integrity_abi()
                        contract = Contract(
                            address=self.verifier_address,
                            abi=abi,
                            provider=account,
                        )
                        try:
                            nonce = await account.get_nonce(block_number="latest")
                            invoke_result = await contract.functions["verify_proof_full_and_register_fact"].invoke_v3(
                                local_verifier,
                                local_proof,
                                resource_bounds=INTEGRITY_RESOURCE_BOUNDS,
                                nonce=nonce,
                            )
                            await invoke_result.wait_for_acceptance(check_interval=1, retries=120)
                            logger.info("✅ Integrity verify_proof_full_and_register_fact invoke succeeded (structured)")
                            return True
                        except Exception as e:
                            logger.error(f"Integrity invoke failed: {e}")
                            raise
                    
                    try:
                        result, _ = await with_rpc_fallback(_call_structured, urls=self.rpc_urls)
                        return bool(result)
                    except Exception as e:
                        logger.warning(f"Structured proof call failed, falling back to raw bytes: {e}")
            
            # Step 3: Fallback to raw bytes approach
            logger.info("Falling back to raw bytes serialization for Integrity call")
            verifier_bytes = verifier_config if isinstance(verifier_config, bytes) else b""
            proof_bytes = stark_proof if isinstance(stark_proof, bytes) else b""
            
            if not verifier_bytes or not proof_bytes:
                logger.warning("No valid structured proof or raw bytes available - attempting fact hash lookup instead")
                # Try to get fact_hash and use verify_proof_on_l2 as last resort
                return False
            
            verifier_felts = self._bytes_to_felts(verifier_bytes)
            proof_felts = self._bytes_to_felts(proof_bytes)
            
            calldata = [
                len(verifier_felts),
                *verifier_felts,
                len(proof_felts),
                *proof_felts,
            ]
            
            logger.info(f"Using fallback with {len(verifier_felts)} verifier felts and {len(proof_felts)} proof felts")
            
            async def _call_fallback(client: FullNodeClient, _rpc_url: str):
                abi = _load_integrity_abi()
                contract = Contract(
                    address=self.verifier_address,
                    abi=abi,
                    provider=client,
                )
                fn = contract.functions.get("verify_proof_full_and_register_fact")
                if not fn:
                    logger.error("Integrity contract missing verify_proof_full_and_register_fact")
                    raise Exception("Integrity contract missing verify_proof_full_and_register_fact")
                
                result = await fn.call(*calldata)
                logger.info("✅ Integrity verify_proof_full_and_register_fact succeeded (fallback)")
                return True if result else False
            
            result, _ = await with_rpc_fallback(_call_fallback, urls=self.rpc_urls)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Integrity full-proof verification failed: {e}", exc_info=True)
            return False

    async def verify_with_calldata(self, calldata: list[int]) -> bool:
        """
        Call Integrity using pre-serialized calldata (e.g., from proof_serializer).

        This is the path to support either:
        - local Stone proofs (cpu_air_prover -> proof_serializer -> calldata)
        - Atlantic proofs (downloaded proof JSON -> proof_serializer -> calldata)
        """
        try:
            selector = get_selector_from_name("verify_proof_full_and_register_fact")

            async def _call(client: FullNodeClient, _rpc_url: str):
                call = Call(
                    to_addr=self.verifier_address,
                    selector=selector,
                    calldata=calldata,
                )
                return await client.call_contract(call, block_number="latest")

            result, _ = await with_rpc_fallback(_call, urls=self.rpc_urls)
            logger.info("Integrity verify_proof_full_and_register_fact call returned OK (raw calldata)")
            return True if result is not None else False
        except Exception as e:
            logger.error(f"Integrity calldata verification failed: {e}", exc_info=True)
            return False

    async def register_calldata_and_get_fact(self, calldata: list[int]) -> tuple[Optional[int], Optional[str], Optional[int]]:
        """
        Register a proof via raw calldata and return the fact hash (if available).

        This performs a read-only call first to extract the fact hash, then submits
        the invoke to actually register it on-chain.
        """
        selector = get_selector_from_name("verify_proof_full_and_register_fact")
        call = Call(
            to_addr=self.verifier_address,
            selector=selector,
            calldata=calldata,
        )

        fact_hash: Optional[int] = None
        call_rpc: Optional[str] = None

        # Preflight call to fetch fact hash (may fail on some RPCs due to size limits).
        try:
            async def _call(client: FullNodeClient, _rpc_url: str):
                return await client.call_contract(call, block_number="latest")

            output, call_rpc = await with_rpc_fallback(_call, urls=self.rpc_urls)
            if output:
                fact_hash = output[0]
            else:
                logger.warning("Integrity calldata preflight returned empty output; will parse from receipt.")
        except Exception as exc:
            logger.warning("Integrity calldata preflight failed; proceeding to invoke: %s", exc)

        try:
            async def _invoke(client: FullNodeClient, _rpc_url: str, retry_count: int = 0):
                account = await self._init_backend_account(client)
                
                # Fetch both pending and latest nonce for comparison
                try:
                    pending_nonce = await account.get_nonce(block_number="pending")
                except Exception as e:
                    logger.warning(f"Failed to get pending nonce: {e}, using latest")
                    pending_nonce = None
                
                try:
                    latest_nonce = await account.get_nonce(block_number="latest")
                except Exception as e:
                    logger.error(f"Failed to get latest nonce: {e}")
                    raise
                
                # Use the higher nonce to avoid nonce mismatch
                if pending_nonce is not None:
                    nonce = max(pending_nonce, latest_nonce)
                else:
                    nonce = latest_nonce
                
                # Log nonce state for debugging
                logger.info(
                    f"Integrity invoke nonce state (attempt {retry_count + 1}): "
                    f"pending_nonce={pending_nonce}, latest_nonce={latest_nonce}, "
                    f"used_nonce={nonce}, rpc={_rpc_url}"
                )
                
                try:
                    invoke = await account.execute_v3(
                        calls=[call],
                        nonce=nonce,
                        resource_bounds=INTEGRITY_RESOURCE_BOUNDS,
                    )
                    await client.wait_for_tx(invoke.transaction_hash)
                    receipt = await client.get_transaction_receipt(invoke.transaction_hash)
                    return nonce, receipt
                except Exception as e:
                    error_str = str(e)
                    # Check if it's a nonce error and we haven't retried yet
                    if ("nonce" in error_str.lower() or "Invalid transaction nonce" in error_str) and retry_count == 0:
                        logger.warning(
                            f"Nonce error on attempt {retry_count + 1}, re-syncing nonce and retrying: {error_str}"
                        )
                        # Re-fetch latest nonce and retry once
                        try:
                            latest_nonce_retry = await account.get_nonce(block_number="latest")
                            logger.info(
                                f"Nonce re-sync: previous={nonce}, new_latest={latest_nonce_retry}, "
                                f"will retry with {latest_nonce_retry}"
                            )
                            # Retry with fresh nonce
                            return await _invoke(client, _rpc_url, retry_count=1)
                        except Exception as retry_e:
                            logger.error(f"Nonce re-sync failed: {retry_e}")
                            raise e  # Re-raise original error
                    else:
                        # Not a nonce error or already retried, re-raise
                        raise

            invoke_result, used_rpc = await with_rpc_fallback(
                _invoke,
                urls=[call_rpc] if call_rpc else self.rpc_urls,
            )
            used_nonce, receipt = invoke_result
            if used_rpc:
                call_rpc = used_rpc

            if fact_hash is None:
                fact_hash = self._extract_fact_hash_from_receipt(receipt)
                if fact_hash is None:
                    logger.error("Integrity invocation succeeded but FactRegistered event not found.")
                    return None, call_rpc, used_nonce + 1 if used_nonce is not None else None

            logger.info("✅ Integrity calldata registered on-chain")
            next_nonce = used_nonce + 1 if used_nonce is not None else None
            return fact_hash, call_rpc, next_nonce
        except Exception as e:
            error_str = str(e)
            logger.error(f"Integrity calldata registration failed: {e}", exc_info=True)
            # Capture and preserve the actual contract error for better debugging
            if "revert_error" in error_str or "Contract error" in error_str or "Invalid" in error_str:
                # Extract the actual error message if available
                import re
                oods_match = re.search(r"Invalid OODS|OODS", error_str, re.IGNORECASE)
                builtin_match = re.search(r"Invalid builtin|builtin", error_str, re.IGNORECASE)
                verifier_match = re.search(r"VERIFIER_NOT_FOUND", error_str, re.IGNORECASE)
                final_pc_match = re.search(r"Invalid final_pc|final_pc", error_str, re.IGNORECASE)
                
                if oods_match:
                    raise RuntimeError(f"Integrity verification failed: Invalid OODS - The proof's OODS values do not match the verifier's expectations. This may indicate an AIR/public input mismatch. Full error: {error_str}") from e
                elif builtin_match:
                    raise RuntimeError(f"Integrity verification failed: Invalid builtin - The proof's builtins do not match the verifier's expectations. Full error: {error_str}") from e
                elif verifier_match:
                    raise RuntimeError(f"Integrity verification failed: VERIFIER_NOT_FOUND - No verifier registered for this configuration. Full error: {error_str}") from e
                elif final_pc_match:
                    raise RuntimeError(f"Integrity verification failed: Invalid final_pc - The proof's final program counter does not match expectations. Full error: {error_str}") from e
                else:
                    # Re-raise with full error details
                    raise RuntimeError(f"Integrity verification failed: {error_str}") from e
            # If it's not a contract error, still raise it so caller can see it
            raise RuntimeError(f"Integrity calldata registration failed: {error_str}") from e

    @staticmethod
    def _extract_fact_hash_from_receipt(receipt) -> Optional[int]:
        """
        Extract FactRegistered.fact_hash from a transaction receipt.
        """
        try:
            selector = get_selector_from_name("FactRegistered")

            def _to_int(value):
                if isinstance(value, int):
                    return value
                if isinstance(value, str):
                    return int(value, 16) if value.startswith("0x") else int(value)
                return int(value)

            events = getattr(receipt, "events", None)
            if events is None and isinstance(receipt, dict):
                events = receipt.get("events", [])

            for event in events or []:
                keys = getattr(event, "keys", None)
                if keys is None and isinstance(event, dict):
                    keys = event.get("keys", [])
                if not keys:
                    continue
                key0 = _to_int(keys[0])
                if key0 != selector:
                    continue
                if len(keys) > 1:
                    return _to_int(keys[1])
            return None
        except Exception as exc:
            logger.warning("Failed to parse FactRegistered from receipt: %s", exc)
            return None

    async def register_mocked_fact(
        self,
        fact_hash: int,
        verifier_config: dict,
        security_bits: int = 128,
    ) -> tuple[bool, Optional[str], Optional[int]]:
        """
        DEPRECATED: Mock registry disabled in strict mode (Stone-only path).
        
        This function is disabled. Use register_calldata_and_get_fact() with real Integrity FactRegistry instead.
        """
        logger.error("register_mocked_fact() is disabled in strict mode. Use real Integrity FactRegistry only.")
        raise RuntimeError(
            "Mock registry is disabled. This is a strict Stone-only system. "
            "All proofs must be verified through the real Integrity FactRegistry."
        )
    
    async def verify_proof_on_l2(
        self,
        fact_hash: str,
        is_mocked: bool = False
    ) -> bool:
        """
        Verify proof on Starknet L2 via Integrity Verifier contract (strict mode)
        
        Args:
            fact_hash: Cairo fact hash (felt252) as hex string or int
            is_mocked: DEPRECATED - Always False in strict mode. Mock registry is disabled.
        
        Returns:
            True if verified in real FactRegistry, False otherwise
        
        Note:
            This function only queries the real Integrity FactRegistry.
            Mock registry is disabled in strict Stone-only mode.
        """
        if is_mocked:
            logger.warning("is_mocked=True is deprecated. Mock registry is disabled. Using real FactRegistry only.")
        try:
            # Convert fact_hash to int if it's a string
            if isinstance(fact_hash, str):
                if fact_hash.startswith('0x'):
                    fact_hash_int = int(fact_hash, 16)
                else:
                    fact_hash_int = int(fact_hash, 16)  # Try hex first, then decimal
            else:
                fact_hash_int = fact_hash
            
            async def _call(client: FullNodeClient, _rpc_url: str):
                abi = _load_integrity_abi()
                contract = Contract(
                    address=self.verifier_address,
                    abi=abi,
                    provider=client,
                )

                if "get_all_verifications_for_fact_hash" not in contract.functions:
                    logger.error("Integrity FactRegistry ABI missing get_all_verifications_for_fact_hash")
                    return False

                result = await contract.functions["get_all_verifications_for_fact_hash"].call(
                    fact_hash_int,
                    block_number="latest",
                )

                # starknet_py returns tuples; normalize to a list-like object
                verifications = result[0] if isinstance(result, tuple) and result else result
                return bool(verifications) and len(verifications) > 0

            is_valid, _ = await with_rpc_fallback(_call, urls=self.rpc_urls)
            
            logger.info(
                f"L2 verification result: {is_valid} for fact_hash {hex(fact_hash_int)[:16]}... "
                f"(network: {self.network})"
            )
            return is_valid
            
        except Exception as e:
            logger.error(f"L2 verification failed: {e}", exc_info=True)
            return False
    
    async def get_verification_hash(
        self,
        fact_hash: str
    ) -> Optional[str]:
        """
        Get verification hash for a fact_hash (if verified)
        
        Note: This method depends on the Integrity contract interface.
        If the contract doesn't have this method, it will return None.
        
        Args:
            fact_hash: Cairo fact hash
        
        Returns:
            Verification hash or None
        """
        try:
            async def _call(client: FullNodeClient, _rpc_url: str):
                contract = await Contract.from_address(
                    address=self.verifier_address,
                    provider=client,
                )

                if "get_verification" in contract.functions:
                    result = await contract.functions["get_verification"].call(fact_hash)
                    return hex(result[0]) if result else None

                return None

            result, _ = await with_rpc_fallback(_call, urls=self.rpc_urls)
            return result
        except Exception as e:
            logger.debug(f"Could not get verification hash: {e}")
            return None


# Singleton instance
_integrity_service_instance = None


def get_integrity_service(rpc_url: str = None, network: str = None) -> IntegrityService:
    """
    Get singleton Integrity Service instance
    
    Args:
        rpc_url: Optional RPC URL (uses settings if not provided)
        network: Optional network name (uses settings if not provided)
    
    Returns:
        IntegrityService instance
    """
    global _integrity_service_instance
    
    if _integrity_service_instance is None:
        from app.config import get_settings
        settings = get_settings()
        
        rpc_url = rpc_url or settings.STARKNET_RPC_URL
        network = network or getattr(settings, 'STARKNET_NETWORK', 'sepolia')
        
        _integrity_service_instance = IntegrityService(rpc_url=rpc_url, network=network)
    
    return _integrity_service_instance
