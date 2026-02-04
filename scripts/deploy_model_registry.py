#!/usr/bin/env python3
"""
Deploy Model Registry contract using backend's RPC utilities
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping, Call
from starknet_py.hash.selector import get_selector_from_name

from app.config import get_settings
from app.utils.rpc import with_rpc_fallback, get_rpc_urls

settings = get_settings()

DEFAULT_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=200000, max_price_per_unit=100000000000000),
    l1_data_gas=ResourceBounds(max_amount=200000, max_price_per_unit=1000000000000),
    l2_gas=ResourceBounds(max_amount=300000000, max_price_per_unit=20000000000),
)


async def _init_backend_account(client: FullNodeClient, key_pair: KeyPair, chain_id: StarknetChainId) -> Account:
    """Initialize backend account"""
    account = Account(
        address=int(settings.BACKEND_WALLET_ADDRESS, 16),
        client=client,
        key_pair=key_pair,
        chain=chain_id,
    )
    from starknet_py.net.client_models import SierraContractClass
    try:
        contract_class = await client.get_class_at(
            contract_address=account.address,
            block_number="latest",
        )
        account._cairo_version = 1 if isinstance(contract_class, SierraContractClass) else 0
    except Exception:
        account._cairo_version = 1
    return account


async def deploy_model_registry():
    """Deploy Model Registry contract"""
    if (ROOT / "backend" / ".env").exists():
        load_dotenv(ROOT / "backend" / ".env")
    
    owner_addr = settings.BACKEND_WALLET_ADDRESS
    if not owner_addr:
        raise RuntimeError("BACKEND_WALLET_ADDRESS not set")
    
    private_key = settings.BACKEND_WALLET_PRIVATE_KEY
    if not private_key:
        raise RuntimeError("BACKEND_WALLET_PRIVATE_KEY not set")
    
    network = settings.STARKNET_NETWORK.lower()
    chain_id = StarknetChainId.SEPOLIA if network == "sepolia" else StarknetChainId.MAINNET
    key_pair = KeyPair.from_private_key(int(private_key, 16))
    
    print("🚀 Deploying Model Registry Contract...")
    print(f"  Owner: {owner_addr}")
    print(f"  Network: {network}")
    print()
    
    # Read compiled class hash from artifact
    compiled_file = ROOT / "contracts" / "target" / "dev" / "obsqra_contracts_ModelRegistry.compiled_contract_class.json"
    if not compiled_file.exists():
        raise FileNotFoundError(f"Compiled contract not found: {compiled_file}")
    
    with open(compiled_file) as f:
        compiled_data = json.load(f)
    
    class_hash_hex = compiled_data.get("compiled_class_hash", "")
    if not class_hash_hex:
        raise ValueError("compiled_class_hash not found in compiled contract")
    
    class_hash = int(class_hash_hex, 16)
    print(f"✅ Class Hash: {hex(class_hash)}")
    print()
    
    # Deploy using backend RPC utilities
    async def _deploy(client: FullNodeClient, rpc_url: str):
        account = await _init_backend_account(client, key_pair, chain_id)
        
        try:
            nonce = await account.get_nonce(block_number="pending")
        except Exception:
            nonce = await account.get_nonce(block_number="latest")
        
        print(f"  Using nonce: {nonce} (via {rpc_url})")
        
        # Deploy contract
        deploy_result = await account.deploy_contract_v3(
            class_hash=class_hash,
            constructor_calldata=[int(owner_addr, 16)],
            nonce=nonce,
            resource_bounds=DEFAULT_RESOURCE_BOUNDS,
        )
        
        contract_address = deploy_result.contract_address
        tx_hash = hex(deploy_result.hash)
        
        print(f"✅ Transaction submitted: {tx_hash}")
        print(f"   Waiting for confirmation...")
        
        await client.wait_for_tx(deploy_result.hash, check_interval=2, retries=60)
        
        print(f"✅ Deployment confirmed!")
        print(f"   Contract Address: {hex(contract_address)}")
        return hex(contract_address)
    
    rpc_urls = get_rpc_urls()
    try:
        contract_addr, used_rpc = await with_rpc_fallback(_deploy, urls=rpc_urls)
        print()
        print(f"✅ Success via {used_rpc}")
        print(f"   Contract Address: {contract_addr}")
        print()
        print("📝 Next steps:")
        print(f"   1. Update backend/app/config.py: MODEL_REGISTRY_ADDRESS = \"{contract_addr}\"")
        print(f"   2. Register initial model version")
        return contract_addr
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(deploy_model_registry())
