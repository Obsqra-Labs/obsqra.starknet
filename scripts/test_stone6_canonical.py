#!/usr/bin/env python3
"""
Test Integrity's canonical stone6 example proof on-chain.

This verifies if stone6 verifier is registered in public FactRegistry.
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


async def test_stone6_canonical():
    """Test Integrity's canonical stone6 recursive example proof on-chain."""
    repo_root = Path(__file__).resolve().parent.parent
    
    # Path to canonical stone6 proof
    canonical_stone6_proof = (
        repo_root / "integrity" / "examples" / "proofs" / "recursive" /
        "cairo0_stone6_keccak_160_lsb_example_proof.json"
    )
    
    if not canonical_stone6_proof.exists():
        logger.warning(f"Canonical stone6 proof not found at {canonical_stone6_proof}")
        logger.info("Checking for alternative stone6 examples...")
        # Try to find any stone6 example
        stone6_examples = list(repo_root.glob("integrity/examples/proofs/**/cairo0_stone6_keccak_160_lsb_example_proof.json"))
        if stone6_examples:
            canonical_stone6_proof = stone6_examples[0]
            logger.info(f"Found stone6 example at: {canonical_stone6_proof}")
        else:
            logger.error("No stone6 canonical examples found")
            return False
    
    logger.info(f"Loading canonical stone6 proof from {canonical_stone6_proof}")
    
    # Load proof JSON
    with open(canonical_stone6_proof, 'r') as f:
        proof_data = json.load(f)
    
    logger.info("Canonical stone6 proof loaded successfully")
    
    # Serialize proof
    serializer_bin = Path(
        settings.INTEGRITY_PROOF_SERIALIZER_BIN
        or repo_root / "integrity" / "target" / "release" / "proof_serializer"
    )
    
    if not serializer_bin.exists():
        logger.error(f"proof_serializer binary not found at {serializer_bin}")
        return False
    
    logger.info(f"Serializing proof using {serializer_bin}")
    try:
        calldata_body = serialize_stone_proof(canonical_stone6_proof, serializer_bin)
        logger.info(f"Serialized proof: {len(calldata_body)} felts")
    except Exception as e:
        logger.error(f"Failed to serialize proof: {e}", exc_info=True)
        return False
    
    # Prefix verifier config (stone6 settings)
    calldata = [
        _string_to_felt("recursive"),  # layout
        _string_to_felt("keccak_160_lsb"),  # hasher
        _string_to_felt("stone6"),  # stone_version
        _string_to_felt("strict"),  # memory_verification
        *calldata_body,
    ]
    
    logger.info(f"Total calldata length: {len(calldata)} felts")
    logger.info("Verifier config: layout=recursive, hasher=keccak_160_lsb, stone_version=stone6, memory=strict")
    
    # Initialize Integrity service with PUBLIC FactRegistry
    rpc_url = settings.STARKNET_RPC_URL
    network = settings.STARKNET_NETWORK
    
    logger.info(f"Initializing Integrity service for {network} (RPC: {rpc_url})")
    logger.info("Using PUBLIC FactRegistry (0x4ce7851f...) - checking if stone6 verifier is registered")
    
    integrity = IntegrityService(rpc_url=rpc_url, network=network)
    
    # Attempt on-chain verification
    logger.info("Attempting on-chain verification of canonical stone6 proof...")
    try:
        result = await integrity.verify_with_calldata(calldata)
        
        if result:
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: Canonical stone6 proof verified on-chain!")
            logger.info("=" * 80)
            logger.info("DECISION: stone6 verifier IS registered in public FactRegistry")
            logger.info("Next: Stone v3 might still need different fix, or stone6 verifier works")
            return True
        else:
            logger.error("=" * 80)
            logger.error("❌ FAILURE: Canonical stone6 proof failed on-chain verification")
            logger.error("=" * 80)
            logger.error("DECISION: stone6 verifier may NOT be registered, or proof is invalid")
            logger.error("Next: Revert to stone5 and test Stone v2")
            return False
            
    except Exception as e:
        error_msg = str(e)
        logger.error("=" * 80)
        logger.error(f"❌ ERROR: Exception during verification: {e}")
        logger.error("=" * 80)
        
        if "Invalid OODS" in error_msg:
            logger.error("DECISION: stone6 verifier registered but OODS fails")
            logger.error("   → Stone v3 ≠ stone6, or different issue")
        elif "verifier not registered" in error_msg.lower():
            logger.error("DECISION: stone6 verifier NOT registered in public FactRegistry")
            logger.error("   → Revert to stone5, test Stone v2")
        else:
            logger.error("DECISION: Cannot determine - check error details above")
        
        logger.exception("Full exception traceback:")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_stone6_canonical())
    sys.exit(0 if success else 1)
