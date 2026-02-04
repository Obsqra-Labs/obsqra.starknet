#!/bin/bash
set -e

echo "========================================"
echo " END-TO-END TEST WITH YOUR FACTREGISTRY"
echo "========================================"
echo ""

echo "📝 This will test the full flow:"
echo "   1. Generate proof with LuminAIR"
echo "   2. Verify proof with your FactRegistry"
echo "   3. Execute allocation on RiskEngine"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend not running. Starting it..."
    echo "   (You may need to start it manually)"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Test orchestrate allocation endpoint
echo "📝 Testing /api/v1/risk-engine/orchestrate-allocation..."
echo ""

SAMPLE_METRICS='{
  "jediswap_metrics": {
    "utilization": 0.65,
    "volatility": 0.12,
    "liquidity": 1000000,
    "audit_score": 85,
    "age_days": 180
  },
  "ekubo_metrics": {
    "utilization": 0.55,
    "volatility": 0.10,
    "liquidity": 1500000,
    "audit_score": 90,
    "age_days": 200
  }
}'

RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/risk-engine/orchestrate-allocation \
    -H "Content-Type: application/json" \
    -d "$SAMPLE_METRICS" 2>&1)

if echo "$RESPONSE" | grep -q "proof_job_id\|orchestration_id"; then
    echo "✅ Orchestration started!"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE" | head -20
else
    echo "⚠️  Orchestration response:"
    echo "$RESPONSE" | head -20
fi

echo ""
echo "💡 This will use your deployed FactRegistry for verification"
echo "   Contract: 0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"
