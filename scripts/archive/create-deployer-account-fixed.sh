#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════"
echo "🔧 Creating Local Deployer Account for Starknet"
echo "════════════════════════════════════════════════════════"
echo ""

DEPLOYER_DIR="$HOME/.starkli-wallets/deployer"
RPC="https://starknet-sepolia.public.blastapi.io/rpc/v0_7"

echo "Using existing keystore at: $DEPLOYER_DIR/keystore.json"
echo ""
echo "Public key: 0x02a199a2e8e799487152bf584dc03ddb2360c04d885f9478ae8204250ba13bb5"
echo ""

# Initialize OpenZeppelin account (without --rpc flag)
echo "2️⃣  Initializing OpenZeppelin account..."
echo ""

starkli account oz init \
    --keystore "$DEPLOYER_DIR/keystore.json" \
    "$DEPLOYER_DIR/account.json"

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize account"
    exit 1
fi

echo ""
echo "✅ Account initialized!"
echo ""

# Get the account address
ACCOUNT_ADDRESS=$(cat "$DEPLOYER_DIR/account.json" | jq -r '.deployment.address' 2>/dev/null || grep -oP '"address":\s*"\K0x[0-9a-fA-F]+' "$DEPLOYER_DIR/account.json" | head -1)

if [ -z "$ACCOUNT_ADDRESS" ]; then
    echo "⚠️  Couldn't automatically extract address. Check the file:"
    echo ""
    cat "$DEPLOYER_DIR/account.json"
    echo ""
else
    echo "════════════════════════════════════════════════════════"
    echo "✅ Account Created!"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "Account Address: $ACCOUNT_ADDRESS"
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "💰 STEP 1: Fund This Account!"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "Visit the faucet and request STRK for this address:"
    echo "  https://starknet-faucet.vercel.app/"
    echo ""
    echo "Address to fund: $ACCOUNT_ADDRESS"
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo " STEP 2: Deploy Account (after funding)"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "After you receive STRK, run this command:"
    echo ""
    echo "starkli account deploy \\"
    echo "  $DEPLOYER_DIR/account.json \\"
    echo "  --keystore $DEPLOYER_DIR/keystore.json \\"
    echo "  --rpc $RPC"
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "🎯 STEP 3: Deploy Contracts"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "After deploying the account, you can deploy contracts!"
    echo ""
fi
