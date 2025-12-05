#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════"
echo "🚀 Deploying to Local Katana (Testing)"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Since Sepolia/Argent has issues, let's deploy locally first!"
echo ""

# Check if Katana is running
if ! curl -s http://localhost:5050 > /dev/null 2>&1; then
    echo "❌ Katana is not running!"
    echo ""
    echo "Starting Katana in background..."
    cd /opt/obsqra.starknet
    nohup katana --dev --http.cors_origins "*" > /tmp/katana.log 2>&1 &
    KATANA_PID=$!
    echo "✅ Katana started (PID: $KATANA_PID)"
    echo "📊 Logs: tail -f /tmp/katana.log"
    sleep 3
else
    echo "✅ Katana is already running"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setting up Katana account..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Use first Katana pre-funded account
KATANA_ACCOUNT="0x127fd5f1fe78a71f8bcd1fec63e3fe2f0486b6ecd5c86a0466c3a21fa5cfcec"
KATANA_PRIVATE_KEY="0xc5b2fcab997346f3ea1c00b002ecf6f382c5f9c9659a3894eb783c5320f912"
RPC="http://localhost:5050"

cd /opt/obsqra.starknet/contracts

echo "Using Katana pre-funded account:"
echo "Address: $KATANA_ACCOUNT"
echo ""

# Deploy function
deploy_contract() {
    local NAME=$1
    local FILE=$2
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Deploying $NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "Declaring..."
    DECLARE_OUT=$(starkli declare "$FILE" \
        --rpc "$RPC" \
        --private-key "$KATANA_PRIVATE_KEY" \
        --account "$KATANA_ACCOUNT" 2>&1)
    
    echo "$DECLARE_OUT"
    
    CLASS_HASH=$(echo "$DECLARE_OUT" | grep -oP 'Class hash declared: \K0x[0-9a-fA-F]+' || echo "$DECLARE_OUT" | grep -oP '0x[0-9a-fA-F]{64}' | head -1)
    
    if [ -z "$CLASS_HASH" ]; then
        echo "❌ Failed to get class hash"
        return 1
    fi
    
    echo "✅ Declared with class hash: $CLASS_HASH"
    echo ""
    
    echo "Deploying..."
    DEPLOY_OUT=$(starkli deploy "$CLASS_HASH" "$KATANA_ACCOUNT" \
        --rpc "$RPC" \
        --private-key "$KATANA_PRIVATE_KEY" \
        --account "$KATANA_ACCOUNT" 2>&1)
    
    echo "$DEPLOY_OUT"
    
    CONTRACT_ADDR=$(echo "$DEPLOY_OUT" | grep -oP 'Contract deployed: \K0x[0-9a-fA-F]+' || echo "$DEPLOY_OUT" | grep -oP '0x[0-9a-fA-F]{64}' | tail -1)
    
    if [ -z "$CONTRACT_ADDR" ]; then
        echo "❌ Failed to get contract address"
        return 1
    fi
    
    echo ""
    echo "🎉 $NAME deployed at: $CONTRACT_ADDR"
    echo ""
    
    echo "$CONTRACT_ADDR"
}

# Deploy all contracts
echo "Starting deployments..."

RISK_ENGINE=$(deploy_contract "RiskEngine" "target/dev/obsqra_contracts_RiskEngine.contract_class.json")
STRATEGY_ROUTER=$(deploy_contract "StrategyRouter" "target/dev/obsqra_contracts_StrategyRouter.contract_class.json")
DAO_CONSTRAINT=$(deploy_contract "DAOConstraintManager" "target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json")

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ ALL CONTRACTS DEPLOYED TO KATANA!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "RiskEngine:           $RISK_ENGINE"
echo "StrategyRouter:       $STRATEGY_ROUTER"
echo "DAOConstraintManager: $DAO_CONSTRAINT"
echo ""

# Update frontend
echo "📝 Updating frontend config..."
cat > /opt/obsqra.starknet/frontend/.env.local << EOF
NEXT_PUBLIC_RPC_URL=http://localhost:5050
NEXT_PUBLIC_CHAIN_ID=KATANA
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=$RISK_ENGINE
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$STRATEGY_ROUTER
NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=$DAO_CONSTRAINT
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
EOF

echo "✅ Frontend config updated!"
echo ""

# Save deployment info
cat > /opt/obsqra.starknet/deployed-katana.json << EOF
{
  "network": "katana-local",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "contracts": {
    "riskEngine": "$RISK_ENGINE",
    "strategyRouter": "$STRATEGY_ROUTER",
    "daoConstraintManager": "$DAO_CONSTRAINT"
  }
}
EOF

echo "💾 Saved to: deployed-katana.json"
echo ""

# Restart frontend
echo "🔄 Restarting frontend..."
pkill -f "PORT=3002" 2>/dev/null || true
sleep 2

cd /opt/obsqra.starknet/frontend
nohup npm run dev > /tmp/frontend-katana.log 2>&1 &
FRONTEND_PID=$!

echo "✅ Frontend restarted (PID: $FRONTEND_PID)"
echo "📊 Logs: tail -f /tmp/frontend-katana.log"
echo ""

echo "════════════════════════════════════════════════════════"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "🌐 Frontend: http://localhost:3002"
echo "⚡ Katana RPC: http://localhost:5050"
echo ""
echo "You can now test with Katana's pre-funded accounts!"
echo ""
echo "Use this account in your wallet (if compatible):"
echo "Address: $KATANA_ACCOUNT"
echo "Private Key: $KATANA_PRIVATE_KEY"
echo ""
