"""
Proof generation and SHARP verification API endpoints
"""
import logging
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.luminair_service import get_luminair_service

logger = logging.getLogger(__name__)
router = APIRouter()


class ProtocolMetrics(BaseModel):
    """Protocol risk metrics"""
    utilization: int = Field(..., description="Utilization in basis points (0-10000)")
    volatility: int = Field(..., description="Volatility in basis points (0-10000)")
    liquidity: int = Field(..., description="Liquidity tier (1-3)")
    audit_score: int = Field(..., description="Audit score (0-100)")
    age_days: int = Field(..., description="Age in days")


class ProofGenerateRequest(BaseModel):
    """Request to generate proof"""
    jediswap_metrics: ProtocolMetrics
    ekubo_metrics: ProtocolMetrics


class ProofGenerateResponse(BaseModel):
    """Response with proof generation result"""
    proof_hash: str
    jediswap_score: int
    ekubo_score: int
    status: str
    message: str


@router.post("/generate", response_model=ProofGenerateResponse, tags=["Proofs"])
async def generate_proof(request: ProofGenerateRequest):
    """
    Generate STARK proof for risk scoring
    
    This endpoint:
    1. Calculates risk scores for both protocols
    2. Generates a STARK proof of correct computation
    3. Returns proof hash and scores
    4. (Future) Submits to SHARP for L1 verification
    """
    logger.info("Received proof generation request")
    logger.info(f"Jediswap metrics: {request.jediswap_metrics.dict()}")
    logger.info(f"Ekubo metrics: {request.ekubo_metrics.dict()}")
    
    try:
        # Get proof service
        luminair = get_luminair_service()
        
        # Generate proof
        result = await luminair.generate_proof(
            request.jediswap_metrics.dict(),
            request.ekubo_metrics.dict()
        )
        
        logger.info(f"Proof generated: {result.proof_hash[:32]}...")
        
        return ProofGenerateResponse(
            proof_hash=result.proof_hash,
            jediswap_score=result.output_score_jediswap,
            ekubo_score=result.output_score_ekubo,
            status="generated",
            message="Proof generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Proof generation failed: {e}", exc_info=True)
        raise
