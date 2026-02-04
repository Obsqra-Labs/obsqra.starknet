#!/usr/bin/env python3
"""
Test proof verification with stone6 setting.

This tests if Stone v3 generates proofs with stone6 semantics.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.api.routes.risk_engine import _canonical_integrity_pipeline
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


async def test_stone6_verification():
    """Test proof generation and verification with stone6 setting."""
    logger.info("=" * 80)
    logger.info("PHASE 1: TESTING STONE6 VERIFICATION")
    logger.info("=" * 80)
    logger.info(f"Current config: INTEGRITY_STONE_VERSION = {settings.INTEGRITY_STONE_VERSION}")
    logger.info("Hypothesis: Stone v3 generates stone6 proofs (includes n_verifier_friendly in hash)")
    logger.info("=" * 80)
    
    # Test metrics
    jediswap_metrics = {
        "utilization": 7500,
        "volatility": 3000,
        "liquidity": 1,
        "audit_score": 85,
        "age_days": 365,
    }
    
    ekubo_metrics = {
        "utilization": 6000,
        "volatility": 2500,
        "liquidity": 0,
        "audit_score": 90,
        "age_days": 500,
    }
    
    try:
        import time
        start_time = time.time()
        
        logger.info("Generating proof with Stone v3 (will verify as stone6)...")
        fact_hash, proof_path, output_dir, proof_hash = await _canonical_integrity_pipeline(
            jediswap_metrics,
            ekubo_metrics,
        )
        
        elapsed = time.time() - start_time
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("PROOF GENERATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Proof path: {proof_path}")
        logger.info(f"Time elapsed: {elapsed:.2f}s")
        logger.info("")
        
        # Check verification result
        if fact_hash:
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: OODS PASSED WITH STONE6!")
            logger.info("=" * 80)
            logger.info(f"Fact hash: {hex(fact_hash)}")
            logger.info("")
            logger.info("🎯 CONCLUSION: Stone v3 generates stone6 proofs")
            logger.info("   → Keep INTEGRITY_STONE_VERSION = 'stone6'")
            logger.info("   → Stone v3 = stone6 behavior (includes n_verifier_friendly in hash)")
            return True
        else:
            logger.warning("")
            logger.warning("=" * 80)
            logger.warning("⚠️  OODS STILL FAILING WITH STONE6")
            logger.warning("=" * 80)
            logger.warning("This means:")
            logger.warning("  - Either stone6 verifier not registered in FactRegistry")
            logger.warning("  - Or Stone v3 ≠ stone6 (different issue)")
            logger.warning("")
            logger.warning("Next: Check Phase 2 (stone6 verifier registration)")
            return False
            
    except Exception as e:
        logger.error("")
        logger.error("=" * 80)
        logger.error("❌ PROOF GENERATION FAILED")
        logger.error("=" * 80)
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_stone6_verification())
    sys.exit(0 if success else 1)
