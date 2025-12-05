#!/bin/bash

# Simple script to fund your wallet with ETH on Katana

YOUR_ADDRESS="0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027"

echo "════════════════════════════════════════════════════════"
echo "💰 Funding Your Wallet with Test ETH on Katana"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Your Address: $YOUR_ADDRESS"
echo "Amount: 10 ETH"
echo ""

# Check if Katana is running
echo "🔍 Checking if Katana is running..."
if curl -s -X POST http://localhost:5050 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_chainId","params":[],"id":1}' | grep -q "KATANA"; then
  echo "✅ Katana is running!"
else
  echo "❌ Katana is not running on port 5050"
  echo ""
  echo "Please start Katana in another terminal:"
  echo "  cd /opt/obsqra.starknet"
  echo "  katana --dev --http.cors_origins \"*\""
  echo ""
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "📝 Manual Steps to Get ETH:"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Since Katana pre-funded accounts can't directly send to"
echo "your wallet, here are your options:"
echo ""
echo "OPTION A: Deploy a Simple Transfer Contract"
echo "-------------------------------------------"
echo "1. We'll deploy a simple contract using Katana's account"
echo "2. The contract will transfer ETH to your wallet"
echo ""
echo "OPTION B: Use Starknet Foundry (sncast)"
echo "----------------------------------------"
echo "Run these commands:"
echo ""
echo "  # Install sncast if needed"
echo "  curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh"
echo ""
echo "  # Create account file for Katana's pre-funded account"
echo "  sncast account add katana-account \\"
echo "    --address 0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71 \\"
echo "    --private-key 0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b \\"
echo "    --type oz \\"
echo "    --rpc-url http://localhost:5050"
echo ""
echo "  # Transfer ETH to your wallet"
echo "  sncast invoke \\"
echo "    --account katana-account \\"
echo "    --contract-address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 \\"
echo "    --function transfer \\"
echo "    --calldata 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 0x8ac7230489e80000 0x0 \\"
echo "    --rpc-url http://localhost:5050"
echo ""
echo "OPTION C: Use Python Script (Most Reliable)"
echo "--------------------------------------------"
echo "We have a Python script ready. Run:"
echo ""
echo "  cd /opt/obsqra.starknet"
echo "  python3 scripts/fund_user_wallet.py"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

read -p "Would you like me to try the Python script now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo ""
  echo "Running Python script..."
  python3 /opt/obsqra.starknet/scripts/fund_user_wallet.py
fi
