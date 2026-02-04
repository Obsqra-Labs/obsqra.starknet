#!/bin/bash
# Comprehensive E2E Test Suite for Trustless On-Chain Agent v4
# Run all tests sequentially with results logging

set -e

cd /opt/obsqra.starknet

echo "========================================================================"
echo " TRUSTLESS ON-CHAIN AGENT - COMPREHENSIVE E2E TEST SUITE"
echo "========================================================================"
echo ""
echo "This suite tests the fundamental shift from verifiable AI to trustless"
echo "on-chain agent infrastructure with:"
echo "  - STEP 0.5: Model version enforcement"
echo "  - STEP 0.6: User constraint signatures"
echo "  - Permissionless execution capability"
echo ""
echo "⏱  Estimated time: 30-60 minutes (proof generation is slow)"
echo ""
echo "========================================================================"

# Check backend
echo ""
echo "🔍 Checking backend..."
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running on port 8001"
    echo "   Start with: cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001"
    exit 1
fi

# Create results directory
mkdir -p test_results
RESULTS_DIR="test_results/e2e_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo ""
echo "📁 Results will be saved to: $RESULTS_DIR"
echo ""

# Test 1: DAO Constraints PASS
echo "========================================================================"
echo "TEST 1: DAO Constraints PASS (allocations within limits)"
echo "========================================================================"
python3 test_e2e_dao_pass.py 2>&1 | tee "$RESULTS_DIR/1_dao_pass.log"
TEST1_EXIT=$?

echo ""
echo "⏸  Waiting 10s before next test..."
sleep 10

# Test 2: DAO Constraints FAIL
echo "========================================================================"
echo "TEST 2: DAO Constraints FAIL (allocations violate limits)"
echo "========================================================================"
python3 test_e2e_dao_fail.py 2>&1 | tee "$RESULTS_DIR/2_dao_fail.log"
TEST2_EXIT=$?

echo ""
echo "⏸  Waiting 10s before next test..."
sleep 10

# Test 3: Model Version Enforcement
echo "========================================================================"
echo "TEST 3: Model Version Enforcement (STEP 0.5)"
echo "========================================================================"
python3 test_e2e_model_version.py 2>&1 | tee "$RESULTS_DIR/3_model_version.log"
TEST3_EXIT=$?

echo ""
echo "⏸  Waiting 10s before next test..."
sleep 10

# Test 4: Constraint Signatures
echo "========================================================================"
echo "TEST 4: Constraint Signatures (STEP 0.6)"
echo "========================================================================"
python3 test_e2e_constraint_signature.py 2>&1 | tee "$RESULTS_DIR/4_constraint_sig.log"
TEST4_EXIT=$?

# Final Summary
echo ""
echo "========================================================================"
echo " TEST SUITE COMPLETE"
echo "========================================================================"
echo ""
echo "Results:"
echo "  Test 1 (DAO PASS): $([ $TEST1_EXIT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "  Test 2 (DAO FAIL): $([ $TEST2_EXIT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "  Test 3 (Model Version): $([ $TEST3_EXIT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "  Test 4 (Constraint Sig): $([ $TEST4_EXIT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo ""
echo "📁 Detailed logs: $RESULTS_DIR/"
echo ""

# Check if all passed
if [ $TEST1_EXIT -eq 0 ] && [ $TEST2_EXIT -eq 0 ] && [ $TEST3_EXIT -eq 0 ] && [ $TEST4_EXIT -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo "   Trustless on-chain agent is fully verified."
    exit 0
else
    echo "⚠️  Some tests failed - see logs for details."
    exit 1
fi
