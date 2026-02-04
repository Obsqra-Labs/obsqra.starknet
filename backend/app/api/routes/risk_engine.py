"""
Risk Engine API endpoints for on-chain risk calculations
"""
import asyncio
import time
import tempfile
import subprocess
import shutil
import os
import json
from datetime import datetime
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import logging
from sqlalchemy.orm import Session
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping, SierraContractClass
from starknet_py.net.models import StarknetChainId
from app.config import get_settings
from app.db.session import get_db
from app.models import ProofJob, ProofStatus
from app.services.risk_model import calculate_risk_score as calc_risk_score
from app.services.zkml_service import get_zkml_service
from app.services.zkml_proof_service import ZkmlProofService, ZkmlProofConfig
from app.services.stone_prover_service import StoneProverService
from app.services.proof_loader import serialize_stone_proof
from app.workers.sharp_worker import submit_proof_to_sharp
from app.services.integrity_service import get_integrity_service
from app.services.atlantic_service import get_atlantic_service
from app.services.model_service import get_model_service, get_model_params
from app.workers.atlantic_worker import enqueue_atlantic_status_check
from app.services.protocol_metrics_service import get_protocol_metrics_service
from app.services.market_data_service import get_market_data_service
from app.utils.rpc import with_rpc_fallback, get_rpc_urls, is_retryable_rpc_error

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()
_RISK_ENGINE_ABI = None
_RISK_ENGINE_ONCHAIN_INPUTS: Optional[int] = None

# Manual resource bounds to avoid estimate_fee (which uses unsupported block tags on some RPCs).
# L1 data gas price increased to handle current network conditions
DEFAULT_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=30000, max_price_per_unit=100000000000000),
    l1_data_gas=ResourceBounds(max_amount=30000, max_price_per_unit=150000000000000),  # 150 trillion - Sepolia L1 data gas can exceed 50T (error 55: resource bounds not satisfied)
    l2_gas=ResourceBounds(max_amount=5000000, max_price_per_unit=20000000000),
)


def _load_risk_engine_abi() -> list:
    global _RISK_ENGINE_ABI
    if _RISK_ENGINE_ABI is not None:
        return _RISK_ENGINE_ABI

    repo_root = Path(__file__).resolve().parents[4]
    abi_path = repo_root / "contracts" / "target" / "dev" / "obsqra_contracts_RiskEngine.contract_class.json"
    if not abi_path.exists():
        raise FileNotFoundError(f"RiskEngine ABI not found at {abi_path}")

    import json
    payload = json.loads(abi_path.read_text())
    _RISK_ENGINE_ABI = payload.get("abi", [])
    return _RISK_ENGINE_ABI


async def _get_risk_engine_contract(client: FullNodeClient) -> Contract:
    abi = _load_risk_engine_abi()
    return Contract(
        address=int(settings.RISK_ENGINE_ADDRESS, 16),
        abi=abi,
        provider=client,
    )


async def _get_risk_engine_onchain_inputs(client: FullNodeClient) -> Optional[int]:
    """Detect on-chain RiskEngine signature (legacy 2 inputs vs proof-gated v4 vs v4 with on-chain agent)."""
    global _RISK_ENGINE_ONCHAIN_INPUTS
    if _RISK_ENGINE_ONCHAIN_INPUTS is not None:
        return _RISK_ENGINE_ONCHAIN_INPUTS

    try:
        contract_class = await client.get_class_at(
            contract_address=int(settings.RISK_ENGINE_ADDRESS, 16),
            block_number="latest",
        )
        abi = contract_class.abi
        if isinstance(abi, str):
            abi = json.loads(abi)
        for item in abi or []:
            if item.get("type") == "function" and item.get("name") == "propose_and_execute_allocation":
                input_count = len(item.get("inputs", []))
                _RISK_ENGINE_ONCHAIN_INPUTS = input_count
                logger.info(f"📋 RiskEngine ABI detected: {input_count} inputs for propose_and_execute_allocation")
                # Log detailed ABI info for debugging
                inputs = item.get("inputs", [])
                for idx, inp in enumerate(inputs):
                    logger.info(f"   Input {idx}: {inp.get('name', 'unnamed')} ({inp.get('type', 'unknown')})")
                return _RISK_ENGINE_ONCHAIN_INPUTS
    except Exception as err:
        logger.warning("⚠️ Could not inspect on-chain RiskEngine ABI; defaulting to v4 with on-chain agent calldata. %s", err)

    return None


def _load_demo_integrity_calldata(prefer_profile: str = "cairo1") -> tuple[Optional[list[int]], Optional[str]]:
    """
    Load precomputed Integrity calldata (demo proof) and prefix verifier config felts.

    Returns (calldata, profile) or (None, None) if not available.
    """
    profile = prefer_profile.strip().lower()
    repo_root = Path(__file__).resolve().parents[4]

    if profile == "cairo1":
        default_path = repo_root / "backend" / "data" / "zkml_demo_cairo1.calldata"
        calldata_path = settings.ZKML_PROOF_CALLDATA_PATH_CAIRO1 or settings.ZKML_PROOF_CALLDATA_PATH or str(default_path)
        memory_verification = "cairo1"
    else:
        default_path = repo_root / "backend" / "data" / "zkml_demo_cairo0.calldata"
        calldata_path = settings.ZKML_PROOF_CALLDATA_PATH_CAIRO0 or settings.ZKML_PROOF_CALLDATA_PATH or str(default_path)
        memory_verification = settings.INTEGRITY_MEMORY_VERIFICATION

    calldata_file = Path(calldata_path)
    if not calldata_file.exists():
        return None, None

    config = ZkmlProofConfig(
        proof_json_path=None,
        calldata_path=calldata_file,
        serializer_bin=Path(settings.INTEGRITY_PROOF_SERIALIZER_BIN) if settings.INTEGRITY_PROOF_SERIALIZER_BIN else None,
        layout=settings.INTEGRITY_LAYOUT,
        hasher=settings.INTEGRITY_HASHER,
        stone_version=settings.INTEGRITY_STONE_VERSION,
        memory_verification=memory_verification,
    )
    service = ZkmlProofService(integrity=get_integrity_service(), config=config)
    return service.load_calldata(), profile


def _verifier_config_from_settings(memory_verification: Optional[str] = None) -> dict:
    def _string_to_felt(value: str) -> int:
        return int.from_bytes(value.encode("ascii"), "big")

    mv = memory_verification or settings.INTEGRITY_MEMORY_VERIFICATION
    return {
        "layout": _string_to_felt(settings.INTEGRITY_LAYOUT),
        "hasher": _string_to_felt(settings.INTEGRITY_HASHER),
        "stone_version": _string_to_felt(settings.INTEGRITY_STONE_VERSION),
        "memory_verification": _string_to_felt(mv),
    }


def _string_to_felt(value: str) -> int:
    return int.from_bytes(value.encode("ascii"), "big")


