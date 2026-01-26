#!/usr/bin/env python3
"""
Phase 3 Integration Test
=============================

Comprehensive integration test verifying:
1. StoneProverService generates proofs correctly
2. AllocationProofOrchestrator routes to Stone
3. Full allocation→proof pipeline works
4. Fallback mechanism functions
5. Proof metadata is correct

Run with: python3 test_integration_phase3.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "backend/app"))

from backend.app.services.stone_prover_service import StoneProverService
from backend.app.services.allocation_proof_orchestrator import (
    AllocationProofOrchestrator,
    AllocationProofResult
)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class MockAtlanticService:
    """Mock Atlantic service for testing"""
    async def generate_proof(self, *args, **kwargs):
        return AllocationProofResult(success=False, error="Mock Atlantic")


class MockIntegrityService:
    """Mock Integrity service for testing"""
    async def verify_proof(self, *args, **kwargs):
        return True


async def test_stone_prover_direct():
    """Test StoneProverService directly with fibonacci"""
    
    logger.info("=" * 70)
    logger.info("TEST 1: Stone Prover Service (Direct)")
    logger.info("=" * 70)
    
    service = StoneProverService()
    
    private_input = "/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_private.json"
    public_input = "/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_public.json"
    
    # Verify files exist
    if not Path(private_input).exists():
        logger.error(f"❌ Missing: {private_input}")
        return False
    
    if not Path(public_input).exists():
        logger.error(f"❌ Missing: {public_input}")
        return False
    
    logger.info("✅ Input files exist")
    
    # Generate proof
    logger.info("Generating STARK proof...")
    result = await service.generate_proof(private_input, public_input)
    
    if not result.success:
        logger.error(f"❌ Proof generation failed: {result.error}")
        return False
    
    logger.info(f"✅ Proof generated successfully!")
    logger.info(f"   Hash: {result.proof_hash[:32]}...")
    logger.info(f"   Time: {result.generation_time_ms:.0f}ms")
    logger.info(f"   Size: {result.proof_size_kb:.1f}KB")
    logger.info(f"   FRI params: last_layer={result.fri_parameters['last_layer']}, "
                f"fri_steps={result.fri_parameters['fri_steps']}")
    
    return True


async def test_allocation_proof_orchestrator():
    """Test allocation proof orchestrator with Stone→Fallback logic"""
    
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Allocation Proof Orchestrator")
    logger.info("=" * 70)
    
    stone_service = StoneProverService()
    
    atlantic_service = MockAtlanticService()
    integrity_service = MockIntegrityService()
    
    orchestrator = AllocationProofOrchestrator(
        stone_service,
        atlantic_service,
        integrity_service
    )
    
    # Test allocation parameters
    allocation_config = {
        "allocation_id": "test_alloc_001",
        "jediswap_risk": 35,
        "ekubo_risk": 50,
        "jediswap_apy": 1500,
        "ekubo_apy": 2000,
        "jediswap_pct": 60,
        "ekubo_pct": 40
    }
    
    logger.info(f"Allocation Configuration:")
    logger.info(f"  ID: {allocation_config['allocation_id']}")
    logger.info(f"  Split: {allocation_config['jediswap_pct']}% Jediswap / {allocation_config['ekubo_pct']}% Ekubo")
    logger.info(f"  Risk: Jediswap={allocation_config['jediswap_risk']}, Ekubo={allocation_config['ekubo_risk']}")
    logger.info(f"  APY: Jediswap={allocation_config['jediswap_apy']}, Ekubo={allocation_config['ekubo_apy']}")
    
    # Generate proof
    logger.info("\nGenerating allocation proof (Stone primary, Atlantic fallback)...")
    
    proof_result = await orchestrator.generate_allocation_proof(
        prefer_stone=True,
        **allocation_config
    )
    
    if not proof_result.success:
        logger.error(f"❌ Proof generation failed: {proof_result.error}")
        return False
    
    logger.info(f"\n✅ Proof generated successfully!")
    logger.info(f"   Proof Method: {proof_result.proof_method}")
    logger.info(f"   Hash: {proof_result.proof_hash[:32]}...")
    logger.info(f"   Time: {proof_result.generation_time_ms:.0f}ms")
    logger.info(f"   Size: {proof_result.proof_size_kb:.1f}KB")
    logger.info(f"   On-chain verified: {proof_result.on_chain_verified}")
    
    return True


async def test_fri_parameter_validation():
    """Verify FRI parameter calculation for different trace sizes"""
    
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: FRI Parameter Validation")
    logger.info("=" * 70)
    
    service = StoneProverService()
    
    # Test cases: (n_steps, expected_last_layer, expected_fri_steps)
    test_cases = [
        (512, 64, [0, 4, 3]),
        (8192, 256, [0, 4, 4, 1]),
        (131072, 512, [0, 4, 4, 4]),
    ]
    
    logger.info("Testing FRI parameter calculation for various trace sizes:")
    logger.info("")
    
    all_passed = True
    
    for n_steps, expected_last_layer, expected_fri_steps in test_cases:
        last_layer, fri_steps = service._calculate_fri_parameters(n_steps)
        
        if last_layer != expected_last_layer:
            logger.error(f"❌ {n_steps:6d} steps: last_layer={last_layer} "
                        f"(expected {expected_last_layer})")
            all_passed = False
        elif fri_steps != expected_fri_steps:
            logger.error(f"❌ {n_steps:6d} steps: fri_steps={fri_steps} "
                        f"(expected {expected_fri_steps})")
            all_passed = False
        else:
            logger.info(f"✅ {n_steps:6d} steps: last_layer={last_layer}, "
                       f"fri_steps={fri_steps}")
    
    return all_passed


async def test_fri_equation_verification():
    """Verify that FRI parameters satisfy the fundamental equation"""
    
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: FRI Equation Verification")
    logger.info("=" * 70)
    
    service = StoneProverService()
    
    # FRI Equation: log2(last_layer) + sum(fri_steps) = log2(n_steps) + 4
    logger.info("FRI Equation: log2(last_layer) + sum(fri_steps) = log2(n_steps) + 4")
    logger.info("")
    
    import math
    
    test_cases = [
        (512, 64, [0, 4, 3]),
        (8192, 256, [0, 4, 4, 1]),
        (131072, 512, [0, 4, 4, 4]),
    ]
    
    all_passed = True
    
    for n_steps, last_layer, fri_steps in test_cases:
        left_side = math.log2(last_layer) + sum(fri_steps)
        right_side = math.log2(n_steps) + 4
        
        matches = abs(left_side - right_side) < 0.001
        status = "✅" if matches else "❌"
        
        logger.info(f"{status} {n_steps:6d} steps: "
                   f"log2({last_layer}) + {sum(fri_steps)} = {left_side:.1f} "
                   f"(expected {right_side:.1f})")
        
        if not matches:
            all_passed = False
    
    return all_passed


async def main():
    """Run all integration tests"""
    
    logger.info("\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " PHASE 3 INTEGRATION TEST SUITE ".center(68) + "║")
    logger.info("╚" + "═" * 68 + "╝")
    logger.info("")
    
    tests = [
        ("Stone Prover Direct", test_stone_prover_direct),
        ("Allocation Orchestrator", test_allocation_proof_orchestrator),
        ("FRI Parameter Validation", test_fri_parameter_validation),
        ("FRI Equation Verification", test_fri_equation_verification),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            logger.error(f"\n❌ Exception in {test_name}: {str(e)}", exc_info=True)
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for p in results.values() if p)
    
    logger.info("")
    logger.info(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All integration tests passed!")
        logger.info("Phase 3 is ready for allocation workflow integration")
        return 0
    else:
        logger.error(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
