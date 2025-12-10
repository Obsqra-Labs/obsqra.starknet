#!/bin/bash
# Test JediSwap deposit using starkli
# This tests adding liquidity to JediSwap individually

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing JediSwap Deposit (starkli)"
echo "════════════════════════════════════════════════════════════════"

# Configuration
RPC_URL="https://starknet-sepolia-rpc.publicnode.com"
ACCOUNT="deployer"

# Protocol addresses
JEDISWAP_NFT_MANAGER="0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
ETH_TOKEN="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
STRATEGY_ROUTER="0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a"

# Test amount (1 STRK = 1000000000000000000 wei)
TEST_AMOUNT_STRK="1000000000000000000"  # 1 STRK
TEST_AMOUNT_ETH="1000000000000000000"   # 1 ETH (for liquidity pair)

echo ""
echo "📋 Test Configuration:"
echo "  Strategy Router (has STRK): $STRATEGY_ROUTER"
echo "  JediSwap NFT Manager: $JEDISWAP_NFT_MANAGER"
echo "  Test Amount: 1 STRK + 1 ETH"
echo ""

echo "🔍 Step 1: Check Strategy Router STRK balance..."
STRK_BALANCE=$(starkli call $STRK_TOKEN balanceOf $STRATEGY_ROUTER --rpc $RPC_URL 2>&1)
echo "  STRK Balance: $STRK_BALANCE"
echo ""

echo "💡 Step 2: Approve NFT Manager to spend STRK..."
echo "  Command: starkli invoke $STRK_TOKEN approve \\"
echo "    --spender $JEDISWAP_NFT_MANAGER \\"
echo "    --amount $TEST_AMOUNT_STRK \\"
echo "    --account $ACCOUNT \\"
echo "    --rpc $RPC_URL"
echo ""
echo "⚠️  Note: This requires the Strategy Router contract to have a function"
echo "   that allows owner to approve tokens on behalf of the contract."
echo ""

echo "💡 Step 3: Call mint() on JediSwap NFT Manager..."
echo "  This requires the full JediSwap NFT Manager ABI and mint parameters:"
echo "  - token0: $STRK_TOKEN"
echo "  - token1: $ETH_TOKEN"
echo "  - fee: 3000 (0.3%)"
echo "  - tick_lower: -887272"
echo "  - tick_upper: 887272"
echo "  - amount0_desired: $TEST_AMOUNT_STRK"
echo "  - amount1_desired: $TEST_AMOUNT_ETH"
echo ""

echo "📝 This script is a template. To use it:"
echo "  1. Ensure Strategy Router has approve function for owner"
echo "  2. Get JediSwap NFT Manager ABI"
echo "  3. Construct mint() call with proper parameters"
echo "  4. Execute via starkli invoke"
echo ""

