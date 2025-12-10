#!/bin/bash
# Test Ekubo directly from Strategy Router contract
# This tests adding liquidity to Ekubo individually

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Ekubo Deposit (Direct Test)"
echo "════════════════════════════════════════════════════════════════"

# Configuration
RPC_URL="https://starknet-sepolia-rpc.publicnode.com"
ACCOUNT="deployer"

# Contract with test functions
NEW_CONTRACT="0x06c7791f5b4870e2a014fff85d78b83924f05c6b3b066788fafa3aad51c2ffe1"

# Protocol addresses
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

# Test amount (1 STRK = 1000000000000000000 wei)
TEST_AMOUNT="1000000000000000000"

echo ""
echo "📋 Test Configuration:"
echo "  Contract: $NEW_CONTRACT"
echo "  Ekubo Core: $EKUBO_CORE"
echo "  Test Amount: 1 STRK"
echo ""

echo "💡 Step 1: First, deposit STRK to the new contract"
echo "   (The contract needs STRK to test with)"
echo ""

echo "💡 Step 2: Approve Ekubo Core to spend STRK"
echo "   Call: approve_token_for_testing($STRK_TOKEN, $EKUBO_CORE, $TEST_AMOUNT)"
echo ""

echo "💡 Step 3: Test Ekubo"
echo "   Call: test_ekubo_only($TEST_AMOUNT)"
echo ""

echo "📝 To execute:"
echo "   sncast --account $ACCOUNT invoke \\"
echo "     --contract-address $NEW_CONTRACT \\"
echo "     --function approve_token_for_testing \\"
echo "     --arguments $STRK_TOKEN $EKUBO_CORE $TEST_AMOUNT 0 \\"
echo "     --network sepolia"
echo ""

