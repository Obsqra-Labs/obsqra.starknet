#!/bin/bash
# Check for locked funds in ETH-based Strategy Router contracts

echo "🔍 Checking for locked funds in ETH contracts..."
echo ""

# Your wallet address (from error logs)
WALLET_ADDRESS="0x199f1c59ffb4403e543b384f8bc77cf390a8671fbbc0f6f7eae0d462b39b777"

# ETH contracts that might have locked funds
ETH_CONTRACT_1="0x01c2e698bc0f263ea62dc3c557d32afe25c13cbc91900d726b84c58a0baa09f0"
ETH_CONTRACT_2="0x01888e3f3d6cd137e63ff1a090a1e2c9ed5754162a8d5739364aba657fab20e4"
ETH_CONTRACT_3="0x053b69775c22246080a17c37a38dbda31d1841c8f6d7b4d928d54a99eda2748c"

# ETH token address
ETH_TOKEN="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

RPC_URL="https://starknet-sepolia-rpc.publicnode.com"

echo "📋 Checking contract ETH balances..."
echo ""

# Check Contract 1
echo "Contract 1: $ETH_CONTRACT_1"
echo "  Starkscan: https://sepolia.starkscan.co/contract/$ETH_CONTRACT_1"
echo "  Checking ETH balance..."
starkli call $ETH_TOKEN balanceOf $ETH_CONTRACT_1 --rpc $RPC_URL 2>/dev/null || echo "  ⚠️ Could not check balance"
echo ""

# Check Contract 2
echo "Contract 2: $ETH_CONTRACT_2"
echo "  Starkscan: https://sepolia.starkscan.co/contract/$ETH_CONTRACT_2"
echo "  Checking ETH balance..."
starkli call $ETH_TOKEN balanceOf $ETH_CONTRACT_2 --rpc $RPC_URL 2>/dev/null || echo "  ⚠️ Could not check balance"
echo ""

# Check Contract 3
echo "Contract 3: $ETH_CONTRACT_3"
echo "  Starkscan: https://sepolia.starkscan.co/contract/$ETH_CONTRACT_3"
echo "  Checking ETH balance..."
starkli call $ETH_TOKEN balanceOf $ETH_CONTRACT_3 --rpc $RPC_URL 2>/dev/null || echo "  ⚠️ Could not check balance"
echo ""

echo "💡 To check your user balance in these contracts, use:"
echo "  starkli call <CONTRACT_ADDRESS> get_user_balance $WALLET_ADDRESS --rpc $RPC_URL"
echo ""
echo "💡 To check total deposits:"
echo "  starkli call <CONTRACT_ADDRESS> get_total_value_locked --rpc $RPC_URL"
echo ""

