"""zkML demo endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.zkml_service import get_zkml_service

router = APIRouter()


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
