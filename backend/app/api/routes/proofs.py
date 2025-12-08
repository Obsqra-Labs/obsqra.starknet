"""
Proofs API endpoints for verifiable AI computations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.proof_generator import ProofGenerator, ProofData

router = APIRouter()


class RiskScoreRequest(BaseModel):
    """Request to generate risk score proof"""
    utilization: int = Field(..., ge=0, le=10000, description="Utilization in basis points")
    volatility: int = Field(..., ge=0, le=10000, description="Volatility in basis points")
    liquidity: int = Field(..., ge=0, le=3, description="Liquidity category (0-3)")
    audit_score: int = Field(..., ge=0, le=100, description="Audit score (0-100)")
    age_days: int = Field(..., ge=0, description="Protocol age in days")


class AllocationRequest(BaseModel):
    """Request to generate allocation proof"""
    jediswap_risk: int = Field(..., ge=0, description="JediSwap risk score")
    ekubo_risk: int = Field(..., ge=0, description="Ekubo risk score")
    jediswap_apy: int = Field(..., ge=0, description="JediSwap APY in basis points")
    ekubo_apy: int = Field(..., ge=0, description="Ekubo APY in basis points")


class ProofResponse(BaseModel):
    """Response containing proof data"""
    proof: ProofData
    verified: bool
    message: str


@router.post("/risk-score", response_model=ProofResponse, tags=["Proofs"])
async def generate_risk_score_proof(request: RiskScoreRequest):
    """
    Generate a SHARP proof for risk score computation.
    
    This proves that the risk score was calculated correctly given the inputs.
    The proof can be verified on-chain.
    
    **Computation Logic:**
    - Utilization Risk = (utilization * 25) / 10000
    - Volatility Risk = (volatility * 40) / 10000
    - Liquidity Risk = categorical mapping
    - Audit Risk = ((100 - audit_score) * 3) / 10
    - Age Risk = max(0, (730 - age_days) * 10 / 730)
    - Total Risk = sum of all risks, clipped to [5, 95]
    """
    try:
        proof = await ProofGenerator.generate_risk_proof(
            utilization=request.utilization,
            volatility=request.volatility,
            liquidity=request.liquidity,
            audit_score=request.audit_score,
            age_days=request.age_days,
        )

        # Verify the proof
        verified = await ProofGenerator.verify_proof(proof)

        return ProofResponse(
            proof=proof,
            verified=verified,
            message=f"Risk score proof generated. Risk Score: {proof.computation_trace['total_risk']}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof generation failed: {str(e)}")


@router.post(
    "/allocation", response_model=ProofResponse, tags=["Proofs"]
)
async def generate_allocation_proof(request: AllocationRequest):
    """
    Generate a SHARP proof for allocation computation.
    
    This proves that the optimal allocation was calculated correctly
    based on risk-adjusted scoring: (APY * 10000) / (Risk + 1)
    
    The allocation percentages (in basis points) are calculated as:
    - Protocol% = (ProtocolScore * 10000) / TotalScore
    
    The result always sums to 10000 (100%).
    """
    try:
        proof = await ProofGenerator.generate_allocation_proof(
            jediswap_risk=request.jediswap_risk,
            ekubo_risk=request.ekubo_risk,
            jediswap_apy=request.jediswap_apy,
            ekubo_apy=request.ekubo_apy,
        )

        # Verify the proof
        verified = await ProofGenerator.verify_proof(proof)

        outputs = proof.computation_trace["outputs"]
        jediswap_pct = outputs.get("jediswap_pct", 0)
        ekubo_pct = outputs.get("ekubo_pct", 0)
        return ProofResponse(
            proof=proof,
            verified=verified,
            message=f"Allocation proof generated from contract. Allocation: JediSwap {jediswap_pct/100:.2f}%, Ekubo {ekubo_pct/100:.2f}%",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof generation failed: {str(e)}")


@router.post("/v1/proofs/verify", tags=["Proofs"])
async def verify_proof(proof: ProofData):
    """
    Verify an existing proof.
    
    Returns whether the proof computation matches the trace.
    In production, this would also verify against the SHARP proof ledger.
    """
    try:
        verified = await ProofGenerator.verify_proof(proof)
        return {
            "proof_id": proof.proof_id,
            "verified": verified,
            "computation_type": proof.computation_type,
            "timestamp": proof.timestamp,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof verification failed: {str(e)}")

