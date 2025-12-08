#!/bin/bash
# Quick smoke test script

RPC_URL="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
ROUTER="0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1"

echo "=== StrategyRouterV2 Smoke Test ==="
echo ""

echo "1. Checking Total Value Locked..."
starkli call $ROUTER get_total_value_locked --rpc $RPC_URL
echo ""

echo "2. Checking Allocation..."
starkli call $ROUTER get_allocation --rpc $RPC_URL
echo ""

echo "3. Checking Protocol Addresses..."
starkli call $ROUTER get_protocol_addresses --rpc $RPC_URL
echo ""

echo "=== Test Complete ==="
