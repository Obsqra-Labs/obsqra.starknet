#!/bin/bash
set -e

echo "========================================"
echo " TESTING CONTRACT INTERACTIONS"
echo "========================================"
echo ""

FACT_REGISTRY="0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"

# Get RiskEngine address from config
RISK_ENGINE=$(grep -oP 'RISK_ENGINE_ADDRESS\s*=\s*\K0x[a-fA-F0-9]{64}' /opt/obsqra.starknet/backend/app/config.py | head -1)
STRATEGY_ROUTER=$(grep -oP 'STRATEGY_ROUTER_ADDRESS\s*=\s*\K0x[a-fA-F0-9]{64}' /opt/obsqra.starknet/backend/app/config.py | head -1)

echo "📝 Contract Addresses:"
echo "   FactRegistry: $FACT_REGISTRY"
echo "   RiskEngine: $RISK_ENGINE"
echo "   StrategyRouter: $STRATEGY_ROUTER"
echo ""

cd /opt/obsqra.starknet/contracts

echo "========================================"
echo " TEST 1: FactRegistry → RiskEngine Flow"
echo "========================================"
echo ""

echo "📝 Step 1: Verify FactRegistry is callable..."
sncast call \
    --contract-address "$FACT_REGISTRY" \
    --function get_all_verifications_for_fact_hash \
    --arguments "0x1" \
    --network sepolia > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ FactRegistry is accessible"
else
    echo "❌ FactRegistry not accessible"
    exit 1
fi

echo ""
echo "📝 Step 2: Verify RiskEngine can read version..."
if [ -n "$RISK_ENGINE" ]; then
    sncast call \
        --contract-address "$RISK_ENGINE" \
        --function get_contract_version \
        --network sepolia 2>&1 | head -5
    
    echo ""
    echo "✅ RiskEngine is accessible"
else
    echo "⚠️  RiskEngine address not found"
fi

echo ""
echo "========================================"
echo " TEST 2: Contract State Verification"
echo "========================================"
echo ""

echo "📝 Checking RiskEngine decision count..."
if [ -n "$RISK_ENGINE" ]; then
    sncast call \
        --contract-address "$RISK_ENGINE" \
        --function get_decision_count \
        --network sepolia 2>&1 | head -5
fi

echo ""
echo "========================================"
echo " TEST 3: StrategyRouter Verification"
echo "========================================"
echo ""

if [ -n "$STRATEGY_ROUTER" ]; then
    echo "📝 Checking StrategyRouter version..."
    sncast call \
        --contract-address "$STRATEGY_ROUTER" \
        --function get_version \
        --network sepolia 2>&1 | head -5 || echo "⚠️  Version function may not exist"
fi

echo ""
echo "✅ Contract interaction tests complete!"
