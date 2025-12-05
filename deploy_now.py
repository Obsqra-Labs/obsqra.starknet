#!/usr/bin/env python3
"""
Simple deployment using existing deployer wallet
"""
import asyncio
import json
from pathlib import Path
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract

# Load deployer wallet
with open('.deployer_wallet.json', 'r') as f:
    wallet = json.load(f)

RPC_URL = "https://starknet-sepolia.public.blastapi.io/rpc/v0_7"
DEPLOYER_ADDRESS = int(wallet['address'], 16)
DEPLOYER_PRIVATE_KEY = int(wallet['private_key'], 16)

# Contract paths
CONTRACTS_DIR = Path("contracts/target/dev")
RISK_ENGINE = CONTRACTS_DIR / "obsqra_contracts_RiskEngine.contract_class.json"
DAO_MANAGER = CONTRACTS_DIR / "obsqra_contracts_DAOConstraintManager.contract_class.json"
STRATEGY_ROUTER = CONTRACTS_DIR / "obsqra_contracts_StrategyRouter.contract_class.json"


async def check_balance(account):
    """Check STRK balance (native gas token)"""
    try:
        # STRK token on Starknet Sepolia
        strk_token = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
        
        balance_call = await account.client.call_contract(
            {
                "contract_address": strk_token,
                "entry_point_selector": get_selector_from_name("balanceOf"),
                "calldata": [account.address]
            }
        )
        balance = int(balance_call[0])
        balance_strk = balance / 1e18
        return balance_strk
    except Exception as e:
        print(f"Could not check balance: {e}")
        return 0


