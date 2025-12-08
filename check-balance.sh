#!/bin/bash

# Check user balance in Strategy Router contract
# Replace USER_ADDRESS with your wallet address

echo "════════════════════════════════════════════════════════════════"
echo "🔍 Checking Strategy Router Balance"
echo "════════════════════════════════════════════════════════════════"

STRATEGY_ROUTER="0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a"
RPC_URL="https://starknet-sepolia.public.blastapi.io"

echo ""
echo "📋 Contract: $STRATEGY_ROUTER"
echo ""

# Prompt for user address
read -p "Enter your wallet address (0x...): " USER_ADDRESS

if [ -z "$USER_ADDRESS" ]; then
    echo "❌ No address provided"
    exit 1
fi

echo ""
echo "🔍 Querying balance for: $USER_ADDRESS"
echo ""

# Call get_user_balance function
# The function signature is: get_user_balance(user: ContractAddress) -> u256
starkli call \
    --rpc $RPC_URL \
    $STRATEGY_ROUTER \
    get_user_balance \
    $USER_ADDRESS

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "💡 The balance is returned as u256 (low, high)"
echo "    To convert to STRK: divide 'low' by 10^18"
echo "════════════════════════════════════════════════════════════════"

