#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════"
echo "💰 Funding Your Wallet on Katana"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Wallet: 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027"
echo ""

# Check if Katana is running
echo "🔍 Checking Katana..."
if curl -s -X POST http://localhost:5050 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_chainId","params":[],"id":1}' 2>/dev/null | grep -q "KATANA"; then
  echo "✅ Katana is running!"
else
  echo ""
  echo "❌ Katana is NOT running!"
  echo ""
  echo "Please start Katana first:"
  echo ""
  echo "  Terminal 1:"
  echo "  cd /opt/obsqra.starknet"
  echo "  katana --dev --http.cors_origins \"*\""
  echo ""
  echo "Then run this script again."
  echo ""
  exit 1
fi

echo ""
echo "💸 Sending 10 ETH to your wallet..."
echo ""

# Check if starknet_py is installed
if ! python3 -c "import starknet_py" 2>/dev/null; then
  echo "⚠️  Installing starknet_py..."
  pip install starknet-py
  echo ""
fi

# Run the Python funding script
python3 /opt/obsqra.starknet/scripts/fund_user_wallet.py

if [ $? -eq 0 ]; then
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo "🎉 DONE!"
  echo "════════════════════════════════════════════════════════"
  echo ""
  echo "Check your wallet:"
  echo "  1. Open Argent X"
  echo "  2. Make sure you're on 'Local Katana' network"
  echo "  3. You should see 10 ETH!"
  echo ""
  echo "Next: Deploy contracts and test!"
  echo ""
else
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo "❌ Funding failed"
  echo "════════════════════════════════════════════════════════"
  echo ""
  echo "See FUND_MY_WALLET.md for alternative methods!"
  echo ""
  exit 1
fi
