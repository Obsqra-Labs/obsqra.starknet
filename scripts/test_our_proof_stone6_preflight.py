#!/usr/bin/env python3
"""
Test our generated proof with stone6 using preflight call (no wallet needed).

This checks if OODS passes with stone6 verification.
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
    """Encode an ASCII string into a felt."""
    return int.from_bytes(value.encode("ascii"), "big")


async def test_our_proof_stone6():
    """Test our generated proof with stone6 verification."""
    repo_root = Path(__file__).resolve().parent.parent
    
    # Find our latest proof
    proof_path = None
    temp_dirs = sorted(Path("/tmp").glob("canonical_integrity_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if temp_dirs:
        proof_path = temp_dirs[0] / "risk_proof.json"
    
    if not proof_path or not proof_path.exists():
        logger.error("Could not find our generated proof")
        logger.info("Run test_stone6_verification.py first to generate a proof")
        return False
    
    logger.info(f"Loading our proof from {proof_path}")
    
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
        calldata_body = serialize_stone_proof(proof_path, serializer_bin)
        logger.info(f"Serialized proof: {len(calldata_body)} felts")
    except Exception as e:
        logger.error(f"Failed to serialize proof: {e}", exc_info=True)
        return False
    
    # Prefix verifier config (stone6)
    calldata = [
        _string_to_felt("recursive"),  # layout
        _string_to_felt("keccak_160_lsb"),  # hasher
        _string_to_felt("stone6"),  # stone_version
        _string_to_felt("strict"),  # memory_verification
        *calldata_body,
    ]
    
    logger.info(f"Total calldata length: {len(calldata)} felts")
    logger.info("Verifier config: layout=recursive, hasher=keccak_160_lsb, stone_version=stone6, memory=strict")
    
    # Initialize Integrity service
    rpc_url = settings.STARKNET_RPC_URL
    network = settings.STARKNET_NETWORK
    
    integrity = IntegrityService(rpc_url=rpc_url, network=network)
    
    # Use preflight call (doesn't require wallet)
    logger.info("Testing with preflight call (no wallet needed)...")
    try:
        # Use verify_with_calldata which does preflight check
        result = await integrity.verify_with_calldata(calldata)
        
        if result:
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: Preflight call passed!")
            logger.info("=" * 80)
            logger.info("DECISION: Our proof verifies with stone6!")
            logger.info("   → Stone v3 generates stone6 proofs")
            logger.info("   → Keep INTEGRITY_STONE_VERSION = 'stone6'")
            return True
        else:
            logger.error("=" * 80)
            logger.error("❌ ERROR: Preflight call failed")
            logger.error("=" * 80)
            logger.error("DECISION: Proof does not verify with stone6")
            logger.error("   → Check error logs above for OODS or other errors")
            return False
        
    except Exception as e:
        error_msg = str(e)
        logger.error("=" * 80)
        logger.error(f"❌ ERROR: Preflight call failed")
        logger.error("=" * 80)
        
        if "Invalid OODS" in error_msg:
            logger.error("DECISION: OODS still fails with stone6")
            logger.error("   → Stone v3 ≠ stone6, or different issue")
            logger.error("   → Next: Test Stone v2")
        elif "verifier not registered" in error_msg.lower():
            logger.error("DECISION: stone6 verifier not registered")
            logger.error("   → But canonical stone6 verified? Check error")
        else:
            logger.error(f"Error: {error_msg}")
        
        logger.exception("Full exception traceback:")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_our_proof_stone6())
    sys.exit(0 if success else 1)
