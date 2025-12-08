#!/bin/bash
set -e

# Configuration
RECIPIENT="0x0348914Bed4FDC65399d347C4498D778B75d5835D9276027a4357FE78B4a7eb3"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"
AMOUNT="5000000000000000000"  # 5 STRK in wei

echo "════════════════════════════════════════════════════════"
echo " Sending 5 STRK via sncast"
echo "════════════════════════════════════════════════════════"
echo ""

# Change to contracts directory so snfoundry.toml is found
cd /opt/obsqra.starknet/contracts

echo "📤 Invoking STRK transfer..."
echo "   To: $RECIPIENT"
echo "   Amount: 5 STRK"
echo ""

# Use sncast invoke with the configured account
sncast invoke \
  --contract-address "$STRK_TOKEN" \
  --function "transfer" \
  --calldata "$RECIPIENT" "$AMOUNT" "0" \
  --network sepolia \
  2>&1

echo ""
echo "✅ Transaction should be submitted!"
echo "🎉 5 STRK is on the way to your wallet!"

