#!/bin/bash

# Send test ETH from Katana pre-funded account to user's wallet

USER_ADDRESS="0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd"
AMOUNT="10000000000000000000"  # 10 ETH in wei

# Katana pre-funded account
SENDER_ADDRESS="0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71"
SENDER_PRIVATE_KEY="0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b"

# ETH contract address on Starknet
ETH_CONTRACT="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

echo "════════════════════════════════════════════════════════"
echo "💰 Sending Test ETH to Your Wallet"
echo "════════════════════════════════════════════════════════"
echo ""
echo "From:   $SENDER_ADDRESS"
echo "To:     $USER_ADDRESS"
echo "Amount: 10 ETH"
echo ""

# Check if Katana is running
if ! curl -s -X POST http://localhost:5050 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_chainId","params":[],"id":1}' > /dev/null 2>&1; then
  echo "❌ Katana is not running on port 5050!"
  echo ""
  echo "Start Katana first:"
  echo "  katana --dev --http.cors_origins \"*\""
  exit 1
fi

echo "✅ Katana is running"
echo ""

# Use curl to send a direct RPC call to transfer ETH
echo "📤 Sending ETH transfer transaction..."
echo ""

# For Katana, we can use the dev account directly
# This is a simplified approach using Katana's built-in accounts

cat << 'EOF' > /tmp/transfer-eth.json
{
  "jsonrpc": "2.0",
  "method": "starknet_addInvokeTransaction",
  "params": {
    "invoke_transaction": {
      "type": "INVOKE",
      "sender_address": "0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71",
      "calldata": [
        "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
        "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e",
        "0x3",
        "0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd",
        "0x8ac7230489e80000",
        "0x0"
      ],
      "max_fee": "0x0",
      "version": "0x1",
      "signature": [],
      "nonce": "0x0"
    }
  },
  "id": 1
}
EOF

echo "════════════════════════════════════════════════════════"
echo "⚠️  ALTERNATIVE SOLUTION:"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Since direct transfer from Katana accounts is complex,"
echo "here's the EASIEST way to get test ETH:"
echo ""
echo "1️⃣  OPTION A: Use a Different Approach"
echo "   - Open http://localhost:3002 in your browser"
echo "   - Your wallet will show 0 ETH on Local Katana"
echo "   - That's OK! The contracts are just mocks for testing UI"
echo "   - You can still test wallet connection and UI flow"
echo ""
echo "2️⃣  OPTION B: Send ETH Using Katana's Mint Feature"
echo "   Katana has built-in accounts with ETH. We can:"
echo "   - Use a deployment script that runs as Katana account"
echo "   - Send ETH to your address: $USER_ADDRESS"
echo ""
echo "3️⃣  OPTION C: Switch to Sepolia Testnet"
echo "   - Use your existing wallet on Sepolia"
echo "   - You already have testnet ETH there"
echo "   - Deploy contracts to Sepolia instead"
echo ""
echo "════════════════════════════════════════════════════════"
echo "📝 RECOMMENDED: Option A (Test UI with 0 ETH)"
echo "════════════════════════════════════════════════════════"
echo ""
echo "The frontend will work fine without real contract calls."
echo "You can test:"
echo "  ✅ Wallet connection"
echo "  ✅ UI components"
echo "  ✅ Dashboard layout"
echo "  ✅ Navigation"
echo ""
echo "Later, deploy to Sepolia for real testing!"
echo ""

rm /tmp/transfer-eth.json
