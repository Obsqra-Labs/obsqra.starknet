#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════"
echo "🚀 Deploying All Contracts to Sepolia"
echo "════════════════════════════════════════════════════════"
echo ""

ACCOUNT="0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd"
RPC="https://starknet-sepolia.public.blastapi.io/rpc/v0_7"
ACCOUNT_FILE="$HOME/.starkli-wallets/deployer/account.json"
KEYSTORE="$HOME/.starkli-wallets/deployer/keystore.json"

cd /opt/obsqra.starknet/contracts

# Function to deploy a contract
deploy_contract() {
    local CONTRACT_NAME=$1
    local CONTRACT_FILE=$2
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Deploying $CONTRACT_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "1️⃣  Declaring contract..."
    DECLARE_OUTPUT=$(starkli declare \
        "$CONTRACT_FILE" \
        --rpc "$RPC" \
        --account "$ACCOUNT_FILE" \
        --keystore "$KEYSTORE" 2>&1)
    
    echo "$DECLARE_OUTPUT"
    
    # Extract class hash
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'Class hash declared: \K0x[0-9a-fA-F]+' || echo "$DECLARE_OUTPUT" | grep -oP 'Class hash: \K0x[0-9a-fA-F]+' || echo "$DECLARE_OUTPUT" | grep -oP '0x[0-9a-fA-F]{64}' | head -1)
    
    if [ -z "$CLASS_HASH" ]; then
        echo "❌ Failed to extract class hash from output"
        echo "Full output was:"
        echo "$DECLARE_OUTPUT"
        return 1
    fi
    
    echo "✅ Class hash: $CLASS_HASH"
    echo ""
    
    echo "2️⃣  Deploying contract..."
    DEPLOY_OUTPUT=$(starkli deploy \
        "$CLASS_HASH" \
        "$ACCOUNT" \
        --rpc "$RPC" \
        --account "$ACCOUNT_FILE" \
        --keystore "$KEYSTORE" 2>&1)
    
    echo "$DEPLOY_OUTPUT"
    
    # Extract contract address
    CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -oP 'Contract deployed: \K0x[0-9a-fA-F]+' || echo "$DEPLOY_OUTPUT" | grep -oP '0x[0-9a-fA-F]{64}' | tail -1)
    
    if [ -z "$CONTRACT_ADDRESS" ]; then
        echo "❌ Failed to extract contract address"
        echo "Full output was:"
        echo "$DEPLOY_OUTPUT"
        return 1
    fi
    
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "🎉 $CONTRACT_NAME Deployed!"
    echo "════════════════════════════════════════════════════════"
    echo "Class Hash:       $CLASS_HASH"
    echo "Contract Address: $CONTRACT_ADDRESS"
    echo "Voyager:          https://sepolia.voyager.online/contract/$CONTRACT_ADDRESS"
    echo "════════════════════════════════════════════════════════"
    
    # Return the address
    echo "$CONTRACT_ADDRESS"
}

# Deploy all contracts
echo "Starting deployment..."
echo ""

RISK_ENGINE=$(deploy_contract "RiskEngine" "target/dev/obsqra_contracts_RiskEngine.contract_class.json")
echo ""

STRATEGY_ROUTER=$(deploy_contract "StrategyRouter" "target/dev/obsqra_contracts_StrategyRouter.contract_class.json")
echo ""

DAO_CONSTRAINT=$(deploy_contract "DAOConstraintManager" "target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json")
echo ""

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ ALL CONTRACTS DEPLOYED!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "RiskEngine:           $RISK_ENGINE"
echo "StrategyRouter:       $STRATEGY_ROUTER"
echo "DAOConstraintManager: $DAO_CONSTRAINT"
echo ""

# Update .env.local
echo "📝 Updating frontend .env.local..."
cat > /opt/obsqra.starknet/frontend/.env.local << EOF
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=$RISK_ENGINE
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$STRATEGY_ROUTER
NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=$DAO_CONSTRAINT
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
EOF

echo "✅ Frontend config updated!"
echo ""

# Save deployment info
cat > /opt/obsqra.starknet/deployed-sepolia.json << EOF
{
  "network": "sepolia",
  "deployer": "$ACCOUNT",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "contracts": {
    "riskEngine": "$RISK_ENGINE",
    "strategyRouter": "$STRATEGY_ROUTER",
    "daoConstraintManager": "$DAO_CONSTRAINT"
  }
}
EOF

echo "💾 Deployment info saved to: deployed-sepolia.json"
echo ""

echo "════════════════════════════════════════════════════════"
echo "🔄 Restarting Frontend..."
echo "════════════════════════════════════════════════════════"
pkill -f "PORT=3002" 2>/dev/null || true
sleep 2

cd /opt/obsqra.starknet/frontend
nohup npm run dev > /tmp/frontend-sepolia.log 2>&1 &
FRONTEND_PID=$!

echo "✅ Frontend starting (PID: $FRONTEND_PID)"
echo "📊 Logs: tail -f /tmp/frontend-sepolia.log"
echo "🌐 URL: http://localhost:3002"
echo ""

echo "════════════════════════════════════════════════════════"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Visit http://localhost:3002"
echo "2. Connect your wallet (Argent X on Sepolia)"
echo "3. Test contract interactions!"
echo ""
echo "View your contracts on Voyager:"
echo "  RiskEngine:           https://sepolia.voyager.online/contract/$RISK_ENGINE"
echo "  StrategyRouter:       https://sepolia.voyager.online/contract/$STRATEGY_ROUTER"
echo "  DAOConstraintManager: https://sepolia.voyager.online/contract/$DAO_CONSTRAINT"
echo ""
