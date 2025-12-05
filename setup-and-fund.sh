#!/bin/bash

echo "════════════════════════════════════════════════════════"
echo "🚀 Katana Setup & Wallet Funding Script"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Your Wallet: 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027"
echo ""

# Check if Katana is running
echo "🔍 Checking Katana status..."
if curl -s -X POST http://localhost:5050 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_chainId","params":[],"id":1}' 2>/dev/null | grep -q "KATANA"; then
  echo "✅ Katana is running!"
else
  echo "❌ Katana is NOT running"
  echo ""
  echo "Please start Katana in a separate terminal:"
  echo ""
  echo "  cd /opt/obsqra.starknet"
  echo "  katana --dev --http.cors_origins \"*\""
  echo ""
  echo "Then run this script again."
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "💰 Funding Your Wallet"
echo "════════════════════════════════════════════════════════"
echo ""

# Run the Python funding script
echo "Running funding script..."
python3 /opt/obsqra.starknet/scripts/fund_user_wallet.py

if [ $? -eq 0 ]; then
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo "✅ SUCCESS!"
  echo "════════════════════════════════════════════════════════"
  echo ""
  echo "Next steps:"
  echo "1. Refresh your wallet (make sure you're on Local Katana network)"
  echo "2. You should see 10 ETH"
  echo "3. Go to http://localhost:3002 and connect"
  echo ""
else
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo "❌ Funding failed - trying alternative method"
  echo "════════════════════════════════════════════════════════"
  echo ""
  echo "Manual funding instructions:"
  echo ""
  echo "Install sncast (Starknet Foundry):"
  echo "  curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh"
  echo "  export PATH=\"\$HOME/.foundry/bin:\$PATH\""
  echo ""
  echo "Create Katana account:"
  echo "  sncast account add katana-dev \\"
  echo "    --address 0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71 \\"
  echo "    --private-key 0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b \\"
  echo "    --type oz \\"
  echo "    --add-profile \\"
  echo "    --rpc-url http://localhost:5050"
  echo ""
  echo "Transfer ETH:"
  echo "  sncast --account katana-dev --url http://localhost:5050 invoke \\"
  echo "    --contract-address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 \\"
  echo "    --function transfer \\"
  echo "    --calldata 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 0x8ac7230489e80000 0x0"
  echo ""
fi
