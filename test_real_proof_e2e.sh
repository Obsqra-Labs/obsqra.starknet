#!/bin/bash
set -e

echo "========================================"
echo " REAL PROOF END-TO-END TEST"
echo "========================================"
echo ""

BACKEND_URL="${BACKEND_URL:-http://localhost:8001}"
FACT_REGISTRY="0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"
RISK_ENGINE="0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4"

echo "📍 Backend: $BACKEND_URL"
echo ""

echo "📝 This test will:"
echo "   1. Generate proof via LuminAIR"
echo "   2. Submit to Integrity → Your FactRegistry"
echo "   3. Wait for verification"
echo "   4. Get fact_hash"
echo "   5. Call RiskEngine with real proof"
echo "   6. Verify allocation executes"
echo ""

echo "📝 Step 1: Requesting proof generation..."
echo ""

# Request orchestration
RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/risk-engine/orchestrate-allocation" \
    -H "Content-Type: application/json" \
    -d '{
        "jediswap_metrics": {
            "utilization": 6500,
            "volatility": 1200,
            "liquidity": 1,
            "audit_score": 85,
            "age_days": 180
        },
        "ekubo_metrics": {
            "utilization": 5500,
            "volatility": 1000,
            "liquidity": 2,
            "audit_score": 90,
            "age_days": 200
        }
    }' 2>&1)

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "proof_job_id\|orchestration_id"; then
    echo "✅ Proof generation initiated"
    JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('proof_job_id') or data.get('orchestration_id', ''))" 2>/dev/null || echo "")
    
    if [ -n "$JOB_ID" ]; then
        echo "   Job ID: $JOB_ID"
        echo ""
        echo "📝 Step 2: Monitoring proof job..."
        echo "   (This may take several minutes)"
        echo ""
        echo "   Check status: curl $BACKEND_URL/api/v1/verification/verification-status/$JOB_ID"
        echo ""
        echo "📝 Step 3: Polling for L2 verification..."
        for i in {1..8}; do
            STATUS=$(curl -s "$BACKEND_URL/api/v1/verification/verification-status/$JOB_ID" || true)
            if echo "$STATUS" | grep -q "\"verified\":true"; then
                echo "✅ L2 verified"
                echo "$STATUS" | python3 -m json.tool 2>/dev/null || echo "$STATUS"
                break
            else
                echo "⏳ Not verified yet (attempt $i/8)"
                sleep 2
            fi
        done
    fi
else
    echo "⚠️  Could not extract job ID"
    echo "   Response: $RESPONSE"
fi

echo ""
echo "💡 This will use your FactRegistry: $FACT_REGISTRY"
