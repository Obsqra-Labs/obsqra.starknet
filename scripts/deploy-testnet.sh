#!/bin/bash

set -e

echo "========================================"
echo "Obsqra Testnet Deployment"
echo "========================================"
echo ""

# Check for wallet address
if [ -z "$1" ]; then
    echo "Usage: ./scripts/deploy-testnet.sh YOUR_WALLET_ADDRESS"
    echo ""
    echo "Get your wallet address from ArgentX:"
    echo "  1. Open ArgentX"
    echo "  2. Click on account name"
    echo "  3. Click 'Copy address'"
    echo ""
    exit 1
fi

OWNER_ADDRESS=$1
RPC_URL=${STARKNET_RPC:-"https://starknet-sepolia.public.blastapi.io"}
ACCOUNT_NAME=${STARKNET_ACCOUNT:-"my_testnet"}

echo "Configuration:"
echo "  RPC: $RPC_URL"
echo "  Account: $ACCOUNT_NAME"
echo "  Owner: $OWNER_ADDRESS"
echo ""

# Build contracts
echo "========================================"
echo "Building Contracts..."
echo "========================================"
cd /opt/obsqra.starknet/contracts
scarb build
echo "✓ Contracts built"
echo ""

# Check if account exists
if ! sncast account list 2>/dev/null | grep -q "$ACCOUNT_NAME"; then
    echo "Account '$ACCOUNT_NAME' not found."
    echo ""
    echo "To import your wallet:"
    echo "  sncast account import \\"
    echo "    --url $RPC_URL \\"
    echo "    --name $ACCOUNT_NAME \\"
    echo "    --address YOUR_ADDRESS \\"
    echo "    --private-key YOUR_PRIVATE_KEY \\"
    echo "    --type oz"
    echo ""
    exit 1
fi

# Declare contracts
echo "========================================"
echo "Declaring Contracts..."
echo "========================================"
echo ""

echo "1. Declaring RiskEngine..."
RISK_ENGINE_DECLARE=$(sncast declare \
    --url "$RPC_URL" \
    --account "$ACCOUNT_NAME" \
    --contract-name RiskEngine \
    2>&1)

RISK_ENGINE_CLASS=$(echo "$RISK_ENGINE_DECLARE" | grep -oP 'class_hash: \K0x[0-9a-f]+' | head -1)
echo "   Class Hash: $RISK_ENGINE_CLASS"
echo ""

echo "2. Declaring DAOConstraintManager..."
DAO_MANAGER_DECLARE=$(sncast declare \
    --url "$RPC_URL" \
    --account "$ACCOUNT_NAME" \
    --contract-name DAOConstraintManager \
    2>&1)

DAO_MANAGER_CLASS=$(echo "$DAO_MANAGER_DECLARE" | grep -oP 'class_hash: \K0x[0-9a-f]+' | head -1)
echo "   Class Hash: $DAO_MANAGER_CLASS"
echo ""

echo "3. Declaring StrategyRouter..."
STRATEGY_ROUTER_DECLARE=$(sncast declare \
    --url "$RPC_URL" \
    --account "$ACCOUNT_NAME" \
    --contract-name StrategyRouter \
    2>&1)

STRATEGY_ROUTER_CLASS=$(echo "$STRATEGY_ROUTER_DECLARE" | grep -oP 'class_hash: \K0x[0-9a-f]+' | head -1)
echo "   Class Hash: $STRATEGY_ROUTER_CLASS"
echo ""

# Deploy contracts
echo "========================================"
echo "Deploying Contracts..."
echo "========================================"
echo ""

echo "1. Deploying RiskEngine..."
RISK_ENGINE_DEPLOY=$(sncast deploy \
    --url "$RPC_URL" \
    --account "$ACCOUNT_NAME" \
    --class-hash "$RISK_ENGINE_CLASS" \
    --constructor-calldata "$OWNER_ADDRESS" \
    2>&1)

RISK_ENGINE_ADDR=$(echo "$RISK_ENGINE_DEPLOY" | grep -oP 'contract_address: \K0x[0-9a-f]+' | head -1)
echo "   ✓ Deployed: $RISK_ENGINE_ADDR"
echo ""

