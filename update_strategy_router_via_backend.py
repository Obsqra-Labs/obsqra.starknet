#!/usr/bin/env python3
"""Update StrategyRouter's risk_engine using backend's RPC helpers"""

import sys
import os
from pathlib import Path

# Load .env.sepolia (backend config will also load it)
env_file = Path(__file__).parent / ".env.sepolia"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.config import get_settings
from app.utils.rpc import with_rpc_fallback
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
import asyncio

settings = get_settings()

STRATEGY_ROUTER = 0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73
NEW_RISK_ENGINE = int(settings.RISK_ENGINE_ADDRESS, 16)

if not settings.BACKEND_WALLET_PRIVATE_KEY or not settings.BACKEND_WALLET_ADDRESS:
    print("❌ Backend wallet not configured")
    sys.exit(1)

print(f"🔧 Updating StrategyRouter's risk_engine...")
print(f"   Wallet: {settings.BACKEND_WALLET_ADDRESS}")
print(f"   StrategyRouter: {hex(STRATEGY_ROUTER)}")
print(f"   New RiskEngine: {hex(NEW_RISK_ENGINE)}")

async def main():
    key_pair = KeyPair.from_private_key(int(settings.BACKEND_WALLET_PRIVATE_KEY, 16))
    network_chain = StarknetChainId.SEPOLIA if settings.STARKNET_NETWORK.lower() == "sepolia" else StarknetChainId.MAINNET
    
    async def _execute(client: FullNodeClient, _rpc_url: str):
        account = Account(
            address=int(settings.BACKEND_WALLET_ADDRESS, 16),
            client=client,
            key_pair=key_pair,
            chain=network_chain
        )
        
        # Get nonce
        try:
            nonce = await account.get_nonce(block_number="pending")
        except:
            nonce = await account.get_nonce(block_number="latest")
        
        print(f"   Nonce: {nonce}")
        
        # Execute
        call = Call(
            to_addr=STRATEGY_ROUTER,
            selector=get_selector_from_name("set_risk_engine"),
            calldata=[NEW_RISK_ENGINE]
        )
        
        result = await account.execute_v3(
            calls=[call],
            nonce=nonce,
            resource_bounds={
                "l1_gas": {"max_amount": 10000, "max_price_per_unit": 200000000000000},
                "l2_gas": {"max_amount": 1000000, "max_price_per_unit": 1000000000},
                "l1_data_gas": {"max_amount": 5000, "max_price_per_unit": 150000000000000},
            },
        )
        
        return result
    
    result, rpc_used = await with_rpc_fallback(_execute)
    
    tx_hash = hex(result.transaction_hash)
    print(f"✅ Transaction sent: {tx_hash}")
    print(f"   RPC used: {rpc_used}")
    print(f"   Waiting for confirmation...")
    
    # Wait for tx (use same RPC)
    async def _wait(client: FullNodeClient, _rpc_url: str):
        await client.wait_for_tx(result.transaction_hash)
        return True
    
    await with_rpc_fallback(_wait, urls=[rpc_used])
    
    print(f"✅ StrategyRouter's risk_engine updated to {hex(NEW_RISK_ENGINE)}!")
    print(f"   Allocation execution is now unblocked")

if __name__ == "__main__":
    asyncio.run(main())
