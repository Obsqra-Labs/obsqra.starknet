#!/bin/bash
set -e

echo "========================================"
echo " DEPLOYING RISKENGINE V4 (FIXED)"
echo "========================================"
echo ""

ACCOUNT="deployer"
NETWORK="sepolia"
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
STRATEGY_ROUTER="0x0000000000000000000000000000000000000000000000000000000000000001"
DAO_MANAGER="0x0000000000000000000000000000000000000000000000000000000000000001"

cd /opt/obsqra.starknet/contracts
scarb build

echo ""
echo "📝 Declaring RiskEngine (fixed FactRegistry interface)..."
DECLARE_OUTPUT=$(sncast --account $ACCOUNT declare --contract-name RiskEngine --network $NETWORK 2>&1)

if echo "$DECLARE_OUTPUT" | grep -q "class_hash"; then
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'class_hash:\s*\K0x[a-fA-F0-9]+' || echo "$DECLARE_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
    echo "✅ Class hash: $CLASS_HASH"
    
    echo ""
    echo "🚀 Deploying..."
    DEPLOY_OUTPUT=$(sncast --account $ACCOUNT deploy \
        --class-hash $CLASS_HASH \
        --constructor-calldata $OWNER $STRATEGY_ROUTER $DAO_MANAGER \
        --network $NETWORK 2>&1)
    
    if echo "$DEPLOY_OUTPUT" | grep -q "contract_address"; then
        ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract_address:\s*\K0x[a-fA-F0-9]+' || echo "$DEPLOY_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
        echo "✅ Deployed: $ADDR"
        echo ""
        echo "Update backend config with: $ADDR"
    else
        echo "❌ Deployment failed"
        echo "$DEPLOY_OUTPUT"
    fi
else
    echo "❌ Declaration failed"
    echo "$DECLARE_OUTPUT"
fi
