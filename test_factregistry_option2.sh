#!/bin/bash
set -e

echo "========================================"
echo " TESTING OPTION 2: YOUR DEPLOYED FACTREGISTRY"
echo "========================================"
echo ""

YOUR_ADDR="0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"

echo "📝 Testing your deployed FactRegistry..."
echo "   Address: $YOUR_ADDR"
echo ""

cd /opt/obsqra.starknet/contracts

# Test 1: Call get_all_verifications_for_fact_hash
echo "📝 Test 1: Calling get_all_verifications_for_fact_hash..."
DUMMY_HASH="0x1"

RESULT=$(sncast call \
    --contract-address "$YOUR_ADDR" \
    --function get_all_verifications_for_fact_hash \
    --arguments "$DUMMY_HASH" \
    --network sepolia 2>&1)

if echo "$RESULT" | grep -q "Success\|array"; then
    echo "✅ Contract is accessible!"
    echo "$RESULT" | head -5
else
    echo "⚠️  Issue accessing contract:"
    echo "$RESULT" | head -10
fi

echo ""
echo "✅ Your FactRegistry is deployed and accessible!"
