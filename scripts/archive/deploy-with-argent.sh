#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════"
echo " Deploying Contracts with Argent Account"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Account: 0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd"
echo ""

cd /opt/obsqra.starknet/contracts

ACCOUNT_FILE="$HOME/.starkli-wallets/deployer/account.json"
KEYSTORE="$HOME/.starkli-wallets/deployer/keystore.json"
RPC="https://starknet-sepolia.public.blastapi.io/rpc/v0_7"

# Deploy RiskEngine
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Deploying RiskEngine"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Declaring..."
starkli declare \
  target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc "$RPC" \
  --account "$ACCOUNT_FILE" \
  --keystore "$KEYSTORE"

echo ""
echo "✅ RiskEngine declared!"
echo ""
echo "Now copy the CLASS_HASH from above and run:"
echo ""
echo "starkli deploy \\"
echo "  <CLASS_HASH> \\"
echo "  0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd \\"
echo "  --rpc $RPC \\"
echo "  --account $ACCOUNT_FILE \\"
echo "  --keystore $KEYSTORE"
echo ""
