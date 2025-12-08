#!/bin/bash

# Use curl to call the RPC directly
DEPLOYER_ADDR="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
RECIPIENT="0x0348914bed4fdc65399d347c4498d778b75d5835d9276027a4357fe78b4a7eb3"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"
RPC="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"

echo " Checking STRK balance via RPC..."

# Check balance of deployer
curl -s -X POST "$RPC" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "starknet_call",
    "params": {
      "request": {
        "contract_address": "'$STRK_TOKEN'",
        "entry_point_selector": "0x02e4663aa5f4b547eadf1fa95d72ff052c4172d45aab9e2a604a558d4d27d91d",
        "calldata": ["'$DEPLOYER_ADDR'"]
      },
      "block_id": "latest"
    }
  }' | head -20

echo ""
echo "✅ Note: To send STRK, you need to use a proper transaction call"
echo "   The deployer wallet is ready but needs account deployment first"
echo ""
echo "💡 Easiest solution: Use the Starknet faucet"
echo "   https://faucet.starknet.io"
echo "   Paste your ArgentX address to get free testnet STRK"

