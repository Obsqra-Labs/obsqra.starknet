#!/usr/bin/env python3
"""
Test Integrity's canonical recursive example proof on-chain.

This script determines if the OODS issue is in our pipeline or verifier/deployment.
If canonical verifies → our pipeline issue
If canonical fails → verifier/deployment issue
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import get_settings
from app.services.integrity_service import IntegrityService
from app.services.proof_loader import serialize_stone_proof

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


def _string_to_felt(value: str) -> int:
    """Encode an ASCII string into a felt (same as verify-on-starknet.sh)."""
    return int.from_bytes(value.encode("ascii"), "big")


async def test_canonical_proof():
    """Test Integrity's canonical recursive example proof on-chain."""
    repo_root = Path(__file__).resolve().parent.parent
    
    # Path to canonical proof
    canonical_proof_path = (
        repo_root / "integrity" / "examples" / "proofs" / "recursive" /
        "cairo0_stone5_keccak_160_lsb_example_proof.json"
    )
    
    if not canonical_proof_path.exists():
        logger.error(f"Canonical proof not found at {canonical_proof_path}")
        return False
    
    logger.info(f"Loading canonical proof from {canonical_proof_path}")
    
    # Load proof JSON
    with open(canonical_proof_path, 'r') as f:
        proof_data = json.load(f)
    
    logger.info("Canonical proof loaded successfully")
    logger.info(f"Proof structure: {list(proof_data.keys())}")
    
    # Check proof structure
    if "public_input" in proof_data:
        public_input = proof_data["public_input"]
        logger.info(f"Public input layout: {public_input.get('layout', 'N/A')}")
        logger.info(f"Public input n_steps: {public_input.get('n_steps', 'N/A')}")
    
    # Serialize proof
    serializer_bin = Path(
        settings.INTEGRITY_PROOF_SERIALIZER_BIN
        or repo_root / "integrity" / "target" / "release" / "proof_serializer"
    )
    
    if not serializer_bin.exists():
        logger.error(f"proof_serializer binary not found at {serializer_bin}")
        logger.info("Build it with: cd integrity && cargo build --release --bin proof_serializer")
        return False
    
    logger.info(f"Serializing proof using {serializer_bin}")
    try:
        calldata_body = serialize_stone_proof(canonical_proof_path, serializer_bin)
        logger.info(f"Serialized proof: {len(calldata_body)} felts")
    except Exception as e:
        logger.error(f"Failed to serialize proof: {e}", exc_info=True)
        return False
    
    # Prefix verifier config (matching canonical settings)
    calldata = [
        _string_to_felt(settings.INTEGRITY_LAYOUT),  # "recursive"
        _string_to_felt(settings.INTEGRITY_HASHER),  # "keccak_160_lsb"
        _string_to_felt(settings.INTEGRITY_STONE_VERSION),  # "stone5"
        _string_to_felt(settings.INTEGRITY_MEMORY_VERIFICATION),  # "strict"
        *calldata_body,
    ]
    
    logger.info(f"Total calldata length: {len(calldata)} felts")
    logger.info(f"Verifier config: layout={settings.INTEGRITY_LAYOUT}, "
                f"hasher={settings.INTEGRITY_HASHER}, "
                f"stone_version={settings.INTEGRITY_STONE_VERSION}, "
                f"memory={settings.INTEGRITY_MEMORY_VERIFICATION}")
    
    # Initialize Integrity service with PUBLIC FactRegistry (has verifiers registered)
    # Public FactRegistry: 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
    rpc_url = settings.STARKNET_RPC_URL
    network = settings.STARKNET_NETWORK
    
    logger.info(f"Initializing Integrity service for {network} (RPC: {rpc_url})")
    logger.info("Using PUBLIC FactRegistry (0x4ce7851f...) - has verifiers registered")
    
    # Temporarily override to use public FactRegistry
    import app.services.integrity_service as integrity_module
    
    # Save original
    original_verifier = integrity_module.INTEGRITY_VERIFIER_SEPOLIA
    # Use public FactRegistry (from Integrity docs: has all verifiers registered)
    PUBLIC_FACT_REGISTRY = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
    integrity_module.INTEGRITY_VERIFIER_SEPOLIA = PUBLIC_FACT_REGISTRY
    
    try:
        integrity = IntegrityService(rpc_url=rpc_url, network=network)
    finally:
        # Restore original
        integrity_module.INTEGRITY_VERIFIER_SEPOLIA = original_verifier
    
    # Attempt on-chain verification
    logger.info("Attempting on-chain verification of canonical proof...")
    try:
        result = await integrity.verify_with_calldata(calldata)
        
        if result:
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: Canonical proof verified on-chain!")
            logger.info("=" * 80)
            logger.info("DECISION: Issue is in our proof generation/serialization pipeline")
            logger.info("Next steps: Compare our proof parameters with canonical, check Stone commit")
            return True
        else:
            logger.error("=" * 80)
            logger.error("❌ FAILURE: Canonical proof failed on-chain verification")
            logger.error("=" * 80)
            logger.error("DECISION: Issue is in verifier contract/config/address or serializer")
            logger.error("Next steps: Check verifier registration, serializer version, contract address")
            return False
            
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR: Exception during verification: {e}")
        logger.error("=" * 80)
        logger.error("DECISION: Cannot determine - check error details above")
        logger.error("Next steps: Fix error and retry")
        logger.exception("Full exception traceback:")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_canonical_proof())
    sys.exit(0 if success else 1)
