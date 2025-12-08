#!/bin/bash
set -e

export PASSWORD='L!nux123'

cd /opt/obsqra.starknet/contracts

RPC="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
ACCOUNT="$HOME/.starkli-wallets/deployer/account.json"
KEYSTORE="$HOME/.starkli-wallets/deployer/keystore.json"

echo "========================================"
echo " Deploying to Sepolia"
echo "========================================"
echo ""

# Get deployer address
DEPLOYER=$(cat $ACCOUNT | grep address | cut -d'"' -f4)
echo "Deployer: $DEPLOYER"
echo ""

echo "Step 1: Declaring Contracts"
echo "========================================"

# Declare RiskEngine
echo "Declaring RiskEngine..."
echo "$PASSWORD" | starkli declare \
  target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc $RPC \
  --account $ACCOUNT \
  --keystore $KEYSTORE \
  > /tmp/risk_declare.txt 2>&1

RISK_CLASS=$(cat /tmp/risk_declare.txt | grep "Class hash declared" | awk '{print $4}')
if [ -z "$RISK_CLASS" ]; then
  RISK_CLASS=$(cat /tmp/risk_declare.txt | grep "0x" | grep -v "Transaction" | head -1 | awk '{print $NF}')
fi
echo "Class Hash: $RISK_CLASS"
cat /tmp/risk_declare.txt | grep -E "(declared|Error)" || true
echo ""

# Declare DAOConstraintManager
echo "Declaring DAOConstraintManager..."
echo "$PASSWORD" | starkli declare \
  target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json \
  --rpc $RPC \
  --account $ACCOUNT \
  --keystore $KEYSTORE \
  > /tmp/dao_declare.txt 2>&1

DAO_CLASS=$(cat /tmp/dao_declare.txt | grep "Class hash declared" | awk '{print $4}')
if [ -z "$DAO_CLASS" ]; then
  DAO_CLASS=$(cat /tmp/dao_declare.txt | grep "0x" | grep -v "Transaction" | head -1 | awk '{print $NF}')
fi
echo "Class Hash: $DAO_CLASS"
cat /tmp/dao_declare.txt | grep -E "(declared|Error)" || true
echo ""

# Declare StrategyRouter
echo "Declaring StrategyRouter..."
echo "$PASSWORD" | starkli declare \
  target/dev/obsqra_contracts_StrategyRouter.contract_class.json \
  --rpc $RPC \
  --account $ACCOUNT \
  --keystore $KEYSTORE \
  > /tmp/router_declare.txt 2>&1

ROUTER_CLASS=$(cat /tmp/router_declare.txt | grep "Class hash declared" | awk '{print $4}')
if [ -z "$ROUTER_CLASS" ]; then
  ROUTER_CLASS=$(cat /tmp/router_declare.txt | grep "0x" | grep -v "Transaction" | head -1 | awk '{print $NF}')
fi
echo "Class Hash: $ROUTER_CLASS"
cat /tmp/router_declare.txt | grep -E "(declared|Error)" || true
echo ""

echo "Step 2: Deploying Contracts"
echo "========================================"

# Deploy RiskEngine
echo "Deploying RiskEngine..."
echo "$PASSWORD" | starkli deploy \
  $RISK_CLASS \
  $DEPLOYER \
  --rpc $RPC \
  --account $ACCOUNT \
  --keystore $KEYSTORE \
  > /tmp/risk_deploy.txt 2>&1

RISK_ADDR=$(cat /tmp/risk_deploy.txt | grep "Contract deployed" | awk '{print $3}')
echo "Address: $RISK_ADDR"
cat /tmp/risk_deploy.txt | grep -E "(deployed|Error)" || true
echo ""

# Deploy DAOConstraintManager
echo "Deploying DAOConstraintManager..."
echo "$PASSWORD" | starkli deploy \
  $DAO_CLASS \
  $DEPLOYER 6000 3 5000 1000000 \
  --rpc $RPC \
  --account $ACCOUNT \
  --keystore $KEYSTORE \
  > /tmp/dao_deploy.txt 2>&1

DAO_ADDR=$(cat /tmp/dao_deploy.txt | grep "Contract deployed" | awk '{print $3}')
echo "Address: $DAO_ADDR"
cat /tmp/dao_deploy.txt | grep -E "(deployed|Error)" || true
echo ""

# Deploy StrategyRouter
echo "Deploying StrategyRouter..."
echo "$PASSWORD" | starkli deploy \
  $ROUTER_CLASS \
  $DEPLOYER 0x456 0x789 0xabc $RISK_ADDR \
  --rpc $RPC \
  --account $ACCOUNT \
  --keystore $KEYSTORE \
  > /tmp/router_deploy.txt 2>&1

ROUTER_ADDR=$(cat /tmp/router_deploy.txt | grep "Contract deployed" | awk '{print $3}')
echo "Address: $ROUTER_ADDR"
cat /tmp/router_deploy.txt | grep -E "(deployed|Error)" || true
echo ""

# Save addresses
cd /opt/obsqra.starknet
cat > .env.sepolia << EOF
NETWORK=sepolia
RPC_URL=$RPC
DEPLOYER_ADDRESS=$DEPLOYER

RISK_ENGINE_ADDRESS=$RISK_ADDR
DAO_MANAGER_ADDRESS=$DAO_ADDR
STRATEGY_ROUTER_ADDRESS=$ROUTER_ADDR
EOF

echo "========================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "Contracts:"
echo "  RiskEngine:          $RISK_ADDR"
echo "  DAOConstraintManager: $DAO_ADDR"
echo "  StrategyRouter:      $ROUTER_ADDR"
echo ""
echo "View on Voyager:"
echo "  https://sepolia.voyager.online/contract/$ROUTER_ADDR"
echo ""

# Cleanup
rm -f /tmp/*_declare.txt /tmp/*_deploy.txt

