#!/bin/bash

# Configuration - use correct STRK token address with proper prefix
DEPLOYER_ACCOUNT="deployer"
RECIPIENT="0x0348914Bed4FDC65399d347C4498D778B75d5835D9276027a4357FE78B4a7eb3"
STRK_TOKEN="0x0704718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"  # Corrected!
AMOUNT="5000000000000000000"  # 5 STRK in wei

echo "════════════════════════════════════════════════════════"
echo " Sending 5 STRK to Your ArgentX Wallet"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📤 Invoking transfer..."
echo "   From: Deployer wallet"
echo "   To:   $RECIPIENT"
echo "   Amount: 5 STRK"
echo ""

# Change to contracts directory so snfoundry.toml is found
cd /opt/obsqra.starknet/contracts

# Use sncast invoke 
sncast --account "$DEPLOYER_ACCOUNT" invoke \
  --contract-address "$STRK_TOKEN" \
  --function "transfer" \
  --calldata "$RECIPIENT" "$AMOUNT" "0" \
  --network sepolia

RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
  echo "✅ Transaction submitted successfully!"
  echo "🎉 5 STRK is on the way to your wallet!"
  echo ""
  echo "💡 Your account will auto-deploy on first transaction"
  echo "   Check your ArgentX wallet in a moment"
else
  echo "⚠️ Transaction may have failed - check output above"
fi

exit $RESULT

