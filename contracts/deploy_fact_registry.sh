#!/bin/bash
set -e

echo "========================================"
echo " DEPLOYING YOUR OWN FACTREGISTRY"
echo "========================================"
echo ""

ACCOUNT="deployer"
NETWORK="sepolia"
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

# Use the Integrity contract from the integrity directory
INTEGRITY_DIR="/opt/obsqra.starknet/integrity"
cd "$INTEGRITY_DIR"

echo "📝 Building Integrity contract..."
scarb build > /dev/null 2>&1

# Find the compiled contract
CONTRACT_FILE=$(find target -name "integrity_FactRegistry.contract_class.json" | head -1)

if [ -z "$CONTRACT_FILE" ]; then
    echo "❌ Could not find compiled contract"
    exit 1
fi

echo "✅ Found contract: $CONTRACT_FILE"
echo ""

cd /opt/obsqra.starknet/contracts

echo "📝 Declaring FactRegistry..."
DECLARE_OUTPUT=$(sncast --account $ACCOUNT declare \
    --contract-name FactRegistry \
    --network $NETWORK \
    --path "$CONTRACT_FILE" 2>&1)

echo "$DECLARE_OUTPUT" | grep -E "class_hash|Class Hash|Success|Error" | head -5

if echo "$DECLARE_OUTPUT" | grep -q "class_hash\|Class Hash\|Success"; then
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'class_hash:\s*\K0x[a-fA-F0-9]+' || \
                 echo "$DECLARE_OUTPUT" | grep -oP 'Class Hash:\s*\K0x[a-fA-F0-9]+' || \
                 echo "$DECLARE_OUTPUT" | grep -oE '0x[a-fA-F0-9]{64}' | head -1)
    
    if [ -n "$CLASS_HASH" ]; then
        echo ""
        echo "✅ Class hash: $CLASS_HASH"
        echo ""
        echo "⏳ Waiting 10 seconds..."
        sleep 10
        
        echo ""
        echo "🚀 Deploying..."
        DEPLOY_OUTPUT=$(sncast --account $ACCOUNT deploy \
            --class-hash $CLASS_HASH \
            --constructor-calldata $OWNER \
            --network $NETWORK 2>&1)
        
        echo "$DEPLOY_OUTPUT" | grep -E "contract_address|Contract Address|Success|Error" | head -5
        
        if echo "$DEPLOY_OUTPUT" | grep -q "contract_address\|Contract Address\|Success"; then
            ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract_address:\s*\K0x[a-fA-F0-9]+' || \
                   echo "$DEPLOY_OUTPUT" | grep -oP 'Contract Address:\s*\K0x[a-fA-F0-9]+' || \
                   echo "$DEPLOY_OUTPUT" | grep -oE '0x[a-fA-F0-9]{64}' | head -1)
            
            if [ -n "$ADDR" ]; then
                echo ""
                echo "========================================"
                echo " ✅ DEPLOYED!"
                echo "========================================"
                echo "Address: $ADDR"
                echo "$ADDR" > /tmp/fact_registry_address.txt
            fi
        fi
    fi
fi
