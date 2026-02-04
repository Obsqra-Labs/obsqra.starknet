#!/bin/bash
set -e

echo "========================================"
echo " VERIFYING FACTREGISTRY ON-CHAIN"
echo "========================================"
echo ""

YOUR_ADDR="0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"

echo "📝 Checking your FactRegistry contract on-chain..."
echo "   Address: $YOUR_ADDR"
echo ""

cd /opt/obsqra.starknet/contracts

# Test 1: Verify contract exists
echo "📝 Test 1: Contract exists..."
RESULT=$(sncast call \
    --contract-address "$YOUR_ADDR" \
    --function get_all_verifications_for_fact_hash \
    --arguments "0x1" \
    --network sepolia 2>&1)

if echo "$RESULT" | grep -q "Success\|array"; then
    echo "✅ Contract is on-chain and accessible"
else
    echo "⚠️  Issue: $RESULT"
fi

echo ""
echo "📝 Test 2: Check contract on Starkscan..."
echo "   Visit: https://sepolia.starkscan.co/contract/$YOUR_ADDR"
echo ""

echo "✅ Verification complete!"
