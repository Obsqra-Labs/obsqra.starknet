#!/bin/bash
set -e

ALCHEMY_KEY="EvhYN6geLrdvbYHVRgPJ7"
RPC="https://starknet-sepolia.g.alchemy.com/v2/$ALCHEMY_KEY"
DEPLOYER_KEYSTORE="/root/.starkli-wallets/deployer/keystore.json"
DEPLOYER_ACCOUNT="/root/.starkli-wallets/deployer/account.json"
PASSWORD="L!nux123"

echo "======================================================================"
echo " DEPLOYING ACCOUNT + CONTRACTS TO SEPOLIA"
echo "======================================================================"
echo ""

# Step 1: Deploy account
echo "Step 1: Deploying Account Contract"
echo "------------------------------"
echo "Address: 0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
echo ""

# Use expect to handle password
expect << 'EOF'
set timeout -1
spawn starkli account deploy --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7 /root/.starkli-wallets/deployer/account.json --keystore /root/.starkli-wallets/deployer/keystore.json
expect "Enter password:"
send "L!nux123\r"
expect eof
EOF

echo ""
echo "✅ Account deployed!"
echo ""

# Wait a bit for propagation
echo "Waiting 10 seconds for block confirmation..."
sleep 10

# Step 2: Declare contracts
echo "======================================================================"
echo "Step 2: Declaring Contracts"
echo "======================================================================"
echo ""

declare_contract() {
    local name=$1
    local file=$2
    
    echo "Declaring $name..."
    
    expect << EOF
set timeout -1
spawn starkli declare --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7 $file --account /root/.starkli-wallets/deployer/account.json --keystore /root/.starkli-wallets/deployer/keystore.json
expect "Enter password:"
send "L!nux123\r"
expect eof
EOF
    
    echo ""
}

declare_contract "RiskEngine" "contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json"
declare_contract "DAOConstraintManager" "contracts/target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json"
declare_contract "StrategyRouter" "contracts/target/dev/obsqra_contracts_StrategyRouter.contract_class.json"

echo ""
echo "======================================================================"
echo "✅ ALL DECLARATIONS COMPLETE!"
echo "======================================================================"
echo ""
echo "Next: Deploy contract instances with starkli deploy"
