#!/usr/bin/env python3
"""
Check for locked ETH funds in the Strategy Router contracts
"""

import json
from starknet_py.net.rpc_client import RpcClient
from starknet_py.net.models import StarknetChainId
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
import asyncio

# Contract addresses
ETH_CONTRACTS = {
    "Contract 1 (Protocol Integration)": "0x01c2e698bc0f263ea62dc3c557d32afe25c13cbc91900d726b84c58a0baa09f0",
    "Contract 2 (Latest ETH)": "0x01888e3f3d6cd137e63ff1a090a1e2c9ed5754162a8d5739364aba657fab20e4",
    "Contract 3 (No Protocol)": "0x053b69775c22246080a17c37a38dbda31d1841c8f6d7b4d928d54a99eda2748c",
}

ETH_TOKEN = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
RPC_URL = "https://starknet-sepolia-rpc.publicnode.com"

# ERC20 ABI for balanceOf
ERC20_ABI = [
    {
        "name": "balanceOf",
        "type": "function",
        "inputs": [{"name": "account", "type": "core::starknet::contract_address::ContractAddress"}],
        "outputs": [{"type": "core::integer::u256"}],
        "state_mutability": "view",
    }
]

# Strategy Router ABI
ROUTER_ABI = [
    {
        "name": "get_total_value_locked",
        "type": "function",
        "inputs": [],
        "outputs": [{"type": "core::integer::u256"}],
        "state_mutability": "view",
    },
    {
        "name": "get_user_balance",
        "type": "function",
        "inputs": [{"name": "user", "type": "core::starknet::contract_address::ContractAddress"}],
        "outputs": [{"type": "core::integer::u256"}],
        "state_mutability": "view",
    },
]

async def check_balances():
    client = RpcClient(node_url=RPC_URL)
    
    print("🔍 Checking for locked ETH funds in Strategy Router contracts...")
    print("=" * 70)
    print()
    
    # Get ETH token contract
    eth_contract = await Contract.from_address(ETH_TOKEN, client, ERC20_ABI)
    
    for name, contract_addr in ETH_CONTRACTS.items():
        print(f"📋 {name}")
        print(f"   Address: {contract_addr}")
        print(f"   Starkscan: https://sepolia.starkscan.co/contract/{contract_addr}")
        print()
        
        try:
            # Check ETH balance in contract
            balance_result = await eth_contract.functions["balanceOf"].call(contract_addr)
            balance = balance_result.balance if hasattr(balance_result, 'balance') else balance_result
            if isinstance(balance, dict) and 'low' in balance:
                balance_wei = balance['low'] + (balance['high'] << 128)
            else:
                balance_wei = int(balance) if balance else 0
            
            balance_eth = balance_wei / 1e18
            
            if balance_eth > 0:
                print(f"   ⚠️  ETH LOCKED: {balance_eth:.6f} ETH")
            else:
                print(f"   ✅ No ETH locked: {balance_eth:.6f} ETH")
            
            # Check total deposits
            try:
                router_contract = await Contract.from_address(contract_addr, client, ROUTER_ABI)
                tvl_result = await router_contract.functions["get_total_value_locked"].call()
                tvl = tvl_result.total_value_locked if hasattr(tvl_result, 'total_value_locked') else tvl_result
                if isinstance(tvl, dict) and 'low' in tvl:
                    tvl_wei = tvl['low'] + (tvl['high'] << 128)
                else:
                    tvl_wei = int(tvl) if tvl else 0
                tvl_eth = tvl_wei / 1e18
                print(f"   📊 Total Deposits: {tvl_eth:.6f} ETH")
            except Exception as e:
                print(f"   ⚠️  Could not check total deposits: {e}")
            
        except Exception as e:
            print(f"   ❌ Error checking contract: {e}")
        
        print()
        print("-" * 70)
        print()

if __name__ == "__main__":
    asyncio.run(check_balances())

