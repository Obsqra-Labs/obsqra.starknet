#!/bin/bash
set -e

echo "========================================"
echo " DEPLOYING RISKENGINE V4 (zkML 4/5)"
echo "========================================"
echo ""
echo "This deployment includes on-chain proof verification"
echo ""

# Configuration
ACCOUNT="deployer"
NETWORK="sepolia"

# Get owner address (deployer account)
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

# Placeholder addresses (will be updated after deployment)
STRATEGY_ROUTER="0x0000000000000000000000000000000000000000000000000000000000000001"
DAO_MANAGER="0x0000000000000000000000000000000000000000000000000000000000000001"

# Build contracts
echo "📦 Building contracts..."
cd /opt/obsqra.starknet/contracts
scarb build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "✅ Build complete"
echo ""
echo "🔑 Deploying with account: $ACCOUNT"
echo "🌐 Network: $NETWORK"
echo "👤 Owner: $OWNER"
echo ""

# Declare RiskEngine
echo "📝 Declaring RiskEngine (new class with proof verification)..."
DECLARE_OUTPUT=$(sncast --account $ACCOUNT declare --contract-name RiskEngine --network $NETWORK 2>&1)

if echo "$DECLARE_OUTPUT" | grep -q "class_hash"; then
    RISK_ENGINE_CLASS=$(echo "$DECLARE_OUTPUT" | grep -oP 'class_hash:\s*\K0x[a-fA-F0-9]+' || echo "$DECLARE_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
    echo "✅ RiskEngine class hash: $RISK_ENGINE_CLASS"
else
    echo "❌ Declaration failed:"
    echo "$DECLARE_OUTPUT"
    exit 1
fi

echo ""

# Deploy RiskEngine with constructor args
echo "🚀 Deploying RiskEngine instance..."
DEPLOY_OUTPUT=$(sncast --account $ACCOUNT deploy \
    --class-hash $RISK_ENGINE_CLASS \
    --constructor-calldata $OWNER $STRATEGY_ROUTER $DAO_MANAGER \
    --network $NETWORK 2>&1)

if echo "$DEPLOY_OUTPUT" | grep -q "contract_address"; then
    RISK_ENGINE_ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract_address:\s*\K0x[a-fA-F0-9]+' || echo "$DEPLOY_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
    echo "✅ RiskEngine deployed at: $RISK_ENGINE_ADDR"
else
    echo "❌ Deployment failed:"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "========================================"
echo ""
echo "📊 Deployment Info:"
echo "  Contract: RiskEngine v4 (zkML 4/5)"
echo "  Address: $RISK_ENGINE_ADDR"
echo "  Class Hash: $RISK_ENGINE_CLASS"
echo "  Network: $NETWORK"
echo ""
echo "🔗 View on Starkscan:"
echo "  https://sepolia.starkscan.co/contract/$RISK_ENGINE_ADDR"
echo ""
echo "📝 Next Steps:"
echo "  1. Update backend config with new address"
echo "  2. Test end-to-end proof verification"
echo "  3. Verify contract rejects invalid proofs"
echo ""

# Save deployment info
mkdir -p /opt/obsqra.starknet/deployments
cat > /opt/obsqra.starknet/deployments/risk_engine_v4_sepolia.json << DEPLOY_JSON
{
  "contract": "RiskEngine",
  "version": "v4-zkml-4-5",
  "network": "sepolia",
  "address": "$RISK_ENGINE_ADDR",
  "class_hash": "$RISK_ENGINE_CLASS",
  "deployed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "features": [
    "on_chain_proof_verification",
    "sharp_fact_registry_integration",
    "risk_score_matching_assertions"
  ],
  "constructor_args": {
    "owner": "$OWNER",
    "strategy_router": "$STRATEGY_ROUTER",
    "dao_manager": "$DAO_MANAGER"
  }
}
DEPLOY_JSON

echo "✅ Deployment info saved to: deployments/risk_engine_v4_sepolia.json"
