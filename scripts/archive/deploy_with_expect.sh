#!/bin/bash
set -e

RPC="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
ACCOUNT="$HOME/.starkli-wallets/deployer/account.json"
KEYSTORE="$HOME/.starkli-wallets/deployer/keystore.json"
PASSWORD="L!nux123"

cd /opt/obsqra.starknet/contracts

echo "========================================"
echo " Deploying to Sepolia via Alchemy"
echo "========================================"
echo ""

DEPLOYER=$(cat $ACCOUNT | grep address | cut -d'"' -f4)
echo "Deployer: $DEPLOYER"
echo "RPC: Alchemy"
echo ""

# Function to run starkli with password
run_with_password() {
    expect << EOF
spawn $@
expect "Enter keystore password:"
send "$PASSWORD\r"
expect eof
EOF
}

echo "Step 1: Declaring Contracts"
echo "========================================"

# Declare RiskEngine
echo "Declaring RiskEngine..."
run_with_password starkli declare \
  target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc "$RPC" \
  --account "$ACCOUNT" \
  --keystore "$KEYSTORE" > /tmp/risk.txt 2>&1

cat /tmp/risk.txt
RISK_CLASS=$(cat /tmp/risk.txt | grep "Class hash declared" | awk '{print $4}')
echo "Class Hash: $RISK_CLASS"
echo ""

# Continue with other contracts...
echo "Deploy script needs expect to be installed"
echo "Install with: yum install expect -y"

