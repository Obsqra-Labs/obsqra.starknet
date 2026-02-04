#!/bin/bash
# Deploy Agent Orchestrator to Starknet Sepolia
#
# Prerequisites:
# - Run `cd contracts && scarb build` first
# - Have starkli configured with your deployer account
#
# Usage: ./scripts/deploy_agent_orchestrator.sh

set -e

echo "=============================================="
echo " DEPLOYING AGENT ORCHESTRATOR"
echo "=============================================="
echo ""

# Configuration
CONTRACT_NAME="obsqra_contracts_AgentOrchestrator"
CONTRACT_FILE="/opt/obsqra.starknet/contracts/target/dev/${CONTRACT_NAME}.contract_class.json"
RPC_URL="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
ACCOUNT_FILE="/root/.starkli-wallets/deployer/account.json"
KEYSTORE_FILE="/root/.starkli-wallets/deployer/keystore.json"

# Owner address (deployer)
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

# Check if contract exists
if [ ! -f "$CONTRACT_FILE" ]; then
    echo "❌ Contract not found. Building..."
    cd /opt/obsqra.starknet/contracts
    scarb build
fi

echo "✅ Contract file: $CONTRACT_FILE"
echo ""

# Step 1: Declare
echo "📝 Step 1: Declaring contract..."
CLASS_HASH=$(starkli declare "$CONTRACT_FILE" \
    --account "$ACCOUNT_FILE" \
    --keystore "$KEYSTORE_FILE" \
    --rpc "$RPC_URL" \
    --compiler-version 2.9.1 \
    2>&1 | grep -oE "0x[0-9a-f]{64}" | head -1)

if [ -z "$CLASS_HASH" ]; then
    echo "❌ Declaration failed. Trying to get existing class hash..."
    CLASS_HASH=$(starkli class-hash "$CONTRACT_FILE")
fi

echo "✅ Class Hash: $CLASS_HASH"
echo ""

# Step 2: Deploy
echo "📝 Step 2: Deploying contract with owner: $OWNER"
echo ""

CONTRACT_ADDRESS=$(starkli deploy "$CLASS_HASH" \
    "$OWNER" \
    --account "$ACCOUNT_FILE" \
    --keystore "$KEYSTORE_FILE" \
    --rpc "$RPC_URL" \
    2>&1 | grep -oE "0x[0-9a-f]{64}" | tail -1)

echo ""
echo "=============================================="
echo " DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "Class Hash:      $CLASS_HASH"
echo "Contract Address: $CONTRACT_ADDRESS"
echo ""
echo "Add to .env.local:"
echo "NEXT_PUBLIC_AGENT_ORCHESTRATOR_ADDRESS=$CONTRACT_ADDRESS"
echo ""

# Save to file
echo "AGENT_ORCHESTRATOR_CLASS_HASH=$CLASS_HASH" > /opt/obsqra.starknet/.agent_orchestrator.deployed
echo "AGENT_ORCHESTRATOR_ADDRESS=$CONTRACT_ADDRESS" >> /opt/obsqra.starknet/.agent_orchestrator.deployed
echo "DEPLOYED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> /opt/obsqra.starknet/.agent_orchestrator.deployed

echo "✅ Deployment info saved to .agent_orchestrator.deployed"
