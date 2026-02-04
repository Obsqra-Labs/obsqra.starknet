"""
Proof generation API endpoints (Stone-only, strict verification)
"""
import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.zkml_service import get_zkml_service
from app.services.risk_model import calculate_risk_score
from app.api.routes.risk_engine import _stone_integrity_fact_for_metrics
from app.services.integrity_service import get_integrity_service

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
    fact_hash: str
    jediswap_score: int
    ekubo_score: int
    zkml: dict | None = None
    status: str
    message: str
    verified: bool


@router.post("/generate", response_model=ProofGenerateResponse, tags=["Proofs"])
async def generate_proof(request: ProofGenerateRequest):
    """
    Generate STARK proof for risk scoring using Stone prover (strict, no mocks)
    
    This endpoint:
    1. Calculates risk scores for both protocols (deterministic model)
    2. Generates a STARK proof using Stone prover
    3. Registers proof with Integrity FactRegistry
    4. Returns proof hash, fact hash, and verification status
    
    **Strict Mode**: This endpoint requires successful Stone proof generation and
    Integrity verification. No mock fallbacks are allowed.
    """
    logger.info("Received proof generation request (Stone-only, strict)")
    logger.info(f"Jediswap metrics: {request.jediswap_metrics.dict()}")
    logger.info(f"Ekubo metrics: {request.ekubo_metrics.dict()}")
    
    start_time = time.time()
    
    try:
        # Step 1: Calculate deterministic risk scores
        jediswap_risk, jediswap_components = calculate_risk_score(request.jediswap_metrics.dict())
        ekubo_risk, ekubo_components = calculate_risk_score(request.ekubo_metrics.dict())
        
        logger.info(f"Risk scores calculated: JediSwap={jediswap_risk}, Ekubo={ekubo_risk}")
        
        # Step 2: Generate Stone proof + register with Integrity (strict, no fallbacks)
        logger.info("Generating Stone proof and registering with Integrity...")
        try:
            stone_fact, stone_proof_path, stone_dir, stone_hash = await _stone_integrity_fact_for_metrics(
                request.jediswap_metrics.dict(),
                request.ekubo_metrics.dict(),
            )
        except Exception as e:
            logger.error(f"Stone proof generation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Stone proof generation failed",
                    "message": f"Failed to generate Stone proof or register with Integrity: {str(e)}",
                    "strict_mode": True,
                    "note": "Check logs for detailed error. Common issues: Stone prover not found, Cairo execution failed, or Integrity contract error (VERIFIER_NOT_FOUND).",
                }
            )
        
        if not stone_fact:
            logger.error("Stone proof generated but fact_hash is None - Integrity registration failed")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Stone proof registration failed",
                    "message": "No fact hash returned from Integrity registration. The proof was generated but could not be registered on-chain. Check Integrity contract address and function availability.",
                    "strict_mode": True,
                    "note": "This usually means the Integrity contract call failed (e.g., VERIFIER_NOT_FOUND). Verify the contract address and that verify_proof_full_and_register_fact function exists.",
                }
            )
        
        fact_hash = hex(stone_fact)
        proof_hash = stone_hash or fact_hash
        
        # Step 3: Verify proof is registered on-chain (strict check)
        integrity = get_integrity_service()
        verified = await integrity.verify_proof_on_l2(fact_hash, is_mocked=False)
        
        if not verified:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Proof verification failed",
                    "message": "Proof was generated but not verified on-chain in FactRegistry. This is a strict error - no fallbacks allowed.",
                    "fact_hash": fact_hash,
                    "fact_registry_address": hex(integrity.verifier_address),
                    "strict_mode": True,
                }
            )
        
        generation_time = time.time() - start_time
        
        # Step 4: zkML demo inference (for display only, not used for verification)
        zkml = get_zkml_service()
        zkml_jedi = zkml.infer_protocol(request.jediswap_metrics.dict())
        zkml_ekubo = zkml.infer_protocol(request.ekubo_metrics.dict())
        
        logger.info(f"✅ Proof generated and verified: {proof_hash[:32]}... (fact: {fact_hash[:20]}...)")
        logger.info(f"   Generation time: {generation_time:.2f}s")
        logger.info(f"   Verified on-chain: {verified}")
        
        return ProofGenerateResponse(
            proof_hash=proof_hash or "0x0",
            fact_hash=fact_hash,
            jediswap_score=jediswap_risk,
            ekubo_score=ekubo_risk,
            zkml={
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
            status="verified",
            message=f"STARK proof generated using Stone prover and verified on-chain in {generation_time:.2f}s",
            verified=True,
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Proof generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Proof generation failed",
                "message": str(e),
                "strict_mode": True,
                "note": "This endpoint requires Stone prover and Integrity verification. No mock fallbacks are available.",
            }
        )
