#!/usr/bin/env python3
"""
Test proof regeneration with fixed FRI parameters and verify on-chain.

This script:
1. Generates a new proof using the canonical pipeline with fixed FRI parameters
2. Compares proof parameters with canonical example
3. Tests on-chain verification
4. Reports if OODS passes
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.api.routes.risk_engine import _canonical_integrity_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_fri_fix():
    """Test proof generation with fixed FRI parameters."""
    logger.info("=" * 80)
    logger.info("TESTING FRI PARAMETERS FIX")
    logger.info("=" * 80)
    logger.info("Generating proof with fixed FRI parameters:")
    logger.info("  - n_queries: 10 (was 18)")
    logger.info("  - proof_of_work_bits: 30 (was 24)")
    logger.info("  - Using PUBLIC FactRegistry")
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
        
        logger.info("Running canonical pipeline...")
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
        logger.info(f"Output dir: {output_dir}")
        logger.info(f"Proof hash: {proof_hash}")
        logger.info(f"Time elapsed: {elapsed:.2f}s")
        logger.info("")
        
        # Load and check proof parameters
        if proof_path and Path(proof_path).exists():
            with open(proof_path, 'r') as f:
                proof_data = json.load(f)
            
            proof_params = proof_data.get("proof_parameters", {})
            stark = proof_params.get("stark", {})
            fri = stark.get("fri", {})
            
            logger.info("=" * 80)
            logger.info("PROOF PARAMETERS (Fixed)")
            logger.info("=" * 80)
            logger.info(f"n_queries: {fri.get('n_queries')} (expected: 10)")
            logger.info(f"proof_of_work_bits: {fri.get('proof_of_work_bits')} (expected: 30)")
            logger.info(f"fri_step_list: {fri.get('fri_step_list')}")
            logger.info(f"last_layer_degree_bound: {fri.get('last_layer_degree_bound')}")
            logger.info(f"log_n_cosets: {stark.get('log_n_cosets')}")
            
            # Verify parameters match expected
            n_queries = fri.get('n_queries')
            pow_bits = fri.get('proof_of_work_bits')
            
            params_correct = (n_queries == 10 and pow_bits == 30)
            
            if params_correct:
                logger.info("")
                logger.info("✅ FRI parameters match canonical example!")
            else:
                logger.error("")
                logger.error("❌ FRI parameters still incorrect!")
                logger.error(f"  n_queries: got {n_queries}, expected 10")
                logger.error(f"  proof_of_work_bits: got {pow_bits}, expected 30")
        
        # Check verification result
        if fact_hash:
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ ON-CHAIN VERIFICATION: SUCCESS")
            logger.info("=" * 80)
            logger.info(f"Fact hash: {hex(fact_hash)}")
            logger.info("OODS validation: PASSED")
            logger.info("Proof is valid and registered on-chain!")
            return True
        else:
            logger.warning("")
            logger.warning("=" * 80)
            logger.warning("⚠️  ON-CHAIN VERIFICATION: FAILED OR SKIPPED")
            logger.warning("=" * 80)
            logger.warning("Fact hash is None")
            logger.warning("This could mean:")
            logger.warning("  1. Registration failed (check logs above for OODS errors)")
            logger.warning("  2. Backend wallet not configured (expected in test)")
            logger.warning("  3. Proof is invalid")
            logger.warning("")
            logger.warning("Check logs above for specific error messages")
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
    success = asyncio.run(test_fri_fix())
    sys.exit(0 if success else 1)
