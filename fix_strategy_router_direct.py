#!/usr/bin/env python3
"""
Direct transaction signing to update StrategyRouter's risk_engine.

This bypasses starknet_py's account.execute_v3() to avoid cairo_version RPC issues.
"""

from pathlib import Path
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.hash.transaction import compute_transaction_hash, TransactionHashPrefix
from starknet_py.cairo.felt import encode_shortstring
from starknet_py.net.client_models import PriceUnit, ResourceBounds
import requests
import sys
import time

# Read backend/.env
backend_env = Path(__file__).parent / "backend" / ".env"
WALLET_ADDRESS = ""
PRIV_KEY = ""

if backend_env.exists():
    with open(backend_env) as f:
        for line in f:
            line = line.strip()
            if line.startswith("BACKEND_WALLET_PRIVATE_KEY="):
                PRIV_KEY = line.split('=', 1)[1]
            if line.startswith("BACKEND_WALLET_ADDRESS="):
                WALLET_ADDRESS = line.split('=', 1)[1]

if not WALLET_ADDRESS or not PRIV_KEY:
    print("❌ Backend wallet not configured")
    sys.exit(1)

# Addresses
STRATEGY_ROUTER = 0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73
NEW_RISK_ENGINE = 0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab
CHAIN_ID = encode_shortstring("SN_SEPOLIA")
RPC_URL = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"

print(f"🔧 Updating StrategyRouter's risk_engine...")
print(f"   Wallet: {WALLET_ADDRESS}")
print(f"   StrategyRouter: {hex(STRATEGY_ROUTER)}")
print(f"   New RiskEngine: {hex(NEW_RISK_ENGINE)}")

# Get nonce
nonce_payload = {
    "jsonrpc": "2.0",
    "method": "starknet_getNonce",
    "params": {"block_id": "latest", "contract_address": WALLET_ADDRESS},
    "id": 1
}

response = requests.post(RPC_URL, json=nonce_payload)
nonce = int(response.json()["result"], 16)
print(f"   Nonce: {nonce}")

# Build call
selector = get_selector_from_name("set_risk_engine")
calldata = [NEW_RISK_ENGINE]

# Account __execute__ call
# For account contracts, we call __execute__ with Call struct array
execute_selector = get_selector_from_name("__execute__")
execute_calldata = [
    1,  # call_array_len
    STRATEGY_ROUTER,  # to
    selector,  # selector
    0,  # data_offset
    len(calldata),  # data_len
    len(calldata),  # calldata_len
] + calldata

print(f"\n📝 Building Invoke V3 transaction...")
print(f"   Calldata: {execute_calldata}")

# Resource bounds
resource_bounds_mapping = {
    0: ResourceBounds(max_amount=10000, max_price_per_unit=200000000000000),  # L1_GAS
    1: ResourceBounds(max_amount=1000000, max_price_per_unit=1000000000),  # L2_GAS  
    2: ResourceBounds(max_amount=5000, max_price_per_unit=150000000000000),  # L1_DATA_GAS
}

# Build resource bounds for tx hash (flattened)
l1_gas = resource_bounds_mapping[0]
l2_gas = resource_bounds_mapping[1]
l1_data_gas = resource_bounds_mapping[2]

# Compute tx hash for v3
key_pair = KeyPair.from_private_key(int(PRIV_KEY, 16))

tx_hash_fields = [
    TransactionHashPrefix.INVOKE.value,
    3,  # version
    int(WALLET_ADDRESS, 16),
    0,  # tip
    l1_gas.max_amount,
    l1_gas.max_price_per_unit,
    l2_gas.max_amount,
    l2_gas.max_price_per_unit,
    l1_data_gas.max_amount,
    l1_data_gas.max_price_per_unit,
    len(execute_calldata),
] + execute_calldata + [
    nonce,
    CHAIN_ID,
    0,  # nonce_data_availability_mode
    0,  # fee_data_availability_mode
    0,  # paymaster_data_len
    0,  # account_deployment_data_len
]

# This is complex - let me use a simpler approach
print("\n⚠️  Manual transaction building is complex.")
print("   Using starkli directly instead...\n")

# Write a starkli command file
starkli_cmd = f"""#!/bin/bash
cd /opt/obsqra.starknet

# Export from backend/.env
export STARKNET_ACCOUNT={WALLET_ADDRESS}
export STARKNET_KEYSTORE_PASSWORD=""

# Create temp keystore
mkdir -p /tmp/obsqra_keystore
echo '{PRIV_KEY}' > /tmp/obsqra_keystore/key.txt

starkli invoke \\
  --rpc {RPC_URL} \\
  --private-key-file /tmp/obsqra_keystore/key.txt \\
  --account {WALLET_ADDRESS} \\
  {hex(STRATEGY_ROUTER)} \\
  set_risk_engine \\
  {hex(NEW_RISK_ENGINE)}

rm -rf /tmp/obsqra_keystore
"""

with open("/tmp/update_strategy_router.sh", "w") as f:
    f.write(starkli_cmd)

print("✅ Script written to /tmp/update_strategy_router.sh")
print("   Run: bash /tmp/update_strategy_router.sh")
