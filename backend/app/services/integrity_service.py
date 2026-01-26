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
INTEGRITY_VERIFIER_SEPOLIA = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
INTEGRITY_VERIFIER_MAINNET = 0xcc63a1e8e7824642b89fa6baf996b8ed21fa4707be90ef7605570ca8e4f00b

# Manual resource bounds for Integrity proof verification invokes.
INTEGRITY_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=50000, max_price_per_unit=100000000000000),
    l1_data_gas=ResourceBounds(max_amount=50000, max_price_per_unit=1000000000000),
    l2_gas=ResourceBounds(max_amount=8000000, max_price_per_unit=20000000000),
)


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
        logger.info(f"Integrity Service initialized for {network} (address: {hex(self.verifier_address)})")

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
                        contract = await Contract.from_address(
                            address=self.verifier_address,
                            provider=client,
                        )
                        try:
                            result = await contract.functions["verify_proof_full_and_register_fact"].call(
                                local_verifier,
                                local_proof,
                            )
                            logger.info("✅ Integrity verify_proof_full_and_register_fact succeeded (structured)")
                            return True if result else False
                        except Exception as e:
                            logger.error(f"Integrity call failed: {e}")
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
                contract = await Contract.from_address(
                    address=self.verifier_address,
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
                return await client.call_contract(call)

            result, _ = await with_rpc_fallback(_call, urls=self.rpc_urls)
            logger.info("Integrity verify_proof_full_and_register_fact call returned OK (raw calldata)")
            return True if result is not None else False
        except Exception as e:
            logger.error(f"Integrity calldata verification failed: {e}", exc_info=True)
            return False
    
    async def verify_proof_on_l2(
        self,
        fact_hash: str,
        is_mocked: bool = False
    ) -> bool:
        """
        Verify proof on Starknet L2 via Integrity Verifier contract
        
        Args:
            fact_hash: Cairo fact hash (felt252) as hex string or int
            is_mocked: Whether this is a mocked proof (for testing)
        
        Returns:
            True if verified, False otherwise
        """
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
                contract = await Contract.from_address(
                    address=self.verifier_address,
                    provider=client,
                )

                # Pick the first available verifier entrypoint
                fn_name = None
                for candidate in [
                    "isCairoFactValid",
                    "is_valid",
                    "isValid",
                    "is_fact_valid",
                ]:
                    if candidate in contract.functions:
                        fn_name = candidate
                        break

                if not fn_name:
                    logger.error("Integrity verifier ABI missing expected entrypoint")
                    return False

                # Try calling with (fact_hash, is_mocked); if that fails, try single-arg
                is_mocked_int = 1 if is_mocked else 0
                try:
                    result = await contract.functions[fn_name].call(
                        fact_hash_int,
                        is_mocked_int,
                    )
                except Exception:
                    result = await contract.functions[fn_name].call(fact_hash_int)

                return bool(result[0]) if result else False

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
