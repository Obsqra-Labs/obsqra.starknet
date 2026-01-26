#!/bin/bash

set -e

# Configuration
ACCOUNT_ADDRESS="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
ACCOUNT_FILE="/root/.starkli-wallets/deployer/account.json"
KEYSTORE_FILE="/root/.starkli-wallets/deployer/keystore.json"
KEYSTORE_PASSWORD="L!nux123"
NETWORK="sepolia"

RISK_ENGINE_PATH="/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json"
STRATEGY_ROUTER_PATH="/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json"

OUTPUT_FILE="/opt/obsqra.starknet/deployment_results.txt"

echo "=" > "$OUTPUT_FILE"
echo "STARKNET DEPLOYMENT WITH STARKLI" >> "$OUTPUT_FILE"
echo "=" >> "$OUTPUT_FILE"
echo "Account: $ACCOUNT_ADDRESS" >> "$OUTPUT_FILE"
echo "Network: $NETWORK" >> "$OUTPUT_FILE"
echo "Time: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Function to declare contract
declare_contract() {
    local name=$1
    local path=$2
    
    echo "Declaring $name..."
    echo "  From: $path"
    
    # Use echo to pipe password
    export STARKLI_KEYSTORE_PASSWORD="$KEYSTORE_PASSWORD"
    
    output=$(starkli declare "$path" \
        --account "$ACCOUNT_FILE" \
        --keystore "$KEYSTORE_FILE" \
        --network "$NETWORK" 2>&1) || {
        echo "✗ Failed to declare $name"
        echo "Error output:" >> "$OUTPUT_FILE"
        echo "$output" >> "$OUTPUT_FILE"
        return 1
    }
    
    echo "$output"
    echo "" >> "$OUTPUT_FILE"
    echo "$name Declaration Output:" >> "$OUTPUT_FILE"
    echo "$output" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Try to declare both contracts
echo ""
echo "Starting declarations..."
echo ""

declare_contract "RiskEngine" "$RISK_ENGINE_PATH"
declare_contract "StrategyRouterV2" "$STRATEGY_ROUTER_PATH"

echo ""
echo "Deployment results saved to: $OUTPUT_FILE"
cat "$OUTPUT_FILE"
