#!/usr/bin/env python3
"""
Check STRK balance and run test transactions on Sepolia
"""
import asyncio
import json
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract

# Sepolia RPC
RPC_URL = "https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_7/EvhYN6geLrdvbYHVRgPJ7"

# STRK token on Sepolia
STRK_TOKEN = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

# Deployer wallet
DEPLOYER_ADDRESS = "0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
DEPLOYER_PRIVATE_KEY = "0xf4506f978f613c4f3d8934b4bf5c3459fba3a16fbc479d5f7dee8e3832404aab"

# ERC20 ABI for balance check
ERC20_ABI = [
    {
        "name": "balanceOf",
        "type": "function",
        "inputs": [{"name": "account", "type": "felt"}],
        "outputs": [{"name": "balance", "type": "Uint256"}],
        "stateMutability": "view"
    },
    {
        "name": "transfer",
        "type": "function",
        "inputs": [
            {"name": "recipient", "type": "felt"},
            {"name": "amount", "type": "Uint256"}
        ],
        "outputs": [{"name": "success", "type": "felt"}]
    }
]

async def check_balance():
    """Check STRK balance of deployer wallet"""
    print("=" * 60)
    print("🔍 Checking STRK Balance on Sepolia")
    print("=" * 60)
    
    client = FullNodeClient(node_url=RPC_URL)
    
    try:
        # Call balanceOf
        result = await client.call_contract({
            "contract_address": int(STRK_TOKEN, 16),
            "entry_point_selector": 0x2e4263afad30923c891518314c3c95dbe830a16874e8abc5777a9a20b54c76e,  # balanceOf
            "calldata": [int(DEPLOYER_ADDRESS, 16)]
        })
        
        # Parse Uint256 (low, high)
        if len(result) >= 2:
            low = result[0]
            high = result[1]
            balance_wei = low + (high << 128)
            balance_strk = balance_wei / 1e18
            
            print(f"\n📍 Deployer Address: {DEPLOYER_ADDRESS}")
            print(f"💰 STRK Balance: {balance_strk:.6f} STRK")
            print(f"   Raw (wei): {balance_wei}")
            
            return balance_strk
        else:
            print(f"Unexpected result: {result}")
            return 0
            
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return 0

async def main():
    balance = await check_balance()
    
    print("\n" + "=" * 60)
    if balance > 0:
        print("✅ You have STRK! You can run transactions.")
        print("\nTo generate history in the UI:")
        print("1. Go to the frontend")
        print("2. Enable Demo Mode (toggle in header)")
        print("3. Make deposits/withdrawals - they'll show in History")
        print("\nFor real transactions, you need to:")
        print("1. Connect a wallet with STRK")
        print("2. Deposit/withdraw through the UI")
    else:
        print("⚠️ No STRK balance found.")
        print("\nOptions:")
        print("1. Use Demo Mode in the UI to simulate transactions")
        print("2. Get testnet STRK from: https://faucet.starknet.io")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
