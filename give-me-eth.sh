#!/bin/bash

set -e

YOUR_WALLET="0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027"
AMOUNT="10"  # 10 ETH

echo "════════════════════════════════════════════════════════"
echo "💰 Getting You ETH on Katana Devnet"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Your Wallet: $YOUR_WALLET"
echo "Amount: ${AMOUNT} ETH"
echo ""

# Step 1: Check Katana is running
echo "🔍 Step 1: Checking if Katana is running..."
if ! curl -s -X POST http://localhost:5050 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_chainId","params":[],"id":1}' 2>/dev/null | grep -q "KATANA"; then
  
  echo "❌ Katana is not running!"
  echo ""
  echo "Please start Katana in another terminal:"
  echo ""
  echo "  cd /opt/obsqra.starknet"
  echo "  katana --dev --http.cors_origins \"*\""
  echo ""
  echo "Then run this script again."
  exit 1
fi
echo "✅ Katana is running!"
echo ""

# Step 2: Check if sncast is installed
echo "🔍 Step 2: Checking for sncast (Starknet Foundry)..."
if ! command -v sncast &> /dev/null; then
  echo "❌ sncast not found. Installing..."
  echo ""
  
  curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh
  
  # Add to current session
  export PATH="$HOME/.foundry/bin:$PATH"
  
  if ! command -v sncast &> /dev/null; then
    echo "❌ Installation failed. Please run manually:"
    echo ""
    echo "  curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh"
    echo "  export PATH=\"\$HOME/.foundry/bin:\$PATH\""
    exit 1
  fi
fi
echo "✅ sncast is installed!"
echo ""

# Step 3: Create Katana account in sncast
echo "🔧 Step 3: Setting up Katana pre-funded account..."

# Remove old account if exists
sncast account delete katana-dev --accounts-file ~/.starknet_accounts/starknet_open_zeppelin_accounts.json 2>/dev/null || true

# Create new account
sncast account add katana-dev \
  --address 0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71 \
  --private-key 0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b \
  --type oz \
  --accounts-file ~/.starknet_accounts/starknet_open_zeppelin_accounts.json \
  --add-profile katana-dev \
  || echo "Account might already exist, continuing..."

echo "✅ Katana account configured!"
echo ""

# Step 4: Transfer ETH
echo "💸 Step 4: Transferring ${AMOUNT} ETH to your wallet..."
echo ""

# ETH contract address on Starknet
ETH_CONTRACT="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

# Calculate amount in wei (10 ETH = 10 * 10^18)
AMOUNT_WEI="0x8ac7230489e80000"  # 10 ETH in hex

# Execute transfer
sncast \
  --account katana-dev \
  --accounts-file ~/.starknet_accounts/starknet_open_zeppelin_accounts.json \
  --url http://localhost:5050 \
  invoke \
  --contract-address $ETH_CONTRACT \
  --function transfer \
  --calldata $YOUR_WALLET $AMOUNT_WEI 0x0

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ SUCCESS! Transfer Complete!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Refresh your Argent X wallet"
echo "2. Make sure you're on 'Local Katana' network"
echo "3. You should see ${AMOUNT} ETH!"
echo "4. Go to http://localhost:3002 and start testing"
echo ""
echo "Your wallet: $YOUR_WALLET"
echo ""
