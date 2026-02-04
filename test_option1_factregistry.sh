#!/bin/bash
set -e

echo "========================================"
echo " TESTING OPTION 1: EXISTING FACTREGISTRY"
echo "========================================"
echo ""

EXISTING_ADDR="0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c"

echo "📝 Testing existing FactRegistry contract..."
echo "   Address: $EXISTING_ADDR"
echo ""

# Try calling a read function to verify it's accessible
echo "📝 Calling get_all_verifications_for_fact_hash (with dummy hash)..."
echo "   This verifies the contract is accessible"

cd /opt/obsqra.starknet/contracts

# Use a dummy fact hash to test the contract is callable
DUMMY_HASH="0x1"

sncast call \
    --contract-address "$EXISTING_ADDR" \
    --function get_all_verifications_for_fact_hash \
    --arguments "$DUMMY_HASH" \
    --network sepolia 2>&1 | head -20

echo ""
echo "✅ If no errors above, the contract is accessible!"
echo "   (Empty result is expected for dummy hash)"
