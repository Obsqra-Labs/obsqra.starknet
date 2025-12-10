#!/bin/bash
# Full Ekubo liquidity test - deposit_liquidity() function
set -e

echo "════════════════════════════════════════════════════════════════"
echo "🧪 Full Ekubo Test - Adding Liquidity (deposit_liquidity)"
echo "════════════════════════════════════════════════════════════════"

ACCOUNT="deployer"
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
ETH_TOKEN="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

# Test amounts (0.1 STRK and 0.1 ETH)
AMOUNT_STRK="100000000000000000"  # 0.1 STRK
AMOUNT_ETH="100000000000000000"  # 0.1 ETH
FEE="3000"  # 0.3% fee tier

echo ""
echo "📋 Test Configuration:"
echo "  Ekubo Core: $EKUBO_CORE"
echo "  Token0 (STRK): $STRK_TOKEN"
echo "  Token1 (ETH): $ETH_TOKEN"
echo "  Amount STRK: 0.1 STRK"
echo "  Amount ETH: 0.1 ETH"
echo "  Fee: 0.3%"
echo ""

# Step 1: Approve STRK
echo "📝 Step 1: Approving STRK..."
sncast --account $ACCOUNT invoke \
  --contract-address $STRK_TOKEN \
  --function approve \
  --calldata $EKUBO_CORE $AMOUNT_STRK 0 \
  --network sepolia > /dev/null 2>&1
echo "✅ STRK approved"

# Step 2: Approve ETH
echo "📝 Step 2: Approving ETH..."
sncast --account $ACCOUNT invoke \
  --contract-address $ETH_TOKEN \
  --function approve \
  --calldata $EKUBO_CORE $AMOUNT_ETH 0 \
  --network sepolia > /dev/null 2>&1
echo "✅ ETH approved"

# Step 3: Call deposit_liquidity()
# deposit_liquidity(token0, token1, amount0, amount1, fee)
echo ""
echo "📝 Step 3: Calling deposit_liquidity() on Ekubo Core..."
echo ""

# Calldata: token0, token1, amount0 (low, high), amount1 (low, high), fee
echo "💡 To call deposit_liquidity(), use:"
echo "   deposit_liquidity("
echo "     token0: $STRK_TOKEN"
echo "     token1: $ETH_TOKEN"
echo "     amount0: $AMOUNT_STRK"
echo "     amount1: $AMOUNT_ETH"
echo "     fee: $FEE"
echo "   )"
echo ""
echo "📝 Calldata:"
echo "   $STRK_TOKEN $ETH_TOKEN $AMOUNT_STRK 0 $AMOUNT_ETH 0 $FEE"
echo ""

# Actually try the call
echo "🚀 Attempting deposit_liquidity() call..."
sncast --account $ACCOUNT invoke \
  --contract-address $EKUBO_CORE \
  --function deposit_liquidity \
  --calldata $STRK_TOKEN $ETH_TOKEN $AMOUNT_STRK 0 $AMOUNT_ETH 0 $FEE \
  --network sepolia 2>&1 | tail -10

