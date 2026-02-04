"""
Model Registry Service
Read/write access to the on-chain ModelRegistry contract.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping, SierraContractClass

from app.config import get_settings
from app.utils.rpc import get_rpc_urls, with_rpc_fallback
from app.services.model_service import ModelService

logger = logging.getLogger(__name__)
settings = get_settings()

# Conservative bounds for a lightweight register call.
# Increased L1 data gas price to handle current network conditions
DEFAULT_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=50000, max_price_per_unit=100000000000000),
    l1_data_gas=ResourceBounds(max_amount=50000, max_price_per_unit=150000000000000),  # 150 trillion - match Integrity/Sepolia L1 data gas
    l2_gas=ResourceBounds(max_amount=5000000, max_price_per_unit=20000000000),
)

_MODEL_REGISTRY_ABI: Optional[list] = None


def _load_model_registry_abi() -> list:
    global _MODEL_REGISTRY_ABI
    if _MODEL_REGISTRY_ABI is not None:
        return _MODEL_REGISTRY_ABI

    repo_root = Path(__file__).resolve().parents[3]
    abi_path = repo_root / "contracts" / "target" / "dev" / "obsqra_contracts_ModelRegistry.contract_class.json"
    if not abi_path.exists():
        raise FileNotFoundError(f"ModelRegistry ABI not found at {abi_path}")

    import json
    payload = json.loads(abi_path.read_text())
    _MODEL_REGISTRY_ABI = payload.get("abi", [])
    return _MODEL_REGISTRY_ABI


def _normalize_model_version(raw: Any) -> Optional[dict]:
    """Normalize ModelVersion output into a simple dict."""
    if raw is None:
        return None

    # Option type (is_some, value)
    if isinstance(raw, (list, tuple)) and len(raw) == 2 and isinstance(raw[0], int):
        if raw[0] == 0:
            return None
        return _normalize_model_version(raw[1])

    # Unwrap single-item tuple
    if isinstance(raw, (list, tuple)) and len(raw) == 1:
        return _normalize_model_version(raw[0])

    if isinstance(raw, dict):
        version = raw.get("version")
        model_hash = raw.get("model_hash")
        deployed_at = raw.get("deployed_at")
        description = raw.get("description", "")
        is_active = raw.get("is_active", False)
        return {
            "version": int(version) if version is not None else 0,
            "model_hash": int(model_hash) if model_hash is not None else 0,
            "deployed_at": int(deployed_at) if deployed_at is not None else 0,
            "description": _coerce_description(description),
            "is_active": bool(is_active),
        }

    # Dataclass-like object
    if hasattr(raw, "version"):
        return {
            "version": int(getattr(raw, "version", 0)),
            "model_hash": int(getattr(raw, "model_hash", 0)),
            "deployed_at": int(getattr(raw, "deployed_at", 0)),
            "description": _coerce_description(getattr(raw, "description", "")),
            "is_active": bool(getattr(raw, "is_active", False)),
        }

    # Tuple from ABI: (version, model_hash, deployed_at, description, is_active)
    if isinstance(raw, (list, tuple)) and len(raw) == 5:
        version, model_hash, deployed_at, description, is_active = raw
        return {
            "version": int(version),
            "model_hash": int(model_hash),
            "deployed_at": int(deployed_at),
            "description": _coerce_description(description),
            "is_active": bool(is_active),
        }

    logger.warning("Unexpected model version format: %s", type(raw))
    return None


def _coerce_description(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except Exception:
            return value.hex()
    return str(value)


async def _init_backend_account(client: FullNodeClient, key_pair: KeyPair, chain_id: StarknetChainId) -> Account:
    account = Account(
        address=int(settings.BACKEND_WALLET_ADDRESS, 16),
        client=client,
        key_pair=key_pair,
        chain=chain_id,
    )
    try:
        contract_class = await client.get_class_at(
            contract_address=account.address,
            block_number="latest",
        )
        account._cairo_version = 1 if isinstance(contract_class, SierraContractClass) else 0
    except Exception as err:
        account._cairo_version = 1
        logger.warning("⚠️ Could not resolve account Cairo version; defaulting to Cairo 1: %s", err)
    return account


class ModelRegistryService:
    """Service for ModelRegistry contract interactions."""

    def __init__(self):
        if not settings.MODEL_REGISTRY_ADDRESS:
            raise ValueError("MODEL_REGISTRY_ADDRESS is not configured")
        self.registry_address = int(settings.MODEL_REGISTRY_ADDRESS, 16)
        self.rpc_urls = get_rpc_urls()
        self.model_service = ModelService()
        self.chain_id = StarknetChainId.SEPOLIA if settings.STARKNET_NETWORK.lower() == "sepolia" else StarknetChainId.MAINNET

    async def _get_contract(self, client: FullNodeClient, provider_override=None) -> Contract:
        abi = _load_model_registry_abi()
        return Contract(
            address=self.registry_address,
            abi=abi,
            provider=provider_override or client,
        )

    async def get_current_model(self) -> Optional[dict]:
        async def _call(client: FullNodeClient, _rpc_url: str):
            contract = await self._get_contract(client)
            return await contract.functions["get_current_model"].call(block_number="latest")

        result, _ = await with_rpc_fallback(_call, urls=self.rpc_urls)
        return _normalize_model_version(result)

    async def get_model_version(self, version_felt: int) -> Optional[dict]:
        async def _call(client: FullNodeClient, _rpc_url: str):
            contract = await self._get_contract(client)
            return await contract.functions["get_model_version"].call(version_felt, block_number="latest")

        result, _ = await with_rpc_fallback(_call, urls=self.rpc_urls)
        return _normalize_model_version(result)

    async def get_model_history(self) -> list[int]:
        async def _call(client: FullNodeClient, _rpc_url: str):
            contract = await self._get_contract(client)
            return await contract.functions["get_model_history"].call(block_number="latest")

        result, _ = await with_rpc_fallback(_call, urls=self.rpc_urls)
        # Result may be a list of felts or a tuple with one list.
        if isinstance(result, (list, tuple)) and len(result) == 1 and isinstance(result[0], list):
            return [int(v) for v in result[0]]
        if isinstance(result, list):
            return [int(v) for v in result]
        return []

    async def register_model_version(
        self,
        version_felt: int,
        model_hash_felt: int,
        description: str,
    ) -> int:
        key_pair = KeyPair.from_private_key(int(settings.BACKEND_WALLET_PRIVATE_KEY, 16))

        async def _invoke(client: FullNodeClient, _rpc_url: str):
            account = await _init_backend_account(client, key_pair, self.chain_id)
            contract = await self._get_contract(client, provider_override=account)
            nonce = await account.get_nonce(block_number="latest")
            invoke_result = await contract.functions["register_model_version"].invoke_v3(
                version_felt,
                model_hash_felt,
                description,
                resource_bounds=DEFAULT_RESOURCE_BOUNDS,
                nonce=nonce,
            )
            # Wait for acceptance so downstream reads see the new model.
            await invoke_result.wait_for_acceptance(check_interval=1, retries=60)
            return invoke_result

        result, _ = await with_rpc_fallback(_invoke, urls=self.rpc_urls)
        return int(result.hash)

    def get_local_model_info(self) -> dict:
        return self.model_service.get_current_model_version()


def get_model_registry_service() -> ModelRegistryService:
    return ModelRegistryService()
