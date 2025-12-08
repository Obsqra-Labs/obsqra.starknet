#!/usr/bin/env python3
"""
Deploy contracts from existing declared classes
"""

import asyncio
import json
from pathlib import Path
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
from starknet_py.common import create_sierra_compiled_contract

# Configuration
RPC_URL = "https://starknet-sepolia-rpc.publicnode.com"
CHAIN_ID = StarknetChainId.SEPOLIA

# Deployer account (from ~/.starknet_accounts/starknet_open_zeppelin_accounts.json)
DEPLOYER_ADDRESS = 0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d
DEPLOYER_PRIVATE_KEY = 0x7fd44d52324945e2d9f2e62bd2dadb794e2274dbd0955251aeca6cc96153afc

# Existing contracts
EXISTING_STRATEGY_ROUTER = 0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a
EXISTING_DAO = 0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856

# Protocol addresses
JEDISWAP_ROUTER = 0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21
EKUBO_CORE = 0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384
STRK_TOKEN = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1

CONTRACT_DIR = Path("/opt/obsqra.starknet/contracts/target/dev")


async def main():
    print("=" * 60)
    print("🚀 Deploying Contracts from Existing Classes")
    print("=" * 60)
    
    # Create client
    client = FullNodeClient(node_url=RPC_URL)
    
    # Create account
    key_pair = KeyPair.from_private_key(DEPLOYER_PRIVATE_KEY)
    account = Account(
        client=client,
        address=DEPLOYER_ADDRESS,
        key_pair=key_pair,
        chain=CHAIN_ID,
    )
    
    print(f"📋 Deployer: {hex(DEPLOYER_ADDRESS)}")
    print(f"📋 RPC: {RPC_URL}")
    
    # Check balance (in STRK, not ETH on Sepolia)
    try:
        balance = await account.get_balance()
        print(f"💰 Balance: {balance / 10**18:.4f} STRK")
    except Exception as e:
        print(f"⚠️  Could not get balance: {e}")
    print()
    
    # ==========================================
    # Step 1: Use existing RiskEngine class hash
    # ==========================================
    print("📝 Step 1: Using existing RiskEngine class hash...")
    
    # From deployments/sepolia.json
    risk_engine_class_hash = 0x61febd39ccffbbd986e071669eb1f712f4dcf5e008aae7fa2bed1f09de6e304
    print(f"   RiskEngine Class Hash: {hex(risk_engine_class_hash)}")
    
    # Load ABI from Sierra file
    risk_engine_sierra = CONTRACT_DIR / "obsqra_contracts_RiskEngine.contract_class.json"
    with open(risk_engine_sierra) as f:
        risk_engine_data = json.load(f)
    risk_engine_abi = risk_engine_data.get("abi", [])
    print(f"✅ Loaded ABI with {len(risk_engine_abi)} entries")
    print()
    
    # ==========================================
    # Step 2: Deploy RiskEngine
    # ==========================================
    print("🚀 Step 2: Deploying RiskEngine...")
    print(f"   Constructor args:")
    print(f"     owner: {hex(DEPLOYER_ADDRESS)}")
    print(f"     strategy_router: {hex(EXISTING_STRATEGY_ROUTER)}")
    print(f"     dao_manager: {hex(EXISTING_DAO)}")
    
    deploy_call = await Contract.deploy_contract_v3(
        account=account,
        class_hash=risk_engine_class_hash,
        abi=risk_engine_abi,
        constructor_args=[
            DEPLOYER_ADDRESS,           # owner
            EXISTING_STRATEGY_ROUTER,   # strategy_router
            EXISTING_DAO,               # dao_manager
        ],
        auto_estimate=True,
    )
    await deploy_call.wait_for_acceptance()
    
    new_risk_engine = deploy_call.deployed_contract.address
    print(f"✅ RiskEngine deployed: {hex(new_risk_engine)}")
    print()
    
    # ==========================================
    # Step 3: Use existing StrategyRouterV2 class hash
    # ==========================================
    print("📝 Step 3: Using existing StrategyRouterV2 class hash...")
    
    # From deployments/sepolia.json (using StrategyRouter which has same interface)
    router_class_hash = 0xe69b66e921099643f7ebdc3b82f6d61b1178cb7e042e51c40073985357238f
    print(f"   StrategyRouterV2 Class Hash: {hex(router_class_hash)}")
    
    # Load ABI from Sierra file
    router_sierra = CONTRACT_DIR / "obsqra_contracts_StrategyRouterV2.contract_class.json"
    with open(router_sierra) as f:
        router_data = json.load(f)
    router_abi = router_data.get("abi", [])
    print(f"✅ Loaded ABI with {len(router_abi)} entries")
    print()
    
    # ==========================================
    # Step 4: Deploy StrategyRouterV2
    # ==========================================
    print("🚀 Step 4: Deploying StrategyRouterV2...")
    print(f"   Constructor args:")
    print(f"     owner: {hex(DEPLOYER_ADDRESS)}")
    print(f"     jediswap_router: {hex(JEDISWAP_ROUTER)}")
    print(f"     ekubo_core: {hex(EKUBO_CORE)}")
    print(f"     risk_engine: {hex(new_risk_engine)}")
    print(f"     dao_manager: {hex(EXISTING_DAO)}")
    print(f"     asset_token: {hex(STRK_TOKEN)}")
    
    router_deploy = await Contract.deploy_contract_v3(
        account=account,
        class_hash=router_class_hash,
        abi=router_abi,
        constructor_args=[
            DEPLOYER_ADDRESS,    # owner
            JEDISWAP_ROUTER,     # jediswap_router
            EKUBO_CORE,          # ekubo_core
            new_risk_engine,     # risk_engine
            EXISTING_DAO,        # dao_manager
            STRK_TOKEN,          # asset_token
        ],
        auto_estimate=True,
    )
    await router_deploy.wait_for_acceptance()
    
    new_router = router_deploy.deployed_contract.address
    print(f"✅ StrategyRouterV2 deployed: {hex(new_router)}")
    print()
    
    # ==========================================
    # Save deployment info
    # ==========================================
    print("📝 Saving deployment info...")
    
    deployment_info = {
        "network": "sepolia",
        "rpc": RPC_URL,
        "deployer": hex(DEPLOYER_ADDRESS),
        "contracts": {
            "riskEngine": hex(new_risk_engine),
            "strategyRouterV2": hex(new_router),
            "daoConstraintManager": hex(EXISTING_DAO),
        },
        "classHashes": {
            "riskEngine": hex(risk_engine_class_hash),
            "strategyRouterV2": hex(router_class_hash),
        }
    }
    
    with open("/opt/obsqra.starknet/deployed-sepolia.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    
    print("✅ Saved to deployed-sepolia.json")
    print()
    
    # ==========================================
    # Summary
    # ==========================================
    print("=" * 60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print()
    print("📋 Contract Addresses:")
    print(f"   RiskEngine: {hex(new_risk_engine)}")
    print(f"   StrategyRouterV2: {hex(new_router)}")
    print(f"   DAOConstraintManager: {hex(EXISTING_DAO)}")
    print()
    print("🔗 Explorer Links:")
    print(f"   RiskEngine: https://sepolia.starkscan.co/contract/{hex(new_risk_engine)}")
    print(f"   StrategyRouterV2: https://sepolia.starkscan.co/contract/{hex(new_router)}")
    print()
    print("🔧 Next Steps:")
    print("   1. Update frontend/.env.local:")
    print(f"      NEXT_PUBLIC_RISK_ENGINE_ADDRESS={hex(new_risk_engine)}")
    print(f"      NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS={hex(new_router)}")
    print("   2. Restart frontend: ./start-frontend-3003.sh")
    print("   3. Test AI orchestration!")


if __name__ == "__main__":
    asyncio.run(main())

