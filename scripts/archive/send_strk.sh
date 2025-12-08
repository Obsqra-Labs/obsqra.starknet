#!/bin/bash

# Configuration
DEPLOYER_ADDR="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
DEPLOYER_KEY="0xf4506f978f613c4f3d8934b4bf5c3459fba3a16fbc479d5f7dee8e3832404aab"
RECIPIENT="0x0348914Bed4FDC65399d347C4498D778B75d5835D9276027a4357FE78B4a7eb3"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"
RPC="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
AMOUNT="5000000000000000000"  # 5 STRK in wei

echo "════════════════════════════════════════════════════════"
echo " Sending STRK from Deployer Wallet"
echo "════════════════════════════════════════════════════════"
echo ""
echo "From:      $DEPLOYER_ADDR"
echo "To:        $RECIPIENT"
echo "Amount:    5 STRK"
echo "RPC:       $RPC"
echo ""

# Create account config in temp location
TEMP_ACCOUNT="/tmp/deployer_account.json"
cat > "$TEMP_ACCOUNT" << EOF
{
  "deployment": {
    "address": "$DEPLOYER_ADDR",
    "class_hash": "0x4c6d6cf894f8bc96bb9c525e6853e5483177841f7388f74a46cfda6f028c755"
  }
}
EOF

# Create keystore
TEMP_KEYSTORE="/tmp/deployer_keystore.json"
cat > "$TEMP_KEYSTORE" << 'KEYEOF'
{
  "description": "Deployer Account",
  "variant": {
    "type": "plain_text",
    "private_key": "0xf4506f978f613c4f3d8934b4bf5c3459fba3a16fbc479d5f7dee8e3832404aab"
  }
}
KEYEOF

echo "📤 Sending transfer transaction..."
echo ""

# Use starkli to send the transfer
starkli invoke \
  --keystore "$TEMP_KEYSTORE" \
  --account "$TEMP_ACCOUNT" \
  --rpc "$RPC" \
  "$STRK_TOKEN" \
  transfer \
  "$RECIPIENT" \
  "$AMOUNT" \
  0

echo ""
echo "⏳ Transaction submitted. Check Voyager or wait a moment..."
echo "   Explorer: https://sepolia.voyager.online"
echo ""
echo "🎉 Your wallet should receive 5 STRK shortly!"

# Cleanup
rm -f "$TEMP_KEYSTORE"

