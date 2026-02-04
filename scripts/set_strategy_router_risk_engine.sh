#!/bin/bash
# Set StrategyRouter's risk_engine address using sncast (proven workaround from dev log)
# This uses --network sepolia which lets sncast figure out the RPC automatically

set -e

# Load environment
if [ -f backend/.env ]; then
    export $(cat backend/.env | grep -v '^#' | xargs)
fi

# Contract addresses
ROUTER_ADDR="${STRATEGY_ROUTER_ADDRESS:-0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73}"
RISK_ENGINE_ADDR="${RISK_ENGINE_ADDRESS:-0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab}"
NETWORK="${STARKNET_NETWORK:-sepolia}"

echo "🔧 Setting StrategyRouter risk_engine address..."
echo "  StrategyRouter: $ROUTER_ADDR"
echo "  RiskEngine:     $RISK_ENGINE_ADDR"
echo "  Network:        $NETWORK"
echo ""

# Use sncast with --network (proven workaround from docs/DEV_LOG.md)
# This lets sncast figure out the RPC automatically, avoiding compatibility issues
echo "📤 Invoking set_risk_engine via sncast..."
sncast --account deployer invoke \
  --contract-address "$ROUTER_ADDR" \
  --function set_risk_engine \
  --arguments "$RISK_ENGINE_ADDR" \
  --network "$NETWORK"

echo ""
echo "✅ Transaction submitted!"
echo "✅ RiskEngine v4 is now authorized to call StrategyRouter.update_allocation()"
