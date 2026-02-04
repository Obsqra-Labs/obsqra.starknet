#!/usr/bin/env python3
"""
Set StrategyRouter's risk_engine address to authorize RiskEngine v4.

This script sets the risk_engine storage variable in StrategyRouter v3.5
so that RiskEngine can call StrategyRouter.update_allocation().

Uses backend's RPC utilities for compatibility (same as backend API routes).

Usage:
    python scripts/set_strategy_router_risk_engine.py

Requirements:
    - BACKEND_WALLET_PRIVATE_KEY must be set (owner wallet)
    - STRATEGY_ROUTER_ADDRESS must be set
    - RISK_ENGINE_ADDRESS must be set
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add backend to path to use RPC utilities
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

# Load env before get_settings() so BACKEND_WALLET_* is available when run from repo root
if (ROOT / "backend" / ".env").exists():
    load_dotenv(ROOT / "backend" / ".env")
if (ROOT / ".env.sepolia").exists():
    load_dotenv(ROOT / ".env.sepolia")

from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping, Call
from starknet_py.hash.selector import get_selector_from_name

# Use backend's RPC utilities (handles compatibility)
from app.utils.rpc import with_rpc_fallback, get_rpc_urls
from app.config import get_settings

BACKEND_ENV = ROOT / "backend" / ".env"
STRATEGY_ROUTER_CLASS = ROOT / "contracts" / "target" / "dev" / "obsqra_contracts_StrategyRouterV35.contract_class.json"

settings = get_settings()

# Default resource bounds (same as backend)
DEFAULT_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=200000, max_price_per_unit=100000000000000),
    l1_data_gas=ResourceBounds(max_amount=200000, max_price_per_unit=1000000000000),
    l2_gas=ResourceBounds(max_amount=300000000, max_price_per_unit=20000000000),
)


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value and name == "STRATEGY_ROUTER_ADDRESS" and settings.STRATEGY_ROUTER_ADDRESS:
        return settings.STRATEGY_ROUTER_ADDRESS
    if not value and name == "RISK_ENGINE_ADDRESS" and settings.RISK_ENGINE_ADDRESS:
        return settings.RISK_ENGINE_ADDRESS
    if not value and name == "BACKEND_WALLET_PRIVATE_KEY" and settings.BACKEND_WALLET_PRIVATE_KEY:
        return settings.BACKEND_WALLET_PRIVATE_KEY
    if not value and name == "BACKEND_WALLET_ADDRESS" and settings.BACKEND_WALLET_ADDRESS:
        return settings.BACKEND_WALLET_ADDRESS
    if not value:
        raise RuntimeError(f"Missing required env var: {name}. Set it in backend/.env or .env.sepolia.")
    return value


async def _init_backend_account(client: FullNodeClient, key_pair: KeyPair, chain_id: StarknetChainId, wallet_address: str) -> Account:
    """Initialize backend account (same as backend API routes)"""
    account = Account(
        address=int(wallet_address, 16),
        client=client,
        key_pair=key_pair,
        chain=chain_id,
    )
    # Set Cairo version (backend does this)
    from starknet_py.net.client_models import SierraContractClass
    try:
        contract_class = await client.get_class_at(
            contract_address=account.address,
            block_number="latest",
        )
        account._cairo_version = 1 if isinstance(contract_class, SierraContractClass) else 0
    except Exception:
        account._cairo_version = 1  # Default to Cairo 1
    return account


async def main() -> None:
    if BACKEND_ENV.exists():
        load_dotenv(BACKEND_ENV)

    router_addr = _require("STRATEGY_ROUTER_ADDRESS")
    risk_engine_addr = _require("RISK_ENGINE_ADDRESS")
    private_key = _require("BACKEND_WALLET_PRIVATE_KEY")
    wallet_address = _require("BACKEND_WALLET_ADDRESS")
    
    network = settings.STARKNET_NETWORK.lower()
    chain_id = StarknetChainId.SEPOLIA if network == "sepolia" else StarknetChainId.MAINNET
    key_pair = KeyPair.from_private_key(int(private_key, 16))

    if not STRATEGY_ROUTER_CLASS.exists():
        raise RuntimeError(f"Missing ABI file: {STRATEGY_ROUTER_CLASS}")

    with STRATEGY_ROUTER_CLASS.open("r", encoding="utf-8") as f:
        abi = json.load(f).get("abi")

    if not abi:
        raise RuntimeError("StrategyRouter ABI not found in contract_class JSON.")

    print("🔧 Setting StrategyRouter risk_engine address...")
    print(f"  StrategyRouter: {router_addr}")
    print(f"  RiskEngine:     {risk_engine_addr}")
    print(f"  Signer:         {wallet_address}")
    print(f"  Network:        {network}")

    # Use backend's RPC utilities (handles compatibility automatically)
    rpc_urls = get_rpc_urls()
    print(f"  RPC URLs:       {len(rpc_urls)} configured")

    # Use with_rpc_fallback (same pattern as backend)
    async def _set_risk_engine(client: FullNodeClient, rpc_url: str):
        account = await _init_backend_account(client, key_pair, chain_id, wallet_address)
        
        # Get nonce with fallback (same as backend)
        try:
            nonce = await account.get_nonce(block_number="pending")
        except Exception:
            nonce = await account.get_nonce(block_number="latest")
        
        print(f"  Using nonce: {nonce} (via {rpc_url})")
        
        # Use account.execute_v3 with Call object (same as backend)
        selector = get_selector_from_name("set_risk_engine")
        call = Call(
            to_addr=int(router_addr, 16),
            selector=selector,
            calldata=[int(risk_engine_addr, 16)]
        )
        
        invocation = await account.execute_v3(
            calls=[call],
            nonce=nonce,
            resource_bounds=DEFAULT_RESOURCE_BOUNDS,
        )
        
        tx_hash_val = getattr(invocation, "transaction_hash", None) or getattr(invocation, "hash", None)
        tx_hash = hex(tx_hash_val) if tx_hash_val is not None else str(invocation)
        print(f"✅ Transaction submitted: {tx_hash}")
        print(f"   Waiting for confirmation...")
        
        # Wait for transaction (with timeout)
        await client.wait_for_tx(tx_hash_val, check_interval=2, retries=60)
        
        print("✅ Transaction confirmed")
        print(f"✅ RiskEngine v4 is now authorized to call StrategyRouter.update_allocation()")
        return tx_hash

    try:
        result, used_rpc = await with_rpc_fallback(_set_risk_engine, urls=rpc_urls)
        print(f"\n✅ Success via {used_rpc}")
        print(f"   Transaction: {result}")
    except Exception as e:
        print(f"\n❌ All RPC attempts failed: {e}")
        print("\n💡 Alternative: Use sncast (recommended from dev log):")
        print(f"   sncast --account deployer invoke \\")
        print(f"     --contract-address {router_addr} \\")
        print(f"     --function set_risk_engine \\")
        print(f"     --arguments {risk_engine_addr} \\")
        print(f"     --network {network}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
