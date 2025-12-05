#!/bin/bash

set -e

echo "════════════════════════════════════════════════════════"
echo "💰 Funding Your Wallet on Katana"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Your Wallet: 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027"
echo "Amount: 10 ETH"
echo ""

# Check Katana
if ! curl -s http://localhost:5050 > /dev/null 2>&1; then
  echo "❌ Katana not running!"
  echo ""
  echo "Start Katana first:"
  echo "  katana --dev --http.cors_origins \"*\""
  exit 1
fi

echo "✅ Katana is running"
echo ""

# Check if starkli is installed
if ! command -v starkli &> /dev/null; then
  echo "Installing starkli..."
  curl https://get.starkli.sh | sh
  export PATH="$HOME/.starkli/bin:$PATH"
fi

echo "Creating Katana account file..."
mkdir -p ~/.starkli-wallets/katana

# Create account file
cat > ~/.starkli-wallets/katana/account.json << 'EOF'
{
  "version": 1,
  "variant": {
    "type": "open_zeppelin",
    "version": 1,
    "public_key": "0x4c0f884b8e5b4f00d97a3aad26b2e5de0c0c76a555060c837da2e287403c01d"
  },
  "deployment": {
    "status": "deployed",
    "class_hash": "0x061dac032f228abef9c6626f995015233097ae253a7f72d68552db02f2971b8f",
    "address": "0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71"
  }
}
EOF

# Create keystore
cat > ~/.starkli-wallets/katana/keystore.json << 'EOF'
{
  "crypto": {
    "cipher": "aes-128-ctr",
    "cipherparams": {
      "iv": "dba5d5f8e1f5f1e5f1e5f1e5f1e5f1e5"
    },
    "ciphertext": "33003003001800009900180300d206308b0070db00121318d17b5e6262150b",
    "kdf": "scrypt",
    "kdfparams": {
      "dklen": 32,
      "n": 8192,
      "p": 1,
      "r": 8,
      "salt": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    "mac": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "id": "katana-dev",
  "version": 3
}
EOF

echo "✅ Account files created"
echo ""
echo "Sending 10 ETH to your wallet..."
echo ""

# Use starkli to invoke transfer
starkli invoke \
  --rpc http://localhost:5050 \
  --account ~/.starkli-wallets/katana/account.json \
  --keystore ~/.starkli-wallets/katana/keystore.json \
  0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 \
  transfer \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  u256:10000000000000000000 || {
  
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo "Alternative: Use Python Script"
  echo "════════════════════════════════════════════════════════"
  echo ""
  python3 /opt/obsqra.starknet/scripts/fund_user_wallet.py
}

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Done!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Check your wallet balance at:"
echo "http://localhost:3002"
echo ""
