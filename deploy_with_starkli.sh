#!/bin/bash
set -e

echo "========================================"
echo " DEPLOYING YOUR OWN FACTREGISTRY"
echo "========================================"
echo ""

OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
CONTRACT_FILE="/opt/obsqra.starknet/integrity/target/dev/integrity_FactRegistry.contract_class.json"
STARKLI="/root/.starkli/bin/starkli"
KEYSTORE="$HOME/.starknet_accounts/starknet_open_zeppelin_accounts.json"

# Check if contract exists
if [ ! -f "$CONTRACT_FILE" ]; then
    echo "❌ Contract file not found. Building..."
    cd /opt/obsqra.starknet/integrity
    scarb build
fi

echo "✅ Contract file: $CONTRACT_FILE"
echo ""

# Check starkli
if [ ! -f "$STARKLI" ]; then
    echo "❌ starkli not found at $STARKLI"
    exit 1
fi

echo "📝 Step 1: Declaring contract..."
echo ""

# Try to declare - need to figure out keystore path
# The accounts file might have the keystore info
if [ -f "$KEYSTORE" ]; then
    echo "   Using keystore: $KEYSTORE"
    # Extract account name from keystore or use deployer
    ACCOUNT_NAME="deployer"
    
    # Try declaring
    DECLARE_OUTPUT=$($STARKLI declare "$CONTRACT_FILE" \
        --network sepolia \
        --account "$ACCOUNT_NAME" \
        --keystore "$KEYSTORE" 2>&1 || echo "FAILED")
    
    if echo "$DECLARE_OUTPUT" | grep -q "class_hash\|0x[0-9a-f]\{64\}"; then
        echo "✅ Declaration successful!"
        echo "$DECLARE_OUTPUT" | grep -E "class_hash|0x[0-9a-f]{64}" | head -3
        
        # Extract class hash
        CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oE "0x[0-9a-f]{64}" | head -1)
        
        if [ -n "$CLASS_HASH" ]; then
            echo ""
            echo "📝 Step 2: Deploying contract..."
            echo "   Class hash: $CLASS_HASH"
            echo "   Owner: $OWNER"
            echo ""
            
            sleep 5
            
            DEPLOY_OUTPUT=$($STARKLI deploy "$CLASS_HASH" \
                --network sepolia \
                --account "$ACCOUNT_NAME" \
                --keystore "$KEYSTORE" \
                --constructor-calldata "$OWNER" 2>&1 || echo "FAILED")
            
            if echo "$DEPLOY_OUTPUT" | grep -q "contract_address\|0x[0-9a-f]\{64\}"; then
                echo "✅ Deployment successful!"
                echo "$DEPLOY_OUTPUT" | grep -E "contract_address|0x[0-9a-f]{64}" | head -3
                
                CONTRACT_ADDR=$(echo "$DEPLOY_OUTPUT" | grep -oE "0x[0-9a-f]{64}" | head -1)
                
                echo ""
                echo "========================================"
                echo " ✅ YOUR FACTREGISTRY DEPLOYED!"
                echo "========================================"
                echo ""
                echo "Address: $CONTRACT_ADDR"
                echo ""
                echo "Next steps:"
                echo "1. Update backend/app/config.py:"
                echo "   INTEGRITY_VERIFIER_SEPOLIA = $CONTRACT_ADDR"
                echo ""
                echo "2. Update backend/.env:"
                echo "   INTEGRITY_VERIFIER_SEPOLIA=$CONTRACT_ADDR"
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
        echo "💡 Tip: You may need to set up starkli keystore separately"
    fi
else
    echo "⚠️  Keystore not found at $KEYSTORE"
    echo ""
    echo "Manual steps:"
    echo "1. Set up starkli keystore: starkli signer keystore from-key <private_key>"
    echo "2. starkli declare $CONTRACT_FILE --network sepolia"
    echo "3. starkli deploy <class_hash> --constructor-calldata $OWNER"
fi
