#!/bin/bash

# Deployment Workaround for StrategyRouterV35
# This script attempts deployment using alternative methods when sncast hits the PublicNode fee estimation bug

set -e

echo "=== StrategyRouterV35 Deployment Workaround ==="
echo ""
echo "Issue: PublicNode RPC returns l1_gas.max_amount=0, blocking all deployments"
echo "Status: RiskEngine successfully deployed; StrategyRouterV35 code compiled"
echo ""

ACCOUNT="deployer"
CONTRACT="StrategyRouterV35"
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
STRATEGY_ROUTER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

echo "📝 Configuration:"
echo "  Account: $ACCOUNT"
echo "  Contract: $CONTRACT"
echo "  Owner: $OWNER"
echo "  Strategy Router: $STRATEGY_ROUTER"
echo ""

cd /opt/obsqra.starknet/contracts

# Approach 1: Try with explicit high L1 gas amount
echo "🔴 Attempting Approach 1: Explicit L1 gas parameters..."
sncast --account=$ACCOUNT deploy \
  --contract-name $CONTRACT \
  --constructor-calldata "$OWNER" "$STRATEGY_ROUTER" \
  --network sepolia \
  --l1-gas 1000000 \
  --l1-gas-price 109129041718878 \
  --l2-gas 3880272960 \
  --l2-gas-price 12000000000 \
  --l1-data-gas 288 \
  --l1-data-gas-price 436536712003 2>&1 || {
  echo "❌ Approach 1 failed"
  
  # Approach 2: Try with devnet (if available)
  echo ""
  echo "🟡 Attempting Approach 2: Check for local devnet..."
  if [ -f "/tmp/devnet-running" ] || pgrep -f "starknet.*devnet" > /dev/null 2>&1; then
    echo "✅ Devnet found! Deploying..."
    sncast --account=$ACCOUNT deploy \
      --contract-name $CONTRACT \
      --constructor-calldata "$OWNER" "$STRATEGY_ROUTER" \
      --url http://127.0.0.1:5050 2>&1
  else
    echo "❌ Devnet not available"
    
    # Approach 3: Provide manual deployment instructions
    echo ""
    echo "🔵 Approach 3: Manual Deployment Instructions"
    echo "============================================="
    echo ""
    echo "Since the PublicNode RPC has a fee estimation bug, deployment must be done manually:"
    echo ""
    echo "Option A: Use a different RPC with valid API key"
    echo "  export ALCHEMY_API_KEY='<your-key>'"
    echo "  sncast --account=$ACCOUNT deploy \\"
    echo "    --contract-name $CONTRACT \\"
    echo "    --constructor-calldata '$OWNER' '$STRATEGY_ROUTER' \\"
    echo "    --url https://starknet-sepolia.g.alchemy.com/v2/\$ALCHEMY_API_KEY"
    echo ""
    echo "Option B: Use Starkli instead of sncast"
    echo "  starkli deploy \\"
    echo "    --account ~/.starknet_accounts/starknet_open_zeppelin_accounts.json \\"
    echo "    $(grep 'sierra_class_hash' target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json | cut -d'"' -f4) \\"
    echo "    $OWNER $STRATEGY_ROUTER"
    echo ""
    echo "Option C: Wait for PublicNode RPC to fix the L1 gas estimation bug"
    echo ""
    exit 1
  fi
}

echo ""
echo "✅ Deployment completed!"
echo ""
echo "Next steps:"
echo "  1. Verify contract on https://sepolia.starkscan.co/"
echo "  2. Test contract functions"
echo "  3. Connect RiskEngine ↔ StrategyRouterV35"
