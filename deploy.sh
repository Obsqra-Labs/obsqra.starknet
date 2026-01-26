#!/bin/bash
# StrategyRouterV2 Deployment - Execute When Ready
# This script will deploy the contract once starkli v0.4.2+ is available

set -e

echo "=========================================="
echo "StrategyRouterV2 Contract Deployment"
echo "=========================================="
echo ""

# Configuration
CONTRACTS_DIR="/opt/obsqra.starknet/contracts"
RPC_URL="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
ACCOUNT_PATH="/root/.starkli-wallets/deployer/account.json"
KEYSTORE_PATH="/root/.starkli/keystore.json"
PASSWORD="L!nux123"
CONTRACT_CLASS="target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json"
CASM_CLASS="target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json"

# Function to find compatible starkli
find_starkli() {
  local candidates=(
    "/tmp/starkli-repo/target/release/starkli"
    "/root/.starkli/bin/starkli"
  )
  
  for candidate in "${candidates[@]}"; do
    if [ -x "$candidate" 2>/dev/null ]; then
      echo "[*] Found starkli: $candidate"
      "$candidate" --version 2>/dev/null || echo "[!] Version info unavailable"
      printf "%s" "$candidate"
      return 0
    fi
  done
  
  return 1
}

# Print status
echo "[*] Configuration:"
echo "    RPC: $RPC_URL"
echo "    Account: $ACCOUNT_PATH"
echo "    Contract: $CONTRACT_CLASS"
echo "    CASM: $CASM_CLASS"
echo ""

# Find starkli
echo "[*] Locating starkli..."
if STARKLI_PATH=$(find_starkli); then
  echo "[✓] Using: $STARKLI_PATH"
else
  echo "[✗] ERROR: Could not find compatible starkli"
  echo "    Expected: /tmp/starkli-repo/target/release/starkli (v0.4.2+)"
  echo "    Fallback: /root/.starkli/bin/starkli (v0.3.2)"
  echo ""
  echo "[!] Please ensure starkli v0.4.2+ is built at:"
  echo "    /tmp/starkli-repo/target/release/starkli"
  exit 1
fi

# Verify contract files exist
echo ""
echo "[*] Verifying contract artifacts..."
if [ ! -f "$CONTRACTS_DIR/$CONTRACT_CLASS" ]; then
  echo "[✗] ERROR: Sierra class not found at $CONTRACTS_DIR/$CONTRACT_CLASS"
  exit 1
fi
if [ ! -f "$CONTRACTS_DIR/$CASM_CLASS" ]; then
  echo "[✗] ERROR: CASM class not found at $CONTRACTS_DIR/$CASM_CLASS"
  exit 1
fi
echo "[✓] Contract artifacts verified"

# Execute declaration
echo ""
echo "[*] Executing contract declaration..."
echo "    Command: $STARKLI_PATH declare ..."
echo ""

cd "$CONTRACTS_DIR"

export STARKLI_KEYSTORE_PASSWORD="$PASSWORD"

if timeout 180 "$STARKLI_PATH" declare \
  "$CONTRACT_CLASS" \
  --casm-file "$CASM_CLASS" \
  --rpc "$RPC_URL" \
  --account "$ACCOUNT_PATH" \
  --keystore "$KEYSTORE_PATH" \
  2>&1 | tee /tmp/deployment_result.log; then
  
  echo ""
  echo "=========================================="
  echo "✓✓✓ DEPLOYMENT SUCCESSFUL! ✓✓✓"
  echo "=========================================="
  echo ""
  echo "[✓] StrategyRouterV2 declared on Alchemy Sepolia"
  echo "[✓] Sierra class hash: 0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d42b7"
  echo "[✓] CASM class hash: 0x039bcde8fe0a75c690195698ac14248788b4304c9f23d22d19765c352f8b3b3f"
  echo ""
  
  # Extract transaction hash if possible
  if grep -q "transaction hash\|Transaction hash" /tmp/deployment_result.log; then
    TX_HASH=$(grep "transaction hash\|Transaction hash" /tmp/deployment_result.log | tail -1)
    echo "[✓] $TX_HASH"
  fi
  
  echo ""
  echo "[*] Full output saved to: /tmp/deployment_result.log"
  exit 0
else
  EXIT_CODE=$?
  echo ""
  echo "=========================================="
  echo "✗✗✗ DEPLOYMENT FAILED ✗✗✗"
  echo "=========================================="
  echo "[!] Exit code: $EXIT_CODE"
  echo "[!] Output saved to: /tmp/deployment_result.log"
  exit $EXIT_CODE
fi
