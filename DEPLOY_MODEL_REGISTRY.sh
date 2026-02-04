#!/bin/bash
# Deploy Model Registry Contract to Sepolia

set -e

echo "========================================"
echo " Deploying Model Registry Contract"
echo "========================================"
echo ""

cd /opt/obsqra.starknet/contracts

# Check if sncast is available
if ! command -v sncast &> /dev/null; then
    echo "❌ sncast not found. Please install Starknet Foundry."
    exit 1
fi

# Declare the contract
echo "📝 Declaring ModelRegistry contract..."
CLASS_HASH=$(sncast --account deployer declare --contract-name ModelRegistry --network=sepolia 2>&1 | grep -oP 'class_hash: \K0x[a-fA-F0-9]+' || echo "")

if [ -z "$CLASS_HASH" ]; then
    echo "❌ Failed to get class hash. Trying alternative method..."
    CLASS_HASH=$(sncast --account deployer declare --contract-name ModelRegistry --network=sepolia 2>&1 | tail -1 | grep -oP '0x[a-fA-F0-9]{64}' || echo "")
fi

if [ -z "$CLASS_HASH" ]; then
    echo "❌ Declaration failed. Please check the output above."
    exit 1
fi

echo "✅ Class hash: $CLASS_HASH"
echo ""

# Wait for class propagation
echo "⏳ Waiting 30 seconds for class propagation..."
sleep 30

# Get owner address (from config or use deployer)
OWNER_ADDRESS=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/obsqra.starknet/backend')
from app.config import get_settings
settings = get_settings()
# Use deployer account address or RiskEngine owner
print(settings.DEPLOYER_ADDRESS if hasattr(settings, 'DEPLOYER_ADDRESS') else "0x0")
PYEOF
)

if [ "$OWNER_ADDRESS" = "0x0" ] || [ -z "$OWNER_ADDRESS" ]; then
    echo "⚠️  Owner address not found. Please provide owner address:"
    read -r OWNER_ADDRESS
fi

echo "📝 Deploying ModelRegistry with owner: $OWNER_ADDRESS"
echo ""

# Deploy the contract
DEPLOY_OUTPUT=$(sncast --account deployer deploy \
    --class-hash "$CLASS_HASH" \
    --constructor-calldata "$OWNER_ADDRESS" \
    --network=sepolia 2>&1)

CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract_address: \K0x[a-fA-F0-9]+' || echo "")

if [ -z "$CONTRACT_ADDRESS" ]; then
    CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | tail -1 | grep -oP '0x[a-fA-F0-9]{64}' || echo "")
fi

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "❌ Deployment failed. Output:"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

echo "✅ ModelRegistry deployed!"
echo "   Address: $CONTRACT_ADDRESS"
echo ""

# Save deployment info
cat > /opt/obsqra.starknet/deployments/model_registry_sepolia.json << DEPLOYJSON
{
  "contract_name": "ModelRegistry",
  "network": "sepolia",
  "class_hash": "$CLASS_HASH",
  "contract_address": "$CONTRACT_ADDRESS",
  "owner": "$OWNER_ADDRESS",
  "deployed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
DEPLOYJSON

echo "📝 Deployment info saved to deployments/model_registry_sepolia.json"
echo ""
echo "========================================"
echo " ✅ DEPLOYMENT COMPLETE"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Register initial model version"
echo "  2. Update RiskEngine to use model hash"
echo "  3. Test model registry functions"
