#!/usr/bin/env python3
"""
Deploy contracts using starknet.py (compatible with RPC 0.8)
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
from starknet_py.hash.casm_class_hash import compute_casm_class_hash
from starknet_py.common import create_casm_class

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
    print("🚀 Deploying Contracts with starknet.py")
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
    
    # Check balance
    balance = await account.get_balance()
    print(f"💰 Balance: {balance / 10**18:.4f} ETH")
    print()
    
    # ==========================================
    # Step 1: Declare RiskEngine
    # ==========================================
    print("📝 Step 1: Declaring RiskEngine...")
    
    risk_engine_sierra = CONTRACT_DIR / "obsqra_contracts_RiskEngine.contract_class.json"
    risk_engine_casm = CONTRACT_DIR / "obsqra_contracts_RiskEngine.compiled_contract_class.json"
    
    with open(risk_engine_sierra) as f:
        risk_engine_compiled = f.read()
    with open(risk_engine_casm) as f:
        risk_engine_casm_compiled = f.read()
    
    # Use the expected CASM class hash from RPC (if class already declared)
    # If fresh declare, compute from CASM
    casm_class = create_casm_class(risk_engine_casm_compiled)
    casm_class_hash = compute_casm_class_hash(casm_class)
    print(f"   Computed CASM class hash: {hex(casm_class_hash)}")
    
    try:
        declare_result = await Contract.declare_v3(
            account=account,
            compiled_contract=risk_engine_compiled,
            compiled_contract_casm=risk_engine_casm_compiled,
            compiled_class_hash=casm_class_hash,
            auto_estimate=True,
        )
        await declare_result.wait_for_acceptance()
        risk_engine_class_hash = declare_result.class_hash
        print(f"✅ RiskEngine Class Hash: {hex(risk_engine_class_hash)}")
    except Exception as e:
        if "already declared" in str(e).lower() or "Duplicate" in str(e):
            print("   ⚠️  RiskEngine class already declared, getting class hash...")
            # Get class hash from the Sierra contract
            from starknet_py.hash.class_hash import compute_class_hash
            sierra_contract = create_sierra_compiled_contract(risk_engine_compiled)
            risk_engine_class_hash = compute_class_hash(sierra_contract)
            print(f"✅ RiskEngine Class Hash (existing): {hex(risk_engine_class_hash)}")
        else:
            raise e
    
    print()
    
    # ==========================================
    # Step 2: Deploy RiskEngine
    # ==========================================
    print("🚀 Step 2: Deploying RiskEngine...")
    
    deploy_result = await declare_result.deploy_v3(
        constructor_args=[
            DEPLOYER_ADDRESS,           # owner
            EXISTING_STRATEGY_ROUTER,   # strategy_router
            EXISTING_DAO,               # dao_manager
        ],
        auto_estimate=True,
    )
    await deploy_result.wait_for_acceptance()
    
    new_risk_engine = deploy_result.deployed_contract.address
    print(f"✅ RiskEngine deployed: {hex(new_risk_engine)}")
    print()
    
    # ==========================================
    # Step 3: Declare StrategyRouterV2
    # ==========================================
    print("📝 Step 3: Declaring StrategyRouterV2...")
    
    router_sierra = CONTRACT_DIR / "obsqra_contracts_StrategyRouterV2.contract_class.json"
    router_casm = CONTRACT_DIR / "obsqra_contracts_StrategyRouterV2.compiled_contract_class.json"
    
    with open(router_sierra) as f:
        router_compiled = f.read()
    with open(router_casm) as f:
        router_casm_compiled = f.read()
    
    # Compute CASM class hash for router
    router_casm_class = create_casm_class(router_casm_compiled)
    router_casm_class_hash = compute_casm_class_hash(router_casm_class)
    print(f"   CASM class hash: {hex(router_casm_class_hash)}")
    
    router_declare = await Contract.declare_v3(
        account=account,
        compiled_contract=router_compiled,
        compiled_contract_casm=router_casm_compiled,
        compiled_class_hash=router_casm_class_hash,
        auto_estimate=True,
    )
    
    await router_declare.wait_for_acceptance()
    router_class_hash = router_declare.class_hash
    print(f"✅ StrategyRouterV2 Class Hash: {hex(router_class_hash)}")
    print()
    
    # ==========================================
    # Step 4: Deploy StrategyRouterV2
    # ==========================================
    print("🚀 Step 4: Deploying StrategyRouterV2...")
    
    router_deploy = await router_declare.deploy_v3(
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