def _resolve_cairo1_run_bin() -> str:
    candidates = [
        os.environ.get("CAIRO1_RUN_BIN"),
        "/opt/obsqra.starknet/cairo-vm/target/release/cairo1-run",
        "/opt/obsqra.starknet/cairo-vm/cairo1-run/target/release/cairo1-run",
        "cairo1-run",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if Path(candidate).is_absolute():
            if Path(candidate).exists():
                return candidate
        else:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
    raise FileNotFoundError(
        "cairo1-run binary not found. Build it with: "
        "cd /opt/obsqra.starknet/cairo-vm/cairo1-run && cargo build --release"
    )


def _resolve_cairo1_compile_bin() -> str:
    """Resolve cairo1-compile binary path (or scarb for Cairo 1 compilation)"""
    candidates = [
        os.environ.get("CAIRO1_COMPILE_BIN"),
        "/opt/obsqra.starknet/cairo-vm/target/release/cairo1-compile",
        "/opt/obsqra.starknet/cairo-vm/cairo1-compile/target/release/cairo1-compile",
        "cairo1-compile",
        "scarb",  # Scarb can compile Cairo 1 programs
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if Path(candidate).is_absolute():
            if Path(candidate).exists():
                return candidate
        else:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
    raise FileNotFoundError(
        "cairo1-compile not found. Set CAIRO1_COMPILE_BIN env var or install cairo-vm/scarb."
    )


def _resolve_cairo0_compile_bin() -> str:
    candidates = [
        os.environ.get("CAIRO_COMPILE_BIN"),
        "cairo-compile",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if Path(candidate).is_absolute():
            if Path(candidate).exists():
                return candidate
        else:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
    raise FileNotFoundError("cairo-compile binary not found in PATH.")


def _resolve_cairo0_run_bin() -> str:
    candidates = [
        os.environ.get("CAIRO_RUN_BIN"),
        "cairo-run",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if Path(candidate).is_absolute():
            if Path(candidate).exists():
                return candidate
        else:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
    raise FileNotFoundError("cairo-run binary not found in PATH.")


async def _stone_integrity_fact_for_metrics(
    jediswap_metrics: dict,
    ekubo_metrics: dict,
) -> tuple[Optional[int], Optional[str], Optional[str], Optional[str]]:
    """
    Generate a Stone proof for the Cairo1 risk example and register it with Integrity.
    Returns (fact_hash_int, proof_json_path, output_dir).
    """
    repo_root = Path(__file__).resolve().parents[4]
    output_dir = Path(tempfile.mkdtemp(prefix="risk_stone_"))
    trace_file = output_dir / "risk_trace.bin"
    memory_file = output_dir / "risk_memory.bin"
    public_input_file = output_dir / "risk_public.json"
    private_input_file = output_dir / "risk_private.json"
    proof_output_file = output_dir / "risk_proof.json"

    use_cairo1 = settings.INTEGRITY_MEMORY_VERIFICATION == "cairo1"
    if use_cairo1:
        cairo1_run = _resolve_cairo1_run_bin()
        cairo_program = repo_root / "verification" / "risk_example.cairo"
        if not cairo_program.exists():
            raise FileNotFoundError(f"risk_example.cairo not found at {cairo_program}")

        arg_values = " ".join(
            str(x)
            for x in [
                jediswap_metrics["utilization"],
                jediswap_metrics["volatility"],
                jediswap_metrics["liquidity"],
                jediswap_metrics["audit_score"],
                jediswap_metrics["age_days"],
                ekubo_metrics["utilization"],
                ekubo_metrics["volatility"],
                ekubo_metrics["liquidity"],
                ekubo_metrics["audit_score"],
                ekubo_metrics["age_days"],
            ]
        )
        args = f"[{arg_values}]"

        cmd = [
            cairo1_run,
            str(cairo_program),
            "--layout",
            settings.INTEGRITY_LAYOUT,
            "--proof_mode",
            "--trace_file",
            str(trace_file),
            "--memory_file",
            str(memory_file),
            "--air_public_input",
            str(public_input_file),
            "--air_private_input",
            str(private_input_file),
            "--print_output",
            "--args",
            args,
        ]

        # Use configurable timeout (increased for recursive layout)
        cairo_timeout = getattr(settings, "INTEGRITY_CAIRO_TIMEOUT", 300)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=cairo_timeout,
            check=True,
            cwd=str(repo_root / "cairo-vm" / "cairo1-run"),
        )
        if proc.stdout:
            logger.info("cairo1-run output: %s", proc.stdout.strip().splitlines()[-1])
    else:
        cairo_compile = _resolve_cairo0_compile_bin()
        cairo_run = _resolve_cairo0_run_bin()
        cairo_program = repo_root / "verification" / "risk_example_cairo0.cairo"
        if not cairo_program.exists():
            raise FileNotFoundError(f"risk_example_cairo0.cairo not found at {cairo_program}")

        compiled_program = output_dir / "risk_compiled.json"
        program_input = {
            "jedi_utilization": jediswap_metrics["utilization"],
            "jedi_volatility": jediswap_metrics["volatility"],
            "jedi_liquidity": jediswap_metrics["liquidity"],
            "jedi_audit_score": jediswap_metrics["audit_score"],
            "jedi_age_days": jediswap_metrics["age_days"],
            "ekubo_utilization": ekubo_metrics["utilization"],
            "ekubo_volatility": ekubo_metrics["volatility"],
            "ekubo_liquidity": ekubo_metrics["liquidity"],
            "ekubo_audit_score": ekubo_metrics["audit_score"],
            "ekubo_age_days": ekubo_metrics["age_days"],
        }
        program_input_file = output_dir / "risk_program_input.json"
        program_input_file.write_text(json.dumps(program_input))

        compile_cmd = [
            cairo_compile,
            str(cairo_program),
            "--output",
            str(compiled_program),
            "--proof_mode",
        ]
        subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )

        run_cmd = [
            cairo_run,
            "--program",
            str(compiled_program),
            "--layout",
            settings.INTEGRITY_LAYOUT,
            "--proof_mode",
            "--program_input",
            str(program_input_file),
            "--trace_file",
            str(trace_file),
            "--memory_file",
            str(memory_file),
            "--air_public_input",
            str(public_input_file),
            "--air_private_input",
            str(private_input_file),
            "--print_output",
        ]
        # Use configurable timeout (increased for recursive layout)
        cairo_timeout = getattr(settings, "INTEGRITY_CAIRO_TIMEOUT", 300)
        proc = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            timeout=cairo_timeout,
            check=True,
        )
        if proc.stdout:
            logger.info("cairo-run output: %s", proc.stdout.strip().splitlines()[-1])
        
        # Note: We cannot remove ecdsa segment from public input here because Stone prover
        # requires it to match the trace. We'll remove it from the proof JSON after Stone generates it.

    # HARD LOG: Dump active settings at proof generation start
    logger.info("=" * 80)
    logger.info("🔍 PROOF GENERATION - ACTIVE SETTINGS")
    logger.info("=" * 80)
    logger.info(f"INTEGRITY_LAYOUT: {settings.INTEGRITY_LAYOUT}")
    logger.info(f"INTEGRITY_STONE_VERSION: {settings.INTEGRITY_STONE_VERSION}")
    logger.info(f"INTEGRITY_HASHER: {settings.INTEGRITY_HASHER}")
    logger.info(f"INTEGRITY_MEMORY_VERIFICATION: {settings.INTEGRITY_MEMORY_VERIFICATION}")
    logger.info(f"INTEGRITY_CAIRO_TIMEOUT: {getattr(settings, 'INTEGRITY_CAIRO_TIMEOUT', 300)}s")
    logger.info("=" * 80)
    
    stone = StoneProverService()
    # Use configurable timeout for Stone prover (increased for recursive layout)
    stone_timeout = getattr(settings, "INTEGRITY_CAIRO_TIMEOUT", 300)
    stone_result = await stone.generate_proof(
        private_input_file=str(private_input_file),
        public_input_file=str(public_input_file),
        proof_output_file=str(proof_output_file),
        timeout_seconds=stone_timeout,
    )
    if not stone_result.success:
        raise RuntimeError(stone_result.error or "Stone prover failed")
    
        # HARD LOG: Dump proof parameters after generation
    if proof_output_file.exists():
        with open(proof_output_file) as f:
            proof_data = json.load(f)
        
        logger.info("=" * 80)
        logger.info("🔍 PROOF GENERATION - PROOF PARAMETERS")
        logger.info("=" * 80)
        
        # Extract public input
        public_input = proof_data.get("public_input", {})
        proof_layout = public_input.get("layout")
        n_steps = public_input.get("n_steps")
        logger.info(f"Proof Layout: {proof_layout}")
        logger.info(f"Proof n_steps: {n_steps}")
        
        # Extract proof parameters - read from proof_parameters first (Stone JSON structure), fallback to config
        proof_params = proof_data.get("proof_parameters", {})
        if not proof_params:
            proof_params = proof_data.get("config", {})
            logger.warning("⚠️  Proof JSON uses 'config' instead of 'proof_parameters' - may be wrong structure")
        
        stark = proof_params.get("stark", {})
        fri = stark.get("fri", {})
        logger.info(f"FRI step_list: {fri.get('fri_step_list')}")
        logger.info(f"FRI last_layer_degree_bound: {fri.get('last_layer_degree_bound')}")
        logger.info(f"FRI n_queries: {fri.get('n_queries')}")
        logger.info(f"FRI log_n_cosets: {stark.get('log_n_cosets')}")
        logger.info(f"FRI proof_of_work_bits: {fri.get('proof_of_work_bits')}")
        
        # Extract channel/commitment hash info
        channel_hash = proof_params.get("channel_hash")
        commitment_hash = proof_params.get("commitment_hash")
        pow_hash = proof_params.get("pow_hash")
        logger.info(f"Channel hash: {channel_hash}")
        logger.info(f"Commitment hash: {commitment_hash}")
        logger.info(f"Pow hash: {pow_hash}")
        
        # Extract n_verifier_friendly_commitment_layers
        n_verifier_friendly = proof_params.get("n_verifier_friendly_commitment_layers")
        logger.info(f"n_verifier_friendly_commitment_layers: {n_verifier_friendly}")
        logger.info(f"Verifier friendly channel updates: {proof_params.get('verifier_friendly_channel_updates')}")
        logger.info(f"Verifier friendly commitment hash: {proof_params.get('verifier_friendly_commitment_hash')}")
        
        # Extract FRI parameters
        logger.info(f"FRI Parameters (from Stone): {stone_result.fri_parameters}")
        
        logger.info("=" * 80)
        
        # CRITICAL: Verify ALL verifier config fields match Integrity expectations
        # This prevents layout/version/hasher mismatch errors
        expected_layout = settings.INTEGRITY_LAYOUT
        expected_stone_version = settings.INTEGRITY_STONE_VERSION
        expected_hasher = settings.INTEGRITY_HASHER
        expected_memory_verification = settings.INTEGRITY_MEMORY_VERIFICATION
        
        mismatches = []
        if proof_layout != expected_layout:
            mismatches.append(f"layout: proof='{proof_layout}' vs expected='{expected_layout}'")
        
        # Note: stone_version and hasher are not in proof JSON, they're in calldata prefix
        # But we log them for comparison
        
        if mismatches:
            error_msg = (
                f"Verifier config mismatch detected:\n"
                f"  {chr(10).join('  - ' + m for m in mismatches)}\n"
                f"Expected verifier config:\n"
                f"  - layout: {expected_layout}\n"
                f"  - stone_version: {expected_stone_version}\n"
                f"  - hasher: {expected_hasher}\n"
                f"  - memory_verification: {expected_memory_verification}\n"
                f"This will cause verification errors (Invalid builtin, OODS, etc.).\n"
                f"Check backend/.env settings and ensure cairo-run uses matching --layout."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info(f"✅ Verifier config match: proof layout='{proof_layout}' matches expected='{expected_layout}'")
        logger.info(f"   (stone_version={expected_stone_version}, hasher={expected_hasher}, memory={expected_memory_verification} will be in calldata)")

    serializer_bin = Path(
        settings.INTEGRITY_PROOF_SERIALIZER_BIN
        or "/opt/obsqra.starknet/integrity/target/release/proof_serializer"
    )
    calldata_body = serialize_stone_proof(proof_output_file, serializer_bin)
    calldata = [
        _string_to_felt(settings.INTEGRITY_LAYOUT),  # Use config layout instead of hardcoded "small"
        _string_to_felt(settings.INTEGRITY_HASHER),
        _string_to_felt(settings.INTEGRITY_STONE_VERSION),
        _string_to_felt(settings.INTEGRITY_MEMORY_VERIFICATION),
        *calldata_body,
    ]

    integrity = get_integrity_service()
    try:
        fact_hash_int, _, _ = await integrity.register_calldata_and_get_fact(calldata)
    except RuntimeError as e:
        # Re-raise with better context - this will be caught by caller
        raise RuntimeError(f"Stone proof registration failed: {str(e)}") from e
    return fact_hash_int, str(proof_output_file), str(output_dir), stone_result.proof_hash


def _build_integrity_error_report(
    *,
    reason: str,
    proof,
    fact_hash: Optional[str],
    verification_error: Optional[str],
    integrity,
    verifier_struct: Optional[dict],
    proof_struct: Optional[dict],
    verifier_bytes: Optional[bytes],
    proof_bytes: Optional[bytes],
    luminair_use_mock: bool,
) -> dict:
    return {
        "stage": "integrity_verification",
        "reason": reason,
        "proof_hash": getattr(proof, "proof_hash", None),
        "fact_hash": fact_hash,
        "verification_error": verification_error,
        "luminair_use_mock": luminair_use_mock,
        "verifier_payload_format": getattr(proof, "verifier_payload_format", None),
        "payload_presence": {
            "verifier_struct": bool(verifier_struct),
            "proof_struct": bool(proof_struct),
            "verifier_bytes_len": len(verifier_bytes) if verifier_bytes else 0,
            "proof_bytes_len": len(proof_bytes) if proof_bytes else 0,
        },
        "payload_paths": {
            "verifier_config_path": getattr(proof, "verifier_config_path", None),
            "stark_proof_path": getattr(proof, "stark_proof_path", None),
        },
        "integrity_registry_address": hex(integrity.verifier_address) if integrity else None,
        "next_step": (
            "Provide Integrity-compatible verifier_config + stark_proof JSON (or base64) "
            "Use Stone prover with proof_serializer for Integrity-compatible proofs."
        ),
    }


async def _init_backend_account(
    client: FullNodeClient,
    key_pair: KeyPair,
    network_chain: StarknetChainId,
) -> Account:
    account = Account(
        address=int(settings.BACKEND_WALLET_ADDRESS, 16),
        client=client,
        key_pair=key_pair,
        chain=network_chain,
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


async def _wait_for_receipt_raw(
    tx_hash: int | str,
    urls: list[str],
    timeout_sec: int = 120,
    poll_interval_sec: float = 2.0,
) -> dict:
    tx_hash_hex = hex(tx_hash) if isinstance(tx_hash, int) else str(tx_hash)

    async def _poll(client: FullNodeClient, _rpc_url: str):
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            try:
                receipt = await client._client.call(
                    method_name="getTransactionReceipt",
                    params={"transaction_hash": tx_hash_hex},
                )
                finality = receipt.get("status") or receipt.get("finality_status")
                execution = receipt.get("execution_status")
                if execution in {"REVERTED", "REJECTED"}:
                    reason = receipt.get("revert_reason") or receipt.get("rejection_reason") or ""
                    raise RuntimeError(f"Transaction {execution}: {reason}".strip())
                if finality in {"ACCEPTED_ON_L2", "ACCEPTED_ON_L1", "ACCEPTED", "FINALIZED"}:
                    return receipt
            except Exception as exc:  # noqa: BLE001 - retry on not-found
                msg = str(exc).lower()
                if "not found" not in msg and "unknown transaction" not in msg:
                    raise
            await asyncio.sleep(poll_interval_sec)
        raise TimeoutError("Timed out waiting for transaction acceptance")

    receipt, _ = await with_rpc_fallback(_poll, urls=urls)
    return receipt


class RiskMetricsRequest(BaseModel):
    """Request to calculate risk score"""
    utilization: int = Field(..., ge=0, le=10000, description="Utilization in basis points")
    volatility: int = Field(..., ge=0, le=10000, description="Volatility in basis points")
    liquidity: int = Field(..., ge=0, le=3, description="Liquidity category (0-3)")
    audit_score: int = Field(..., ge=0, le=100, description="Audit score (0-100)")
    age_days: int = Field(..., ge=0, description="Protocol age in days")


class AllocationRequest(BaseModel):
    """Request to calculate allocation"""
    jediswap_risk: int = Field(..., ge=5, le=95, description="JediSwap risk score")
    ekubo_risk: int = Field(..., ge=5, le=95, description="Ekubo risk score")
    jediswap_apy: int = Field(..., ge=0, description="JediSwap APY in basis points")
    ekubo_apy: int = Field(..., ge=0, description="Ekubo APY in basis points")


class RiskScoreResponse(BaseModel):
    """Risk score response"""
    score: int
    category: str
    description: str


class AllocationResponse(BaseModel):
    """Allocation response"""
    jediswap_pct: int
    ekubo_pct: int


@router.post("/calculate-risk", response_model=RiskScoreResponse, tags=["Risk Engine"])
async def calculate_risk_score(request: RiskMetricsRequest):
    """
    Calculate risk score for a protocol via Risk Engine contract
    
    Returns the calculated risk score (5-95) from on-chain Cairo contract
    """
    try:
        logger.info(f"📊 Calculating risk score via contract: {request.dict()}")
        
        async def _call_risk(client: FullNodeClient, _rpc_url: str):
            contract = await _get_risk_engine_contract(client)
            return await contract.functions["calculate_risk_score"].call(
                request.utilization,
                request.volatility,
                request.liquidity,
                request.audit_score,
                request.age_days,
                block_number="latest",
            )

        result, _ = await with_rpc_fallback(_call_risk)
        
        # Extract risk_score from result (felt252)
        risk_score = int(result[0])
        
        # Determine category
        if risk_score < 30:
            category = "low"
            description = "Low risk protocol - Safe for allocation"
        elif risk_score < 70:
            category = "medium"
            description = "Medium risk - Consider allocation limits"
        else:
            category = "high"
            description = "High risk - Use small allocation only"
        
        logger.info(f"✅ Risk score from contract: {risk_score} ({category})")
        
        return RiskScoreResponse(
            score=risk_score,
            category=category,
            description=description
        )
        
    except Exception as e:
        logger.error(f"❌ Risk calculation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Risk calculation failed: {str(e)}"
        )


@router.get("/model-params/{version}", tags=["Risk Engine"])
async def get_model_params_endpoint(version: int = 0):
    """
    Get parameterized model params from RiskEngine (Stage 3A).
    Returns weights and clamp bounds for the given model version.
    """
    try:
        params = await get_model_params(version)
        return params
    except Exception as e:
        logger.warning("get_model_params failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate-allocation", response_model=AllocationResponse, tags=["Risk Engine"])
async def calculate_allocation(request: AllocationRequest):
    """
    Calculate optimal allocation across JediSwap and Ekubo via Risk Engine contract
    
    Returns allocation percentages in basis points (10000 = 100%) from on-chain Cairo contract
    
    NOTE: This is the legacy endpoint. For full on-chain orchestration, use /orchestrate-allocation
    """
    try:
        logger.info(f"📊 Calculating allocation via contract: {request.dict()}")
        
        async def _call_allocation(client: FullNodeClient, _rpc_url: str):
            contract = await _get_risk_engine_contract(client)
            return await contract.functions["calculate_allocation"].call(
                request.jediswap_risk,  # nostra_risk (mapped from jediswap)
                0,                       # zklend_risk (not used, set to 0)
                request.ekubo_risk,      # ekubo_risk
                request.jediswap_apy,    # nostra_apy (mapped from jediswap)
                0,                       # zklend_apy (not used, set to 0)
                request.ekubo_apy,       # ekubo_apy
                block_number="latest",
            )

        result, _ = await with_rpc_fallback(_call_allocation)
        
        # Extract allocation percentages from contract result
        # Contract returns ((nostra_pct, zklend_pct, ekubo_pct),) - nested tuple
        # We map nostra_pct -> jediswap_pct and ignore zklend_pct
        allocation_tuple = result[0]  # Get inner tuple
        jediswap_pct = int(allocation_tuple[0])  # nostra_pct maps to jediswap
        ekubo_pct = int(allocation_tuple[2])      # ekubo_pct
        
        logger.info(f"✅ Allocation from contract: JediSwap {jediswap_pct} bps, Ekubo {ekubo_pct} bps")
        
        return AllocationResponse(
            jediswap_pct=jediswap_pct,
            ekubo_pct=ekubo_pct
        )
        
    except Exception as e:
        logger.error(f"❌ Allocation calculation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Allocation calculation failed: {str(e)}"
        )


class ConstraintSignatureRequest(BaseModel):
    """User-signed constraint approval for on-chain agent"""
    signer: str  # Wallet address (ContractAddress as hex string)
    max_single: int
    min_diversification: int
    max_volatility: int
    min_liquidity: int
    signature_r: str  # ECDSA signature r (felt252 as hex string)
    signature_s: str  # ECDSA signature s (felt252 as hex string)
    timestamp: int  # Unix timestamp


class OrchestrationRequest(BaseModel):
    """Request for full on-chain orchestration"""
    jediswap_metrics: RiskMetricsRequest = Field(..., description="JediSwap protocol metrics")
    ekubo_metrics: RiskMetricsRequest = Field(..., description="Ekubo protocol metrics")
    constraint_signature: Optional[ConstraintSignatureRequest] = Field(None, description="User-signed constraint approval (optional)")


class OrchestrationResponse(BaseModel):
    """Response from orchestration - read-only decision data"""
    decision_id: int
    block_number: int
    timestamp: int
    jediswap_pct: int
    ekubo_pct: int
    jediswap_risk: int
    ekubo_risk: int
    jediswap_apy: int
    ekubo_apy: int
    rationale_hash: str
    strategy_router_tx: str  # Decision ID from contract (legacy)
    tx_hash: str = None  # Actual on-chain transaction hash
    message: str
    # Proof information
    proof_job_id: str = None
    proof_hash: str = None
    proof_status: str = None
    proof_error: Optional[str] = None


class ProposalResponse(BaseModel):
    """Response from proposal (proof + allocation preview, no execution)."""
    proposal_id: str
    block_number: Optional[int] = None
    timestamp: Optional[int] = None
    jediswap_pct: int
    ekubo_pct: int
    jediswap_risk: int
    ekubo_risk: int
    jediswap_apy: int
    ekubo_apy: int
    message: str
    proof_job_id: str
    proof_hash: str = None
    proof_status: str = None
    proof_error: Optional[str] = None
    proof_source: Optional[str] = None
    l2_verified_at: Optional[str] = None
    can_execute: bool = False


class ExecuteRequest(BaseModel):
    """Execute a verified proposal by proof job id."""
    proof_job_id: str


async def _create_proof_job(
    request: OrchestrationRequest,
    db: Session,
    snapshot: Optional[dict] = None,
    extra_metrics: Optional[dict] = None,
) -> tuple[ProofJob, dict, dict, Optional[str]]:
    """
    Generate Stone proof + verify via Integrity + store ProofJob.
    Returns (proof_job, zkml_jedi, zkml_ekubo, verification_error).
    """
    proof_start_time = time.time()
    stone_fact, stone_proof_path, stone_dir, stone_hash = await _stone_integrity_fact_for_metrics(
        request.jediswap_metrics.dict(),
        request.ekubo_metrics.dict(),
    )
    proof_generation_time = time.time() - proof_start_time

    if not stone_fact:
        # Try to get more detailed error from Integrity service
        error_detail = {
            "error": "Stone proof registration failed",
            "message": "No fact hash returned from Integrity registration. The proof was generated but could not be registered on-chain. Check Integrity contract address and function availability.",
            "strict_mode": True,
            "note": "This usually means the Integrity contract call failed (e.g., VERIFIER_NOT_FOUND, Invalid OODS, Invalid builtin). Verify the contract address and that verify_proof_full_and_register_fact function exists."
        }
        raise HTTPException(status_code=500, detail=error_detail)

    fact_hash = hex(stone_fact)
    proof_bytes = None
    proof_size_bytes = 0
    if stone_proof_path:
        proof_bytes = Path(stone_proof_path).read_bytes()
        proof_size_bytes = len(proof_bytes)

    proof_hash = stone_hash
    if not proof_hash and proof_bytes:
        import hashlib
        proof_hash = f"0x{hashlib.sha256(proof_bytes).hexdigest()}"

    integrity = get_integrity_service()
    l2_verified = await integrity.verify_proof_on_l2(fact_hash, is_mocked=False)
    l2_verified_at = datetime.utcnow() if l2_verified else None
    verification_error = None if l2_verified else "Integrity verification failed (strict mode - real FactRegistry only)"

    if not l2_verified:
        error_report = {
            "stage": "integrity_verification",
            "reason": "stone_verification_failed",
            "fact_hash": fact_hash,
            "verification_error": verification_error,
            "integrity_registry_address": hex(integrity.verifier_address),
        }
        raise HTTPException(status_code=400, detail=error_report)

    # Compute deterministic risk scores for display
    jediswap_risk, jediswap_components = calc_risk_score(request.jediswap_metrics.dict())
    ekubo_risk, ekubo_components = calc_risk_score(request.ekubo_metrics.dict())

    # zkML demo inference (tiny linear model)
    zkml = get_zkml_service()
    zkml_jedi = zkml.infer_protocol(request.jediswap_metrics.dict())
    zkml_ekubo = zkml.infer_protocol(request.ekubo_metrics.dict())

    # Get model hash for provenance (5/5 zkML requirement)
    model_service = get_model_service()
    model_info = model_service.get_current_model_version()

    metrics_payload = {
        "jediswap": request.jediswap_metrics.dict(),
        "ekubo": request.ekubo_metrics.dict(),
        "jediswap_risk": jediswap_risk,
        "ekubo_risk": ekubo_risk,
        "jediswap_components": jediswap_components,
        "ekubo_components": ekubo_components,
        "zkml": {
            "model": "linear_v0",
            "threshold": zkml_jedi.threshold,
            "jediswap": {
                "score": zkml_jedi.score,
                "decision": zkml_jedi.decision,
                "components": zkml_jedi.components,
            },
            "ekubo": {
                "score": zkml_ekubo.score,
                "decision": zkml_ekubo.decision,
                "components": zkml_ekubo.components,
            },
        },
        "proof_generation_time_seconds": proof_generation_time,
        "proof_data_size_bytes": proof_size_bytes,
        "proof_source": "stone_prover",
        "verification_error": verification_error,
        "fact_registry_address": hex(integrity.verifier_address),
        "stone_proof_path": stone_proof_path,
        "stone_output_dir": stone_dir,
        "stone_proof_hash": stone_hash,
        "model_version": {
            "version": model_info.get("version", "1.0.0"),
            "version_felt": model_info.get("version_felt", 0x010000),
            "model_hash": model_info.get("model_hash", ""),
            "model_hash_felt": model_info.get("model_hash_felt", 0),
            "description": model_info.get("description", "Initial risk scoring model"),
        },
    }
    if snapshot:
        metrics_payload["snapshot"] = snapshot
    if extra_metrics:
        metrics_payload.update(extra_metrics)

    proof_job = ProofJob(
        proof_hash=proof_hash or fact_hash,
        status=ProofStatus.VERIFIED,
        fact_hash=fact_hash,
        l2_fact_hash=fact_hash,
        l2_verified_at=l2_verified_at,
        proof_source="stone_prover",
        network=settings.STARKNET_NETWORK,
        metrics=metrics_payload,
        proof_data=proof_bytes,
        error=verification_error,
        jediswap_risk=jediswap_risk,
        ekubo_risk=ekubo_risk,
    )
    db.add(proof_job)
    db.commit()
    db.refresh(proof_job)

    return proof_job, zkml_jedi, zkml_ekubo, verification_error


async def _compute_allocation_preview(
    jediswap_risk: int,
    ekubo_risk: int
) -> tuple[int, int, int, int]:
    """
    Compute allocation preview using on-chain formulas (read-only).
    Returns (jediswap_pct, ekubo_pct, jediswap_apy, ekubo_apy).
    """
    rpc_client = FullNodeClient(node_url=settings.STARKNET_RPC_URL)
    contract = await _get_risk_engine_contract(rpc_client)

    # Read on-chain APYs (stored values)
    jediswap_apy_result = await contract.functions["query_jediswap_apy"].call(block_number="latest")
    ekubo_apy_result = await contract.functions["query_ekubo_apy"].call(block_number="latest")
    jediswap_apy = int(jediswap_apy_result[0]) if jediswap_apy_result else 0
    ekubo_apy = int(ekubo_apy_result[0]) if ekubo_apy_result else 0

    # Call allocation function (maps jediswap -> nostra, ekubo -> ekubo)
    allocation_result = await contract.functions["calculate_allocation"].call(
        jediswap_risk,  # nostra_risk (mapped)
        0,              # zklend_risk (unused)
        ekubo_risk,     # ekubo_risk
        jediswap_apy,   # nostra_apy (mapped)
        0,              # zklend_apy (unused)
        ekubo_apy,      # ekubo_apy
        block_number="latest",
    )

    allocation_tuple = allocation_result[0] if allocation_result else (0, 0, 0)
    jediswap_pct = int(allocation_tuple[0])
    ekubo_pct = int(allocation_tuple[2])

    return jediswap_pct, ekubo_pct, jediswap_apy, ekubo_apy


@router.post("/orchestrate-allocation", response_model=OrchestrationResponse, tags=["Risk Engine"])
async def orchestrate_allocation(
    request: OrchestrationRequest,
    db: Session = Depends(get_db)
):
    """
    🤖 AI-Driven Orchestration: Backend executes verified allocation decision
    
    This is the CORE of verifiable AI:
    1. AI proposes allocation based on protocol metrics
    2. Generates STARK proof that decision respects constraints
    3. Backend EXECUTES the transaction on-chain
    4. Returns decision + proof for audit trail
    
    The backend signs and submits the transaction using its authorized account.
    This enables fully automated AI execution without user wallet interaction.
    """
    try:
        proof_job = None
        logger.info(f"🤖 AI Orchestration Starting...")
        logger.info(f"📊 JediSwap metrics: util={request.jediswap_metrics.utilization}, "
                   f"vol={request.jediswap_metrics.volatility}, liq={request.jediswap_metrics.liquidity}, "
                   f"audit={request.jediswap_metrics.audit_score}, age={request.jediswap_metrics.age_days}")
        logger.info(f"📊 Ekubo metrics: util={request.ekubo_metrics.utilization}, "
                   f"vol={request.ekubo_metrics.volatility}, liq={request.ekubo_metrics.liquidity}, "
                   f"audit={request.ekubo_metrics.audit_score}, age={request.ekubo_metrics.age_days}")
        
        # STEP 1: Generate Stone proof + register with Integrity (strict)
        logger.info("🔐 Generating Stone proof (strict)...")
        proof_job, zkml_jedi, zkml_ekubo, verification_error = await _create_proof_job(
            request=request,
            db=db,
            snapshot=None,
        )
        logger.info("✅ Stone proof registered (job: %s, fact: %s)", proof_job.id, proof_job.fact_hash)

        # Expected on-chain risk scores (deterministic model)
        expected_jediswap_score, _ = calc_risk_score(request.jediswap_metrics.dict())
        expected_ekubo_score, _ = calc_risk_score(request.ekubo_metrics.dict())

        fact_registry_address = proof_job.metrics.get("fact_registry_address") if proof_job.metrics else None
        if not fact_registry_address:
            fact_registry_address = hex(get_integrity_service().verifier_address)
        registration_rpc = None
        registration_next_nonce = None
        
        # Validate backend wallet is configured
        if not settings.BACKEND_WALLET_PRIVATE_KEY or not settings.BACKEND_WALLET_ADDRESS:
            raise HTTPException(
                status_code=500,
                detail="Backend wallet not configured. Set BACKEND_WALLET_PRIVATE_KEY in .env"
            )

        # Create backend account (AI orchestrator account)
        key_pair = KeyPair.from_private_key(int(settings.BACKEND_WALLET_PRIVATE_KEY, 16))
        network_chain = StarknetChainId.SEPOLIA if settings.STARKNET_NETWORK.lower() == "sepolia" else StarknetChainId.MAINNET
        logger.info(f"✅ Backend account initialized: {settings.BACKEND_WALLET_ADDRESS}")
        
        # Prepare protocol metrics as Python dicts (starknet.py maps to Cairo structs)
        jediswap_metrics = {
            'utilization': request.jediswap_metrics.utilization,
            'volatility': request.jediswap_metrics.volatility,
            'liquidity': request.jediswap_metrics.liquidity,
            'audit_score': request.jediswap_metrics.audit_score,
            'age_days': request.jediswap_metrics.age_days,
        }
        
        ekubo_metrics = {
            'utilization': request.ekubo_metrics.utilization,
            'volatility': request.ekubo_metrics.volatility,
            'liquidity': request.ekubo_metrics.liquidity,
            'audit_score': request.ekubo_metrics.audit_score,
            'age_days': request.ekubo_metrics.age_days,
        }
        
        logger.info(f"🚀 EXECUTING propose_and_execute_allocation on-chain...")
        logger.info(f"   Contract: {settings.RISK_ENGINE_ADDRESS}")
        logger.info(f"   Caller: {settings.BACKEND_WALLET_ADDRESS}")
        
        # Get function selector
        from starknet_py.hash.selector import get_selector_from_name
        from starknet_py.cairo.felt import encode_shortstring
        
        selector = get_selector_from_name("propose_and_execute_allocation")
        
        # Get proof fact hash from Integrity verification
        # The fact_hash is the Cairo fact hash that gets registered in SHARP registry
        proof_fact_hash = proof_job.fact_hash
        if not proof_fact_hash:
            raise HTTPException(
                status_code=400,
                detail="Proof fact hash not available. Proof must be verified before execution."
            )
        
        # Convert fact_hash to int (it's stored as hex string)
        # Ensure it fits in felt252 (max 2^251 - 1)
        MAX_FELT252 = 2**251 - 1
        if isinstance(proof_fact_hash, str):
            if proof_fact_hash.startswith('0x'):
                proof_fact_int = int(proof_fact_hash, 16)
            else:
                proof_fact_int = int(proof_fact_hash, 16)
        else:
            proof_fact_int = proof_fact_hash
        
        # Ensure fact hash fits in felt252 (modulo if needed)
        if proof_fact_int > MAX_FELT252:
            logger.warning(f"Proof fact hash {hex(proof_fact_int)} exceeds felt252 max, reducing modulo")
            proof_fact_int = proof_fact_int % (MAX_FELT252 + 1)
        
        # For now, use the same fact hash for both protocols (single proof covers both)
        # TODO: If separate proofs are generated, use separate fact hashes
        jediswap_proof_fact = proof_fact_int
        ekubo_proof_fact = proof_fact_int
        
        # Get expected risk scores from proof
        expected_jediswap_score = proof_job.jediswap_risk or 0
        expected_ekubo_score = proof_job.ekubo_risk or 0
        
        # Fact registry address for proof verification
        fact_registry_address = (
            fact_registry_address
            if isinstance(fact_registry_address, int)
            else int(fact_registry_address, 16)
        )
        
        rpc_urls = get_rpc_urls()
        abi_probe_url = rpc_urls[0] if rpc_urls else settings.STARKNET_RPC_URL
        abi_client = FullNodeClient(node_url=abi_probe_url)
        onchain_inputs = await _get_risk_engine_onchain_inputs(abi_client)
        # v4 with on-chain agent has 9 ABI inputs (2 structs + 5 proof params + 2 new params)
        # Proof-gated v4 has 7 ABI inputs (2 structs + 5 proof params)
        # Legacy has 2 ABI inputs (2 structs only)
        # If ABI inspection fails (None), default to v4 with on-chain agent (safer)
        expects_proof_args = (onchain_inputs is None) or (onchain_inputs >= 7)
        expects_onchain_agent = (onchain_inputs is None) or (onchain_inputs >= 9)

        # Get model version from proof job or model service
        model_service = get_model_service()
        model_info = model_service.get_current_model_version()
        model_version = model_info.get("model_hash_felt", 0)
        if model_version == 0:
            logger.warning("⚠️ Model version not found, using 0 (legacy mode)")

        # Get constraint signature from request or create zero signature
        if request.constraint_signature:
            constraint_sig = request.constraint_signature
            constraint_signer = int(constraint_sig.signer, 16) if constraint_sig.signer.startswith('0x') else int(constraint_sig.signer, 16)
            constraint_max_single = constraint_sig.max_single
            constraint_min_diversification = constraint_sig.min_diversification
            constraint_max_volatility = constraint_sig.max_volatility
            constraint_min_liquidity = constraint_sig.min_liquidity
            constraint_sig_r = int(constraint_sig.signature_r, 16) if constraint_sig.signature_r.startswith('0x') else int(constraint_sig.signature_r, 16)
            constraint_sig_s = int(constraint_sig.signature_s, 16) if constraint_sig.signature_s.startswith('0x') else int(constraint_sig.signature_s, 16)
            constraint_timestamp = constraint_sig.timestamp
            logger.info("✅ Using user-signed constraint signature")
        else:
            # Zero signature (signer = 0 means not provided)
            constraint_signer = 0
            constraint_max_single = 0
            constraint_min_diversification = 0
            constraint_max_volatility = 0
            constraint_min_liquidity = 0
            constraint_sig_r = 0
            constraint_sig_s = 0
            constraint_timestamp = 0
            logger.info("ℹ️ No constraint signature provided, using zero signature")

        # Serialize structs to calldata manually
        # ProtocolMetrics struct: (utilization, volatility, liquidity, audit_score, age_days)
        # ContractAddress is just felt252 in Cairo, so serialize as int
        calldata = [
            # jediswap_metrics struct (5 elements)
            int(jediswap_metrics['utilization']),
            int(jediswap_metrics['volatility']),
            int(jediswap_metrics['liquidity']),
            int(jediswap_metrics['audit_score']),
            int(jediswap_metrics['age_days']),
            # ekubo_metrics struct (5 elements)
            int(ekubo_metrics['utilization']),
            int(ekubo_metrics['volatility']),
            int(ekubo_metrics['liquidity']),
            int(ekubo_metrics['audit_score']),
            int(ekubo_metrics['age_days']),
        ]

        if expects_proof_args:
            calldata.extend([
                int(jediswap_proof_fact),        # jediswap_proof_fact (felt252)
                int(ekubo_proof_fact),           # ekubo_proof_fact (felt252)
                int(expected_jediswap_score),    # expected_jediswap_score (felt252)
                int(expected_ekubo_score),       # expected_ekubo_score (felt252)
                int(fact_registry_address),      # fact_registry_address (ContractAddress = felt252)
            ])
            logger.info("✅ Using proof-gated execution (proof parameters included)")
            
            if expects_onchain_agent:
                # Add on-chain agent parameters
                calldata.extend([
                    int(model_version),              # model_version (felt252)
                    # ConstraintSignature struct (8 fields)
                    int(constraint_signer),          # signer (ContractAddress = felt252)
                    int(constraint_max_single),      # max_single (felt252)
                    int(constraint_min_diversification),  # min_diversification (felt252)
                    int(constraint_max_volatility),   # max_volatility (felt252)
                    int(constraint_min_liquidity),    # min_liquidity (felt252)
                    int(constraint_sig_r),            # signature_r (felt252)
                    int(constraint_sig_s),            # signature_s (felt252)
                    int(constraint_timestamp),        # timestamp (u64 = felt252)
                ])
                logger.info("✅ Using v4 with on-chain agent (model_version and constraint_signature included)")
            else:
                logger.warning(
                    "⚠️ RiskEngine contract is proof-gated v4 but not v4 with on-chain agent. "
                    "Missing model_version and constraint_signature parameters. "
                    "Deploy RiskEngine v4 with on-chain agent for full functionality."
                )
        else:
            # Contract doesn't accept proof parameters - raise error (no demo mode fallback)
            raise HTTPException(
                status_code=400,
                detail=(
                    "RiskEngine contract does not accept proof parameters. "
                    "Deploy RiskEngine v4 with on-chain agent to enable proof-gated execution. "
                    "Current contract only accepts 2 inputs (legacy version)."
                )
            )
        
        logger.info(f"📝 Calldata: {calldata}")
        
        # Execute via account
        from starknet_py.net.client_models import Call
        
        call = Call(
            to_addr=int(settings.RISK_ENGINE_ADDRESS, 16),
            selector=selector,
            calldata=calldata
        )
        
        preferred_rpc_urls = [registration_rpc] if registration_rpc else rpc_urls
        nonce_override = registration_next_nonce

        # Use v3 invoke with manual resource bounds (avoid estimate_fee + unsupported block tags).
        async def _submit_with_client_v3(client: FullNodeClient, _rpc_url: str):
            account = await _init_backend_account(client, key_pair, network_chain)
            if nonce_override is not None:
                nonce = nonce_override
            else:
                try:
                    nonce = await account.get_nonce(block_number="pending")
                except Exception:
                    nonce = await account.get_nonce(block_number="latest")
            return await account.execute_v3(
                calls=[call],
                nonce=nonce,
                resource_bounds=DEFAULT_RESOURCE_BOUNDS,
            )

        invoke_result, submit_rpc = await with_rpc_fallback(
            _submit_with_client_v3, urls=preferred_rpc_urls
        )
        
        tx_hash = hex(invoke_result.transaction_hash)
        logger.info(f"📤 Transaction submitted: {tx_hash}")
        
        # Update proof job with transaction hash
        proof_job.tx_hash = tx_hash
        proof_job.status = ProofStatus.SUBMITTED
        db.commit()
        db.refresh(proof_job)
        
        logger.info(f"⏳ Waiting for acceptance...")

        wait_urls = [submit_rpc] + [url for url in rpc_urls if url != submit_rpc]
        # Wait for transaction to be accepted (raw receipt to avoid RPC schema mismatch)
        receipt = await _wait_for_receipt_raw(
            invoke_result.transaction_hash,
            urls=wait_urls,
        )

        logger.info(f"✅ Transaction accepted on-chain!")

        # Update proof status to executed (on-chain transaction succeeded)
        # Keep VERIFIED status if proof was verified locally, otherwise set to SUBMITTED
        if proof_job.status != ProofStatus.VERIFIED:
            # If Integrity already marked as FAILED, keep it; otherwise mark submitted
            if proof_job.status != ProofStatus.FAILED:
                proof_job.status = ProofStatus.SUBMITTED  # "SUBMITTED" = on-chain execution succeeded
        proof_job.submitted_at = datetime.utcnow()
        try:
            proof_job.l2_block_number = receipt.get("block_number")
        except Exception as receipt_err:
            logger.warning(f"⚠️ Could not extract transaction receipt: {receipt_err}")
        # Set verified_at if Integrity verification succeeded
        if proof_job.status == ProofStatus.VERIFIED and not proof_job.verified_at:
            proof_job.verified_at = datetime.utcnow()
        db.commit()
        db.refresh(proof_job)
        
        # Optional L1 settlement (Atlantic) disabled for Stone-only path.
        logger.info("⏭️ Skipping Atlantic submission (Stone-only proof path).")
        
        # Trigger background SHARP submission (non-blocking, won't affect orchestration response)
        # Note: SHARP submission is optional; this does not affect on-chain verification.
        logger.info("⏭️ Skipping SHARP submission (Stone proofs not wired to SHARP)")
        
        # Now fetch the decision that was just created
        async def _get_decision_count(client: FullNodeClient, _rpc_url: str):
            contract = await _get_risk_engine_contract(client)
            return await contract.functions["get_decision_count"].call(block_number="latest")

        decision_count_result, _ = await with_rpc_fallback(
            _get_decision_count, urls=wait_urls
        )
        decision_count = int(decision_count_result[0]) if decision_count_result else 0
        
        if decision_count > 0:
            async def _get_decision(client: FullNodeClient, _rpc_url: str):
                contract = await _get_risk_engine_contract(client)
                return await contract.functions["get_decision"].call(decision_count, block_number="latest")

            latest_decision_result, _ = await with_rpc_fallback(
                _get_decision, urls=wait_urls
            )
            decision_data = latest_decision_result[0] if latest_decision_result else None
            
            if decision_data:
                # decision_data is an OrderedDict from starknet.py
                logger.info(f"✅ AI Decision #{decision_count} executed:")
                logger.info(f"   JediSwap: {int(decision_data['jediswap_pct'])/100}%")
                logger.info(f"   Ekubo: {int(decision_data['ekubo_pct'])/100}%")
                
                # Update proof_job with allocation decision results
                proof_job.jediswap_pct = int(decision_data['jediswap_pct'])
                proof_job.ekubo_pct = int(decision_data['ekubo_pct'])
                proof_job.jediswap_risk = int(decision_data['jediswap_risk'])
                proof_job.ekubo_risk = int(decision_data['ekubo_risk'])
                db.commit()
                db.refresh(proof_job)
                
                return OrchestrationResponse(
                    decision_id=int(decision_data['decision_id']),
                    block_number=int(decision_data['block_number']),
                    timestamp=int(decision_data['timestamp']),
                    jediswap_pct=int(decision_data['jediswap_pct']),
                    ekubo_pct=int(decision_data['ekubo_pct']),
                    jediswap_risk=int(decision_data['jediswap_risk']),
                    ekubo_risk=int(decision_data['ekubo_risk']),
                    jediswap_apy=int(decision_data['jediswap_apy']),
                    ekubo_apy=int(decision_data['ekubo_apy']),
                    rationale_hash=str(decision_data['rationale_hash']),
                    strategy_router_tx=str(decision_data['strategy_router_tx']),  # Decision ID (legacy)
                    tx_hash=tx_hash if tx_hash else None,  # Actual on-chain transaction hash
                    message=f"✅ AI executed decision #{decision_count} on-chain (tx: {tx_hash})",
                    # Proof information
                    proof_job_id=str(proof_job.id),
                    proof_hash=proof_job.proof_hash,
                    proof_status=proof_job.status.value if hasattr(proof_job.status, 'value') else str(proof_job.status),
                    proof_error=proof_job.error,
                )
        
        raise HTTPException(
            status_code=500,
            detail="Transaction succeeded but failed to retrieve decision"
        )
        
    except HTTPException as e:
        # If we already created a proof job, mark it failed with the error
        try:
            if 'proof_job' in locals() and proof_job:
                proof_job.status = ProofStatus.FAILED
                proof_job.error = str(e.detail) if hasattr(e, "detail") else str(e)
                db.commit()
        except Exception:
            pass
        raise e
    except Exception as e:
        logger.error(f"❌ AI Orchestration failed: {str(e)}", exc_info=True)
        try:
            if 'proof_job' in locals() and proof_job:
                proof_job.status = ProofStatus.FAILED
                proof_job.error = str(e)
                db.commit()
        except Exception:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"AI execution failed: {str(e)}"
        )


@router.post("/propose-allocation", response_model=ProposalResponse, tags=["Risk Engine"])
async def propose_allocation(
    request: OrchestrationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate proof + allocation preview without executing on-chain.
    This is the manual-execute flow: proof first, execution later.
    """
    proof_job = None
    try:
        proof_job, _, _, _ = await _create_proof_job(request, db)

        # Compute allocation preview using on-chain formulas
        jediswap_pct, ekubo_pct, jediswap_apy, ekubo_apy = await _compute_allocation_preview(
            proof_job.jediswap_risk or 0,
            proof_job.ekubo_risk or 0
        )

        # Persist allocation preview on the proof job
        proof_job.jediswap_pct = jediswap_pct
        proof_job.ekubo_pct = ekubo_pct
        proof_job.metrics["apys"] = {
            "jediswap": jediswap_apy,
            "ekubo": ekubo_apy,
        }
        proof_job.metrics["allocation_preview"] = {
            "jediswap_pct": jediswap_pct,
            "ekubo_pct": ekubo_pct,
        }
        db.commit()
        db.refresh(proof_job)

        can_execute = (proof_job.status == ProofStatus.VERIFIED)
        # NOTE: ALLOW_UNVERIFIED_EXECUTION bypass is deprecated.
        # Contract now enforces proof verification on-chain, so backend bypass is less critical.
        # However, we still check it here to prevent unnecessary contract calls.
        if not can_execute and settings.ALLOW_UNVERIFIED_EXECUTION:
            logger.warning("⚠️ ALLOW_UNVERIFIED_EXECUTION=True: Bypassing backend verification check. Contract will still enforce proof verification.")
            can_execute = True

        return ProposalResponse(
            proposal_id=str(proof_job.id),
            jediswap_pct=jediswap_pct,
            ekubo_pct=ekubo_pct,
            jediswap_risk=proof_job.jediswap_risk or 0,
            ekubo_risk=proof_job.ekubo_risk or 0,
            jediswap_apy=jediswap_apy,
            ekubo_apy=ekubo_apy,
            message="✅ Proposal ready. Execute when proof is verified.",
            proof_job_id=str(proof_job.id),
            proof_hash=proof_job.proof_hash,
            proof_status=proof_job.status.value if hasattr(proof_job.status, 'value') else str(proof_job.status),
            proof_error=proof_job.error,
            proof_source=proof_job.proof_source,
            l2_verified_at=proof_job.l2_verified_at.isoformat() if proof_job.l2_verified_at else None,
            can_execute=can_execute,
        )
    except HTTPException as e:
        try:
            if proof_job:
                proof_job.status = ProofStatus.FAILED
                proof_job.error = str(e.detail) if hasattr(e, "detail") else str(e)
                db.commit()
        except Exception:
            pass
        raise e
    except Exception as e:
        logger.error(f"❌ Proposal failed: {str(e)}", exc_info=True)
        try:
            if proof_job:
                proof_job.status = ProofStatus.FAILED
                proof_job.error = str(e)
                db.commit()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Proposal failed: {str(e)}")


@router.post("/propose-from-market", response_model=ProposalResponse, tags=["Risk Engine"])
async def propose_from_market(db: Session = Depends(get_db)):
    """
    Generate proof + allocation preview using read-only mainnet-derived proxy metrics.
    """
    metrics_service = get_protocol_metrics_service()
    metrics = await metrics_service.get_protocol_metrics()

    # Snapshot block context for auditability
    data_rpc = settings.DATA_RPC_URL or settings.STARKNET_RPC_URL
    data_network = settings.DATA_NETWORK or settings.STARKNET_NETWORK
    market_service = get_market_data_service(rpc_url=data_rpc, network=data_network)
    snapshot = await market_service.get_snapshot()

    request = OrchestrationRequest(
        jediswap_metrics=RiskMetricsRequest(**{
            "utilization": metrics["jediswap"].utilization,
            "volatility": metrics["jediswap"].volatility,
            "liquidity": metrics["jediswap"].liquidity,
            "audit_score": metrics["jediswap"].audit_score,
            "age_days": metrics["jediswap"].age_days,
        }),
        ekubo_metrics=RiskMetricsRequest(**{
            "utilization": metrics["ekubo"].utilization,
            "volatility": metrics["ekubo"].volatility,
            "liquidity": metrics["ekubo"].liquidity,
            "audit_score": metrics["ekubo"].audit_score,
            "age_days": metrics["ekubo"].age_days,
        }),
    )

    # Attach snapshot metadata for audit trail
    snapshot_payload = {
        "block_number": snapshot.block_number,
        "block_hash": snapshot.block_hash,
        "timestamp": snapshot.timestamp,
        "network": snapshot.network,
    }

    proof_job, _, _, _ = await _create_proof_job(
        request,
        db,
        snapshot=snapshot_payload,
    )

    jediswap_pct, ekubo_pct, jediswap_apy, ekubo_apy = await _compute_allocation_preview(
        proof_job.jediswap_risk or 0,
        proof_job.ekubo_risk or 0
    )

    proof_job.jediswap_pct = jediswap_pct
    proof_job.ekubo_pct = ekubo_pct
    proof_job.metrics["apys"] = {
        "jediswap": jediswap_apy,
        "ekubo": ekubo_apy,
    }
    proof_job.metrics["allocation_preview"] = {
        "jediswap_pct": jediswap_pct,
        "ekubo_pct": ekubo_pct,
    }
    db.commit()
    db.refresh(proof_job)

    can_execute = (proof_job.status == ProofStatus.VERIFIED)
    # STRICT MODE: No bypass allowed
    if not can_execute:
        if settings.ALLOW_UNVERIFIED_EXECUTION:
            logger.error("⚠️ ALLOW_UNVERIFIED_EXECUTION=True is ignored in strict Stone-only mode.")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Proof not verified",
                "message": "Proof must be verified in FactRegistry before execution.",
                "strict_mode": True,
            }
        )

    return ProposalResponse(
        proposal_id=str(proof_job.id),
        block_number=snapshot.block_number,
        timestamp=snapshot.timestamp,
        jediswap_pct=jediswap_pct,
        ekubo_pct=ekubo_pct,
        jediswap_risk=proof_job.jediswap_risk or 0,
        ekubo_risk=proof_job.ekubo_risk or 0,
        jediswap_apy=jediswap_apy,
        ekubo_apy=ekubo_apy,
        message="✅ Market proposal ready. Execute when proof is verified.",
        proof_job_id=str(proof_job.id),
        proof_hash=proof_job.proof_hash,
        proof_status=proof_job.status.value if hasattr(proof_job.status, 'value') else str(proof_job.status),
        proof_error=proof_job.error,
        proof_source=proof_job.proof_source,
        l2_verified_at=proof_job.l2_verified_at.isoformat() if proof_job.l2_verified_at else None,
        can_execute=can_execute,
    )


@router.post("/execute-allocation", response_model=OrchestrationResponse, tags=["Risk Engine"])
async def execute_allocation(
    request: ExecuteRequest,
    db: Session = Depends(get_db)
):
    """
    Execute a previously proposed allocation once proof is verified.
    """
    try:
        proof_job = db.query(ProofJob).filter(ProofJob.id == request.proof_job_id).first()
        if not proof_job:
            raise HTTPException(status_code=404, detail="Proposal not found")

        can_execute = (proof_job.status == ProofStatus.VERIFIED)
        
        # STRICT MODE: No bypass allowed - proof must be verified
        if not can_execute:
            if settings.ALLOW_UNVERIFIED_EXECUTION:
                logger.error("⚠️ ALLOW_UNVERIFIED_EXECUTION=True is ignored in strict Stone-only mode. Proof must be verified on-chain.")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Proof not verified",
                    "message": "Proof must be verified in FactRegistry before execution. This is enforced in strict Stone-only mode.",
                    "proof_job_id": str(proof_job.id),
                    "proof_status": proof_job.status.value if hasattr(proof_job.status, 'value') else str(proof_job.status),
                    "fact_hash": proof_job.fact_hash,
                    "strict_mode": True,
                }
            )

        # Build orchestration request from stored metrics
        metrics = proof_job.metrics or {}
        jediswap_metrics = metrics.get("jediswap", {})
        ekubo_metrics = metrics.get("ekubo", {})

        if not settings.BACKEND_WALLET_PRIVATE_KEY or not settings.BACKEND_WALLET_ADDRESS:
            raise HTTPException(
                status_code=500,
                detail="Backend wallet not configured. Set BACKEND_WALLET_PRIVATE_KEY in .env"
            )

        key_pair = KeyPair.from_private_key(int(settings.BACKEND_WALLET_PRIVATE_KEY, 16))
        network_chain = (
            StarknetChainId.SEPOLIA
            if settings.STARKNET_NETWORK.lower() == "sepolia"
            else StarknetChainId.MAINNET
        )

        # Get proof fact hash from proof job (required for v4 proof-gated execution)
        proof_fact_hash = proof_job.fact_hash
        if not proof_fact_hash:
            raise HTTPException(
                status_code=400,
                detail="Proof fact hash not found in proof job. Cannot execute without proof verification."
            )

        # Convert fact_hash to int (it's stored as hex string)
        MAX_FELT252 = 2**251 - 1
        if isinstance(proof_fact_hash, str):
            if proof_fact_hash.startswith('0x'):
                proof_fact_int = int(proof_fact_hash, 16)
            else:
                proof_fact_int = int(proof_fact_hash, 16)
        else:
            proof_fact_int = proof_fact_hash
        
        if proof_fact_int > MAX_FELT252:
            logger.warning(f"Proof fact hash {hex(proof_fact_int)} exceeds felt252 max, reducing modulo")
            proof_fact_int = proof_fact_int % (MAX_FELT252 + 1)
        
        # Use same fact hash for both protocols (single proof covers both)
        jediswap_proof_fact = proof_fact_int
        ekubo_proof_fact = proof_fact_int

        # Calculate expected risk scores (must match on-chain calculation)
        expected_jediswap_score, _ = calc_risk_score(jediswap_metrics)
        expected_ekubo_score, _ = calc_risk_score(ekubo_metrics)

        # Get fact registry address
        integrity = get_integrity_service()
        fact_registry_address = int(integrity.verifier_address)

        # Detect ABI to determine if we need proof params and on-chain agent params
        rpc_urls = get_rpc_urls()
        abi_probe_url = rpc_urls[0] if rpc_urls else settings.STARKNET_RPC_URL
        abi_client = FullNodeClient(node_url=abi_probe_url)
        onchain_inputs = await _get_risk_engine_onchain_inputs(abi_client)
        expects_proof_args = (onchain_inputs is None) or (onchain_inputs >= 7)
        expects_onchain_agent = (onchain_inputs is None) or (onchain_inputs >= 9)

        # Get model version
        model_service = get_model_service()
        model_info = model_service.get_current_model_version()
        model_version = model_info.get("model_hash_felt", 0)
        if model_version == 0:
            logger.warning("⚠️ Model version not found, using 0 (legacy mode)")

        # Constraint signature (zero signature when not provided)
        constraint_signer = 0
        constraint_max_single = 0
        constraint_min_diversification = 0
        constraint_max_volatility = 0
        constraint_min_liquidity = 0
        constraint_sig_r = 0
        constraint_sig_s = 0
        constraint_timestamp = 0
        logger.info("ℹ️ No constraint signature provided, using zero signature")

        from starknet_py.hash.selector import get_selector_from_name
        selector = get_selector_from_name("propose_and_execute_allocation")

        # Build full calldata (same as orchestrate-allocation) - 24 elements for v4 with on-chain agent
        calldata = [
            # jediswap_metrics struct (5 elements)
            int(jediswap_metrics['utilization']),
            int(jediswap_metrics['volatility']),
            int(jediswap_metrics['liquidity']),
            int(jediswap_metrics['audit_score']),
            int(jediswap_metrics['age_days']),
            # ekubo_metrics struct (5 elements)
            int(ekubo_metrics['utilization']),
            int(ekubo_metrics['volatility']),
            int(ekubo_metrics['liquidity']),
            int(ekubo_metrics['audit_score']),
            int(ekubo_metrics['age_days']),
        ]

        if expects_proof_args:
            calldata.extend([
                int(jediswap_proof_fact),
                int(ekubo_proof_fact),
                int(expected_jediswap_score),
                int(expected_ekubo_score),
                int(fact_registry_address),
            ])
            logger.info("✅ Using proof-gated execution (proof parameters included)")
            
            if expects_onchain_agent:
                calldata.extend([
                    int(model_version),
                    int(constraint_signer),
                    int(constraint_max_single),
                    int(constraint_min_diversification),
                    int(constraint_max_volatility),
                    int(constraint_min_liquidity),
                    int(constraint_sig_r),
                    int(constraint_sig_s),
                    int(constraint_timestamp),
                ])
                logger.info("✅ Using v4 with on-chain agent (model_version and constraint_signature included)")
        else:
            raise HTTPException(
                status_code=400,
                detail="RiskEngine contract does not accept proof parameters. Deploy RiskEngine v4 with on-chain agent."
            )

        logger.info(f"📝 Calldata ({len(calldata)} elements): {calldata}")

        from starknet_py.net.client_models import Call
        call = Call(
            to_addr=int(settings.RISK_ENGINE_ADDRESS, 16),
            selector=selector,
            calldata=calldata
        )

        # Use v3 invoke with manual resource bounds (avoid estimate_fee + unsupported block tags).
        async def _submit_with_client_v3(client: FullNodeClient, _rpc_url: str):
            account = await _init_backend_account(client, key_pair, network_chain)
            try:
                nonce = await account.get_nonce(block_number="pending")
            except Exception:
                nonce = await account.get_nonce(block_number="latest")
            return await account.execute_v3(
                calls=[call],
                nonce=nonce,
                resource_bounds=DEFAULT_RESOURCE_BOUNDS,
            )

        invoke_result, submit_rpc = await with_rpc_fallback(
            _submit_with_client_v3, urls=rpc_urls
        )

        tx_hash = hex(invoke_result.transaction_hash)
        proof_job.tx_hash = tx_hash
        if proof_job.status != ProofStatus.VERIFIED:
            proof_job.status = ProofStatus.SUBMITTED
        proof_job.submitted_at = datetime.utcnow()
        db.commit()
        db.refresh(proof_job)

        wait_urls = [submit_rpc] + [url for url in rpc_urls if url != submit_rpc]
        receipt = await _wait_for_receipt_raw(
            invoke_result.transaction_hash,
            urls=wait_urls,
        )

        try:
            proof_job.l2_block_number = receipt.get("block_number")
        except Exception as receipt_err:
            logger.warning(f"⚠️ Could not extract transaction receipt: {receipt_err}")

        # Fetch latest decision from RiskEngine
        async def _get_decision_count(client: FullNodeClient, _rpc_url: str):
            contract = await _get_risk_engine_contract(client)
            return await contract.functions["get_decision_count"].call(block_number="latest")

        decision_count_result, _ = await with_rpc_fallback(
            _get_decision_count, urls=wait_urls
        )
        decision_count = int(decision_count_result[0]) if decision_count_result else 0
        if decision_count <= 0:
            raise HTTPException(status_code=500, detail="Execution succeeded but no decision found")

        async def _get_decision(client: FullNodeClient, _rpc_url: str):
            contract = await _get_risk_engine_contract(client)
            return await contract.functions["get_decision"].call(decision_count, block_number="latest")

        latest_decision_result, _ = await with_rpc_fallback(
            _get_decision, urls=wait_urls
        )
        decision_data = latest_decision_result[0] if latest_decision_result else None
        if not decision_data:
            raise HTTPException(status_code=500, detail="Execution succeeded but decision data missing")

        proof_job.decision_id = int(decision_data['decision_id'])
        proof_job.jediswap_pct = int(decision_data['jediswap_pct'])
        proof_job.ekubo_pct = int(decision_data['ekubo_pct'])
        proof_job.jediswap_risk = int(decision_data['jediswap_risk'])
        proof_job.ekubo_risk = int(decision_data['ekubo_risk'])
        db.commit()
        db.refresh(proof_job)

        return OrchestrationResponse(
            decision_id=int(decision_data['decision_id']),
            block_number=int(decision_data['block_number']),
            timestamp=int(decision_data['timestamp']),
            jediswap_pct=int(decision_data['jediswap_pct']),
            ekubo_pct=int(decision_data['ekubo_pct']),
            jediswap_risk=int(decision_data['jediswap_risk']),
            ekubo_risk=int(decision_data['ekubo_risk']),
            jediswap_apy=int(decision_data['jediswap_apy']),
            ekubo_apy=int(decision_data['ekubo_apy']),
            rationale_hash=str(decision_data['rationale_hash']),
            strategy_router_tx=str(decision_data['strategy_router_tx']),
            tx_hash=tx_hash,
            message=f"✅ Executed decision #{decision_count} on-chain (tx: {tx_hash})",
            proof_job_id=str(proof_job.id),
            proof_hash=proof_job.proof_hash,
            proof_status=proof_job.status.value if hasattr(proof_job.status, 'value') else str(proof_job.status),
            proof_error=proof_job.error,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        message = str(e)
        if is_retryable_rpc_error(e):
            message = "Starknet RPC unavailable. Retried all endpoints."
        elif "Client failed with code 502" in message:
            message = "Starknet RPC returned 502 (bad gateway). Try again or switch RPC."
        logger.error(f"❌ Execution failed: {message}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Execution failed: {message}")


@router.post("/orchestrate-from-market", response_model=OrchestrationResponse, tags=["Risk Engine"])
async def orchestrate_from_market(db: Session = Depends(get_db)):
    """
    Orchestrate allocation using read-only mainnet-derived proxy metrics.
    This avoids fake testnet inputs while keeping execution optional.
    """
    metrics_service = get_protocol_metrics_service()
    metrics = await metrics_service.get_protocol_metrics()

    request = OrchestrationRequest(
        jediswap_metrics=RiskMetricsRequest(**{
            "utilization": metrics["jediswap"].utilization,
            "volatility": metrics["jediswap"].volatility,
            "liquidity": metrics["jediswap"].liquidity,
            "audit_score": metrics["jediswap"].audit_score,
            "age_days": metrics["jediswap"].age_days,
        }),
        ekubo_metrics=RiskMetricsRequest(**{
            "utilization": metrics["ekubo"].utilization,
            "volatility": metrics["ekubo"].volatility,
            "liquidity": metrics["ekubo"].liquidity,
            "audit_score": metrics["ekubo"].audit_score,
            "age_days": metrics["ekubo"].age_days,
        }),
    )

    return await orchestrate_allocation(request, db)


async def _canonical_integrity_pipeline(
    jediswap_metrics: dict,
    ekubo_metrics: dict,
) -> tuple[Optional[int], Optional[str], Optional[str], Optional[str]]:
    """
    One-shot canonical Integrity pipeline following Integrity's generate.py approach exactly.
    
    This function uses Integrity's canonical proof generation workflow to isolate
    AIR and serialization mismatches. It follows the exact steps from:
    integrity/examples/proofs/generate.py
    
    Returns:
        (fact_hash_int, proof_json_path, output_dir, proof_hash)
    """
    from math import ceil, log
    
    logger.info("=" * 80)
    logger.info("🔬 CANONICAL INTEGRITY PIPELINE")
    logger.info("=" * 80)
    logger.info("Following Integrity's generate.py approach exactly")
    logger.info("=" * 80)
    
    repo_root = Path(__file__).resolve().parents[4]
    output_dir = Path(tempfile.mkdtemp(prefix="canonical_integrity_"))
    
    try:
        # Step 1: Compile Cairo0 program (canonical Integrity approach)
        cairo_program = repo_root / "verification" / "risk_example_cairo0.cairo"
        if not cairo_program.exists():
            raise FileNotFoundError(f"risk_example_cairo0.cairo not found at {cairo_program}")
        
        logger.info("Step 1: Compiling Cairo0 program (canonical Integrity approach)...")
        compiled_program = output_dir / "risk_compiled.json"
        cairo_compile = _resolve_cairo0_compile_bin()
        
        program_input = {
            "jedi_utilization": jediswap_metrics["utilization"],
            "jedi_volatility": jediswap_metrics["volatility"],
            "jedi_liquidity": jediswap_metrics["liquidity"],
            "jedi_audit_score": jediswap_metrics["audit_score"],
            "jedi_age_days": jediswap_metrics["age_days"],
            "ekubo_utilization": ekubo_metrics["utilization"],
            "ekubo_volatility": ekubo_metrics["volatility"],
            "ekubo_liquidity": ekubo_metrics["liquidity"],
            "ekubo_audit_score": ekubo_metrics["audit_score"],
            "ekubo_age_days": ekubo_metrics["age_days"],
        }
        program_input_file = output_dir / "risk_program_input.json"
        program_input_file.write_text(json.dumps(program_input))
        
        compile_cmd = [
            cairo_compile,
            str(cairo_program),
            "--output",
            str(compiled_program),
            "--proof_mode",
        ]
        
        logger.debug(f"Compile command: {' '.join(compile_cmd[:3])} ...")
        subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        logger.info("✅ Compilation complete")
        
        # Step 2: Run Cairo0 program to generate traces
        logger.info("Step 2: Running Cairo0 program to generate traces...")
        trace_file = output_dir / "risk_trace.bin"
        memory_file = output_dir / "risk_memory.bin"
        public_input_file = output_dir / "risk_public.json"
        private_input_file = output_dir / "risk_private.json"
        
        cairo_run = _resolve_cairo0_run_bin()
        run_cmd = [
            cairo_run,
            "--program",
            str(compiled_program),
            "--layout",
            settings.INTEGRITY_LAYOUT,
            "--proof_mode",
            "--program_input",
            str(program_input_file),
            "--trace_file",
            str(trace_file),
            "--memory_file",
            str(memory_file),
            "--air_public_input",
            str(public_input_file),
            "--air_private_input",
            str(private_input_file),
            "--print_output",
        ]
        
        logger.debug(f"Run command: {' '.join(run_cmd[:4])} ...")
        cairo_timeout = getattr(settings, "INTEGRITY_CAIRO_TIMEOUT", 300)
        proc = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            timeout=cairo_timeout,
            check=True,
        )
        if proc.stdout:
            logger.info(f"cairo-run output: {proc.stdout.strip().splitlines()[-1]}")
        logger.info("✅ Trace generation complete")
        
        # Step 2: Extract n_steps and compute FRI step_list (canonical approach)
        with open(public_input_file) as f:
            public_input = json.load(f)
        n_steps = public_input.get("n_steps")
        if not n_steps:
            raise ValueError("n_steps not found in public input")
        
        logger.info(f"Step 3: Computing FRI parameters for n_steps={n_steps}...")
        
        # Load base parameters (canonical Integrity params)
        base_params_file = repo_root / "integrity" / "examples" / "proofs" / "cpu_air_params.json"
        if not base_params_file.exists():
            raise FileNotFoundError(f"Canonical params file not found: {base_params_file}")
        
        with open(base_params_file) as f:
            params = json.load(f)
        
        # Compute FRI step_list using Integrity's exact formula
        n_steps_log = ceil(log(n_steps, 2))
        last_layer_degree_bound = params["stark"]["fri"]["last_layer_degree_bound"]
        last_layer_degree_bound_log = ceil(log(last_layer_degree_bound, 2))
        sigma_fri_step_list = n_steps_log + 4 - last_layer_degree_bound_log
        
        q, r = divmod(sigma_fri_step_list, 4)
        fri_step_list = [0] + [4] * q + ([r] if r > 0 else [])
        
        # Update params with computed FRI step_list
        params["stark"]["fri"]["fri_step_list"] = fri_step_list
        
        logger.info(f"  FRI step_list: {fri_step_list}")
        logger.info(f"  Last layer degree bound: {last_layer_degree_bound}")
        logger.info(f"  Equation: log2({n_steps})={n_steps_log} + 4 - log2({last_layer_degree_bound})={last_layer_degree_bound_log} = {sigma_fri_step_list}")
        logger.info("✅ FRI parameters computed")
        
        # Save updated params to temp file
        updated_params_file = output_dir / "updated_cpu_air_params.json"
        with open(updated_params_file, 'w') as f:
            json.dump(params, f, indent=2)
        
        # Step 3: Run Stone prover with canonical parameters
        proof_output_file = output_dir / "risk_proof.json"
        prover_config_file = repo_root / "integrity" / "examples" / "proofs" / "cpu_air_prover_config.json"
        
        if not prover_config_file.exists():
            raise FileNotFoundError(f"Prover config file not found: {prover_config_file}")
        
        stone_binary = Path(
            "/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover"
        )
        if not stone_binary.exists():
            raise FileNotFoundError(f"Stone prover binary not found: {stone_binary}")
        
        prover_cmd = [
            str(stone_binary),
            "--parameter_file",
            str(updated_params_file),
            "--prover_config_file",
            str(prover_config_file),
            "--public_input_file",
            str(public_input_file),
            "--private_input_file",
            str(private_input_file),
            "--out_file",
            str(proof_output_file),
            "--generate_annotations",
        ]
        
        logger.info("Step 4: Running Stone prover with canonical parameters...")
        logger.debug(f"Command: {' '.join(prover_cmd[:3])} ...")
        stone_timeout = getattr(settings, "INTEGRITY_CAIRO_TIMEOUT", 300)
        proc = subprocess.run(
            prover_cmd,
            capture_output=True,
            text=True,
            timeout=stone_timeout,
            check=True,
        )
        logger.info("✅ Stone proof generation complete")
        
        # Step 4: Verify proof structure and log parameters
        with open(proof_output_file) as f:
            proof_data = json.load(f)
        
        logger.info("=" * 80)
        logger.info("🔍 CANONICAL PROOF - PARAMETERS")
        logger.info("=" * 80)
        
        # Read from proof_parameters first (Stone proof JSON structure), fallback to config
        proof_params = proof_data.get("proof_parameters", {})
        if not proof_params:
            proof_params = proof_data.get("config", {})
        
        public_input = proof_data.get("public_input", {})
        logger.info(f"Proof layout: {public_input.get('layout')}")
        logger.info(f"Proof n_steps: {public_input.get('n_steps')}")
        
        stark = proof_params.get("stark", {})
        fri = stark.get("fri", {})
        logger.info(f"FRI step_list: {fri.get('fri_step_list')}")
        logger.info(f"FRI last_layer_degree_bound: {fri.get('last_layer_degree_bound')}")
        logger.info(f"FRI n_queries: {fri.get('n_queries')}")
        logger.info(f"FRI log_n_cosets: {stark.get('log_n_cosets')}")
        logger.info(f"Channel hash: {proof_params.get('channel_hash')}")
        logger.info(f"Commitment hash: {proof_params.get('commitment_hash')}")
        logger.info(f"Pow hash: {proof_params.get('pow_hash')}")
        logger.info(f"n_verifier_friendly_commitment_layers: {proof_params.get('n_verifier_friendly_commitment_layers')}")
        logger.info(f"Verifier friendly channel updates: {proof_params.get('verifier_friendly_channel_updates')}")
        logger.info(f"Verifier friendly commitment hash: {proof_params.get('verifier_friendly_commitment_hash')}")
        logger.info("=" * 80)
        
        # Step 6: Serialize and register with Integrity
        serializer_bin = Path(
            settings.INTEGRITY_PROOF_SERIALIZER_BIN
            or "/opt/obsqra.starknet/integrity/target/release/proof_serializer"
        )
        calldata_body = serialize_stone_proof(proof_output_file, serializer_bin)
        calldata = [
            _string_to_felt(settings.INTEGRITY_LAYOUT),
            _string_to_felt(settings.INTEGRITY_HASHER),
            _string_to_felt(settings.INTEGRITY_STONE_VERSION),
            _string_to_felt(settings.INTEGRITY_MEMORY_VERIFICATION),
            *calldata_body,
        ]
        
        # Calculate proof hash first (before registration attempt)
        with open(proof_output_file, 'rb') as f:
            proof_bytes = f.read()
        import hashlib
        proof_hash = hashlib.sha256(proof_bytes).hexdigest()
        
        logger.info("Step 5: Registering proof with Integrity FactRegistry...")
        fact_hash_int = None
        try:
            integrity = get_integrity_service()
            fact_hash_int, _, _ = await integrity.register_calldata_and_get_fact(calldata)
            logger.info(f"✅ Proof registered: fact_hash={hex(fact_hash_int)}")
        except Exception as reg_error:
            # Registration failure is expected in test environments or if proof is invalid
            # The important part is that proof was generated
            error_msg = str(reg_error)
            if "BACKEND_WALLET_PRIVATE_KEY" in error_msg or "invalid literal" in error_msg:
                logger.warning("⚠️  Registration skipped: Backend wallet not configured (expected in test)")
            elif "Invalid final_pc" in error_msg or "Invalid OODS" in error_msg:
                logger.error(f"❌ Registration failed: {error_msg}")
                logger.info("   This indicates OODS/final_pc mismatch - proof generated but invalid for verifier")
            else:
                logger.error(f"❌ Registration failed: {error_msg}")
        
        logger.info("=" * 80)
        logger.info("✅ CANONICAL PIPELINE COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Proof generated: {proof_output_file}")
        logger.info(f"Proof hash: {proof_hash}")
        logger.info(f"Fact hash: {hex(fact_hash_int) if fact_hash_int else 'None (registration failed/skipped)'}")
        logger.info("=" * 80)
        
        return fact_hash_int, str(proof_output_file), str(output_dir), proof_hash
        
    except Exception as e:
        logger.error(f"❌ Canonical pipeline failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Canonical Integrity pipeline failed: {str(e)}") from e
