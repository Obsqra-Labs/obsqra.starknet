#!/usr/bin/env python3
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ENV = ROOT / "backend" / ".env"
STRATEGY_ROUTER_CLASS = ROOT / "contracts" / "target" / "dev" / "obsqra_contracts_StrategyRouterV35.contract_class.json"


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


async def main() -> None:
    if BACKEND_ENV.exists():
        load_dotenv(BACKEND_ENV)

    rpc_url = _require("STARKNET_RPC_URL")
    router_addr = _require("STRATEGY_ROUTER_ADDRESS")
    risk_engine_addr = _require("RISK_ENGINE_ADDRESS")
    wallet_addr = _require("BACKEND_WALLET_ADDRESS")
    private_key = _require("BACKEND_WALLET_PRIVATE_KEY")
    rpc_candidates = [rpc_url]
    rpc_list = os.getenv("STARKNET_RPC_URLS")
    if rpc_list:
        rpc_candidates = [r.strip() for r in rpc_list.split(",") if r.strip()] + rpc_candidates

    if not STRATEGY_ROUTER_CLASS.exists():
        raise RuntimeError(f"Missing ABI file: {STRATEGY_ROUTER_CLASS}")

    with STRATEGY_ROUTER_CLASS.open("r", encoding="utf-8") as f:
        abi = json.load(f).get("abi")

    if not abi:
        raise RuntimeError("StrategyRouter ABI not found in contract_class JSON.")

    print("🔧 Syncing StrategyRouter risk_engine...")
    print(f"  StrategyRouter: {router_addr}")
    print(f"  RiskEngine:     {risk_engine_addr}")
    print(f"  Signer:         {wallet_addr}")

    key_pair = KeyPair.from_private_key(int(private_key, 16))
    last_error = None

    for candidate in rpc_candidates:
        try:
            client = FullNodeClient(node_url=candidate)
            account = Account(
                address=int(wallet_addr, 16),
                client=client,
                key_pair=key_pair,
                chain=StarknetChainId.SEPOLIA,
            )
            contract = Contract(
                address=int(router_addr, 16),
                abi=abi,
                provider=account,
            )

            nonce = await account.get_nonce(block_number="latest")
            invocation = await contract.functions["set_risk_engine"].invoke_v3(
                int(risk_engine_addr, 16),
                nonce=nonce,
            )
            tx_hash = hex(invocation.hash)
            print(f"✅ Submitted tx via {candidate}: {tx_hash}")
            await client.wait_for_tx(invocation.hash)
            print("✅ Transaction confirmed")
            return
        except Exception as exc:
            last_error = exc
            print(f"⚠️  RPC failed: {candidate} → {exc}")

    raise RuntimeError(f"All RPC attempts failed: {last_error}")


if __name__ == "__main__":
    asyncio.run(main())
