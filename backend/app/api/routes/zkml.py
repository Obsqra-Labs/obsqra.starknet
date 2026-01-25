"""zkML demo endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.zkml_service import get_zkml_service
from app.services.integrity_service import get_integrity_service
from app.services.zkml_proof_service import ZkmlProofService, ZkmlProofConfig
from app.config import get_settings
from pathlib import Path

router = APIRouter()
settings = get_settings()


class ProtocolMetrics(BaseModel):
    utilization: int = Field(..., ge=0, le=10000)
    volatility: int = Field(..., ge=0, le=10000)
    liquidity: int = Field(..., ge=0, le=3)
    audit_score: int = Field(..., ge=0, le=100)
    age_days: int = Field(..., ge=0)


class ZkmlRequest(BaseModel):
    jediswap_metrics: ProtocolMetrics
    ekubo_metrics: ProtocolMetrics


@router.post("/infer", tags=["zkML"])
async def zkml_infer(request: ZkmlRequest):
    """
    Run the tiny zkML demo model (linear classifier).
    Returns score + decision for each protocol.
    """
    zkml = get_zkml_service()

    jedi = zkml.infer_protocol(request.jediswap_metrics.dict())
    ekubo = zkml.infer_protocol(request.ekubo_metrics.dict())

    return {
        "model": "linear_v0",
        "threshold": jedi.threshold,
        "jediswap": {
            "score": jedi.score,
            "decision": jedi.decision,
            "components": jedi.components,
        },
        "ekubo": {
            "score": ekubo.score,
            "decision": ekubo.decision,
            "components": ekubo.components,
        },
    }


@router.post("/verify-demo", tags=["zkML"])
async def zkml_verify_demo(profile: str = Query("cairo0", description="Proof profile: cairo0 | cairo1")):
    """
    Verify a precomputed zkML proof via Integrity.

    Uses either:
    - ZKML_PROOF_CALLDATA_PATH_* (preferred), or
    - ZKML_PROOF_JSON_PATH + INTEGRITY_PROOF_SERIALIZER_BIN
    """
    integrity = get_integrity_service()
    normalized = profile.strip().lower()
    if normalized not in {"cairo0", "cairo1"}:
        raise HTTPException(status_code=400, detail="Invalid profile. Use cairo0 or cairo1.")

    def resolve_path(primary: str, fallback: str) -> Path | None:
        if primary:
            return Path(primary)
        if fallback:
            candidate = Path(fallback)
            return candidate if candidate.exists() else None
        return None

    if normalized == "cairo1":
        calldata_default = "data/zkml_demo_cairo1.calldata"
        json_default = ""
        calldata_path = resolve_path(
            settings.ZKML_PROOF_CALLDATA_PATH_CAIRO1 or settings.ZKML_PROOF_CALLDATA_PATH,
            calldata_default,
        )
        proof_json_path = resolve_path(
            settings.ZKML_PROOF_JSON_PATH_CAIRO1 or settings.ZKML_PROOF_JSON_PATH,
            json_default,
        )
        memory_verification = "cairo1"
    else:
        calldata_default = "data/zkml_demo_cairo0.calldata"
        json_default = ""
        calldata_path = resolve_path(
            settings.ZKML_PROOF_CALLDATA_PATH_CAIRO0 or settings.ZKML_PROOF_CALLDATA_PATH,
            calldata_default,
        )
        proof_json_path = resolve_path(
            settings.ZKML_PROOF_JSON_PATH_CAIRO0 or settings.ZKML_PROOF_JSON_PATH,
            json_default,
        )
        memory_verification = settings.INTEGRITY_MEMORY_VERIFICATION

    config = ZkmlProofConfig(
        proof_json_path=proof_json_path,
        calldata_path=calldata_path,
        serializer_bin=Path(settings.INTEGRITY_PROOF_SERIALIZER_BIN) if settings.INTEGRITY_PROOF_SERIALIZER_BIN else None,
        layout=settings.INTEGRITY_LAYOUT,
        hasher=settings.INTEGRITY_HASHER,
        stone_version=settings.INTEGRITY_STONE_VERSION,
        memory_verification=memory_verification,
    )
    if not config.calldata_path and not config.proof_json_path:
        return {"verified": False, "calldata_source": "missing", "detail": "ZKML proof paths not configured", "profile": normalized}
    service = ZkmlProofService(integrity=integrity, config=config)
    try:
        verified = await service.verify_demo()
    except FileNotFoundError as exc:
        return {"verified": False, "calldata_source": "missing", "detail": str(exc), "profile": normalized}
    return {
        "verified": verified,
        "calldata_source": "file" if config.calldata_path else "serialized" if config.proof_json_path else "missing",
        "profile": normalized,
    }
