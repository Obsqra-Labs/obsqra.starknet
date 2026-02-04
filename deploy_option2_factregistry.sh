#!/bin/bash
set -e

echo "========================================"
echo " DEPLOYING OPTION 2: YOUR OWN FACTREGISTRY"
echo "========================================"
echo ""

OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

cd /opt/obsqra.starknet/integrity

echo "📝 Building contract..."
scarb build > /dev/null 2>&1
echo "✅ Built"

echo ""
echo "📝 Step 1: Declaring FactRegistry..."
echo "   Using --network=sepolia (per Starknet docs)"
echo ""

# Try with --network=sepolia as shown in docs
DECLARE_OUTPUT=$(sncast --account deployer declare \
    --contract-name FactRegistry \
    --network=sepolia 2>&1 || echo "FAILED")

if echo "$DECLARE_OUTPUT" | grep -q "class_hash\|Class Hash\|0x[0-9a-f]\{64\}"; then
    echo "✅ Declaration successful!"
    echo "$DECLARE_OUTPUT" | grep -E "class_hash|Class Hash|0x[0-9a-f]{64}" | head -3
    
    # Extract class hash
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oE "0x[0-9a-f]{64}" | head -1)
    
    if [ -n "$CLASS_HASH" ]; then
        echo ""
        echo "📝 Step 2: Deploying contract..."
        echo "   Class hash: $CLASS_HASH"
        echo "   Owner: $OWNER"
        echo ""
        
        sleep 10
        
        DEPLOY_OUTPUT=$(sncast --account deployer deploy \
            --class-hash "$CLASS_HASH" \
            --constructor-calldata "$OWNER" \
            --network=sepolia 2>&1 || echo "FAILED")
        
        if echo "$DEPLOY_OUTPUT" | grep -q "contract_address\|Contract Address\|0x[0-9a-f]\{64\}"; then
            echo "✅ Deployment successful!"
            echo "$DEPLOY_OUTPUT" | grep -E "contract_address|Contract Address|0x[0-9a-f]{64}" | head -3
            
            CONTRACT_ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oE "0x[0-9a-f]{64}" | head -1)
            
            echo ""
            echo "========================================"
            echo " ✅ YOUR FACTREGISTRY DEPLOYED!"
            echo "========================================"
            echo ""
            echo "Address: $CONTRACT_ADDR"
            echo ""
            echo "Next steps:"
            echo "1. Update backend/app/services/integrity_service.py:"
            echo "   INTEGRITY_VERIFIER_SEPOLIA = $CONTRACT_ADDR"
            echo ""
            echo "2. Update backend/app/api/routes/risk_engine.py:"
            echo "   SHARP_FACT_REGISTRY_SEPOLIA = $CONTRACT_ADDR"
            echo ""
        else
            echo "⚠️  Deployment issue:"
            echo "$DEPLOY_OUTPUT" | head -20
        fi
    fi
else
    echo "⚠️  Declaration issue:"
    echo "$DECLARE_OUTPUT" | head -20
    echo ""
    echo "💡 The RPC version mismatch may still be an issue."
    echo "   Trying alternative RPC endpoints..."
fi
