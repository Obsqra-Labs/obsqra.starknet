#!/usr/bin/env python3
"""
Deploy RiskEngine and StrategyRouter contracts using starknet_py
"""

import sys
import asyncio
import json
from pathlib import Path

# Check if we need to use venv
ai_service_venv = Path("/opt/obsqra.starknet/ai-service/venv")
if ai_service_venv.exists():
    sys.path.insert(0, str(ai_service_venv / "lib/python3.12/site-packages"))

from starknet_py.net.account.account import Account
from starknet_py.net.client import Client
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.networks import SEPOLIA
from starknet_py.contract import Contract
from starknet_py.net.key_pair import KeyPair

# Configuration
RPC_URL = "https://starknet-sepolia-rpc.publicnode.com"
RISK_ENGINE_CLASS_HASH = 0x03ea934f4442de174715b458377bf5d1900c2a7c2a1d5e7486fcde9e522e2216
STRATEGY_ROUTER_CLASS_HASH = 0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d72b7

# Account credentials from sncast
ACCOUNT_ADDRESS = 0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d
ACCOUNT_PRIVATE_KEY = 0x7fd44d52324945e2d9f2e62bd2dadb794e2274dbd0955251aeca6cc96153afc
ACCOUNT_CLASS_HASH = 0x5b4b537eaa2399e3aa99c4e2e0208ebd6c71bc1467938cd52c798c601e43564

async def main():
    """Deploy contracts"""
    try:
        # Create client
        client = FullNodeClient(node_url=RPC_URL)
        
        # Create account
        key_pair = KeyPair.from_private_key(ACCOUNT_PRIVATE_KEY)
        account = Account(
            client=client,
            address=ACCOUNT_ADDRESS,
            key_pair=key_pair,
            chain=SEPOLIA,
        )
        
        print(f"✓ Connected to: {RPC_URL}")
        print(f"✓ Account: {hex(ACCOUNT_ADDRESS)}")
        
        # Deploy RiskEngine
        print("\n=== Deploying RiskEngine ===")
        owner = ACCOUNT_ADDRESS
        strategy_router = 0x0000000000000000000000000000000000000000000000000000000000000001
        dao_manager = 0x0000000000000000000000000000000000000000000000000000000000000001
        
        constructor_args = [owner, strategy_router, dao_manager]
        
        try:
            deploy_result = await account.deploy_contract(
                class_hash=RISK_ENGINE_CLASS_HASH,
                abi=None,
                constructor_args=constructor_args,
                unique=True,
            )
            
            print(f"✓ RiskEngine deployment hash: {hex(deploy_result.hash)}")
            print(f"✓ RiskEngine address: {hex(deploy_result.address)}")
            
            # Wait for transaction
            await account.client.wait_for_tx(deploy_result.hash)
            print("✓ RiskEngine deployment confirmed")
            
        except Exception as e:
            print(f"✗ RiskEngine deployment failed: {e}")
        
        print("\n=== Deployment Complete ===")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
