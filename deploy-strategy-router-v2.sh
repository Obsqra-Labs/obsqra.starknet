#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "🚀 Deploying StrategyRouterV2 to Starknet Sepolia"
echo "════════════════════════════════════════════════════════════════"

cd /opt/obsqra.starknet/contracts

# Configuration (Sepolia testnet addresses)
ACCOUNT="katana-0"
ACCOUNT_ADDRESS="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
RPC_URL="https://starknet-sepolia.public.blastapi.io"

# Contract addresses (from deployments)
RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
DAO_MANAGER="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"

# STRK token on Sepolia
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

# Placeholder protocol addresses (will be updated later when protocols are integrated)
JEDISWAP_ROUTER="0x0000000000000000000000000000000000000000000000000000000000000001"
EKUBO_CORE="0x0000000000000000000000000000000000000000000000000000000000000002"

echo "📋 Deployment Parameters:"
echo "  Owner: $ACCOUNT_ADDRESS"
echo "  STRK Token: $STRK_TOKEN"
echo "  Risk Engine: $RISK_ENGINE"
echo "  DAO Manager: $DAO_MANAGER"
echo ""

# Step 1: Declare the contract
echo "📝 Step 1: Declaring StrategyRouterV2 contract..."
DECLARE_OUTPUT=$(scarb --release build 2>&1 || true)

CLASS_HASH=$(starkli declare target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1 | grep -oP 'Class hash declared:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$CLASS_HASH" ]; then
  echo "⚠️  Declaration might have failed or class already declared. Checking..."
  # Try to get class hash from compiled contract
  CLASS_HASH=$(cat target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json | python3 -c "import sys, json; print(json.load(sys.stdin).get('class_hash', ''))" 2>/dev/null || echo "")
  
  if [ -z "$CLASS_HASH" ]; then
    echo "❌ Could not determine class hash. Please check compilation."
    exit 1
  fi
  echo "📌 Using class hash: $CLASS_HASH"
fi

echo "✅ Class Hash: $CLASS_HASH"
echo ""

# Step 2: Deploy the contract
echo "🚀 Step 2: Deploying StrategyRouterV2..."

DEPLOY_ARGS="$ACCOUNT_ADDRESS $JEDISWAP_ROUTER $EKUBO_CORE $RISK_ENGINE $DAO_MANAGER $STRK_TOKEN"

echo "Constructor args: $DEPLOY_ARGS"
echo ""

TX_HASH=$(starkli deploy $CLASS_HASH \
  $DEPLOY_ARGS \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1 | tee /dev/tty | grep -oP 'Contract deployed:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$TX_HASH" ]; then
  echo "❌ Deployment failed. Please check the output above."
  exit 1
fi

echo ""
echo "✅ StrategyRouterV2 deployed!"
echo "   Contract Address: $TX_HASH"
echo "   Class Hash: $CLASS_HASH"
echo ""

# Update deployments file
echo "📝 Updating deployments/sepolia.json..."

python3 << EOF
import json
from datetime import date

# Load existing deployments
with open('deployments/sepolia.json', 'r') as f:
    deployments = json.load(f)

# Add StrategyRouterV2
deployments['contracts']['StrategyRouterV2'] = {
    'address': '$TX_HASH',
    'classHash': '$CLASS_HASH',
    'txHash': '$TX_HASH'
}

# Add explorer link
deployments['explorer']['StrategyRouterV2'] = f"https://sepolia.starkscan.co/contract/$TX_HASH"

# Save
with open('deployments/sepolia.json', 'w') as f:
    json.dump(deployments, f, indent=2)

print("✅ Updated deployments/sepolia.json")
EOF

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Contract Details:"
echo "   Address: $TX_HASH"
echo "   Class Hash: $CLASS_HASH"
echo "   Explorer: https://sepolia.starkscan.co/contract/$TX_HASH"
echo ""
echo "🔧 Next Steps:"
echo "   1. Update frontend/.env.local with new address"
echo "   2. Rebuild frontend"
echo "   3. Test deposit/withdraw functions"
echo ""