echo "2. Deploying DAOConstraintManager..."
DAO_MANAGER_DEPLOY=$(sncast deploy \
    --url "$RPC_URL" \
    --account "$ACCOUNT_NAME" \
    --class-hash "$DAO_MANAGER_CLASS" \
    --constructor-calldata \
        "$OWNER_ADDRESS" \
        "6000" \
        "3" \
        "5000" \
        "1000000" \
    2>&1)

DAO_MANAGER_ADDR=$(echo "$DAO_MANAGER_DEPLOY" | grep -oP 'contract_address: \K0x[0-9a-f]+' | head -1)
echo "   ✓ Deployed: $DAO_MANAGER_ADDR"
echo ""

echo "3. Deploying StrategyRouter..."
# Using placeholder Starknet protocol addresses (update with real addresses)
NOSTRA_ADDR="0x0456"  # TODO: Replace with real Nostra lending pool address
ZKLEND_ADDR="0x0789"  # TODO: Replace with real zkLend market address
EKUBO_ADDR="0x0abc"   # TODO: Replace with real Ekubo protocol address

STRATEGY_ROUTER_DEPLOY=$(sncast deploy \
    --url "$RPC_URL" \
    --account "$ACCOUNT_NAME" \
    --class-hash "$STRATEGY_ROUTER_CLASS" \
    --constructor-calldata \
        "$OWNER_ADDRESS" \
        "$NOSTRA_ADDR" \
        "$ZKLEND_ADDR" \
        "$EKUBO_ADDR" \
        "$RISK_ENGINE_ADDR" \
    2>&1)

STRATEGY_ROUTER_ADDR=$(echo "$STRATEGY_ROUTER_DEPLOY" | grep -oP 'contract_address: \K0x[0-9a-f]+' | head -1)
echo "   ✓ Deployed: $STRATEGY_ROUTER_ADDR"
echo ""

# Save addresses
echo "========================================"
echo "Saving Addresses..."
echo "========================================"

cat > /opt/obsqra.starknet/.env.testnet << EOF
# Starknet Testnet Deployment
STARKNET_RPC=$RPC_URL
STARKNET_ACCOUNT=$ACCOUNT_NAME
OWNER_ADDRESS=$OWNER_ADDRESS

# Contract Addresses
RISK_ENGINE_ADDRESS=$RISK_ENGINE_ADDR
DAO_MANAGER_ADDRESS=$DAO_MANAGER_ADDR
STRATEGY_ROUTER_ADDRESS=$STRATEGY_ROUTER_ADDR

# Starknet Protocol Addresses (placeholders - update with real addresses)
NOSTRA_ADDRESS=$NOSTRA_ADDR
ZKLEND_ADDRESS=$ZKLEND_ADDR
EKUBO_ADDRESS=$EKUBO_ADDR

# Block Explorer
VOYAGER=https://sepolia.voyager.online/contract/$STRATEGY_ROUTER_ADDR
STARKSCAN=https://sepolia.starkscan.co/contract/$STRATEGY_ROUTER_ADDR
EOF

echo "✓ Saved to .env.testnet"
echo ""

# Summary
echo "========================================"
echo "DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "Contract Addresses:"
echo "  RiskEngine:          $RISK_ENGINE_ADDR"
echo "  DAOConstraintManager: $DAO_MANAGER_ADDR"
echo "  StrategyRouter:      $STRATEGY_ROUTER_ADDR"
echo ""
echo "View on Block Explorer:"
echo "  Voyager:   https://sepolia.voyager.online/contract/$STRATEGY_ROUTER_ADDR"
echo "  Starkscan: https://sepolia.starkscan.co/contract/$STRATEGY_ROUTER_ADDR"
echo ""
echo "Next steps:"
echo "  1. Update frontend/.env.local with these addresses"
echo "  2. Test contracts: sncast call --contract-address $DAO_MANAGER_ADDR --function get_constraints"
echo "  3. Start frontend: cd frontend && npm run dev"
echo ""

