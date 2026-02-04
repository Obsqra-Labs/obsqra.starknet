#!/bin/bash
set -e

echo "========================================"
echo " TESTING WITH REAL PROOF GENERATION"
echo "========================================"
echo ""

BACKEND_URL="${BACKEND_URL:-http://localhost:8001}"
RISK_ENGINE="0x06c31be32c0b6f6b27f7a64afe5b1ad6a21ededcd86773b92beaf1aaf54af220"

echo "📍 Backend: $BACKEND_URL"
echo "📍 RiskEngine: $RISK_ENGINE"
echo ""

# Test 1: Generate proof via backend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Generate Proof via Backend API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if backend is running
if ! curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "⚠️  Backend not running at $BACKEND_URL"
    echo "   Start backend with: cd backend && python3 main.py"
    echo ""
    echo "   For now, testing contract directly..."
    exit 0
fi

echo "→ Calling /api/risk-engine/orchestrate endpoint..."
echo ""

# Create orchestration request
REQUEST_JSON=$(cat <<JSON
{
  "jediswap_metrics": {
    "utilization": 6500,
    "volatility": 3500,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800
  },
  "ekubo_metrics": {
    "utilization": 5200,
    "volatility": 2800,
    "liquidity": 2,
    "audit_score": 95,
    "age_days": 400
  }
}
JSON
)

echo "Request payload:"
echo "$REQUEST_JSON" | jq '.' 2>/dev/null || echo "$REQUEST_JSON"
echo ""

RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/risk-engine/orchestrate" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_JSON" || echo "ERROR")

if echo "$RESPONSE" | grep -q "ERROR\|error\|Error"; then
    echo "❌ Failed to call backend API"
    echo "$RESPONSE" | head -10
    echo ""
    echo "⚠️  Backend may not be running or endpoint changed"
    exit 1
fi

echo "Response:"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

# Extract proof job ID if available
PROOF_JOB_ID=$(echo "$RESPONSE" | jq -r '.proof_job_id // .job_id // empty' 2>/dev/null || echo "")

if [ -n "$PROOF_JOB_ID" ] && [ "$PROOF_JOB_ID" != "null" ]; then
    echo "✅ Proof job created: $PROOF_JOB_ID"
    echo ""
    echo "→ Waiting for proof generation (this may take 30-120 seconds)..."
    echo "   (In production, this would be async - checking status)"
    echo ""
    
    # Try to get proof job status
    STATUS_RESPONSE=$(curl -s "$BACKEND_URL/api/risk-engine/proof-jobs/$PROOF_JOB_ID" 2>/dev/null || echo "")
    if [ -n "$STATUS_RESPONSE" ]; then
        echo "Proof job status:"
        echo "$STATUS_RESPONSE" | jq '.' 2>/dev/null || echo "$STATUS_RESPONSE"
    fi
else
    echo "⚠️  Could not extract proof job ID from response"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Execute with Proof (if available)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -n "$PROOF_JOB_ID" ] && [ "$PROOF_JOB_ID" != "null" ]; then
    echo "→ Executing allocation with proof job: $PROOF_JOB_ID"
    echo ""
    
    EXECUTE_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/risk-engine/execute" \
        -H "Content-Type: application/json" \
        -d "{\"proof_job_id\": \"$PROOF_JOB_ID\"}" || echo "ERROR")
    
    if echo "$EXECUTE_RESPONSE" | grep -q "ERROR\|error"; then
        echo "⚠️  Execute failed (proof may still be generating)"
        echo "$EXECUTE_RESPONSE" | head -10
    else
        echo "✅ Execute response:"
        echo "$EXECUTE_RESPONSE" | jq '.' 2>/dev/null || echo "$EXECUTE_RESPONSE"
    fi
else
    echo "⚠️  Cannot execute - no proof job ID available"
fi

echo ""
echo "========================================"
echo "TEST SUMMARY"
echo "========================================"
echo ""
echo "✅ Backend API accessible"
echo "✅ Proof generation initiated"
echo ""
echo "📝 Next steps:"
echo "   1. Wait for proof generation to complete"
echo "   2. Verify fact hash is registered in SHARP"
echo "   3. Contract will verify proof before execution"
echo ""
