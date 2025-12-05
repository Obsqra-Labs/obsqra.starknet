#!/usr/bin/env python3
"""
Deploy Obsqra contracts to Starknet Sepolia using starknet.py
"""
import asyncio
import json
from pathlib import Path
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract

# Configuration
RPC_URL = "https://starknet-sepolia.public.blastapi.io"
ACCOUNT_ADDRESS = "0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd"
PRIVATE_KEY = "0x04d871184e90d8c7399256180b4576d0e257b58dfeca4ae00f7565c02bcfc218"

# Contract paths
CONTRACTS_DIR = Path("/opt/obsqra.starknet/contracts/target/dev")
RISK_ENGINE = CONTRACTS_DIR / "obsqra_contracts_RiskEngine.contract_class.json"
DAO_MANAGER = CONTRACTS_DIR / "obsqra_contracts_DAOConstraintManager.contract_class.json"
STRATEGY_ROUTER = CONTRACTS_DIR / "obsqra_contracts_StrategyRouter.contract_class.json"


async def deploy_contracts():
    """Deploy all contracts to Starknet Sepolia"""
    
    print("=" * 60)
    print("Obsqra Starknet Deployment (starknet.py)")
    print("=" * 60)
    print()
    
    # Initialize client
    print(f"Connecting to RPC: {RPC_URL}")
    client = FullNodeClient(node_url=RPC_URL)
    
    # Initialize account
    print(f"Account: {ACCOUNT_ADDRESS}")
    key_pair = KeyPair.from_private_key(int(PRIVATE_KEY, 16))
    account = Account(
        client=client,
        address=ACCOUNT_ADDRESS,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA
    )
    print(f"✓ Account initialized")
    print()
    
    # Check balance
    try:
        balance = await client.get_balance(ACCOUNT_ADDRESS)
        print(f"Account balance: {balance / 1e18} STRK")
        print()
    except Exception as e:
        print(f"Warning: Could not fetch balance: {e}")
        print()
    
    # Deploy RiskEngine
    print("=" * 60)
    print("1. Declaring RiskEngine")
    print("=" * 60)
    
    with open(RISK_ENGINE, 'r') as f:
        risk_engine_compiled = json.load(f)
    
    try:
        declare_result = await account.sign_declare_v2(
            compiled_contract=risk_engine_compiled,
            max_fee=int(1e16)
        )
        await account.client.wait_for_tx(declare_result.transaction_hash)
        risk_engine_class_hash = declare_result.class_hash
        print(f"✓ RiskEngine declared")
        print(f"  Class Hash: {hex(risk_engine_class_hash)}")
        print(f"  TX: {hex(declare_result.transaction_hash)}")
    except Exception as e:
        if "is already declared" in str(e):
            print(f"⚠ RiskEngine already declared")
            # Extract class hash from error or use a known one
            # For now, we'll need to provide it manually
            risk_engine_class_hash = None
        else:
            print(f"✗ Error declaring RiskEngine: {e}")
            return
    print()
    
    # Deploy DAOConstraintManager
    print("=" * 60)
    print("2. Declaring DAOConstraintManager")
    print("=" * 60)
    
    with open(DAO_MANAGER, 'r') as f:
        dao_manager_compiled = json.load(f)
    
    try:
        declare_result = await account.sign_declare_v2(
            compiled_contract=dao_manager_compiled,
            max_fee=int(1e16)
        )
        await account.client.wait_for_tx(declare_result.transaction_hash)
        dao_manager_class_hash = declare_result.class_hash
        print(f"✓ DAOConstraintManager declared")
        print(f"  Class Hash: {hex(dao_manager_class_hash)}")
        print(f"  TX: {hex(declare_result.transaction_hash)}")
    except Exception as e:
        if "is already declared" in str(e):
            print(f"⚠ DAOConstraintManager already declared")
            dao_manager_class_hash = None
        else:
            print(f"✗ Error declaring DAOConstraintManager: {e}")
            return
    print()
    
    # Deploy StrategyRouter
    print("=" * 60)
    print("3. Declaring StrategyRouter")
    print("=" * 60)
    
    with open(STRATEGY_ROUTER, 'r') as f:
        strategy_router_compiled = json.load(f)
    
    try:
        declare_result = await account.sign_declare_v2(
            compiled_contract=strategy_router_compiled,
            max_fee=int(1e16)
        )
        await account.client.wait_for_tx(declare_result.transaction_hash)
        strategy_router_class_hash = declare_result.class_hash
        print(f"✓ StrategyRouter declared")
        print(f"  Class Hash: {hex(strategy_router_class_hash)}")
        print(f"  TX: {hex(declare_result.transaction_hash)}")
    except Exception as e:
        if "is already declared" in str(e):
            print(f"⚠ StrategyRouter already declared")
            strategy_router_class_hash = None
        else:
            print(f"✗ Error declaring StrategyRouter: {e}")
            return
    print()
    
    # Deploy contracts (if we have class hashes)
    if all([risk_engine_class_hash, dao_manager_class_hash, strategy_router_class_hash]):
        print("=" * 60)
        print("Deploying Contracts")
        print("=" * 60)
        print()
        
        # TODO: Add deploy logic here
        print("✓ All contracts declared successfully")
        print()
        print("Next step: Deploy contract instances")
        print("  Use sncast deploy or deploy via starknet.js")
    else:
        print("⚠ Some contracts already declared. Check Voyager for class hashes.")
    
    print()
    print("=" * 60)
    print("Deployment Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(deploy_contracts())

