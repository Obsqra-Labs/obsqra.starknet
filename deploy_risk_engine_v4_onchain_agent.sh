#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT/contracts" || exit 1

echo "========================================"
echo " DEPLOYING RISKENGINE V4 WITH ON-CHAIN AGENT"
echo "========================================"
echo ""
echo "This deployment includes:"
echo "  - On-chain proof verification (proof gate)"
echo "  - Model version enforcement"
echo "  - User constraint signature support"
echo "  - Permissionless execution mode (optional)"
echo "  - Stage 3A: parameterized model (get_model_params / set_model_params)"
echo ""

# Configuration
ACCOUNT="deployer"
NETWORK="sepolia"

# Get owner address (deployer account)
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

# Contract addresses (from backend config)
STRATEGY_ROUTER="${STRATEGY_ROUTER:-0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73}"
DAO_MANAGER="${DAO_MANAGER:-0x0000000000000000000000000000000000000000000000000000000000000001}"
MODEL_REGISTRY="${MODEL_REGISTRY:-0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc}"

echo "📋 Configuration:"
echo "  Account: $ACCOUNT"
echo "  Network: $NETWORK"
echo "  Owner: $OWNER"
echo "  Strategy Router: $STRATEGY_ROUTER"
echo "  DAO Manager: $DAO_MANAGER"
echo "  Model Registry: $MODEL_REGISTRY"
echo ""

# Build contracts
echo "📦 Building contracts..."
scarb build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "✅ Build complete"
echo ""

# Declare RiskEngine
echo "📝 Declaring RiskEngine v4 with on-chain agent..."
DECLARE_OUTPUT=$(sncast --account $ACCOUNT declare --contract-name RiskEngine --network $NETWORK 2>&1)

if echo "$DECLARE_OUTPUT" | grep -qi "class hash\|declaration completed\|already declared"; then
    RISK_ENGINE_CLASS=$(echo "$DECLARE_OUTPUT" | grep -oP '0x[a-fA-F0-9]{63,64}' | head -1)
    if [ -z "$RISK_ENGINE_CLASS" ]; then
        RISK_ENGINE_CLASS=$(echo "$DECLARE_OUTPUT" | grep -i "class hash" | grep -oP '0x[a-fA-F0-9]+' | head -1)
    fi
    if [ -z "$RISK_ENGINE_CLASS" ]; then
        echo "  (extracting class hash via sncast utils class-hash...)"
        RISK_ENGINE_CLASS=$(sncast utils class-hash --contract-name RiskEngine 2>/dev/null | grep -oP '0x[a-fA-F0-9]{63,64}' | head -1)
    fi
    if [ -z "$RISK_ENGINE_CLASS" ]; then
        echo "❌ Could not extract class hash from declare output:"
        echo "$DECLARE_OUTPUT"
        exit 1
    fi
    echo "✅ RiskEngine class hash: $RISK_ENGINE_CLASS"
else
    echo "❌ Declaration failed:"
    echo "$DECLARE_OUTPUT"
    exit 1
fi

echo ""

# Deploy RiskEngine with constructor args (now 4 parameters including model_registry)
echo "🚀 Deploying RiskEngine instance..."
DEPLOY_OUTPUT=$(sncast --account $ACCOUNT deploy \
    --class-hash $RISK_ENGINE_CLASS \
    --constructor-calldata $OWNER $STRATEGY_ROUTER $DAO_MANAGER $MODEL_REGISTRY \
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
echo "  Contract: RiskEngine v4 with On-Chain Agent"
echo "  Address: $RISK_ENGINE_ADDR"
echo "  Class Hash: $RISK_ENGINE_CLASS"
echo "  Network: $NETWORK"
echo ""
echo "🔗 View on Starkscan:"
echo "  https://sepolia.starkscan.co/contract/$RISK_ENGINE_ADDR"
echo ""
echo "📝 Post-Deployment Steps:"
echo "  1. Approve model versions:"
echo "     sncast --account $ACCOUNT invoke --contract-address $RISK_ENGINE_ADDR \\"
echo "       --function approve_model_version --calldata <model_hash> --network $NETWORK"
echo ""
echo "  2. Set Model Registry (if using):"
echo "     sncast --account $ACCOUNT invoke --contract-address $RISK_ENGINE_ADDR \\"
echo "       --function set_model_registry --calldata <model_registry_address> --network $NETWORK"
echo ""
echo "  3. Enable permissionless mode (optional):"
echo "     sncast --account $ACCOUNT invoke --contract-address $RISK_ENGINE_ADDR \\"
echo "       --function set_permissionless_mode --calldata 1 --network $NETWORK"
echo ""
echo "  4. Wire StrategyRouter to new RiskEngine (required for allocations):"
echo "     cd $REPO_ROOT && bash scripts/set_strategy_router_risk_engine.sh"
echo "     (or set RISK_ENGINE_ADDRESS=$RISK_ENGINE_ADDR then run the script)"
echo ""
echo "  5. Update backend/frontend config:"
echo "     RISK_ENGINE_ADDRESS=$RISK_ENGINE_ADDR"
echo ""

# Save deployment info
mkdir -p "$REPO_ROOT/deployments"
cat > /opt/obsqra.starknet/deployments/risk_engine_v4_onchain_agent_sepolia.json << DEPLOY_JSON
{
  "contract": "RiskEngine",
  "version": "v4-onchain-agent",
  "network": "sepolia",
  "address": "$RISK_ENGINE_ADDR",
  "class_hash": "$RISK_ENGINE_CLASS",
  "deployed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "features": [
    "on_chain_proof_verification",
    "model_version_enforcement",
    "user_constraint_signatures",
    "permissionless_execution",
    "enhanced_receipts"
  ],
  "constructor_args": {
    "owner": "$OWNER",
    "strategy_router": "$STRATEGY_ROUTER",
    "dao_manager": "$DAO_MANAGER",
    "model_registry": "$MODEL_REGISTRY"
  },
  "abi_inputs": {
    "propose_and_execute_allocation": 9
  }
}
DEPLOY_JSON

echo "✅ Deployment info saved to: $REPO_ROOT/deployments/risk_engine_v4_onchain_agent_sepolia.json"
