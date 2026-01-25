"""zkML demo endpoints."""
from fastapi import APIRouter
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
async def zkml_verify_demo():
    """
    Verify a precomputed zkML proof via Integrity.

    Uses either:
    - ZKML_PROOF_CALLDATA_PATH (preferred), or
    - ZKML_PROOF_JSON_PATH + INTEGRITY_PROOF_SERIALIZER_BIN
    """
    integrity = get_integrity_service()
    config = ZkmlProofConfig(
        proof_json_path=Path(settings.ZKML_PROOF_JSON_PATH) if settings.ZKML_PROOF_JSON_PATH else None,
        calldata_path=Path(settings.ZKML_PROOF_CALLDATA_PATH) if settings.ZKML_PROOF_CALLDATA_PATH else None,
        serializer_bin=Path(settings.INTEGRITY_PROOF_SERIALIZER_BIN) if settings.INTEGRITY_PROOF_SERIALIZER_BIN else None,
    )
    service = ZkmlProofService(integrity=integrity, config=config)
    verified = await service.verify_demo()
    return {
        "verified": verified,
        "calldata_source": "file" if config.calldata_path else "serialized" if config.proof_json_path else "missing",
    }
