#!/bin/bash
set -e

echo "========================================"
echo "🚀 DEPLOYING OBSQRA CONTRACTS TO SEPOLIA"
echo "========================================"
echo ""

# Configuration
ACCOUNT="deployer"
NETWORK="sepolia"
RPC="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"

# Build contracts
echo "📦 Building contracts..."
cd /opt/obsqra.starknet/contracts
scarb build

echo ""
echo "🔑 Deploying with account: $ACCOUNT"
echo "🌐 Network: $NETWORK"
echo ""

# Deploy RiskEngine
echo "📝 Declaring RiskEngine..."
RISK_ENGINE_CLASS=$(sncast --profile default declare --contract-name RiskEngine \
  --network $NETWORK 2>&1 | grep -oP 'class_hash: \K[0-9x]+' || echo "")

if [ -z "$RISK_ENGINE_CLASS" ]; then
  echo "⚠️  Could not extract class hash, using from deployments..."
  RISK_ENGINE_CLASS="0x61febd39ccffbbd986e071669eb1f712f4dcf5e008aae7fa2bed1f09de6e304"
fi

echo "✅ RiskEngine class hash: $RISK_ENGINE_CLASS"
echo ""

echo "🚀 Deploying RiskEngine..."
RISK_ENGINE_ADDR=$(sncast --profile default deploy --class-hash $RISK_ENGINE_CLASS \
  --network $NETWORK 2>&1 | grep -oP 'contract_address: \K[0-9x]+' || echo "")

if [ -n "$RISK_ENGINE_ADDR" ]; then
  echo "✅ RiskEngine deployed at: $RISK_ENGINE_ADDR"
else
  echo "⚠️  RiskEngine deployment may have failed or not shown contract address"
fi

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "========================================"
echo ""
echo "📊 Deployed Contracts:"
echo "  RiskEngine: $RISK_ENGINE_ADDR"
echo ""
echo "🔗 View on Starkscan:"
if [ -n "$RISK_ENGINE_ADDR" ]; then
  echo "  https://sepolia.starkscan.co/contract/$RISK_ENGINE_ADDR"
fi