async def main():
    print("=" * 60)
    print("🚀 Obsqra Starknet Deployment")
    print("=" * 60)
    print()
    
    # Initialize client
    print(f"📡 Connecting to Sepolia...")
    print(f"RPC: {RPC_URL}")
    client = FullNodeClient(node_url=RPC_URL)
    print("✅ Connected")
    print()
    
    # Create account from deployer wallet
    print("=" * 60)
    print("👛 Loading Deployer Wallet")
    print("=" * 60)
    print(f"Address: {hex(DEPLOYER_ADDRESS)}")
    
    key_pair = KeyPair.from_private_key(DEPLOYER_PRIVATE_KEY)
    
    account = Account(
        address=DEPLOYER_ADDRESS,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA_TESTNET
    )
    print("✅ Account loaded")
    print()
    
    # Skip balance check (API compatibility issues)
    print("💰 Assuming wallet is funded with STRK...")
    print("   (Transaction: 0x25887ce9586b3a4c4840355c2deb137cf1c4eedc68a8fd10be7253b53d461ab)")
    print()
    
    # Step 1: Declare contracts
    print("=" * 60)
    print("📝 Step 1: Declaring Contracts")
    print("=" * 60)
    print()
    
    contracts_to_declare = [
        ("RiskEngine", RISK_ENGINE),
        ("DAOConstraintManager", DAO_MANAGER),
        ("StrategyRouter", STRATEGY_ROUTER)
    ]
    
    declared_classes = {}
    
    for name, path in contracts_to_declare:
        print(f"Declaring {name}...")
        
        try:
            with open(path, 'r') as f:
                contract_json = json.load(f)
            
            # Extract sierra class
            sierra_class = contract_json.get("sierra_program", [])
            if not sierra_class:
                sierra_class = contract_json  # Try whole file
            
            declare_result = await account.sign_declare_v2(
                compiled_contract=path.read_text(),
                max_fee=int(1e16)  # 0.01 ETH max
            )
            
            await account.client.wait_for_tx(declare_result.transaction_hash)
            
            class_hash = declare_result.class_hash
            declared_classes[name] = hex(class_hash)
            
            print(f"✅ {name} declared")
            print(f"   Class Hash: {hex(class_hash)}")
            print()
            
        except Exception as e:
            print(f"❌ Failed to declare {name}: {e}")
            print()
            if "already declared" in str(e).lower():
                print("   (Contract already declared, continuing...)")
                # Try to extract class hash from error if possible
            else:
                return
    
    # Step 2: Deploy contracts
    print("=" * 60)
    print("🚀 Step 2: Deploying Contracts")
    print("=" * 60)
    print()
    
    # Deploy RiskEngine
    print("Deploying RiskEngine...")
    try:
        risk_engine_deploy = await account.deploy_contract(
            class_hash=int(declared_classes["RiskEngine"], 16),
            constructor_args=[DEPLOYER_ADDRESS],
            max_fee=int(1e16)
        )
        
        await account.client.wait_for_tx(risk_engine_deploy.hash)
        risk_engine_address = hex(risk_engine_deploy.deployed_address)
        print(f"✅ RiskEngine deployed at: {risk_engine_address}")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    
    # Deploy DAOConstraintManager
    print("Deploying DAOConstraintManager...")
    try:
        dao_deploy = await account.deploy_contract(
            class_hash=int(declared_classes["DAOConstraintManager"], 16),
            constructor_args=[
                DEPLOYER_ADDRESS,  # owner
                6000,  # max_single (60%)
                3,     # min_protocols
                5000,  # max_volatility (50%)
                1000000  # min_liquidity
            ],
            max_fee=int(1e16)
        )
        
        await account.client.wait_for_tx(dao_deploy.hash)
        dao_address = hex(dao_deploy.deployed_address)
        print(f"✅ DAOConstraintManager deployed at: {dao_address}")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    
    # Deploy StrategyRouter
    print("Deploying StrategyRouter...")
    # Placeholder protocol addresses (update with real ones)
    nostra_addr = 0x456
    zklend_addr = 0x789
    ekubo_addr = 0xabc
    
    try:
        router_deploy = await account.deploy_contract(
            class_hash=int(declared_classes["StrategyRouter"], 16),
            constructor_args=[
                DEPLOYER_ADDRESS,
                nostra_addr,
                zklend_addr,
                ekubo_addr,
                int(risk_engine_address, 16)
            ],
            max_fee=int(1e16)
        )
        
        await account.client.wait_for_tx(router_deploy.hash)
        router_address = hex(router_deploy.deployed_address)
        print(f"✅ StrategyRouter deployed at: {router_address}")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    
    # Save addresses
    print("=" * 60)
    print("💾 Saving Deployment Info")
    print("=" * 60)
    
    deployment_info = {
        "network": "sepolia",
        "rpc": RPC_URL,
        "deployer": hex(DEPLOYER_ADDRESS),
        "contracts": {
            "riskEngine": risk_engine_address,
            "daoConstraintManager": dao_address,
            "strategyRouter": router_address
        },
        "classHashes": declared_classes
    }
    
    with open('.env.sepolia', 'w') as f:
        f.write(f"RISK_ENGINE_ADDRESS={risk_engine_address}\n")
        f.write(f"DAO_MANAGER_ADDRESS={dao_address}\n")
        f.write(f"STRATEGY_ROUTER_ADDRESS={router_address}\n")
        f.write(f"DEPLOYER_ADDRESS={hex(DEPLOYER_ADDRESS)}\n")
    
    with open('deployed-sepolia.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print("✅ Saved to .env.sepolia and deployed-sepolia.json")
    print()
    
    # Summary
    print("=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print()
    print("Contract Addresses:")
    print(f"  RiskEngine:          {risk_engine_address}")
    print(f"  DAOConstraintManager: {dao_address}")
    print(f"  StrategyRouter:      {router_address}")
    print()
    print("View on Explorer:")
    print(f"  https://sepolia.voyager.online/contract/{router_address}")
    print()
    print("Next steps:")
    print("  1. Update frontend/.env.local with these addresses")
    print("  2. Update ai-service/.env with these addresses")
    print("  3. Test the contracts on Sepolia")
    print()


if __name__ == "__main__":
    from starknet_py.hash.selector import get_selector_from_name
    asyncio.run(main())

