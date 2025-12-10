#!/bin/bash
# Test script to deploy STRK to Ekubo individually
# This tests the Ekubo integration before combining with Strategy Router

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Ekubo Deposit (Individual Test)"
echo "════════════════════════════════════════════════════════════════"

# Configuration
RPC_URL="https://starknet-sepolia-rpc.publicnode.com"
ACCOUNT="deployer"  # Your account profile

# Protocol addresses (from protocol_addresses_sepolia.json)
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"

# Tokens
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
ETH_TOKEN="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

# Your contract address (where you have STRK)
CONTRACT_ADDRESS="0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a"

echo ""
echo "📋 Test Configuration:"
echo "  Contract (has STRK): $CONTRACT_ADDRESS"
echo "  Ekubo Core: $EKUBO_CORE"
echo "  STRK Token: $STRK_TOKEN"
echo "  ETH Token: $ETH_TOKEN"
echo ""

echo "🔍 Step 1: Check contract STRK balance..."
STRK_BALANCE=$(starkli call $STRK_TOKEN balanceOf $CONTRACT_ADDRESS --rpc $RPC_URL 2>&1)
echo "  STRK Balance: $STRK_BALANCE"
echo ""

echo "💡 To test Ekubo deposit manually, you would need to:"
echo "  1. Approve Ekubo Core to spend STRK"
echo "  2. Approve Ekubo Core to spend ETH (if swapping first)"
echo "  3. Call deposit_liquidity() on Ekubo Core with parameters"
echo ""
echo "This script is a template - you'll need to implement the actual calls"
echo "based on Ekubo's interface."

