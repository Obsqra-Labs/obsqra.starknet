#!/bin/bash
# Test JediSwap directly from Strategy Router contract
# This tests adding liquidity to JediSwap individually

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing JediSwap Deposit (Direct Test)"
echo "════════════════════════════════════════════════════════════════"

# Configuration
RPC_URL="https://starknet-sepolia-rpc.publicnode.com"
ACCOUNT="deployer"

# Contract with test functions
NEW_CONTRACT="0x06c7791f5b4870e2a014fff85d78b83924f05c6b3b066788fafa3aad51c2ffe1"

# Protocol addresses
JEDISWAP_NFT_MANAGER="0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

# Test amount (1 STRK = 1000000000000000000 wei)
TEST_AMOUNT="1000000000000000000"

echo ""
echo "📋 Test Configuration:"
echo "  Contract: $NEW_CONTRACT"
echo "  JediSwap NFT Manager: $JEDISWAP_NFT_MANAGER"
echo "  Test Amount: 1 STRK"
echo ""

echo "💡 Step 1: First, deposit STRK to the new contract"
echo "   (The contract needs STRK to test with)"
echo ""

echo "💡 Step 2: Approve NFT Manager to spend STRK"
echo "   Call: approve_token_for_testing($STRK_TOKEN, $JEDISWAP_NFT_MANAGER, $TEST_AMOUNT)"
echo ""

echo "💡 Step 3: Test JediSwap"
echo "   Call: test_jediswap_only($TEST_AMOUNT)"
echo ""

echo "📝 To execute:"
echo "   sncast --account $ACCOUNT invoke \\"
echo "     --contract-address $NEW_CONTRACT \\"
echo "     --function approve_token_for_testing \\"
echo "     --arguments $STRK_TOKEN $JEDISWAP_NFT_MANAGER $TEST_AMOUNT 0 \\"
echo "     --network sepolia"
echo ""

