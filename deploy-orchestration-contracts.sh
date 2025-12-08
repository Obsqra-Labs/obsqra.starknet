#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "🚀 Deploying Updated Contracts with On-Chain Orchestration"
echo "════════════════════════════════════════════════════════════════"

cd /opt/obsqra.starknet/contracts

# Configuration
ACCOUNT="katana-0"
ACCOUNT_ADDRESS="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
RPC_URL="https://starknet-sepolia.public.blastapi.io"

# Existing deployed contracts (from sepolia.json)
EXISTING_RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
EXISTING_DAO="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
EXISTING_STRATEGY_ROUTER="0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a"

# Protocol addresses (from protocol_addresses_sepolia.json)
JEDISWAP_ROUTER="0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21"
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"

echo "📋 Deployment Configuration:"
echo "  Account: $ACCOUNT_ADDRESS"
echo "  RPC: $RPC_URL"
echo "  Existing RiskEngine: $EXISTING_RISK_ENGINE"
echo "  Existing DAO: $EXISTING_DAO"
echo "  Existing StrategyRouter: $EXISTING_STRATEGY_ROUTER"
echo ""

# Step 1: Build contracts
echo "🔨 Step 1: Building contracts..."
scarb build
echo "✅ Build complete"
echo ""

# Step 2: Deploy updated RiskEngine
echo "📝 Step 2: Declaring updated RiskEngine..."
RISK_ENGINE_CLASS_HASH=$(starkli declare target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1 | grep -oP 'Class hash declared:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$RISK_ENGINE_CLASS_HASH" ]; then
  echo "⚠️  RiskEngine may already be declared. Extracting from contract..."
  RISK_ENGINE_CLASS_HASH=$(cat target/dev/obsqra_contracts_RiskEngine.contract_class.json | python3 -c "import sys, json; print(json.load(sys.stdin).get('class_hash', ''))" 2>/dev/null || echo "")
fi

echo "✅ RiskEngine Class Hash: $RISK_ENGINE_CLASS_HASH"
echo ""

echo "🚀 Step 3: Deploying updated RiskEngine..."
RISK_ENGINE_ARGS="$ACCOUNT_ADDRESS $EXISTING_STRATEGY_ROUTER $EXISTING_DAO"

NEW_RISK_ENGINE=$(starkli deploy $RISK_ENGINE_CLASS_HASH \
  $RISK_ENGINE_ARGS \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1 | grep -oP 'Contract deployed:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$NEW_RISK_ENGINE" ]; then
  echo "❌ RiskEngine deployment failed"
  exit 1
fi

echo "✅ RiskEngine deployed: $NEW_RISK_ENGINE"
echo ""

# Step 4: Deploy updated StrategyRouterV2
echo "📝 Step 4: Declaring updated StrategyRouterV2..."
ROUTER_CLASS_HASH=$(starkli declare target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1 | grep -oP 'Class hash declared:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$ROUTER_CLASS_HASH" ]; then
  echo "⚠️  StrategyRouterV2 may already be declared. Extracting from contract..."
  ROUTER_CLASS_HASH=$(cat target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json | python3 -c "import sys, json; print(json.load(sys.stdin).get('class_hash', ''))" 2>/dev/null || echo "")
fi

echo "✅ StrategyRouterV2 Class Hash: $ROUTER_CLASS_HASH"
echo ""

echo "🚀 Step 5: Deploying updated StrategyRouterV2..."
ROUTER_ARGS="$ACCOUNT_ADDRESS $JEDISWAP_ROUTER $EKUBO_CORE $NEW_RISK_ENGINE $EXISTING_DAO $STRK_TOKEN"

NEW_STRATEGY_ROUTER=$(starkli deploy $ROUTER_CLASS_HASH \
  $ROUTER_ARGS \
  --rpc $RPC_URL \
  --account $ACCOUNT \
  2>&1 | grep -oP 'Contract deployed:\s*\K0x[a-fA-F0-9]+' || echo "")

if [ -z "$NEW_STRATEGY_ROUTER" ]; then
  echo "❌ StrategyRouterV2 deployment failed"
  exit 1
fi

echo "✅ StrategyRouterV2 deployed: $NEW_STRATEGY_ROUTER"
echo ""

# Step 6: Update RiskEngine with new StrategyRouter address
echo "🔧 Step 6: Updating RiskEngine with new StrategyRouter address..."
# Note: This would require a setter function or redeployment
# For now, we'll note this in the output
echo "⚠️  Note: RiskEngine needs to be updated with new StrategyRouter address"
echo "   Current: $EXISTING_STRATEGY_ROUTER"
echo "   New: $NEW_STRATEGY_ROUTER"
echo ""

# Step 7: Update deployment files
echo "📝 Step 7: Updating deployment files..."

python3 << EOF
import json
from datetime import datetime

# Load existing deployments
try:
    with open('deployments/sepolia.json', 'r') as f:
        deployments = json.load(f)
except:
    deployments = {
        "network": "sepolia",
        "rpc": "$RPC_URL",
        "deployer": "$ACCOUNT_ADDRESS",
        "contracts": {},
        "classHashes": {},
        "explorer": {}
    }

# Update RiskEngine
deployments['contracts']['riskEngine'] = "$NEW_RISK_ENGINE"
deployments['classHashes']['riskEngine'] = "$RISK_ENGINE_CLASS_HASH"
deployments['explorer']['riskEngine'] = f"https://sepolia.starkscan.co/contract/$NEW_RISK_ENGINE"

# Update StrategyRouterV2
deployments['contracts']['strategyRouterV2'] = "$NEW_STRATEGY_ROUTER"
deployments['classHashes']['strategyRouterV2'] = "$ROUTER_CLASS_HASH"
deployments['explorer']['strategyRouterV2'] = f"https://sepolia.starkscan.co/contract/$NEW_STRATEGY_ROUTER"

# Keep existing DAO
deployments['contracts']['daoConstraintManager'] = "$EXISTING_DAO"

# Add deployment timestamp
deployments['deployedAt'] = datetime.now().isoformat()
deployments['version'] = "orchestration-v1"

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
        "deployer": "$ACCOUNT_ADDRESS",
        "contracts": {
            "riskEngine": "$NEW_RISK_ENGINE",
            "daoConstraintManager": "$EXISTING_DAO",
            "strategyRouter": "$NEW_STRATEGY_ROUTER"
        },
        "classHashes": {
            "riskEngine": "$RISK_ENGINE_CLASS_HASH",
            "daoConstraintManager": "",
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
echo "⚠️  IMPORTANT: Update RiskEngine with new StrategyRouter address"
echo "   (May require contract upgrade or setter function)"
echo ""

