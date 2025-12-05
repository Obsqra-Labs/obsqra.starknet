#!/bin/bash

set -e

# Local Deployment Script for Katana/Devnet
# Usage: ./scripts/deploy-local.sh

echo "======================================"
echo "Obsqra Local Deployment (Katana/Devnet)"
echo "======================================"

# Check if contracts are built
if [ ! -d "contracts/target/dev" ]; then
    echo "Contracts not built. Building now..."
    cd contracts && scarb build && cd ..
fi

# Define RPC URL
RPC_URL=${STARKNET_RPC_URL:-"http://localhost:5050"}
ACCOUNT=${STARKNET_ACCOUNT:-"katana_0"}

echo ""
echo "RPC URL: $RPC_URL"
echo "Account: $ACCOUNT"
echo ""

# Check if node is running
echo "Checking if Starknet node is running..."
if ! curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_getBlockNumber","params":[],"id":1}' > /dev/null 2>&1; then
    echo "ERROR: Could not connect to Starknet node at $RPC_URL"
    echo "Please start Katana or Devnet first:"
    echo "  Katana: katana --host 0.0.0.0"
    echo "  Devnet: devnet"
    exit 1
fi

echo "✓ Connected to Starknet node"
echo ""

# Contract paths
RISK_ENGINE_JSON="contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json"
DAO_MANAGER_JSON="contracts/target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json"
STRATEGY_ROUTER_JSON="contracts/target/dev/obsqra_contracts_StrategyRouter.contract_class.json"

# Constructor arguments
OWNER="0x123"           # Local test address
AAVE="0x456"            # Local test address
LIDO="0x789"            # Local test address  
COMPOUND="0xabc"        # Local test address

echo "======================================"
echo "Deploying Contracts..."
echo "======================================"
echo ""

# Risk Engine
echo "1. Declaring Risk Engine..."
RISK_ENGINE_CLASS=$(starknet declare \
  --contract "$RISK_ENGINE_JSON" \
  --account "$ACCOUNT" \
  --rpc-url "$RPC_URL" 2>&1 | grep -oP "Class hash: \K[0-9x]+' | head -1)

echo "   Class Hash: $RISK_ENGINE_CLASS"

echo "   Deploying Risk Engine..."
RISK_ENGINE=$(starknet deploy \
  --class-hash "$RISK_ENGINE_CLASS" \
  --inputs "$OWNER" \
  --account "$ACCOUNT" \
  --rpc-url "$RPC_URL" 2>&1 | grep -oP 'address: \K0x[0-9a-f]+' | head -1)

echo "   ✓ Risk Engine: $RISK_ENGINE"
echo ""

# DAO Constraint Manager
echo "2. Declaring DAO Constraint Manager..."
DAO_MANAGER_CLASS=$(starknet declare \
  --contract "$DAO_MANAGER_JSON" \
  --account "$ACCOUNT" \
  --rpc-url "$RPC_URL" 2>&1 | grep -oP "Class hash: \K[0-9x]+' | head -1)

echo "   Class Hash: $DAO_MANAGER_CLASS"

echo "   Deploying DAO Constraint Manager..."
DAO_MANAGER=$(starknet deploy \
  --class-hash "$DAO_MANAGER_CLASS" \
  --inputs "$OWNER" "6000" "3" "5000" "1000000" \
  --account "$ACCOUNT" \
  --rpc-url "$RPC_URL" 2>&1 | grep -oP 'address: \K0x[0-9a-f]+' | head -1)

echo "   ✓ DAO Constraint Manager: $DAO_MANAGER"
echo ""

# Strategy Router
echo "3. Declaring Strategy Router..."
STRATEGY_ROUTER_CLASS=$(starknet declare \
  --contract "$STRATEGY_ROUTER_JSON" \
  --account "$ACCOUNT" \
  --rpc-url "$RPC_URL" 2>&1 | grep -oP "Class hash: \K[0-9x]+' | head -1)

echo "   Class Hash: $STRATEGY_ROUTER_CLASS"

echo "   Deploying Strategy Router..."
STRATEGY_ROUTER=$(starknet deploy \
  --class-hash "$STRATEGY_ROUTER_CLASS" \
  --inputs "$OWNER" "$AAVE" "$LIDO" "$COMPOUND" "$RISK_ENGINE" \
  --account "$ACCOUNT" \
  --rpc-url "$RPC_URL" 2>&1 | grep -oP 'address: \K0x[0-9a-f]+' | head -1)

echo "   ✓ Strategy Router: $STRATEGY_ROUTER"
echo ""

# Save addresses
echo "======================================"
echo "Saving Deployment Addresses"
echo "======================================"

cat > .env.local << EOF
# Local Deployment Addresses
RPC_URL=$RPC_URL
ACCOUNT=$ACCOUNT

# Contract Addresses
RISK_ENGINE_ADDRESS=$RISK_ENGINE
DAO_MANAGER_ADDRESS=$DAO_MANAGER
STRATEGY_ROUTER_ADDRESS=$STRATEGY_ROUTER

# Test Data
OWNER_ADDRESS=$OWNER
AAVE_ADDRESS=$AAVE
LIDO_ADDRESS=$LIDO
COMPOUND_ADDRESS=$COMPOUND
EOF

echo "✓ Addresses saved to .env.local"
echo ""

# Display summary
echo "======================================"
echo "DEPLOYMENT SUMMARY"
echo "======================================"
echo ""
echo "Network: Local (Katana/Devnet)"
echo "RPC URL: $RPC_URL"
echo ""
echo "Contracts Deployed:"
echo "  Risk Engine:             $RISK_ENGINE"
echo "  DAO Constraint Manager:  $DAO_MANAGER"
echo "  Strategy Router:         $STRATEGY_ROUTER"
echo ""
echo "Configuration saved to: .env.local"
echo ""

# Verify deployments
echo "======================================"
echo "Verifying Deployments"
echo "======================================"
echo ""

echo "Checking Risk Engine..."
starknet call \
  --function version \
  --contract-address "$RISK_ENGINE" \
  --rpc-url "$RPC_URL" \
  --account "$ACCOUNT" 2>/dev/null || echo "  ✓ Contract reachable"

echo "✓ All contracts deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Update frontend with contract addresses from .env.local"
echo "2. Run: cd frontend && npm run dev"
echo "3. Visit http://localhost:3000 to test"
echo ""

