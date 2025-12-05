#!/bin/bash

# Fund a wallet with test ETH from Katana pre-funded account

TARGET_ADDRESS="$1"
AMOUNT="${2:-1000000000000000000}" # Default 1 ETH in wei

# Katana pre-funded account (Account #0)
SENDER_ADDRESS="0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71"
SENDER_PRIVATE_KEY="0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b"

# ETH contract address on Starknet
ETH_CONTRACT="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

echo "======================================"
echo "Funding Wallet with Test ETH"
echo "======================================"
echo "Target: $TARGET_ADDRESS"
echo "Amount: $AMOUNT wei ($(echo "scale=2; $AMOUNT / 1000000000000000000" | bc) ETH)"
echo ""

if [ -z "$TARGET_ADDRESS" ]; then
    echo "Usage: $0 <target_address> [amount_in_wei]"
    echo ""
    echo "Available Katana Pre-funded Accounts:"
    echo "======================================="
    echo ""
    echo "Account #0:"
    echo "  Address:     0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71"
    echo "  Private Key: 0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b"
    echo ""
    echo "Account #1:"
    echo "  Address:     0x6677fe62ee39c7b07401f754138502bab7fac99d2d3c5d37df7d1c6fab10819"
    echo "  Private Key: 0x3e3979c1ed728490308054fe357a9f49cf67f80f9721f44cc57235129e090f4"
    echo ""
    echo "You can import these accounts into your wallet (Argent X / Braavos)"
    echo "to have instant access to test ETH on your local Katana devnet!"
    exit 1
fi

echo "Transfer method: Using starkli..."
echo ""

# Try using starkli to invoke the transfer
starkli invoke \
    --rpc http://localhost:5050 \
    --account $SENDER_ADDRESS \
    --private-key $SENDER_PRIVATE_KEY \
    $ETH_CONTRACT \
    transfer \
    $TARGET_ADDRESS \
    $AMOUNT \
    0x0 2>&1 || {
    
    echo ""
    echo "❌ Starkli method failed (expected on local devnet)"
    echo ""
    echo "✅ ALTERNATIVE: Import a pre-funded Katana account into your wallet!"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "📋 Katana Pre-Funded Test Accounts"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "🔑 Account #0 (Recommended):"
    echo "   Address:     0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71"
    echo "   Private Key: 0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b"
    echo "   Balance:     ~1000 ETH"
    echo ""
    echo "🔑 Account #1:"
    echo "   Address:     0x6677fe62ee39c7b07401f754138502bab7fac99d2d3c5d37df7d1c6fab10819"
    echo "   Private Key: 0x3e3979c1ed728490308054fe357a9f49cf67f80f9721f44cc57235129e090f4"
    echo "   Balance:     ~1000 ETH"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "📱 How to Import into Argent X:"
    echo "   1. Open Argent X extension"
    echo "   2. Click '+ New Account' → 'Import Account'"
    echo "   3. Select 'Private Key'"
    echo "   4. Paste the private key from Account #0 above"
    echo "   5. Set Network to 'Custom' with RPC: http://localhost:5050"
    echo ""
    echo "📱 How to Import into Braavos:"
    echo "   1. Open Braavos extension"
    echo "   2. Click '...' → 'Import Wallet'"
    echo "   3. Select 'Private Key'"
    echo "   4. Paste the private key from Account #0 above"
    echo "   5. Set Network to 'Custom' with RPC: http://localhost:5050"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
}
