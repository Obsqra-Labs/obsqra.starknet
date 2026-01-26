#!/bin/bash
set -e

RPC="https://starknet-sepolia-rpc.publicnode.com"
RISK_ENGINE_CLASS="0x03ea934f4442de174715b458377bf5d1900c2a7c2a1d5e7486fcde9e522e2216"
ACCOUNT="/root/.starkli-wallets/deployer/account.json"
KEYSTORE="/root/.starkli-wallets/deployer/keystore.json"

# Using deployer as owner for now
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
# Placeholder addresses (can be updated later)
STRATEGY_ROUTER="0x0000000000000000000000000000000000000000000000000000000000000001"
DAO_MANAGER="0x0000000000000000000000000000000000000000000000000000000000000001"

echo "Deploying RiskEngine..."
echo "  Owner: $OWNER"
echo "  Strategy Router (placeholder): $STRATEGY_ROUTER"
echo "  DAO Manager (placeholder): $DAO_MANAGER"

STARKLI_KEYSTORE_PASSWORD='L!nux123' starkli deploy \
  "$RISK_ENGINE_CLASS" \
  "$OWNER" \
  "$STRATEGY_ROUTER" \
  "$DAO_MANAGER" \
  --account "$ACCOUNT" \
  --keystore "$KEYSTORE" \
  --rpc "$RPC"
