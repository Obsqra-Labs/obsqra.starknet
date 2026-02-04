#!/bin/bash
set -e

echo "========================================"
echo " DEPLOYING YOUR OWN FACTREGISTRY"
echo "========================================"
echo ""

ACCOUNT="deployer"
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

cd /opt/obsqra.starknet/integrity

echo "📝 Declaring FactRegistry..."
DECLARE_OUTPUT=$(sncast --account $ACCOUNT declare --contract-name FactRegistry 2>&1)

echo "$DECLARE_OUTPUT" | head -20

if echo "$DECLARE_OUTPUT" | grep -q "class_hash\|Class Hash\|Success"; then
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'class_hash:\s*\K0x[a-fA-F0-9]+' || \
                 echo "$DECLARE_OUTPUT" | grep -oP 'Class Hash:\s*\K0x[a-fA-F0-9]+' || \
                 echo "$DECLARE_OUTPUT" | grep -oE '0x[a-fA-F0-9]{64}' | head -1)
    
    if [ -z "$CLASS_HASH" ]; then
        # Try to get it from the full output
        CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -i "class" | grep -oE '0x[a-fA-F0-9]{64}' | head -1)
    fi
    
    if [ -n "$CLASS_HASH" ]; then
        echo ""
        echo "✅ Class hash: $CLASS_HASH"
        echo ""
        echo "⏳ Waiting 10 seconds for declaration to settle..."
        sleep 10
        
        echo ""
        echo "🚀 Deploying FactRegistry..."
        echo "   Owner: $OWNER"
        
        DEPLOY_OUTPUT=$(sncast --account $ACCOUNT deploy \
            --class-hash $CLASS_HASH \
            --constructor-calldata $OWNER 2>&1)
        
        echo "$DEPLOY_OUTPUT"
        
        if echo "$DEPLOY_OUTPUT" | grep -q "contract_address\|Contract Address\|Success"; then
            ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract_address:\s*\K0x[a-fA-F0-9]+' || \
                   echo "$DEPLOY_OUTPUT" | grep -oP 'Contract Address:\s*\K0x[a-fA-F0-9]+' || \
                   echo "$DEPLOY_OUTPUT" | grep -oE '0x[a-fA-F0-9]{64}' | head -1)
            
            if [ -n "$ADDR" ]; then
                echo ""
                echo "========================================"
                echo " ✅ FACTREGISTRY DEPLOYED!"
                echo "========================================"
                echo ""
                echo "Address: $ADDR"
                echo ""
                echo "📝 Update your code:"
                echo ""
                echo "1. Backend integrity_service.py:"
                echo "   INTEGRITY_VERIFIER_SEPOLIA = $ADDR"
                echo ""
                echo "2. Save this address!"
                echo "$ADDR" > /tmp/fact_registry_address.txt
            else
                echo "⚠️  Could not extract address"
            fi
        fi
    else
        echo "❌ Could not extract class hash"
        echo "Full output:"
        echo "$DECLARE_OUTPUT"
    fi
else
    echo "⚠️  Declaration output:"
    echo "$DECLARE_OUTPUT"
fi
