#!/usr/bin/env python3
"""Update StrategyRouter's risk_engine to point to RiskEngine v4

Direct approach: Read backend/.env, build tx, send via curl to RPC.
"""

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
PRIV_KEY = env_vars.get("BACKEND_WALLET_PRIVATE_KEY", "")

if not WALLET_ADDRESS or not PRIV_KEY:
    print("❌ Backend wallet not configured in backend/.env")
    sys.exit(1)

STRATEGY_ROUTER = "0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73"
NEW_RISK_ENGINE = "0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab"
RPC_URL = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"

print(f"🔧 Updating StrategyRouter's risk_engine...")
print(f"   Wallet: {WALLET_ADDRESS}")
print(f"   StrategyRouter: {STRATEGY_ROUTER}")
print(f"   New RiskEngine: {NEW_RISK_ENGINE}")

# Use starkli for the invoke (simpler than dealing with starknet_py RPC issues)
cmd = f"""
starkli invoke \\
  --rpc {RPC_URL} \\
  --private-key {PRIV_KEY} \\
  --account {WALLET_ADDRESS} \\
  {STRATEGY_ROUTER} \\
  set_risk_engine \\
  {NEW_RISK_ENGINE}
"""

print(f"\n📝 Running starkli invoke...")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Transaction sent!")
    print(result.stdout)
    print(f"\n✅ StrategyRouter's risk_engine updated!")
    print(f"   Allocation execution is now unblocked")
else:
    print(f"❌ Transaction failed:")
    print(result.stderr)
    sys.exit(1)
