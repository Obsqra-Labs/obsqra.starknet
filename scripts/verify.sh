#!/bin/bash

CONTRACT_ADDRESS=$1
CONTRACT_NAME=$2

if [ -z "$CONTRACT_ADDRESS" ] || [ -z "$CONTRACT_NAME" ]; then
    echo "Usage: ./verify.sh <CONTRACT_ADDRESS> <CONTRACT_NAME>"
    exit 1
fi

echo "Verifying contract $CONTRACT_NAME at $CONTRACT_ADDRESS..."

starknet verify \
  --contract $CONTRACT_ADDRESS \
  --name $CONTRACT_NAME \
  --network testnet

echo "Verification complete!"

