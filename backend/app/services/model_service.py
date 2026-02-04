"""
Model Service
Calculates model hashes and manages model versions.
Stage 3A: get_model_params / set_model_params (RiskEngine parameterized formula).
"""
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _load_risk_engine_abi() -> list:
    """Load RiskEngine ABI for get_model_params / set_model_params (Stage 3A)."""
    backend_dir = Path(__file__).resolve().parent.parent.parent
    repo_root = backend_dir.parent
    abi_path = repo_root / "contracts" / "target" / "dev" / "obsqra_contracts_RiskEngine.contract_class.json"
    if not abi_path.exists():
        raise FileNotFoundError(f"RiskEngine ABI not found at {abi_path}")
    payload = json.loads(abi_path.read_text())
    return payload.get("abi", [])


async def get_model_params(version: int) -> dict[str, Any]:
    """
    Get parameterized model params from RiskEngine contract (Stage 3A).
    Returns dict with keys: w_utilization, w_volatility, w_liquidity_0..3, w_audit, w_age, age_cap_days, clamp_min, clamp_max.
    """
    from app.config import get_settings
    from app.utils.rpc import get_rpc_urls, with_rpc_fallback
    from starknet_py.contract import Contract
    from starknet_py.net.full_node_client import FullNodeClient

    settings = get_settings()
    if not getattr(settings, "PARAMETERIZED_MODEL_ENABLED", False):
        return _default_model_params()

    abi = _load_risk_engine_abi()
    rpc_urls = get_rpc_urls()
    for url in rpc_urls:
        try:
            client = FullNodeClient(node_url=url)
            contract = Contract(
                address=int(settings.RISK_ENGINE_ADDRESS, 16),
                abi=abi,
                provider=client,
            )
            result = await contract.functions["get_model_params"].call(version)
            # Result is a named tuple or tuple of 11 felt252s in order
            if hasattr(result, "as_tuple"):
                t = result.as_tuple()
            elif isinstance(result, (list, tuple)):
                t = tuple(result)
            else:
                t = (result,)
            if len(t) >= 11:
                return {
                    "w_utilization": t[0],
                    "w_volatility": t[1],
                    "w_liquidity_0": t[2],
                    "w_liquidity_1": t[3],
                    "w_liquidity_2": t[4],
                    "w_liquidity_3": t[5],
                    "w_audit": t[6],
                    "w_age": t[7],
                    "age_cap_days": t[8],
                    "clamp_min": t[9],
                    "clamp_max": t[10],
                }
            return _default_model_params()
        except Exception as e:
            logger.warning("get_model_params RPC attempt failed: %s", e)
            continue
    return _default_model_params()


def _default_model_params() -> dict[str, Any]:
    """Default (Stage 2) formula params."""
    return {
        "w_utilization": 25,
        "w_volatility": 40,
        "w_liquidity_0": 0,
        "w_liquidity_1": 5,
        "w_liquidity_2": 15,
        "w_liquidity_3": 30,
        "w_audit": 3,
        "w_age": 10,
        "age_cap_days": 730,
        "clamp_min": 5,
        "clamp_max": 95,
    }


def set_model_params(version: int, params: dict[str, Any]) -> str:
    """
    Set parameterized model params on RiskEngine (Stage 3A). Owner only.
    Returns message: use admin script (sncast) or backend wallet to invoke set_model_params.
    """
    from app.config import get_settings
    settings = get_settings()
    if not getattr(settings, "PARAMETERIZED_MODEL_ENABLED", False):
        return "PARAMETERIZED_MODEL_ENABLED is false; enable in config to use set_model_params."
    # Actual invocation requires owner wallet; direct from backend is optional later.
    return "Use admin script (e.g. sncast invoke RiskEngine set_model_params) or add backend wallet invocation in a dedicated admin endpoint."


class ModelService:
    """Service for calculating and managing model hashes"""
    
    def __init__(self):
        # Path to risk_engine.cairo from backend directory
        backend_dir = Path(__file__).parent.parent.parent
        self.model_code_path = backend_dir.parent / "contracts" / "src" / "risk_engine.cairo"
    
    def calculate_model_hash(self, model_code: Optional[str] = None) -> str:
        """
        Calculate hash of the risk model code
        
        Args:
            model_code: Optional model code string. If None, reads from risk_engine.cairo
            
        Returns:
            Hex string of model hash
        """
        if model_code is None:
            try:
                with open(self.model_code_path, "r") as f:
                    model_code = f.read()
            except Exception as e:
                logger.error(f"Could not read model code: {e}")
                # Fallback: hash a placeholder
                model_code = "risk_engine_v1"
        
        # Calculate SHA-256 hash
        hash_obj = hashlib.sha256(model_code.encode('utf-8'))
        model_hash_hex = hash_obj.hexdigest()
        
        logger.info(f"Model hash calculated: {model_hash_hex[:16]}...")
        return model_hash_hex
    
    def get_model_hash_felt252(self, model_code: Optional[str] = None) -> int:
        """
        Get model hash as felt252 (for Cairo contracts)
        
        Args:
            model_code: Optional model code string
            
        Returns:
            Integer representation of hash (modulo felt252 max)
        """
        hash_hex = self.calculate_model_hash(model_code)
        # Convert to int, then modulo felt252 max
        hash_int = int(hash_hex, 16)
        MAX_FELT252 = 2**251 - 1
        if hash_int > MAX_FELT252:
            hash_int = hash_int % (MAX_FELT252 + 1)
        return hash_int
    
    def get_current_model_version(self) -> dict:
        """
        Get current model version info
        
        Returns:
            Dict with version, hash, description
        """
        model_hash = self.calculate_model_hash()
        model_hash_felt = self.get_model_hash_felt252()
        
        return {
            "version": "1.0.0",
            "version_felt": 0x010000,  # v1.0.0 as felt252
            "model_hash": model_hash,
            "model_hash_felt": model_hash_felt,
            "description": "Initial risk scoring model",
            "code_path": str(self.model_code_path)
        }


def get_model_service() -> ModelService:
    """Get ModelService instance"""
    return ModelService()
