#!/usr/bin/env python3
"""
Phase 3.3: End-to-End Allocation Integration Tests

Tests the complete workflow: allocation → trace → proof → storage
"""

import asyncio
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "backend/app"))

from backend.app.services.stone_prover_service import StoneProverService
from backend.app.services.cairo_trace_generator_v2 import AllocationToTraceAdapter
from backend.app.services.allocation_proposal_service import AllocationProposalService

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class MockAtlanticService:
    async def generate_proof(self, *args, **kwargs):
        return None


class MockIntegrityService:
    async def verify_proof(self, *args, **kwargs):
        return True


async def test_e2e_allocation_workflow():
    """Test complete allocation workflow"""
    
    logger.info("=" * 70)
    logger.info("TEST 1: Complete Allocation Workflow")
    logger.info("=" * 70)
    
    # Initialize services
    stone_service = StoneProverService()
    atlantic_service = MockAtlanticService()
    trace_generator = AllocationToTraceAdapter()
    integrity_service = MockIntegrityService()
    
    # Create allocation service
    allocation_service = AllocationProposalService(
        stone_service=stone_service,
        atlantic_service=atlantic_service,
        trace_generator=trace_generator,
        integrity_service=integrity_service,
        db_session=None  # No database for test
    )
    
    # Create allocation
    logger.info("")
    logger.info("Creating allocation proposal...")
    
    result = await allocation_service.create_allocation_proposal(
        jediswap_risk=35,
        ekubo_risk=50,
        jediswap_apy=1500,
        ekubo_apy=2000,
        jediswap_pct=60,
        ekubo_pct=40,
        prefer_stone=True
    )
    
    # Validate result
    if not result.get("success"):
        logger.error(f"❌ Workflow failed: {result.get('error')}")
        return False
    
    logger.info("")
    logger.info("✅ Workflow completed successfully!")
    logger.info(f"   Allocation ID: {result.get('allocation_id')}")
    logger.info(f"   Allocation: {result.get('jediswap_pct')}% / {result.get('ekubo_pct')}%")
    logger.info(f"   Proof Hash: {result.get('proof_hash', '')[:32]}...")
    logger.info(f"   Proof Method: {result.get('proof_method')}")
    logger.info(f"   Proof Time: {result.get('proof_time_ms', 0):.0f}ms")
    logger.info(f"   Trace Steps: {result.get('trace_n_steps')}")
    logger.info(f"   Status: {result.get('status')}")
    
    return True


async def test_allocation_validation():
    """Test allocation parameter validation"""
    
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Allocation Parameter Validation")
    logger.info("=" * 70)
    
    allocation_service = AllocationProposalService(
        stone_service=None,
        atlantic_service=None,
        trace_generator=None,
        integrity_service=None
    )
    
    test_cases = [
        # (name, jediswap_pct, ekubo_pct, jediswap_risk, ekubo_risk, apy_j, apy_e, expected_valid)
        ("Valid allocation", 60, 40, 35, 50, 1500, 2000, True),
        ("Invalid sum (99%)", 50, 49, 35, 50, 1500, 2000, False),
        ("Invalid sum (101%)", 50, 51, 35, 50, 1500, 2000, False),
        ("Invalid risk (101)", 50, 50, 101, 50, 1500, 2000, False),
        ("Invalid APY (-1)", 50, 50, 35, 50, -1, 2000, False),
    ]
    
    all_passed = True
    
    for name, j_pct, e_pct, j_risk, e_risk, j_apy, e_apy, expected_valid in test_cases:
        valid = allocation_service._validate_allocation(
            j_pct, e_pct, j_risk, e_risk, j_apy, e_apy
        )
        
        status = "✅" if valid == expected_valid else "❌"
        result = "Valid" if valid else "Invalid"
        
        logger.info(f"{status} {name}: {result} (expected {'Valid' if expected_valid else 'Invalid'})")
        
        if valid != expected_valid:
            all_passed = False
    
    return all_passed


async def test_multiple_allocations():
    """Test generating multiple allocation proofs"""
    
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Multiple Allocations")
    logger.info("=" * 70)
    
    stone_service = StoneProverService()
    atlantic_service = MockAtlanticService()
    trace_generator = AllocationToTraceAdapter()
    
    allocation_service = AllocationProposalService(
        stone_service=stone_service,
        atlantic_service=atlantic_service,
        trace_generator=trace_generator,
        integrity_service=None
    )
    
    # Test different allocations
    allocations = [
        ("Conservative", 80, 20, 25, 30, 1000, 1500),
        ("Balanced", 60, 40, 35, 50, 1500, 2000),
        ("Aggressive", 40, 60, 45, 60, 2000, 2500),
    ]
    
    all_passed = True
    total_time = 0
    
    for name, j_pct, e_pct, j_risk, e_risk, j_apy, e_apy in allocations:
        logger.info(f"\nGenerating {name} allocation...")
        
        result = await allocation_service.create_allocation_proposal(
            jediswap_risk=j_risk,
            ekubo_risk=e_risk,
            jediswap_apy=j_apy,
            ekubo_apy=e_apy,
            jediswap_pct=j_pct,
            ekubo_pct=e_pct,
            prefer_stone=True
        )
        
        if not result.get("success"):
            logger.error(f"  ❌ Failed: {result.get('error')}")
            all_passed = False
        else:
            time_ms = result.get('proof_time_ms', 0)
            total_time += time_ms
            logger.info(f"  ✅ Success: {result.get('proof_method')}, {time_ms:.0f}ms")
    
    if all_passed:
        logger.info(f"\n✅ All {len(allocations)} allocations created successfully")
        logger.info(f"   Total proof time: {total_time:.0f}ms")
        logger.info(f"   Average time: {total_time / len(allocations):.0f}ms")
    
    return all_passed


async def test_workflow_with_errors():
    """Test workflow error handling"""
    
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: Error Handling")
    logger.info("=" * 70)
    
    # Create service with mock that simulates errors
    mock_stone = MagicMock()
    mock_stone.generate_proof = AsyncMock(return_value=MagicMock(success=True, proof_hash="test"))
    
    allocation_service = AllocationProposalService(
        stone_service=mock_stone,
        atlantic_service=None,
        trace_generator=AllocationToTraceAdapter(),
        integrity_service=None
    )
    
    # Test invalid allocation
    logger.info("Testing invalid allocation (sum != 100)...")
    result = await allocation_service.create_allocation_proposal(
        jediswap_risk=35,
        ekubo_risk=50,
        jediswap_apy=1500,
        ekubo_apy=2000,
        jediswap_pct=50,  # Should sum to 100 with ekubo_pct
        ekubo_pct=49,     # This makes sum = 99
        prefer_stone=True
    )
    
    if not result.get("success"):
        logger.info("  ✅ Correctly rejected invalid allocation")
        return True
    else:
        logger.error("  ❌ Failed to reject invalid allocation")
        return False


async def main():
    """Run all Phase 3.3 tests"""
    
    logger.info("\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " PHASE 3.3 END-TO-END INTEGRATION TESTS ".center(68) + "║")
    logger.info("╚" + "═" * 68 + "╝")
    logger.info("")
    
    tests = [
        ("E2E Allocation Workflow", test_e2e_allocation_workflow),
        ("Parameter Validation", test_allocation_validation),
        ("Multiple Allocations", test_multiple_allocations),
        ("Error Handling", test_workflow_with_errors),
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
        logger.info("\n🎉 All Phase 3.3 tests passed!")
        logger.info("End-to-end allocation workflow is complete")
        return 0
    else:
        logger.error(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
