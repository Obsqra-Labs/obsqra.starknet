#!/bin/bash
echo "Checking if account exists on Sepolia..."
echo ""

ACCOUNT="0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd"

# Try with different RPC endpoints
echo "1️⃣ Trying Blast API..."
starkli account fetch \
  $ACCOUNT \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --output ~/.starkli-wallets/deployer/account.json 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Success with Blast API!"
    exit 0
fi

echo ""
echo "2️⃣ Trying Infura..."
starkli account fetch \
  $ACCOUNT \
  --rpc https://starknet-sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161 \
  --output ~/.starkli-wallets/deployer/account.json 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Success with Infura!"
    exit 0
fi

echo ""
echo "3️⃣ Trying Alchemy..."
starkli account fetch \
  $ACCOUNT \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/demo \
  --output ~/.starkli-wallets/deployer/account.json 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Success with Alchemy!"
    exit 0
fi

echo ""
echo "❌ All RPCs failed. This likely means:"
echo "   1. Your account isn't deployed on Sepolia yet"
echo "   2. Or the account address is incorrect"
echo ""
echo "To deploy your account, you need to make a transaction from Argent X first."
echo "Try sending 0.001 STRK to yourself in Argent X to deploy the account."
