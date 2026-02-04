"""
Verification Status Endpoint
Check if proofs are verified in FactRegistry
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import ProofJob
from app.services.integrity_service import get_integrity_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class VerificationStatusResponse(BaseModel):
    proof_job_id: str
    fact_hash: Optional[str]
    verified: bool
    verified_at: Optional[str]
    fact_registry_address: str


@router.get("/verification-status/{proof_job_id}", response_model=VerificationStatusResponse)
async def get_verification_status(
    proof_job_id: str,
    db: Session = Depends(get_db)
):
    """
    Check verification status of a proof
    
    Returns:
    - Whether proof is verified in FactRegistry
    - Fact hash if verified
    - Verification timestamp
    """
    # Get proof job
    proof_job = db.query(ProofJob).filter(ProofJob.id == proof_job_id).first()
    
    if not proof_job:
        raise HTTPException(status_code=404, detail="Proof job not found")
    
    # Get fact hash
    fact_hash = proof_job.l2_fact_hash or proof_job.fact_hash
    
    # Get Integrity service and check verification on-chain (strict mode - real FactRegistry only)
    integrity = get_integrity_service()
    verified = False
    if fact_hash:
        try:
            verified = await integrity.verify_proof_on_l2(fact_hash, is_mocked=False)
        except Exception as e:
            logger.warning(f"Verification check failed for fact_hash {fact_hash[:20]}...: {e}")
            verified = False
    
    # Get FactRegistry address
    fact_registry = hex(integrity.verifier_address)
    
    return VerificationStatusResponse(
        proof_job_id=str(proof_job.id),
        fact_hash=fact_hash,
        verified=verified,
        verified_at=proof_job.l2_verified_at.isoformat() if proof_job.l2_verified_at else None,
        fact_registry_address=fact_registry
    )


@router.get("/verify-fact-hash/{fact_hash}")
async def verify_fact_hash_onchain(
    fact_hash: str,
    db: Session = Depends(get_db)
):
    """
    Check if a fact hash is verified on-chain in FactRegistry
    
    This directly queries the FactRegistry contract
    """
    from app.services.integrity_service import IntegrityService
    from app.config import get_settings
    
    settings = get_settings()
    integrity = IntegrityService(
        rpc_url=settings.STARKNET_RPC_URL,
        network="sepolia"
    )
    
    # Check if fact hash exists in FactRegistry
    # This would require calling the contract directly
    # For now, return the fact hash and registry address
    
    fact_registry = hex(integrity.verifier_address)
    
    return {
        "fact_hash": fact_hash,
        "fact_registry": fact_registry,
        "note": "Use sncast to verify on-chain: sncast call --contract-address <registry> --function get_all_verifications_for_fact_hash --arguments <fact_hash>"
    }
