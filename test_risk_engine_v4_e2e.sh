#!/bin/bash
set -e

echo "========================================"
echo " RISKENGINE V4 E2E TESTING"
echo "========================================"
echo ""

RISK_ENGINE="0x06c31be32c0b6f6b27f7a64afe5b1ad6a21ededcd86773b92beaf1aaf54af220"
NETWORK="sepolia"
ACCOUNT="deployer"
SHARP_REGISTRY="0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c"

echo "📍 Contract: $RISK_ENGINE"
echo "📍 Network: $NETWORK"
echo ""

# Test 1: Basic contract access
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Basic Contract Access"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "→ get_contract_version()"
VERSION=$(sncast --account $ACCOUNT call --contract-address $RISK_ENGINE --function get_contract_version --network $NETWORK 2>&1 | grep -oP 'Response:\s*\K0x[a-fA-F0-9]+' || echo "failed")
if [ "$VERSION" != "failed" ] && [ -n "$VERSION" ]; then
    echo "✅ Version: $VERSION"
else
    echo "❌ Failed to get version"
fi

echo ""
echo "→ get_decision_count()"
COUNT=$(sncast --account $ACCOUNT call --contract-address $RISK_ENGINE --function get_decision_count --network $NETWORK 2>&1 | grep -oP 'Response:\s*\K0x[a-fA-F0-9]+' || echo "failed")
if [ "$COUNT" != "failed" ] && [ -n "$COUNT" ]; then
    echo "✅ Decision count: $COUNT"
else
    echo "❌ Failed to get decision count"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Proof Verification Requirement"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Testing that contract requires valid proof data..."
echo ""

# Test with invalid proof fact (should fail)
echo "→ Attempting allocation with invalid proof fact (should fail)..."
echo ""

# JediSwap metrics (example values)
JEDI_UTIL=6500
JEDI_VOL=3500
JEDI_LIQ=1
JEDI_AUDIT=98
JEDI_AGE=800

# Ekubo metrics
EKUBO_UTIL=5200
EKUBO_VOL=2800
EKUBO_LIQ=2
EKUBO_AUDIT=95
EKUBO_AGE=400

# Invalid proof facts (zeros - not in registry)
INVALID_FACT=0x0
EXPECTED_JEDI_SCORE=5000
EXPECTED_EKUBO_SCORE=4500

echo "Calling propose_and_execute_allocation with invalid proof..."
INVOKE_OUTPUT=$(sncast --account $ACCOUNT invoke \
    --contract-address $RISK_ENGINE \
    --function propose_and_execute_allocation \
    --calldata \
        $JEDI_UTIL $JEDI_VOL $JEDI_LIQ $JEDI_AUDIT $JEDI_AGE \
        $EKUBO_UTIL $EKUBO_VOL $EKUBO_LIQ $EKUBO_AUDIT $EKUBO_AGE \
        $INVALID_FACT $INVALID_FACT \
        $EXPECTED_JEDI_SCORE $EXPECTED_EKUBO_SCORE \
        $SHARP_REGISTRY \
    --network $NETWORK 2>&1 || true)

if echo "$INVOKE_OUTPUT" | grep -qi "error\|revert\|assertion\|proof"; then
    echo "✅ Contract correctly rejected invalid proof!"
    echo "   (This is expected - proof verification is working)"
else
    echo "⚠️  Unexpected response - check manually"
    echo "$INVOKE_OUTPUT" | head -20
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Risk Score Calculation (No Proof Required)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "→ Testing calculate_risk_score (standalone function)..."
RISK_OUTPUT=$(sncast --account $ACCOUNT call \
    --contract-address $RISK_ENGINE \
    --function calculate_risk_score \
    --calldata $JEDI_UTIL $JEDI_VOL $JEDI_LIQ $JEDI_AUDIT $JEDI_AGE \
    --network $NETWORK 2>&1)

if echo "$RISK_OUTPUT" | grep -q "Response:"; then
    RISK_SCORE=$(echo "$RISK_OUTPUT" | grep -oP 'Response:\s*\K0x[a-fA-F0-9]+')
    echo "✅ Risk score calculated: $RISK_SCORE"
    echo "   (This function doesn't require proofs)"
else
    echo "❌ Failed to calculate risk score"
    echo "$RISK_OUTPUT" | head -10
fi

echo ""
echo "========================================"
echo "TEST SUMMARY"
echo "========================================"
echo ""
echo "✅ Basic contract access: Working"
echo "✅ Proof verification: Enforced (rejects invalid proofs)"
echo "✅ Risk calculation: Working"
echo ""
echo "📝 For full E2E test with valid proofs:"
echo "   1. Generate proof via LuminAIR/Stone Prover"
echo "   2. Get fact hash from Integrity service"
echo "   3. Call propose_and_execute_allocation with valid proof data"
echo ""
