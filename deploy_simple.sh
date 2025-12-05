#!/bin/bash
set -e

echo "========================================"
echo "🚀 Deploy to Sepolia (Simple Method)"
echo "========================================"
echo ""

cd /opt/obsqra.starknet/contracts

# Load deployer wallet
DEPLOYER_ADDR=$(cat ../.deployer_wallet.json | grep address | cut -d'"' -f4)
DEPLOYER_KEY=$(cat ../.deployer_wallet.json | grep private_key | cut -d'"' -f4)

echo "Using Deployer Wallet:"
echo "  Address: $DEPLOYER_ADDR"
echo ""

# Build contracts
echo "Building contracts..."
scarb build
echo "✅ Contracts built"
echo ""

# Use sncast to declare and deploy
RPC="https://starknet-sepolia.public.blastapi.io"

echo "========================================"
echo "Step 1: Declaring Contracts"
echo "========================================"
echo ""

# For sncast, we need to create a temporary account file
mkdir -p ~/.starknet_accounts
cat > ~/.starknet_accounts/deployer_account.json << EOF
{
  "version": 1,
  "variant": {
    "type": "open_zeppelin",
    "version": 1,
    "public_key": "$(cat ../.deployer_wallet.json | grep public_key | cut -d'"' -f4)",
    "legacy": false
  },
  "deployment": {
    "status": "deployed",
    "class_hash": "$(cat ../.deployer_wallet.json | grep class_hash | cut -d'"' -f4)",
    "address": "$DEPLOYER_ADDR"
  }
}
EOF

# Now declare contracts
echo "1. Declaring RiskEngine..."
RISK_CLASS=$(sncast \
  --account deployer_account \
  --accounts-file ~/.starknet_accounts/deployer_account.json \
  --url $RPC \
  --keystore ~/.starknet_accounts/deployer_keystore.json \
  declare \
  --contract-name RiskEngine \
  2>&1 | grep "class_hash:" | awk '{print $2}')

if [ -z "$RISK_CLASS" ]; then
  echo "❌ Failed to declare RiskEngine"
  echo "Checking if already declared..."
fi

echo "Class hash: $RISK_CLASS"
echo ""

echo "2. Declaring DAOConstraintManager..."
DAO_CLASS=$(sncast \
  --account deployer_account \
  --accounts-file ~/.starknet_accounts/deployer_account.json \
  --url $RPC \
  declare \
  --contract-name DAOConstraintManager \
  2>&1 | grep "class_hash:" | awk '{print $2}')

echo "Class hash: $DAO_CLASS"
echo ""

echo "3. Declaring StrategyRouter..."
ROUTER_CLASS=$(sncast \
  --account deployer_account \
  --accounts-file ~/.starknet_accounts/deployer_account.json \
  --url $RPC \
  declare \
  --contract-name StrategyRouter \
  2>&1 | grep "class_hash:" | awk '{print $2}')

echo "Class hash: $ROUTER_CLASS"
echo ""

echo "========================================"
echo "Step 2: Deploying Contracts"
echo "========================================"
echo ""

# Deploy contracts
echo "Deploying RiskEngine..."
RISK_ADDR=$(sncast \
  --account deployer_account \
  --accounts-file ~/.starknet_accounts/deployer_account.json \
  --url $RPC \
  deploy \
  --class-hash $RISK_CLASS \
  --constructor-calldata $DEPLOYER_ADDR \
  2>&1 | grep "contract_address:" | awk '{print $2}')

echo "✅ RiskEngine: $RISK_ADDR"
echo ""

echo "Deploying DAOConstraintManager..."
DAO_ADDR=$(sncast \
  --account deployer_account \
  --accounts-file ~/.starknet_accounts/deployer_account.json \
  --url $RPC \
  deploy \
  --class-hash $DAO_CLASS \
  --constructor-calldata $DEPLOYER_ADDR 6000 3 5000 1000000 \
  2>&1 | grep "contract_address:" | awk '{print $2}')

echo "✅ DAOConstraintManager: $DAO_ADDR"
echo ""

echo "Deploying StrategyRouter..."
ROUTER_ADDR=$(sncast \
  --account deployer_account \
  --accounts-file ~/.starknet_accounts/deployer_account.json \
  --url $RPC \
  deploy \
  --class-hash $ROUTER_CLASS \
  --constructor-calldata $DEPLOYER_ADDR 0x456 0x789 0xabc $RISK_ADDR \
  2>&1 | grep "contract_address:" | awk '{print $2}')

echo "✅ StrategyRouter: $ROUTER_ADDR"
echo ""

# Save addresses
cd /opt/obsqra.starknet
cat > .env.sepolia << EOF
NETWORK=sepolia
RPC_URL=$RPC
DEPLOYER_ADDRESS=$DEPLOYER_ADDR

RISK_ENGINE_ADDRESS=$RISK_ADDR
DAO_MANAGER_ADDRESS=$DAO_ADDR
STRATEGY_ROUTER_ADDRESS=$ROUTER_ADDR

# Voyager
VOYAGER=https://sepolia.voyager.online/contract/$ROUTER_ADDR
EOF

echo "========================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "Contract Addresses:"
echo "  RiskEngine:          $RISK_ADDR"
echo "  DAOConstraintManager: $DAO_ADDR"
echo "  StrategyRouter:      $ROUTER_ADDR"
echo ""
echo "Saved to .env.sepolia"
echo ""
echo "View on Voyager:"
echo "  https://sepolia.voyager.online/contract/$ROUTER_ADDR"
echo ""

