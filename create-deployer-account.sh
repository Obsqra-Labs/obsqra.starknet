#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════"
echo "🔧 Creating Local Deployer Account for Starknet"
echo "════════════════════════════════════════════════════════"
echo ""

DEPLOYER_DIR="$HOME/.starkli-wallets/deployer"
RPC="https://starknet-sepolia.public.blastapi.io/rpc/v0_7"

# Clean up old files
rm -rf "$DEPLOYER_DIR"
mkdir -p "$DEPLOYER_DIR"

echo "1️⃣  Generating new account with starkli..."
echo ""

# Use OpenZeppelin account
cd "$DEPLOYER_DIR"

# Create a new signer
echo "Creating new signer (private key)..."
starkli signer keystore new "$DEPLOYER_DIR/keystore.json"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create keystore"
    exit 1
fi

echo ""
echo "✅ Keystore created at: $DEPLOYER_DIR/keystore.json"
echo ""

# Initialize OpenZeppelin account
echo "2️⃣  Initializing OpenZeppelin account..."
echo ""

starkli account oz init \
    --keystore "$DEPLOYER_DIR/keystore.json" \
    --rpc "$RPC" \
    "$DEPLOYER_DIR/account.json"

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize account"
    exit 1
fi

echo ""
echo "✅ Account initialized!"
echo ""

# Get the account address
ACCOUNT_ADDRESS=$(cat "$DEPLOYER_DIR/account.json" | grep -oP '"deployment":\s*{\s*"address":\s*"\K0x[0-9a-fA-F]+' || cat "$DEPLOYER_DIR/account.json" | grep -oP 'address.*0x[0-9a-fA-F]+' | head -1 | grep -oP '0x[0-9a-fA-F]+')

echo "════════════════════════════════════════════════════════"
echo "✅ Account Created!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Account Address: $ACCOUNT_ADDRESS"
echo ""
echo "════════════════════════════════════════════════════════"
echo "💰 IMPORTANT: Fund This Account!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Before deploying, you need to fund this account with STRK tokens."
echo ""
echo "Option 1: Use a faucet"
echo "  https://starknet-faucet.vercel.app/"
echo "  Paste address: $ACCOUNT_ADDRESS"
echo ""
echo "Option 2: Send STRK from your Argent X wallet"
echo "  (if it starts working again)"
echo ""
echo "════════════════════════════════════════════════════════"
echo "🚀 After Funding"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Once you have STRK in the account, deploy it:"
echo ""
echo "starkli account deploy \\"
echo "  $DEPLOYER_DIR/account.json \\"
echo "  --keystore $DEPLOYER_DIR/keystore.json \\"
echo "  --rpc $RPC"
echo ""
