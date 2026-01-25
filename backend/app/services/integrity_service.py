"""
Herodotus Integrity Verifier service for L2 proof verification

Verifies STARK proofs on Starknet L2 via the Integrity Verifier contract.
This provides always-on verification for every proof.
"""
import logging
import json
from typing import Optional
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Integrity Verifier contract addresses
INTEGRITY_VERIFIER_SEPOLIA = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
INTEGRITY_VERIFIER_MAINNET = 0xcc63a1e8e7824642b89fa6baf996b8ed21fa4707be90ef7605570ca8e4f00b


class IntegrityService:
    """L2 proof verification via Herodotus Integrity Verifier"""
    
    def __init__(self, rpc_url: str, network: str = "sepolia"):
        """
        Initialize Integrity Service
        
        Args:
            rpc_url: Starknet RPC URL
            network: Network name ('sepolia' or 'mainnet')
        """
        self.rpc_client = FullNodeClient(node_url=rpc_url)
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

    async def verify_proof_full_and_register_fact(
        self,
        verifier_config,
        stark_proof
    ) -> bool:
        """
        Pragmatic verification using Integrity's full proof entrypoint.
        Accepts either ABI-shaped dicts (preferred) or raw byte blobs (chunked to felts).
        """
        try:
            contract = await Contract.from_address(
                address=self.verifier_address,
                provider=self.rpc_client
            )

            # Preferred path: ABI-shaped dicts
            if isinstance(verifier_config, dict) and isinstance(stark_proof, dict):
                logger.info("Calling Integrity with structured verifier_config/stark_proof")
                result = await contract.functions["verify_proof_full_and_register_fact"].call(
                    verifier_config,
                    stark_proof,
                )
                logger.info("Integrity verify_proof_full_and_register_fact call returned OK (structured)")
                return True if result is not None else False

            # Allow JSON strings by decoding
            if isinstance(verifier_config, str):
                try:
                    verifier_config = json.loads(verifier_config)
                except Exception:
                    pass
            if isinstance(stark_proof, str):
                try:
                    stark_proof = json.loads(stark_proof)
                except Exception:
                    pass
            if isinstance(verifier_config, dict) and isinstance(stark_proof, dict):
                logger.info("Calling Integrity with JSON-decoded structs")
                result = await contract.functions["verify_proof_full_and_register_fact"].call(
                    verifier_config,
                    stark_proof,
                )
                logger.info("Integrity verify_proof_full_and_register_fact call returned OK (json)")
                return True if result is not None else False

            # Fallback: raw bytes -> felts
            verifier_felts = self._bytes_to_felts(verifier_config or b"")
            proof_felts = self._bytes_to_felts(stark_proof or b"")

            # Integrity expects (Span<felt>, Span<felt>)
            calldata = [
                len(verifier_felts),
                *verifier_felts,
                len(proof_felts),
                *proof_felts,
            ]

            fn = contract.functions.get("verify_proof_full_and_register_fact")
            if not fn:
                logger.error("Integrity contract missing verify_proof_full_and_register_fact")
                return False

            result = await fn.call(*calldata)
            logger.info("Integrity verify_proof_full_and_register_fact call returned OK (felts fallback)")
            return True if result is not None else False
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
            contract = await Contract.from_address(
                address=self.verifier_address,
                provider=self.rpc_client
            )
            fn = contract.functions.get("verify_proof_full_and_register_fact")
            if not fn:
                logger.error("Integrity contract missing verify_proof_full_and_register_fact")
                return False

            # Starknet.py expects args expanded; calldata is a flat list of felts.
            result = await fn.call(*calldata)
            logger.info("Integrity verify_proof_full_and_register_fact call returned OK (calldata path)")
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
            
            contract = await Contract.from_address(
                address=self.verifier_address,
                provider=self.rpc_client
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
                    is_mocked_int
                )
            except Exception:
                result = await contract.functions[fn_name].call(fact_hash_int)

            is_valid = bool(result[0]) if result else False
            
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
            contract = await Contract.from_address(
                address=self.verifier_address,
                provider=self.rpc_client
            )
            
            # Try to call get_verification if it exists
            # This is optional and may not be available on all contracts
            if "get_verification" in contract.functions:
                result = await contract.functions["get_verification"].call(fact_hash)
                return hex(result[0]) if result else None
            
            return None
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

