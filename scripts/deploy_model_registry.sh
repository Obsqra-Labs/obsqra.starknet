#!/bin/bash
# Deploy Model Registry contract to Sepolia
# Uses sncast --network sepolia (proven workaround from dev log)

set -e

# Load environment
if [ -f backend/.env ]; then
    export $(cat backend/.env | grep -v '^#' | xargs)
fi

OWNER_ADDR="${BACKEND_WALLET_ADDRESS:-0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d}"
NETWORK="${STARKNET_NETWORK:-sepolia}"

echo "🚀 Deploying Model Registry Contract..."
echo "  Owner: $OWNER_ADDR"
echo "  Network: $NETWORK"
echo ""

cd contracts

# Step 1: Get class hash (try declaration first, fallback to compiled artifact)
echo "📝 Step 1: Getting ModelRegistry class hash..."
DECLARE_OUTPUT=$(sncast --account deployer declare \
  --contract-name ModelRegistry \
  --network "$NETWORK" 2>&1)

# Extract class hash from output
CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'class hash: \K0x[a-fA-F0-9]+' || echo "")

# If declaration failed (already declared), get from compiled artifact
if [ -z "$CLASS_HASH" ]; then
    echo "   Contract already declared, reading from compiled artifact..."
    COMPILED_FILE="target/dev/obsqra_contracts_ModelRegistry.compiled_contract_class.json"
    if [ -f "$COMPILED_FILE" ]; then
        CLASS_HASH=$(python3 -c "import sys, json; data=json.load(open('$COMPILED_FILE')); print(data.get('compiled_class_hash', ''))" 2>/dev/null || echo "")
    fi
fi

if [ -z "$CLASS_HASH" ]; then
    echo "❌ Failed to get class hash"
    echo "   Declaration output: $DECLARE_OUTPUT"
    exit 1
fi

echo "✅ Class Hash: $CLASS_HASH"
echo ""

# Step 2: Deploy contract
echo "📦 Step 2: Deploying ModelRegistry instance..."
DEPLOY_OUTPUT=$(sncast --account deployer deploy \
  --class-hash "$CLASS_HASH" \
  --constructor-calldata "$OWNER_ADDR" \
  --network "$NETWORK" 2>&1)

echo "$DEPLOY_OUTPUT"

# Extract contract address from output
CONTRACT_ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract address: \K0x[a-fA-F0-9]+' || echo "")

if [ -z "$CONTRACT_ADDR" ]; then
    echo "❌ Failed to extract contract address from deployment output"
    echo "   Output: $DEPLOY_OUTPUT"
    exit 1
fi

echo ""
echo "✅ Deployment successful!"
echo "   Contract Address: $CONTRACT_ADDR"
echo "   Class Hash: $CLASS_HASH"
echo ""
echo "📝 Next steps:"
echo "   1. Update backend/app/config.py: MODEL_REGISTRY_ADDRESS = \"$CONTRACT_ADDR\""
echo "   2. Register initial model version"
echo ""
