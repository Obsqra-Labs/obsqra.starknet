#!/bin/bash

set -e

NETWORK=${1:-testnet}
OWNER_ADDRESS=${2:-"0x..."}

echo "Deploying to $NETWORK..."

# Deploy Risk Engine
echo "Deploying Risk Engine..."
RISK_ENGINE=$(starknet deploy \
  --contract contracts/target/release/obsqra_contracts_RiskEngine.sierra.json \
  --inputs $OWNER_ADDRESS \
  --network $NETWORK \
  --no_wallet)

echo "Risk Engine deployed at: $RISK_ENGINE"

# Deploy DAO Constraint Manager
echo "Deploying DAO Constraint Manager..."
DAO_MANAGER=$(starknet deploy \
  --contract contracts/target/release/obsqra_contracts_DAOConstraintManager.sierra.json \
  --inputs $OWNER_ADDRESS 6000 3 5000 1000000 \
  --network $NETWORK \
  --no_wallet)

echo "DAO Constraint Manager deployed at: $DAO_MANAGER"

# Deploy Strategy Router
echo "Deploying Strategy Router..."
STRATEGY_ROUTER=$(starknet deploy \
  --contract contracts/target/release/obsqra_contracts_StrategyRouter.sierra.json \
  --inputs $OWNER_ADDRESS $AAVE_ADDRESS $LIDO_ADDRESS $COMPOUND_ADDRESS $RISK_ENGINE \
  --network $NETWORK \
  --no_wallet)

echo "Strategy Router deployed at: $STRATEGY_ROUTER"

# Save addresses
echo "RISK_ENGINE=$RISK_ENGINE" > .env.deployed
echo "DAO_MANAGER=$DAO_MANAGER" >> .env.deployed
echo "STRATEGY_ROUTER=$STRATEGY_ROUTER" >> .env.deployed

echo "Deployment complete!"

