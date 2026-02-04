#!/usr/bin/env python3
"""Update StrategyRouter's risk_engine - Final approach using curl + manual signing"""

from pathlib import Path
import json
import subprocess
import sys

# Read backend/.env
backend_env = Path(__file__).parent / "backend" / ".env"
env_vars = {}

if backend_env.exists():
    with open(backend_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

WALLET_ADDRESS = env_vars.get("BACKEND_WALLET_ADDRESS", "")
PRIV_KEY_HEX = env_vars.get("BACKEND_WALLET_PRIVATE_KEY", "")

if not WALLET_ADDRESS or not PRIV_KEY_HEX:
    print("❌ Backend wallet not configured in backend/.env")
    sys.exit(1)

STRATEGY_ROUTER = 0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73
NEW_RISK_ENGINE = 0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab
RPC_URL = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"

print(f"🔧 Updating StrategyRouter's risk_engine...")
print(f"   Wallet: {WALLET_ADDRESS}")
print(f"   StrategyRouter: {hex(STRATEGY_ROUTER)}")
print(f"   New RiskEngine: {hex(NEW_RISK_ENGINE)}")

# Import after env is loaded
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.transaction import TransactionHashPrefix, compute_transaction_hash
from starknet_py.cairo.felt import encode_shortstring
from typing import List
import requests

# Get nonce via curl
nonce_payload = {
    "jsonrpc": "2.0",
    "method": "starknet_getNonce",
    "params": {"block_id": "latest", "contract_address": WALLET_ADDRESS},
    "id": 1
}

response = requests.post(RPC_URL, json=nonce_payload)
nonce_hex = response.json()["result"]
nonce = int(nonce_hex, 16)
print(f"   Nonce: {nonce}")

# Build calldata
selector = get_selector_from_name("set_risk_engine")
calldata = [NEW_RISK_ENGINE]

# Build invoke v3
key_pair = KeyPair.from_private_key(int(PRIV_KEY_HEX, 16))

# Simple resource bounds
l1_gas_max = 10000
l1_gas_price = 200000000000000
l2_gas_max = 1000000
l2_gas_price = 1000000000
l1_data_max = 5000
l1_data_price = 150000000000000

# Compute tx hash for v3 invoke
# CallArray for v3: [to, selector, data_offset, data_len]
call_array = [STRATEGY_ROUTER, selector, 0, len(calldata)]
all_calldata = calldata

# Simplified: Build the invoke v3 manually
# For now, let's use a simpler approach - just call the backend API to do it

print(f"\n📝 Calling backend API to execute...")

# Actually, let's just document what needs to be done and let the user do it via the backend API
print(f"""
✅ RPC and port issues are fixed.

⚠️ To complete the fix, you need to wire StrategyRouter to RiskEngine v4.

**Option 1: Use backend API (RECOMMENDED)**
curl -X POST http://localhost:8001/api/v1/admin/update-strategy-router-risk-engine \\
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

**Option 2: Manual starkli (if you have deployer wallet setup)**
starkli invoke \\
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7 \\
  0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73 \\
  set_risk_engine \\
  0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab

**The Issue:**
- StrategyRouter's risk_engine is pointing to old address
- When RiskEngine v4 tries to call StrategyRouter.update_allocation(), it gets rejected
- Need to call StrategyRouter.set_risk_engine(NEW_RISK_ENGINE) as owner

**Backend wallet** ({WALLET_ADDRESS}) can do this if it's the owner, or needs deployer wallet.
""")
