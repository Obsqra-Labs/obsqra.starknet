#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════"
echo "🚀 Deploy to Sepolia with sncast (Starknet Foundry)"
echo "════════════════════════════════════════════════════════"
echo ""

cd /opt/obsqra.starknet/contracts

# Step 1: Install sncast if needed
if ! command -v sncast &> /dev/null; then
    echo "📦 Installing Starknet Foundry (sncast)..."
    curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh
    export PATH="$HOME/.foundry/bin:$PATH"
    echo "✅ sncast installed"
else
    echo "✅ sncast already installed"
fi

echo ""
sncast --version
echo ""

# Step 2: Create Sepolia account
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Creating Sepolia Account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sncast account create \
    --url https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
    --name sepolia_deployer

echo ""
echo "════════════════════════════════════════════════════════"
echo "⚠️  IMPORTANT: Fund Your Account!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Before deploying, you MUST fund this account with STRK."
echo ""
echo "The account address is shown above (starts with 0x...)"
echo ""
echo "Fund it at: https://starknet-faucet.vercel.app/"
echo ""
echo "After funding, press ENTER to continue..."
read

# Step 3: Deploy account
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Deploying Account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sncast account deploy \
    --url https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
    --name sepolia_deployer

echo ""
echo "✅ Account deployed!"
echo ""

# Function to deploy a contract
deploy_contract() {
    local NAME=$1
    local FILE=$2
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Deploying $NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "Declaring..."
    DECLARE_OUT=$(sncast --account sepolia_deployer declare \
        --url https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
        --contract-name $(basename $FILE .json) 2>&1 || true)
    
    echo "$DECLARE_OUT"
    
    # Extract class hash
    CLASS_HASH=$(echo "$DECLARE_OUT" | grep -oP 'class_hash: \K0x[0-9a-fA-F]+' | head -1)
    
    if [ -z "$CLASS_HASH" ]; then
        # Try alternative pattern
        CLASS_HASH=$(echo "$DECLARE_OUT" | grep -oP '0x[0-9a-fA-F]{64}' | head -1)
    fi
    
    if [ -z "$CLASS_HASH" ]; then
        echo "⚠️  Could not extract class hash, it may already be declared"
        echo "Please enter the class hash manually:"
        read CLASS_HASH
    fi
    
    echo "✅ Class hash: $CLASS_HASH"
    echo ""
    
    echo "Deploying..."
    DEPLOY_OUT=$(sncast --account sepolia_deployer deploy \
        --url https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
        --class-hash $CLASS_HASH 2>&1)
    
    echo "$DEPLOY_OUT"
    
    CONTRACT_ADDR=$(echo "$DEPLOY_OUT" | grep -oP 'contract_address: \K0x[0-9a-fA-F]+')
    
    if [ -z "$CONTRACT_ADDR" ]; then
        CONTRACT_ADDR=$(echo "$DEPLOY_OUT" | grep -oP '0x[0-9a-fA-F]{64}' | tail -1)
    fi
    
    if [ -z "$CONTRACT_ADDR" ]; then
        echo "❌ Failed to extract contract address"
        return 1
    fi
    
    echo ""
    echo "🎉 $NAME deployed!"
    echo "Address: $CONTRACT_ADDR"
    echo "Voyager: https://sepolia.voyager.online/contract/$CONTRACT_ADDR"
    echo ""
    
    echo "$CONTRACT_ADDR"
}

# Step 4: Deploy contracts
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Deploying Contracts"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RISK_ENGINE=$(deploy_contract "RiskEngine" "target/dev/obsqra_contracts_RiskEngine.contract_class.json")
STRATEGY_ROUTER=$(deploy_contract "StrategyRouter" "target/dev/obsqra_contracts_StrategyRouter.contract_class.json")
DAO_CONSTRAINT=$(deploy_contract "DAOConstraintManager" "target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json")

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ ALL CONTRACTS DEPLOYED!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "RiskEngine:           $RISK_ENGINE"
echo "StrategyRouter:       $STRATEGY_ROUTER"
echo "DAOConstraintManager: $DAO_CONSTRAINT"
echo ""

# Update frontend
echo "📝 Updating frontend..."
cat > /opt/obsqra.starknet/frontend/.env.local << EOF
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=$RISK_ENGINE
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$STRATEGY_ROUTER
NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=$DAO_CONSTRAINT
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
EOF

echo "✅ Frontend updated!"
echo ""

# Save deployment
cat > /opt/obsqra.starknet/deployed-sepolia.json << EOF
{
  "network": "sepolia",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "contracts": {
    "riskEngine": "$RISK_ENGINE",
    "strategyRouter": "$STRATEGY_ROUTER",
    "daoConstraintManager": "$DAO_CONSTRAINT"
  }
}
EOF

echo "💾 Saved to: deployed-sepolia.json"
echo ""

# Restart frontend
echo "🔄 Restarting frontend..."
pkill -f "PORT=3002" 2>/dev/null || true
sleep 2

cd /opt/obsqra.starknet/frontend
nohup npm run dev > /tmp/frontend-sepolia.log 2>&1 &

echo "✅ Frontend started!"
echo "🌐 http://localhost:3002"
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
