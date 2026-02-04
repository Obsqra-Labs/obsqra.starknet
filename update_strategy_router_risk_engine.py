#!/usr/bin/env python3
"""Update StrategyRouter's risk_engine to point to RiskEngine v4"""

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.selector import get_selector_from_name
import asyncio
import os
import sys
from pathlib import Path

# Contract addresses
STRATEGY_ROUTER = 0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73
NEW_RISK_ENGINE = 0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab

# Load from .env.sepolia
env_file = Path(__file__).parent / ".env.sepolia"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Get credentials - use backend wallet (deployed and has the key)
backend_env = Path(__file__).parent / "backend" / ".env"
DEPLOYER_ADDRESS = ""
PRIV_KEY = ""

if backend_env.exists():
    with open(backend_env) as f:
        for line in f:
            line = line.strip()
            if line.startswith("BACKEND_WALLET_PRIVATE_KEY="):
                PRIV_KEY = line.split('=', 1)[1]
            if line.startswith("BACKEND_WALLET_ADDRESS="):
                DEPLOYER_ADDRESS = line.split('=', 1)[1]

if not DEPLOYER_ADDRESS or not PRIV_KEY:
    print("❌ Backend wallet credentials not found in backend/.env")
    sys.exit(1)

print(f"ℹ️ Using backend wallet: {DEPLOYER_ADDRESS}")

# Resource bounds for v3 transactions
DEFAULT_RESOURCE_BOUNDS = {
    "l1_gas": {"max_amount": 10000, "max_price_per_unit": 200000000000000},
    "l2_gas": {"max_amount": 1000000, "max_price_per_unit": 1000000000},
    "l1_data_gas": {"max_amount": 5000, "max_price_per_unit": 150000000000000},
}

async def main():
    # Use Alchemy for better RPC compatibility
    client = FullNodeClient(node_url="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7")
    
    # Create account
    key_pair = KeyPair.from_private_key(int(PRIV_KEY, 16))
    account = Account(
        address=int(DEPLOYER_ADDRESS, 16),
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA
    )
    
    print(f"🔧 Updating StrategyRouter's risk_engine...")
    print(f"   Deployer: {DEPLOYER_ADDRESS}")
    print(f"   StrategyRouter: {hex(STRATEGY_ROUTER)}")
    print(f"   New RiskEngine: {hex(NEW_RISK_ENGINE)}")
    
    # Get nonce (use latest block to avoid RPC issues)
    nonce_response = await client._client.call(
        method_name="starknet_getNonce",
        params={"block_id": "latest", "contract_address": hex(account.address)}
    )
    nonce = int(nonce_response, 16)
    
    # Build call manually to avoid RPC version issues
    from starknet_py.net.client_models import Call
    call = Call(
        to_addr=STRATEGY_ROUTER,
        selector=get_selector_from_name("set_risk_engine"),
        calldata=[NEW_RISK_ENGINE]
    )
    
    # Sign and execute
    prepared_call = await account.sign_invoke_v3(
        calls=[call],
        nonce=nonce,
        resource_bounds=DEFAULT_RESOURCE_BOUNDS,
    )
    
    # Send transaction
    invoke_result = await client.send_transaction(prepared_call)
    
    tx_hash = hex(invoke_result.transaction_hash)
    print(f"✅ Transaction sent: {tx_hash}")
    print(f"   Waiting for confirmation...")
    
    await account.client.wait_for_tx(invoke_result.transaction_hash)
    print(f"✅ StrategyRouter's risk_engine updated!")
    print(f"   You can now execute allocations")

if __name__ == "__main__":
    asyncio.run(main())
