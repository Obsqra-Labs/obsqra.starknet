#!/bin/bash
#
# Starknet Contract Deployment Script
# Declares RiskEngine and StrategyRouterV2 to Sepolia testnet
#

set -e

# Configuration
ACCOUNT_FILE="/root/.starkli-wallets/deployer/account.json"
KEYSTORE_FILE="/root/.starkli-wallets/deployer/keystore.json"
KEYSTORE_PASSWORD="L!nux123"

# Try RPC endpoints in order of compatibility with starkli v0.3.2
# starkli v0.3.2 expects RPC v0_6 or v0_7 (not v0_10+)
RPC_URLS=(
  "https://starknet-sepolia-rpc.publicnode.com"                     # PublicNode (WORKING!)
  "https://rpc.starknet.lava.build"                                 # Lava Network
  "https://starknet-sepolia.blastapi.io"                            # Blast (no /rpc/v path)
  "https://starknet-sepolia.infura.io/v3"                           # Infura
  "https://starknet-sepolia.reddio.com"                             # Reddio
  "https://starknet-sepolia.public.blastapi.io/rpc/v0_6"           # Blast v0_6 endpoint
  "https://starknet-sepolia.public.blastapi.io/rpc/v0_7"           # Blast v0_7 endpoint
  "https://free-rpc.nethermind.io/sepolia-juno"                     # Nethermind
)

# Try to find a working RPC
RPC_URL=""
for url in "${RPC_URLS[@]}"; do
  echo "Testing RPC: $url"
  if timeout 3 curl -s -X POST "$url" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"starknet_blockNumber","params":[],"id":1}' 2>&1 | grep -q '"result"'; then
    RPC_URL="$url"
    echo "✓ Found working RPC: $RPC_URL"
    break
  fi
done

if [ -z "$RPC_URL" ]; then
  echo "❌ No working RPC endpoints found"
  exit 1
fi

RISK_ENGINE_PATH="/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json"
STRATEGY_ROUTER_PATH="/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json"

OUTPUT_FILE="/opt/obsqra.starknet/deployment_hashes.txt"

echo "======================================================================"
echo "STARKNET CONTRACT DEPLOYMENT"
echo "======================================================================"
echo ""
echo "Network: Sepolia ($(date))"
echo "RPC: $RPC_URL"
echo ""

> "$OUTPUT_FILE"

# Function to declare contract
declare_contract() {
    local name=$1
    local path=$2
    
    echo "📋 Declaring $name..."
    echo "   File: $(basename "$path")"
    echo "   Size: $(du -h "$path" | cut -f1)"
    echo ""
    
    local output
    output=$(starkli declare \
        "$path" \
        --account "$ACCOUNT_FILE" \
        --keystore "$KEYSTORE_FILE" \
        --keystore-password "$KEYSTORE_PASSWORD" \
        --rpc "$RPC_URL" 2>&1) || {
        echo "❌ Failed to declare $name"
        echo "$output" | tee -a "$OUTPUT_FILE"
        return 1
    }
    
    echo "✅ Success!"
    echo "$output"
    echo ""
    
    # Save to file
    {
        echo "================================================"
        echo "$name Declaration"
        echo "================================================"
        echo "$output"
        echo ""
    } >> "$OUTPUT_FILE"
    
    # Extract class hash
    local class_hash
    class_hash=$(echo "$output" | grep -oP 'Class hash: \K0x[a-f0-9]+' | head -1) || true
    
    if [ -n "$class_hash" ]; then
        echo "Class Hash: $class_hash" | tee -a "$OUTPUT_FILE"
        echo ""
    fi
}

# Main deployment flow
echo "=" >> "$OUTPUT_FILE"
echo "STARKNET DEPLOYMENT RESULTS" >> "$OUTPUT_FILE"
echo "Time: $(date)" >> "$OUTPUT_FILE"
echo "=" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Declare RiskEngine
declare_contract "RiskEngine" "$RISK_ENGINE_PATH" || {
    echo ""
    echo "❌ Deployment failed at RiskEngine step"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check RPC is accessible: curl -s $RPC_URL | head"
    echo "  2. Check account is correct: cat $ACCOUNT_FILE"
    echo "  3. Check keystore password: starkli account info 0x05fe... --rpc $RPC_URL"
    echo ""
    exit 1
}

# Declare StrategyRouter
declare_contract "StrategyRouterV2" "$STRATEGY_ROUTER_PATH" || {
    echo ""
    echo "❌ Deployment failed at StrategyRouterV2 step"
    exit 1
}

echo "======================================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "======================================================================"
echo ""
echo "Results saved to: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "  1. Extract class hashes from above output"
echo "  2. Deploy contract instances using class hashes"
echo "  3. Update backend with contract addresses"
echo ""

cat "$OUTPUT_FILE"
