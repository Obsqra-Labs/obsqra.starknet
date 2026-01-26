#!/bin/bash
# Wrapper script to handle starkli declaration with proper stdin handling

set -e

CONTRACTS_DIR="/opt/obsqra.starknet/contracts"
RPC_URL="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
ACCOUNT_PATH="/root/.starkli-wallets/deployer/account.json"
KEYSTORE_PATH="/root/.starkli/keystore.json"
PASSWORD="L!nux123"
CONTRACT_CLASS="target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json"
CASM_CLASS="target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json"

cd "$CONTRACTS_DIR"

echo "[*] Attempting StrategyRouterV2 declaration to Alchemy Sepolia"
echo "[*] RPC: $RPC_URL"
echo "[*] Account: $ACCOUNT_PATH"
echo "[*] Contract class: $CONTRACT_CLASS"
echo ""

# Try direct starkli with explicit password
echo "[*] Attempting starkli v$(starkli --version | cut -d' ' -f1)..."

# Create a temporary script to provide password
mkfifo /tmp/starkli_password_pipe || true

(echo "$PASSWORD" > /tmp/starkli_password_pipe &)

# Run starkli with password from pipe
timeout 60 starkli declare "$CONTRACT_CLASS" \
  --casm-file "$CASM_CLASS" \
  --rpc "$RPC_URL" \
  --account "$ACCOUNT_PATH" \
  --keystore "$KEYSTORE_PATH" \
  < /tmp/starkli_password_pipe \
  2>&1 | tee /tmp/starkli_output.log

STARKLI_EXIT=$?

# Clean up
rm -f /tmp/starkli_password_pipe

if [ $STARKLI_EXIT -eq 0 ]; then
  echo ""
  echo "[✓] Declaration successful!"
  exit 0
else
  echo ""
  echo "[!] Declaration failed with exit code $STARKLI_EXIT"
  echo "[!] Check /tmp/starkli_output.log for details"
  exit 1
fi
