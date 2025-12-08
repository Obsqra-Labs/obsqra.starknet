#!/bin/bash
set -e

DEPLOYER_ADDR="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
DEPLOYER_KEY="0xf4506f978f613c4f3d8934b4bf5c3459fba3a16fbc479d5f7dee8e3832404aab"
RECIPIENT="0x0348914Bed4FDC65399d347C4498D778B75d5835D9276027a4357FE78B4a7eb3"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"

echo "════════════════════════════════════════════════════════"
echo " Sending 5 STRK to Your Wallet"
echo "════════════════════════════════════════════════════════"
echo "From: $DEPLOYER_ADDR"
echo "To:   $RECIPIENT"
echo ""

# Use sncast to invoke transfer
echo "📤 Invoking transfer..."
sncast invoke \
  --private-key "$DEPLOYER_KEY" \
  --account-address "$DEPLOYER_ADDR" \
  --network sepolia \
  "$STRK_TOKEN" \
  transfer \
  "$RECIPIENT" \
  5000000000000000000 \
  0

echo ""
echo "✅ Transfer initiated!"
echo "🎉 Check your ArgentX wallet in a moment - 5 STRK is on the way!"

