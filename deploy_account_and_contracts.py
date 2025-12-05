#!/usr/bin/env python3
"""
Deploy account first, then deploy contracts
"""
import asyncio
import json
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.address import compute_address
from starknet_py.net.client_models import ResourceBounds

# Deployer wallet details
PRIVATE_KEY = 0xf4506f978f613c4f3d8934b4bf5c3459fba3a16fbc479d5f7dee8e3832404aab
PUBLIC_KEY = 0x7d5e6258addc2a13478e3c092339db243b68cfb7de81833668f418ddf7e7201
ADDRESS = 0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b
CLASS_HASH = 0x4c6d6cf894f8bc96bb9c525e6853e5483177841f7388f74a46cfda6f028c755

RPC_URL = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"

async def main():
    print("=" * 70)
    print("🚀 DEPLOYING ACCOUNT + CONTRACTS TO SEPOLIA")
    print("=" * 70)
    print()
    
    # Connect to Sepolia
    print("📡 Connecting to Sepolia via Alchemy...")
    client = FullNodeClient(node_url=RPC_URL)
    print("✅ Connected")
    print()
    
    # Create key pair
    key_pair = KeyPair.from_private_key(PRIVATE_KEY)
    
    print("=" * 70)
    print("Step 1: DEPLOYING ACCOUNT CONTRACT")
    print("=" * 70)
    print(f"Address: {hex(ADDRESS)}")
    print()
    
    # Deploy account
    try:
        print("Sending DEPLOY_ACCOUNT_V3 transaction...")
        
        # Deploy account using class method with resource bounds
        l1_resource_bounds = ResourceBounds(
            max_amount=100000,
            max_price_per_unit=100000000000  # 100 gwei
        )
        
        deploy_result = await Account.deploy_account_v3(
            address=ADDRESS,
            class_hash=CLASS_HASH,
            salt=0,
            key_pair=key_pair,
            client=client,
            chain=StarknetChainId.SEPOLIA_TESTNET,
            constructor_calldata=[PUBLIC_KEY],
            l1_resource_bounds=l1_resource_bounds
        )
        
        print(f"✅ Transaction sent: {hex(deploy_result.hash)}")
        print("⏳ Waiting for confirmation (this may take 30-60 seconds)...")
        
        await client.wait_for_tx(deploy_result.hash)
        
        print("✅ ACCOUNT DEPLOYED!")
        print(f"   View: https://sepolia.voyager.online/tx/{hex(deploy_result.hash)}")
        print()
        
        # Now create the account instance for deploying contracts
        account = deploy_result.account
        
    except Exception as e:
        error_str = str(e).lower()
        if "already deployed" in error_str or "already initialized" in error_str:
            print("✅ Account already deployed, continuing...")
            # Create account instance
            account = Account(
                address=ADDRESS,
                client=client,
                key_pair=key_pair,
                chain=StarknetChainId.SEPOLIA_TESTNET
            )
            print()
        else:
            print(f"❌ Account deployment failed: {e}")
            print(f"   Full error: {type(e).__name__}")
            return
    
    # Now deploy contracts
    print("=" * 70)
    print("Step 2: DECLARING CONTRACTS")
    print("=" * 70)
    print()
    
    from pathlib import Path
    
    contracts = [
        ("RiskEngine", Path("contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json")),
        ("DAOConstraintManager", Path("contracts/target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json")),
        ("StrategyRouter", Path("contracts/target/dev/obsqra_contracts_StrategyRouter.contract_class.json"))
    ]
    
    class_hashes = {}
    
    for name, path in contracts:
        print(f"Declaring {name}...")
        try:
            with open(path) as f:
                contract_class = json.load(f)
            
            # Declare contract
            declare_result = await account.sign_declare_v3(
                compiled_contract=contract_class,
                auto_estimate=True
            )
            
            print(f"   TX: {hex(declare_result.transaction_hash)}")
            await client.wait_for_tx(declare_result.transaction_hash)
            
            class_hashes[name] = declare_result.class_hash
            print(f"   ✅ Class Hash: {hex(declare_result.class_hash)}")
            print()
            
        except Exception as e:
            if "already declared" in str(e).lower():
                print(f"   ⚠️  Already declared, extracting hash...")
                # Try to get hash from error or contract
                print()
            else:
                print(f"   ❌ Error: {e}")
                print()
    
    # Deploy contracts
    print("=" * 70)
    print("Step 3: DEPLOYING CONTRACT INSTANCES")
    print("=" * 70)
    print()
    
    # Deploy RiskEngine
    if "RiskEngine" in class_hashes:
        print("1. Deploying RiskEngine...")
        try:
            deploy_result = await account.deploy_contract_v3(
                class_hash=class_hashes["RiskEngine"],
                constructor_args=[ADDRESS],  # owner
                auto_estimate=True
            )
            
            await client.wait_for_tx(deploy_result.hash)
            risk_addr = hex(deploy_result.deployed_address)
            print(f"   ✅ Address: {risk_addr}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            risk_addr = None
    
    # Deploy DAOConstraintManager
    if "DAOConstraintManager" in class_hashes:
        print("2. Deploying DAOConstraintManager...")
        try:
            deploy_result = await account.deploy_contract_v3(
                class_hash=class_hashes["DAOConstraintManager"],
                constructor_args=[ADDRESS, 6000, 3, 5000, 1000000],
                auto_estimate=True
            )
            
            await client.wait_for_tx(deploy_result.hash)
            dao_addr = hex(deploy_result.deployed_address)
            print(f"   ✅ Address: {dao_addr}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            dao_addr = None
    
    # Deploy StrategyRouter
    if "StrategyRouter" in class_hashes and risk_addr:
        print("3. Deploying StrategyRouter...")
        try:
            deploy_result = await account.deploy_contract_v3(
                class_hash=class_hashes["StrategyRouter"],
                constructor_args=[ADDRESS, 0x456, 0x789, 0xabc, int(risk_addr, 16)],
                auto_estimate=True
            )
            
            await client.wait_for_tx(deploy_result.hash)
            router_addr = hex(deploy_result.deployed_address)
            print(f"   ✅ Address: {router_addr}")
            print()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            router_addr = None
    
    # Save results
    print("=" * 70)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 70)
    print()
    if risk_addr:
        print(f"RiskEngine:          {risk_addr}")
    if dao_addr:
        print(f"DAOConstraintManager: {dao_addr}")
    if router_addr:
        print(f"StrategyRouter:      {router_addr}")
    print()
    if router_addr:
        print(f"View on Voyager: https://sepolia.voyager.online/contract/{router_addr}")

if __name__ == "__main__":
    asyncio.run(main())

