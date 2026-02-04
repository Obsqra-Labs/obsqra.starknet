#!/usr/bin/env python3
"""
Test proof generation with n_steps=16384 (matching canonical example).

This eliminates trace size as a variable to isolate if the issue is:
- Trace-size dependent, OR
- Stone version/AIR config dependent
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.api.routes.risk_engine import _canonical_integrity_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_matching_n_steps():
    """Test proof generation with n_steps matching canonical (16384)."""
    logger.info("=" * 80)
    logger.info("TESTING WITH MATCHING N_STEPS (16384)")
    logger.info("=" * 80)
    logger.info("Canonical example has n_steps=16384")
    logger.info("This test uses minimal input to achieve n_steps=16384")
    logger.info("=" * 80)
    
    # Use minimal metrics to reduce trace size
    # Note: We can't directly control n_steps, but we can use minimal inputs
    # to try to get closer to 16384
    jediswap_metrics = {
        "utilization": 1000,  # Minimal values
        "volatility": 1000,
        "liquidity": 0,
        "audit_score": 50,
        "age_days": 1,
    }
    
    ekubo_metrics = {
        "utilization": 1000,
        "volatility": 1000,
        "liquidity": 0,
        "audit_score": 50,
        "age_days": 1,
    }
    
    try:
        import time
        start_time = time.time()
        
        logger.info("Running canonical pipeline with minimal inputs...")
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
        
        # Check n_steps
        if proof_path and Path(proof_path).exists():
            with open(proof_path, 'r') as f:
                proof_data = json.load(f)
            
            public_input = proof_data.get("public_input", {})
            n_steps = public_input.get("n_steps")
            
            logger.info("=" * 80)
            logger.info("PROOF ANALYSIS")
            logger.info("=" * 80)
            logger.info(f"n_steps: {n_steps}")
            logger.info(f"Expected: 16384 (canonical)")
            logger.info(f"Match: {'✅ YES' if n_steps == 16384 else '❌ NO'}")
            logger.info("")
            
            if n_steps == 16384:
                logger.info("✅ n_steps matches canonical!")
                logger.info("This eliminates trace size as a variable.")
            else:
                logger.warning(f"⚠️  n_steps is {n_steps}, not 16384")
                logger.warning("Trace size differs from canonical example.")
                logger.warning("This may still be a factor in OODS failure.")
        
        # Check verification result
        if fact_hash:
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ ON-CHAIN VERIFICATION: SUCCESS")
            logger.info("=" * 80)
            logger.info(f"Fact hash: {hex(fact_hash)}")
            logger.info("OODS validation: PASSED")
            logger.info("")
            if n_steps == 16384:
                logger.info("🎯 CONCLUSION: Issue was trace-size dependent!")
            else:
                logger.info("🎯 CONCLUSION: Issue is NOT trace-size dependent (n_steps differs)")
            return True
        else:
            logger.warning("")
            logger.warning("=" * 80)
            logger.warning("⚠️  ON-CHAIN VERIFICATION: FAILED")
            logger.warning("=" * 80)
            logger.warning("OODS still failing")
            if n_steps == 16384:
                logger.warning("🎯 CONCLUSION: Issue is NOT trace-size dependent")
                logger.warning("   → Most likely Stone version/AIR config mismatch")
            else:
                logger.warning("🎯 CONCLUSION: Cannot determine (n_steps differs)")
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
    success = asyncio.run(test_matching_n_steps())
    sys.exit(0 if success else 1)
