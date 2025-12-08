"""
Proof job tracking model for SHARP verification
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, JSON, LargeBinary, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from pydantic import BaseModel

from app.db.base_class import Base


class ProofStatus(str, Enum):
    """Status of proof generation and verification"""
    GENERATING = "generating"
    GENERATED = "generated"
    SUBMITTED = "submitted"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ProofJob(Base):
    """
    Database model for tracking STARK proof generation and SHARP verification
    """
    __tablename__ = "proof_jobs"

    id = Column(PostgreSQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tx_hash = Column(String, nullable=True, index=True)
    proof_hash = Column(String, nullable=False, index=True)
    sharp_job_id = Column(String, nullable=True, index=True)
    fact_hash = Column(String, nullable=True)
    
    status = Column(
        SQLEnum(ProofStatus),
        nullable=False,
        default=ProofStatus.GENERATING,
        index=True
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Data
    metrics = Column(JSON, nullable=False)  # Input protocol metrics
    proof_data = Column(LargeBinary, nullable=True)  # Binary STARK proof
    error = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<ProofJob {self.id} status={self.status}>"


# Pydantic schemas for API

class ProofMetrics(BaseModel):
    """Protocol metrics used as proof inputs"""
    utilization: int
    volatility: int
    liquidity: int
    audit_score: int
    age_days: int


class ProofJobCreate(BaseModel):
    """Create new proof job"""
    jediswap_metrics: ProofMetrics
    ekubo_metrics: ProofMetrics


class ProofJobResponse(BaseModel):
    """Proof job API response"""
    id: UUID
    tx_hash: Optional[str]
    proof_hash: str
    sharp_job_id: Optional[str]
    fact_hash: Optional[str]
    status: ProofStatus
    created_at: datetime
    submitted_at: Optional[datetime]
    verified_at: Optional[datetime]
    elapsed_seconds: Optional[int]
    estimated_completion: Optional[int]
    verification_url: Optional[str]
    
    class Config:
        from_attributes = True


class ProofStatsResponse(BaseModel):
    """Proof statistics"""
    generating: int
    verifying: int
    verified: int
    failed: int
    total: int


class ProofListResponse(BaseModel):
    """List of proof jobs with stats"""
    proofs: list[ProofJobResponse]
    stats: ProofStatsResponse

