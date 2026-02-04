#!/bin/bash
set -e

echo "========================================"
echo " DEPLOYING YOUR OWN FACTREGISTRY"
echo "========================================"
echo ""

ACCOUNT="deployer"
NETWORK="sepolia"

# Get owner address (deployer account)
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

cd /opt/obsqra.starknet/integrity

echo "📝 Building Integrity contract..."
scarb build

echo ""
echo "📝 Declaring FactRegistry..."
DECLARE_OUTPUT=$(sncast --account $ACCOUNT declare \
    --contract-name FactRegistry \
    --network $NETWORK 2>&1)

if echo "$DECLARE_OUTPUT" | grep -q "class_hash\|Class Hash"; then
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'class_hash:\s*\K0x[a-fA-F0-9]+' || \
                 echo "$DECLARE_OUTPUT" | grep -oP 'Class Hash:\s*\K0x[a-fA-F0-9]+' || \
                 echo "$DECLARE_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
    echo "✅ Class hash: $CLASS_HASH"
    
    echo ""
    echo "🚀 Deploying FactRegistry..."
    echo "   Owner: $OWNER"
    sleep 5  # Wait for declaration to settle
    
    DEPLOY_OUTPUT=$(sncast --account $ACCOUNT deploy \
        --class-hash $CLASS_HASH \
        --constructor-calldata $OWNER \
        --network $NETWORK 2>&1)
    
    if echo "$DEPLOY_OUTPUT" | grep -q "contract_address\|Contract Address"; then
        ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract_address:\s*\K0x[a-fA-F0-9]+' || \
               echo "$DEPLOY_OUTPUT" | grep -oP 'Contract Address:\s*\K0x[a-fA-F0-9]+' || \
               echo "$DEPLOY_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
        echo ""
        echo "✅ DEPLOYED!"
        echo "   Address: $ADDR"
        echo ""
        echo "📝 Update your code:"
        echo "   1. Backend: backend/app/services/integrity_service.py"
        echo "      INTEGRITY_VERIFIER_SEPOLIA = $ADDR"
        echo ""
        echo "   2. Backend config: backend/app/config.py (optional)"
        echo "      MY_FACT_REGISTRY_ADDRESS = \"$ADDR\""
        echo ""
        echo "   3. Contract: contracts/src/sharp_verifier.cairo"
        echo "      (or pass as parameter)"
        echo ""
        echo "🔗 View on Starkscan:"
        echo "   https://sepolia.starkscan.co/contract/$ADDR"
    else
        echo "❌ Deployment failed"
        echo "$DEPLOY_OUTPUT"
    fi
else
    echo "❌ Declaration failed"
    echo "$DECLARE_OUTPUT"
fi
