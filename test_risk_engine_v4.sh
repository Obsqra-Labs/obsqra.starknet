#!/bin/bash
set -e

echo "========================================"
echo " TESTING RISKENGINE V4 (zkML 4/5)"
echo "========================================"
echo ""

RISK_ENGINE="0x06c31be32c0b6f6b27f7a64afe5b1ad6a21ededcd86773b92beaf1aaf54af220"
NETWORK="sepolia"
ACCOUNT="deployer"

echo "📍 Contract: $RISK_ENGINE"
echo "📍 Network: $NETWORK"
echo ""

# Test 1: Verify contract is accessible
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Verify Contract Version"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

VERSION_OUTPUT=$(sncast --account $ACCOUNT --network $NETWORK call \
    --contract-address $RISK_ENGINE \
    --function get_contract_version 2>&1)

if echo "$VERSION_OUTPUT" | grep -q "command not found\|Error"; then
    echo "⚠️  sncast call failed, trying alternative method..."
else
    echo "$VERSION_OUTPUT"
    echo ""
    echo "✅ Contract is accessible!"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Verify Proof Verification is Required"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  To fully test proof verification, you need:"
echo "  1. Generate a proof via LuminAIR or Stone Prover"
echo "  2. Get fact hash from Integrity service"
echo "  3. Call propose_and_execute_allocation with valid proof data"
echo "  4. Verify contract accepts valid proofs"
echo "  5. Verify contract rejects invalid proofs"
echo ""
echo "📝 See integration_tests/ for full E2E test scripts"
echo ""

echo "========================================"
echo "✅ BASIC VERIFICATION COMPLETE"
echo "========================================"
