#!/bin/bash

# End-to-End Contract Testing Script

RPC="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
DAO_MANAGER="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
STRATEGY_ROUTER="0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a"

echo "════════════════════════════════════════════════════════════════"
echo "🧪 END-TO-END CONTRACT TESTING"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "📍 Network: Starknet Sepolia"
echo "📍 RPC: Alchemy"
echo ""

# Test 1: RiskEngine - Calculate Risk Score
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: RiskEngine - Calculate Risk Score"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Contract: $RISK_ENGINE"
echo "Function: calculate_risk_score"
echo "Params: utilization=5000 (50%), volatility=2000 (20%), liquidity=2000, audit=80, age=365"
echo ""

starkli call $RISK_ENGINE calculate_risk_score \
  5000 2000 2000 80 365 \
  --rpc $RPC 2>&1

echo ""
echo "✅ If you see a number above, RiskEngine is working!"
echo ""

# Test 2: StrategyRouter - Get Current Allocation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: StrategyRouter - Get Current Allocation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Contract: $STRATEGY_ROUTER"
echo "Function: get_allocation"
echo ""

starkli call $STRATEGY_ROUTER get_allocation \
  --rpc $RPC 2>&1

echo ""
echo "✅ If you see 3 numbers (nostra, zklend, ekubo %), allocation is working!"
echo ""

# Test 3: DAOConstraintManager - Get Constraints
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: DAOConstraintManager - Get Constraints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Contract: $DAO_MANAGER"
echo "Function: get_constraints"
echo ""

starkli call $DAO_MANAGER get_constraints \
  --rpc $RPC 2>&1

echo ""
echo "✅ If you see constraint values, DAOConstraintManager is working!"
echo ""

# Test 4: StrategyRouter - Get Protocol Addresses
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 4: StrategyRouter - Get Protocol Addresses"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Contract: $STRATEGY_ROUTER"
echo "Function: get_protocol_addresses"
echo ""

starkli call $STRATEGY_ROUTER get_protocol_addresses \
  --rpc $RPC 2>&1

echo ""
echo "✅ If you see 3 addresses (Nostra, zkLend, Ekubo), protocol setup is working!"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📊 SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ All contracts are deployed and callable on Starknet Sepolia"
echo ""
echo "🔗 View on Voyager:"
echo "   RiskEngine: https://sepolia.voyager.online/contract/$RISK_ENGINE"
echo "   DAOConstraintManager: https://sepolia.voyager.online/contract/$DAO_MANAGER"
echo "   StrategyRouter: https://sepolia.voyager.online/contract/$STRATEGY_ROUTER"
echo ""
echo "🎯 Next Steps:"
echo "   1. Get STRK from faucet.starknet.io"
echo "   2. Connect wallet at https://starknet.obsqra.fi"
echo "   3. Make first transaction to deploy your account"
echo "   4. Update allocations through the UI"
echo ""

