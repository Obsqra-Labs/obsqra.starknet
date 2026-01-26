"""
Risk Engine API endpoints for on-chain risk calculations
"""
import asyncio
import time
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
from app.services.luminair_service import get_luminair_service
from app.services.zkml_service import get_zkml_service
from app.workers.sharp_worker import submit_proof_to_sharp
from app.services.integrity_service import get_integrity_service
from app.services.atlantic_service import get_atlantic_service
from app.workers.atlantic_worker import enqueue_atlantic_status_check
from app.services.protocol_metrics_service import get_protocol_metrics_service
from app.services.market_data_service import get_market_data_service
from app.utils.rpc import with_rpc_fallback, get_rpc_urls, is_retryable_rpc_error

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()
_RISK_ENGINE_ABI = None

# Manual resource bounds to avoid estimate_fee (which uses unsupported block tags on some RPCs).
DEFAULT_RESOURCE_BOUNDS = ResourceBoundsMapping(
    l1_gas=ResourceBounds(max_amount=30000, max_price_per_unit=100000000000000),
    l1_data_gas=ResourceBounds(max_amount=30000, max_price_per_unit=1000000000000),
    l2_gas=ResourceBounds(max_amount=3000000, max_price_per_unit=20000000000),
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


class OrchestrationRequest(BaseModel):
    """Request for full on-chain orchestration"""
    jediswap_metrics: RiskMetricsRequest = Field(..., description="JediSwap protocol metrics")
    ekubo_metrics: RiskMetricsRequest = Field(..., description="Ekubo protocol metrics")


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
    Generate proof + verify via Integrity + store ProofJob.
    Returns (proof_job, zkml_jedi, zkml_ekubo, verification_error).
    """
    proof_start_time = time.time()
    luminair = get_luminair_service()
    proof = await luminair.generate_proof(
        request.jediswap_metrics.dict(),
        request.ekubo_metrics.dict()
    )
    proof_generation_time = time.time() - proof_start_time

    # zkML demo inference (tiny linear model)
    zkml = get_zkml_service()
    zkml_jedi = zkml.infer_protocol(request.jediswap_metrics.dict())
    zkml_ekubo = zkml.infer_protocol(request.ekubo_metrics.dict())

    # Integrity verification
    fact_hash = proof.fact_hash or (
        luminair.calculate_fact_hash(proof.proof_data or b"") if proof.proof_data else None
    )
    if not fact_hash:
        if settings.ALLOW_FAKE_FACT_HASH:
            fact_hash = luminair.calculate_fact_hash(proof.proof_data or b"")
            logger.warning("Using fallback fact hash (stub) because LuminAIR did not emit one")
        else:
            raise HTTPException(status_code=500, detail="No fact hash from LuminAIR; set ALLOW_FAKE_FACT_HASH=True to override")

    integrity = get_integrity_service()
    l2_verified = False
    l2_verified_at = None
    verification_error = None
    skip_integrity = bool(getattr(luminair, "use_mock", False))

    verifier_struct = None
    proof_struct = None
    verifier_bytes = None
    proof_bytes = None

    if getattr(proof, "verifier_config_json", None) and getattr(proof, "stark_proof_json", None):
        verifier_struct = proof.verifier_config_json
        proof_struct = proof.stark_proof_json
        logger.info(f"Using verifier_config_json and stark_proof_json from proof object")
    else:
        if getattr(proof, "verifier_payload_format", None) == "integrity_json":
            import base64
            import json as pyjson
            try:
                if proof.verifier_config_b64:
                    verifier_struct = pyjson.loads(base64.b64decode(proof.verifier_config_b64))
                    logger.info(f"Decoded verifier_config from base64, keys: {list(verifier_struct.keys()) if verifier_struct else 'None'}")
                if proof.stark_proof_b64:
                    proof_struct = pyjson.loads(base64.b64decode(proof.stark_proof_b64))
                    logger.info(f"Decoded stark_proof from base64, keys: {list(proof_struct.keys()) if proof_struct else 'None'}")
            except Exception as decode_err:
                logger.warning(f"Could not decode Integrity JSON payloads: {decode_err}")

    try:
        if proof.verifier_config_path:
            from pathlib import Path
            verifier_bytes = Path(proof.verifier_config_path).read_bytes()
            logger.info(f"Read verifier_config from path: {len(verifier_bytes)} bytes")
        if proof.stark_proof_path:
            from pathlib import Path
            proof_bytes = Path(proof.stark_proof_path).read_bytes()
            logger.info(f"Read stark_proof from path: {len(proof_bytes)} bytes")
    except Exception as read_err:
        logger.warning(f"Could not read verifier/proof blobs: {read_err}")

    attempted_full = False
    if skip_integrity:
        verification_error = "Integrity verification skipped (mock proof)"
        logger.warning(f"Skipping Integrity verification: LuminAIR is in mock mode")
    elif verifier_struct and proof_struct:
        attempted_full = True
        logger.info(f"Attempting Integrity verification with structured proof (verifier keys: {list(verifier_struct.keys())}, proof keys: {list(proof_struct.keys())})")
        l2_verified = await integrity.verify_proof_full_and_register_fact(
            verifier_config=verifier_struct,
            stark_proof=proof_struct
        )
        l2_verified_at = datetime.utcnow() if l2_verified else None
        if l2_verified:
            logger.info(f"✅ Integrity verification PASSED")
        else:
            logger.warning(f"⚠️ Integrity verification FAILED")
    elif verifier_bytes and proof_bytes:
        attempted_full = True
        logger.info(f"Attempting Integrity verification with raw bytes ({len(verifier_bytes)} verifier, {len(proof_bytes)} proof)")
        l2_verified = await integrity.verify_proof_full_and_register_fact(
            verifier_config=verifier_bytes,
            stark_proof=proof_bytes
        )
        l2_verified_at = datetime.utcnow() if l2_verified else None
        if l2_verified:
            logger.info(f"✅ Integrity verification PASSED")
        else:
            logger.warning(f"⚠️ Integrity verification FAILED")
    else:
        attempted_full = True
        logger.warning(f"No structured proof or raw bytes available, attempting L2 verification only with fact_hash: {fact_hash[:20]}...")
        try:
            l2_verified = await integrity.verify_proof_on_l2(fact_hash)
            l2_verified_at = datetime.utcnow() if l2_verified else None
            if not l2_verified:
                verification_error = "L2 verification failed"
                logger.warning(f"⚠️ L2 verification FAILED for fact_hash {fact_hash[:20]}...")
            else:
                logger.info(f"✅ L2 verification PASSED for fact_hash {fact_hash[:20]}...")
        except Exception as ver_err:
            verification_error = str(ver_err)
            l2_verified = False
            l2_verified_at = None
            attempted_full = True
            logger.error(f"L2 verification exception: {ver_err}", exc_info=True)

    proof_status = ProofStatus.VERIFIED if l2_verified else ProofStatus.FAILED if attempted_full else ProofStatus.GENERATED
    proof_source = "luminair_mock" if getattr(luminair, "use_mock", False) else "luminair"

    metrics_payload = {
        "jediswap": request.jediswap_metrics.dict(),
        "ekubo": request.ekubo_metrics.dict(),
        "jediswap_risk": proof.output_score_jediswap,
        "ekubo_risk": proof.output_score_ekubo,
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
        "proof_data_size_bytes": len(proof.proof_data) if proof.proof_data else 0,
        "proof_source": proof_source,
        "verification_error": verification_error,
    }
    if snapshot:
        metrics_payload["snapshot"] = snapshot
    if extra_metrics:
        metrics_payload.update(extra_metrics)

    proof_job = ProofJob(
        proof_hash=proof.proof_hash,
        status=proof_status,
        fact_hash=fact_hash,
        l2_fact_hash=fact_hash,
        l2_verified_at=l2_verified_at,
        proof_source=proof_source,
        network=settings.STARKNET_NETWORK,
        metrics=metrics_payload,
        proof_data=proof.proof_data,
        error=verification_error,
        jediswap_risk=proof.output_score_jediswap,
        ekubo_risk=proof.output_score_ekubo,
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
        
        # STEP 1: Generate STARK Proof
        logger.info(f"🔐 Generating STARK proof...")
        proof_start_time = time.time()
        luminair = get_luminair_service()
        proof = await luminair.generate_proof(
            request.jediswap_metrics.dict(),
            request.ekubo_metrics.dict()
        )
        proof_generation_time = time.time() - proof_start_time
        logger.info(f"✅ Proof generated: {proof.proof_hash[:32]}...")
        logger.info(f"   Jediswap risk: {proof.output_score_jediswap}")
        logger.info(f"   Ekubo risk: {proof.output_score_ekubo}")
        logger.info(f"   Generation time: {proof_generation_time:.2f}s")

        # zkML demo inference (tiny linear model)
        zkml = get_zkml_service()
        zkml_jedi = zkml.infer_protocol(request.jediswap_metrics.dict())
        zkml_ekubo = zkml.infer_protocol(request.ekubo_metrics.dict())
        
        # STEP 2: Calculate fact hash and verify on L2 (Integrity Verifier)
        fact_hash = proof.fact_hash or (
            luminair.calculate_fact_hash(proof.proof_data or b"") if proof.proof_data else None
        )
        if not fact_hash:
            if settings.ALLOW_FAKE_FACT_HASH:
                fact_hash = luminair.calculate_fact_hash(proof.proof_data or b"")
                logger.warning("Using fallback fact hash (stub) because LuminAIR did not emit one")
            else:
                raise HTTPException(status_code=500, detail="No fact hash from LuminAIR; set ALLOW_FAKE_FACT_HASH=True to override")
        integrity = get_integrity_service()
        l2_verified = False
        l2_verified_at = None
        verification_error = None
        skip_integrity = bool(getattr(luminair, "use_mock", False))

        # Prefer structured Integrity payloads, then bytes; else fall back to hash check
        verifier_struct = None
        proof_struct = None
        verifier_bytes = None
        proof_bytes = None

        # Structured JSON from operator
        if getattr(proof, "verifier_config_json", None) and getattr(proof, "stark_proof_json", None):
            verifier_struct = proof.verifier_config_json
            proof_struct = proof.stark_proof_json
        else:
            # Try base64 JSON if format matches
            if getattr(proof, "verifier_payload_format", None) == "integrity_json":
                import base64
                import json as pyjson
                try:
                    if proof.verifier_config_b64:
                        verifier_struct = pyjson.loads(base64.b64decode(proof.verifier_config_b64))
                    if proof.stark_proof_b64:
                        proof_struct = pyjson.loads(base64.b64decode(proof.stark_proof_b64))
                except Exception as decode_err:
                    logger.warning(f"Could not decode Integrity JSON payloads: {decode_err}")

        # Bytes fallback
        try:
            if proof.verifier_config_path:
                from pathlib import Path
                verifier_bytes = Path(proof.verifier_config_path).read_bytes()
            if proof.stark_proof_path:
                from pathlib import Path
                proof_bytes = Path(proof.stark_proof_path).read_bytes()
        except Exception as read_err:
            logger.warning(f"Could not read verifier/proof blobs: {read_err}")

        attempted_full = False
        if skip_integrity:
            verification_error = "Integrity verification skipped (mock proof)"
        elif verifier_struct and proof_struct:
            attempted_full = True
            l2_verified = await integrity.verify_proof_full_and_register_fact(
                verifier_config=verifier_struct,
                stark_proof=proof_struct
            )
            l2_verified_at = datetime.utcnow() if l2_verified else None
        elif verifier_bytes and proof_bytes:
            attempted_full = True
            l2_verified = await integrity.verify_proof_full_and_register_fact(
                verifier_config=verifier_bytes,
                stark_proof=proof_bytes
            )
            l2_verified_at = datetime.utcnow() if l2_verified else None
        else:
            attempted_full = True
            try:
                l2_verified = await integrity.verify_proof_on_l2(fact_hash)
                l2_verified_at = datetime.utcnow() if l2_verified else None
                if not l2_verified:
                    verification_error = "L2 verification failed"
            except Exception as ver_err:
                verification_error = str(ver_err)
                l2_verified = False
                l2_verified_at = None
                attempted_full = True
        
        # STEP 3: Store proof in database with verification metadata
        proof_status = ProofStatus.VERIFIED if l2_verified else ProofStatus.FAILED if attempted_full else ProofStatus.GENERATED
        proof_source = "luminair_mock" if getattr(luminair, "use_mock", False) else "luminair"
        proof_job = ProofJob(
            proof_hash=proof.proof_hash,
            status=proof_status,
            fact_hash=fact_hash,
            l2_fact_hash=fact_hash,
            l2_verified_at=l2_verified_at,
            proof_source=proof_source,
            network=settings.STARKNET_NETWORK,
            metrics={
                "jediswap": request.jediswap_metrics.dict(),
                "ekubo": request.ekubo_metrics.dict(),
                "jediswap_risk": proof.output_score_jediswap,
                "ekubo_risk": proof.output_score_ekubo,
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
                "proof_data_size_bytes": len(proof.proof_data) if proof.proof_data else 0,
                "proof_source": proof_source,
                "verification_error": verification_error
            },
            proof_data=proof.proof_data,
            error=verification_error
        )
        db.add(proof_job)
        db.commit()
        db.refresh(proof_job)
        logger.info(f"💾 Proof stored in database (ID: {proof_job.id})")
        
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
        
        # Serialize structs to calldata manually
        # ProtocolMetrics struct: (utilization, volatility, liquidity, audit_score, age_days)
        calldata = [
            # jediswap_metrics struct
            jediswap_metrics['utilization'],
            jediswap_metrics['volatility'],
            jediswap_metrics['liquidity'],
            jediswap_metrics['audit_score'],
            jediswap_metrics['age_days'],
            # ekubo_metrics struct
            ekubo_metrics['utilization'],
            ekubo_metrics['volatility'],
            ekubo_metrics['liquidity'],
            ekubo_metrics['audit_score'],
            ekubo_metrics['age_days'],
        ]
        
        logger.info(f"📝 Calldata: {calldata}")
        
        # Execute via account
        from starknet_py.net.client_models import Call
        
        call = Call(
            to_addr=int(settings.RISK_ENGINE_ADDRESS, 16),
            selector=selector,
            calldata=calldata
        )
        
        rpc_urls = get_rpc_urls()

        # Use v3 invoke with manual resource bounds (avoid estimate_fee + unsupported block tags).
        async def _submit_with_client_v3(client: FullNodeClient, _rpc_url: str):
            account = await _init_backend_account(client, key_pair, network_chain)
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
        # Set verified_at if proof was verified locally
        if proof.verified and not proof_job.verified_at:
            proof_job.verified_at = datetime.utcnow()
        db.commit()
        db.refresh(proof_job)
        
        # Optional L1 settlement (Atlantic) for Sepolia or when enabled
        if settings.STARKNET_NETWORK.lower() == "sepolia":
            atlantic = get_atlantic_service()
            if atlantic:
                try:
                    trace_path = await luminair.export_trace(
                        request.jediswap_metrics.dict(),
                        request.ekubo_metrics.dict(),
                        proof_data=proof.proof_data,
                        trace_path=proof.trace_path
                    )
                    submission = await atlantic.submit_trace_for_l1_verification(trace_path)
                    proof_job.l1_settlement_enabled = True
                    proof_job.atlantic_query_id = submission.query_id
                    proof_job.l1_fact_hash = fact_hash
                    db.commit()
                    db.refresh(proof_job)
                    enqueue_atlantic_status_check(submission.query_id, proof_job.id)
                except Exception as atl_err:
                    logger.warning(f"⚠️ Atlantic submission failed (non-blocking): {atl_err}")
            else:
                logger.info("Atlantic service not configured; skipping L1 submission")
        
        # Trigger background SHARP submission (non-blocking, won't affect orchestration response)
        # Note: SHARP submission is optional - MVP uses mock proofs, real SHARP integration coming
        if proof.proof_data:
            logger.info(f"📡 Triggering SHARP submission (background)...")
            try:
                asyncio.create_task(submit_proof_to_sharp(
                    job_id=proof_job.id,
                    proof_data=proof.proof_data,
                    proof_hash=proof.proof_hash
                ))
            except Exception as e:
                logger.warning(f"⚠️ SHARP submission task creation failed (non-critical): {e}")
                # Don't fail orchestration if SHARP submission setup fails
        else:
            logger.info(f"⏭️ Skipping SHARP submission (proof_data not available - MVP mode)")
        
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
                    proof_hash=proof.proof_hash,
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
        if not can_execute and settings.ALLOW_UNVERIFIED_EXECUTION:
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
    if not can_execute and settings.ALLOW_UNVERIFIED_EXECUTION:
        can_execute = True

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
        if not can_execute and settings.ALLOW_UNVERIFIED_EXECUTION:
            can_execute = True

        if not can_execute:
            raise HTTPException(status_code=400, detail="Proof not verified. Execution blocked.")

        # Build orchestration request from stored metrics
        metrics = proof_job.metrics or {}
        jediswap_metrics = metrics.get("jediswap", {})
        ekubo_metrics = metrics.get("ekubo", {})

        orchestration_request = OrchestrationRequest(
            jediswap_metrics=RiskMetricsRequest(**jediswap_metrics),
            ekubo_metrics=RiskMetricsRequest(**ekubo_metrics),
        )

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

        from starknet_py.hash.selector import get_selector_from_name
        selector = get_selector_from_name("propose_and_execute_allocation")

        calldata = [
            orchestration_request.jediswap_metrics.utilization,
            orchestration_request.jediswap_metrics.volatility,
            orchestration_request.jediswap_metrics.liquidity,
            orchestration_request.jediswap_metrics.audit_score,
            orchestration_request.jediswap_metrics.age_days,
            orchestration_request.ekubo_metrics.utilization,
            orchestration_request.ekubo_metrics.volatility,
            orchestration_request.ekubo_metrics.liquidity,
            orchestration_request.ekubo_metrics.audit_score,
            orchestration_request.ekubo_metrics.age_days,
        ]

        from starknet_py.net.client_models import Call
        call = Call(
            to_addr=int(settings.RISK_ENGINE_ADDRESS, 16),
            selector=selector,
            calldata=calldata
        )

        rpc_urls = get_rpc_urls()

        # Use v3 invoke with manual resource bounds (avoid estimate_fee + unsupported block tags).
        async def _submit_with_client_v3(client: FullNodeClient, _rpc_url: str):
            account = await _init_backend_account(client, key_pair, network_chain)
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
