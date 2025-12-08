#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "🚀 Deploying Updated Contracts with On-Chain Orchestration (starkli)"
echo "════════════════════════════════════════════════════════════════"

cd /opt/obsqra.starknet/contracts

# Configuration
ACCOUNT="katana-0"
RPC_URL="https://starknet-sepolia.public.blastapi.io"
DEPLOYER_ADDRESS="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"

# Existing deployed contracts
EXISTING_RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
EXISTING_DAO="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
EXISTING_STRATEGY_ROUTER="0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a"

# Protocol addresses
JEDISWAP_ROUTER="0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21"
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"

echo "📋 Deployment Configuration:"
echo "  Account: $ACCOUNT"
echo "  Deployer: $DEPLOYER_ADDRESS"
echo "  RPC: $RPC_URL"
echo ""

# Step 1: Build contracts
echo "🔨 Step 1: Building contracts..."
scarb build
echo "✅ Build complete"
echo ""

# Step 2: Declare RiskEngine
echo "📝 Step 2: Declaring updated RiskEngine..."
RISK_ENGINE_DECLARE_OUTPUT=$(starkli declare target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1)

RISK_ENGINE_CLASS_HASH=$(echo "$RISK_ENGINE_DECLARE_OUTPUT" | grep -oP 'class hash declared:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$RISK_ENGINE_CLASS_HASH" ]; then
  echo "⚠️  RiskEngine may already be declared. Extracting from contract..."
  RISK_ENGINE_CLASS_HASH=$(python3 -c "
import json
with open('target/dev/obsqra_contracts_RiskEngine.contract_class.json') as f:
    data = json.load(f)
    print(data.get('class_hash', ''))
" 2>/dev/null || echo "")
  
  if [ -z "$RISK_ENGINE_CLASS_HASH" ]; then
    echo "❌ Could not determine RiskEngine class hash"
    echo "Output: $RISK_ENGINE_DECLARE_OUTPUT"
    exit 1
  fi
  echo "📌 Using class hash from contract: $RISK_ENGINE_CLASS_HASH"
else
  echo "✅ RiskEngine Class Hash: $RISK_ENGINE_CLASS_HASH"
fi
echo ""

# Step 3: Deploy RiskEngine
echo "🚀 Step 3: Deploying updated RiskEngine..."
echo "   Constructor args: owner=$DEPLOYER_ADDRESS, strategy_router=$EXISTING_STRATEGY_ROUTER, dao_manager=$EXISTING_DAO"

RISK_ENGINE_DEPLOY_OUTPUT=$(starkli deploy $RISK_ENGINE_CLASS_HASH \
  $DEPLOYER_ADDRESS \
  $EXISTING_STRATEGY_ROUTER \
  $EXISTING_DAO \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1)

NEW_RISK_ENGINE=$(echo "$RISK_ENGINE_DEPLOY_OUTPUT" | grep -oP 'Contract deployed:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$NEW_RISK_ENGINE" ]; then
  echo "❌ RiskEngine deployment failed"
  echo "Output: $RISK_ENGINE_DEPLOY_OUTPUT"
  exit 1
fi

echo "✅ RiskEngine deployed: $NEW_RISK_ENGINE"
echo ""

# Step 4: Declare StrategyRouterV2
echo "📝 Step 4: Declaring updated StrategyRouterV2..."
ROUTER_DECLARE_OUTPUT=$(starkli declare target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1)

ROUTER_CLASS_HASH=$(echo "$ROUTER_DECLARE_OUTPUT" | grep -oP 'class hash declared:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$ROUTER_CLASS_HASH" ]; then
  echo "⚠️  StrategyRouterV2 may already be declared. Extracting from contract..."
  ROUTER_CLASS_HASH=$(python3 -c "
import json
with open('target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json') as f:
    data = json.load(f)
    print(data.get('class_hash', ''))
" 2>/dev/null || echo "")
  
  if [ -z "$ROUTER_CLASS_HASH" ]; then
    echo "❌ Could not determine StrategyRouterV2 class hash"
    echo "Output: $ROUTER_DECLARE_OUTPUT"
    exit 1
  fi
  echo "📌 Using class hash from contract: $ROUTER_CLASS_HASH"
else
  echo "✅ StrategyRouterV2 Class Hash: $ROUTER_CLASS_HASH"
fi
echo ""

# Step 5: Deploy StrategyRouterV2
echo "🚀 Step 5: Deploying updated StrategyRouterV2..."
echo "   Constructor args:"
echo "     owner=$DEPLOYER_ADDRESS"
echo "     jediswap_router=$JEDISWAP_ROUTER"
echo "     ekubo_core=$EKUBO_CORE"
echo "     risk_engine=$NEW_RISK_ENGINE"
echo "     dao_manager=$EXISTING_DAO"
echo "     asset_token=$STRK_TOKEN"

ROUTER_DEPLOY_OUTPUT=$(starkli deploy $ROUTER_CLASS_HASH \
  $DEPLOYER_ADDRESS \
  $JEDISWAP_ROUTER \
  $EKUBO_CORE \
  $NEW_RISK_ENGINE \
  $EXISTING_DAO \
  $STRK_TOKEN \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1)

NEW_STRATEGY_ROUTER=$(echo "$ROUTER_DEPLOY_OUTPUT" | grep -oP 'Contract deployed:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$NEW_STRATEGY_ROUTER" ]; then
  echo "❌ StrategyRouterV2 deployment failed"
  echo "Output: $ROUTER_DEPLOY_OUTPUT"
  exit 1
fi

echo "✅ StrategyRouterV2 deployed: $NEW_STRATEGY_ROUTER"
echo ""

# Step 6: Update deployment files
echo "📝 Step 6: Updating deployment files..."

python3 << EOF
import json
from datetime import datetime

# Load existing deployments
try:
    with open('deployments/sepolia.json', 'r') as f:
        deployments = json.load(f)
except:
    deployments = {
        "network": "starknet-sepolia",
        "chainId": "SN_SEPOLIA",
        "deployer": "$DEPLOYER_ADDRESS",
        "contracts": {},
        "classHashes": {},
        "explorer": {"base": "https://sepolia.starkscan.co"}
    }

# Update RiskEngine
deployments['contracts']['RiskEngine'] = {
    "address": "$NEW_RISK_ENGINE",
    "classHash": "$RISK_ENGINE_CLASS_HASH",
    "txHash": "deployed_via_orchestration"
}
deployments['classHashes']['RiskEngine'] = "$RISK_ENGINE_CLASS_HASH"
deployments['explorer']['RiskEngine'] = f"https://sepolia.starkscan.co/contract/$NEW_RISK_ENGINE"

# Update StrategyRouterV2
deployments['contracts']['StrategyRouterV2'] = {
    "address": "$NEW_STRATEGY_ROUTER",
    "classHash": "$ROUTER_CLASS_HASH",
    "txHash": "deployed_via_orchestration"
}
deployments['classHashes']['StrategyRouterV2'] = "$ROUTER_CLASS_HASH"
deployments['explorer']['StrategyRouterV2'] = f"https://sepolia.starkscan.co/contract/$NEW_STRATEGY_ROUTER"

# Keep existing DAO
deployments['contracts']['DAOConstraintManager'] = {
    "address": "$EXISTING_DAO",
    "classHash": "0x2d1f4d6d7becf61f0a8a8becad991327aa20d8bbbb1bec437bfe4c75e64021a",
    "txHash": "existing"
}

# Add deployment metadata
deployments['deployedAt'] = datetime.now().isoformat()
deployments['version'] = "orchestration-v1"
deployments['orchestration'] = True

# Save
with open('deployments/sepolia.json', 'w') as f:
    json.dump(deployments, f, indent=2)

print("✅ Updated deployments/sepolia.json")
EOF

# Also update the root deployed-sepolia.json
python3 << EOF
import json

with open('../deployed-sepolia.json', 'w') as f:
    json.dump({
        "network": "sepolia",
        "rpc": "$RPC_URL",
        "deployer": "$DEPLOYER_ADDRESS",
        "contracts": {
            "riskEngine": "$NEW_RISK_ENGINE",
            "daoConstraintManager": "$EXISTING_DAO",
            "strategyRouter": "$NEW_STRATEGY_ROUTER"
        },
        "classHashes": {
            "riskEngine": "$RISK_ENGINE_CLASS_HASH",
            "daoConstraintManager": "0x2d1f4d6d7becf61f0a8a8becad991327aa20d8bbbb1bec437bfe4c75e64021a",
            "strategyRouter": "$ROUTER_CLASS_HASH"
        }
    }, f, indent=2)

print("✅ Updated ../deployed-sepolia.json")
EOF

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Contract Addresses:"
echo "   RiskEngine: $NEW_RISK_ENGINE"
echo "   StrategyRouterV2: $NEW_STRATEGY_ROUTER"
echo "   DAOConstraintManager: $EXISTING_DAO"
echo ""
echo "🔗 Explorer Links:"
echo "   RiskEngine: https://sepolia.starkscan.co/contract/$NEW_RISK_ENGINE"
echo "   StrategyRouterV2: https://sepolia.starkscan.co/contract/$NEW_STRATEGY_ROUTER"
echo ""
echo "🔧 Next Steps:"
echo "   1. Update frontend/.env.local:"
echo "      NEXT_PUBLIC_RISK_ENGINE_ADDRESS=$NEW_RISK_ENGINE"
echo "      NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$NEW_STRATEGY_ROUTER"
echo "   2. Restart frontend service"
echo "   3. Test AI orchestration flow"
echo ""

