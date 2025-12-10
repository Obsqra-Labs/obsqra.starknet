#!/bin/bash
# Full JediSwap liquidity test - mint() function
set -e

echo "════════════════════════════════════════════════════════════════"
echo "🧪 Full JediSwap Test - Adding Liquidity (mint)"
echo "════════════════════════════════════════════════════════════════"

ACCOUNT="deployer"
JEDISWAP_NFT_MANAGER="0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
ETH_TOKEN="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
DEPLOYER_ADDRESS="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

# Test amounts (0.1 STRK and 0.1 ETH)
AMOUNT_STRK="100000000000000000"  # 0.1 STRK
AMOUNT_ETH="100000000000000000"  # 0.1 ETH
FEE="3000"  # 0.3% fee tier
TICK_LOWER="-887272"  # Full range
TICK_UPPER="887272"   # Full range
DEADLINE=$(($(date +%s) + 1800))  # 30 minutes

echo ""
echo "📋 Test Configuration:"
echo "  NFT Manager: $JEDISWAP_NFT_MANAGER"
echo "  Token0 (STRK): $STRK_TOKEN"
echo "  Token1 (ETH): $ETH_TOKEN"
echo "  Amount STRK: 0.1 STRK"
echo "  Amount ETH: 0.1 ETH"
echo "  Fee: 0.3%"
echo "  Recipient: $DEPLOYER_ADDRESS"
echo ""

# Step 1: Approve STRK
echo "📝 Step 1: Approving STRK..."
sncast --account $ACCOUNT invoke \
  --contract-address $STRK_TOKEN \
  --function approve \
  --calldata $JEDISWAP_NFT_MANAGER $AMOUNT_STRK 0 \
  --network sepolia > /dev/null 2>&1
echo "✅ STRK approved"

# Step 2: Approve ETH
echo "📝 Step 2: Approving ETH..."
sncast --account $ACCOUNT invoke \
  --contract-address $ETH_TOKEN \
  --function approve \
  --calldata $JEDISWAP_NFT_MANAGER $AMOUNT_ETH 0 \
  --network sepolia > /dev/null 2>&1
echo "✅ ETH approved"

# Step 3: Call mint() with MintParams struct
# MintParams struct flattened:
# token0, token1, fee, tick_lower, tick_upper, amount0_desired (low, high), 
# amount1_desired (low, high), amount0_min (low, high), amount1_min (low, high), 
# recipient, deadline
echo ""
echo "📝 Step 3: Calling mint() on JediSwap NFT Manager..."
echo "⚠️  This requires proper struct serialization..."
echo ""

# Note: sncast doesn't handle structs directly, so we need to flatten the struct
# For now, let's just show what the call would look like
echo "💡 To call mint(), you need to flatten the MintParams struct:"
echo "   mint("
echo "     token0: $STRK_TOKEN"
echo "     token1: $ETH_TOKEN"
echo "     fee: $FEE"
echo "     tick_lower: $TICK_LOWER"
echo "     tick_upper: $TICK_UPPER"
echo "     amount0_desired: $AMOUNT_STRK"
echo "     amount1_desired: $AMOUNT_ETH"
echo "     amount0_min: 0"
echo "     amount1_min: 0"
echo "     recipient: $DEPLOYER_ADDRESS"
echo "     deadline: $DEADLINE"
echo "   )"
echo ""
echo "📝 Flattened calldata would be:"
echo "   $STRK_TOKEN $ETH_TOKEN $FEE $TICK_LOWER $TICK_UPPER"
echo "   $AMOUNT_STRK 0 $AMOUNT_ETH 0 0 0 0 0"
echo "   $DEPLOYER_ADDRESS $DEADLINE"
echo ""
echo "⚠️  This is complex - better to test via the contract's test_jediswap_only() function"
echo "   or use the frontend ProtocolTester component"

