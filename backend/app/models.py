"""SQLAlchemy Models for Obsqra"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    wallet_address = Column(String, unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    risk_histories = relationship("RiskHistory", back_populates="user", cascade="all, delete-orphan")
    allocation_histories = relationship("AllocationHistory", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")


class RiskHistory(Base):
    """Historical risk scores for protocols."""
    
    __tablename__ = "risk_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    protocol = Column(String, nullable=False, index=True)  # nostra, zklend, ekubo
    risk_score = Column(Float, nullable=False)
    utilization = Column(Float)
    volatility = Column(Float)
    liquidity = Column(Integer)
    audit_score = Column(Float)
    age_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="risk_histories")


class AllocationHistory(Base):
    """Historical allocation snapshots."""
    
    __tablename__ = "allocation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    nostra_pct = Column(Float, nullable=False)
    zklend_pct = Column(Float, nullable=False)
    ekubo_pct = Column(Float, nullable=False)
    reason = Column(String)  # 'user_initiated', 'auto_rebalance', 'optimization'
    tx_hash = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="allocation_histories")


class Transaction(Base):
    """User transaction log."""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tx_hash = Column(String, unique=True, index=True, nullable=False)
    tx_type = Column(String, nullable=False)  # deposit, withdraw, allocate, rebalance
    amount = Column(Float, nullable=True)
    status = Column(String, default="pending")  # pending, confirmed, failed
    details = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class Prediction(Base):
    """ML predictions and optimizations."""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prediction_type = Column(String, nullable=False)  # risk_forecast, yield_forecast, rebalance_suggestion
    protocol = Column(String, nullable=True)
    predicted_value = Column(Float, nullable=False)
    confidence_score = Column(Float)  # 0.0-1.0
    actual_value = Column(Float, nullable=True)
    model_version = Column(String, default="v1")
    details = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")


class AnalyticsCache(Base):
    """Cache for expensive analytics computations."""
    
    __tablename__ = "analytics_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    cache_key = Column(String, unique=True, nullable=False, index=True)
    cache_value = Column(JSON, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    
    # Allocation decision results (from on-chain execution)
    jediswap_pct = Column(Integer, nullable=True, default=0)  # Basis points (0-10000)
    ekubo_pct = Column(Integer, nullable=True, default=0)  # Basis points (0-10000)
    jediswap_risk = Column(Integer, nullable=True, default=0)
    ekubo_risk = Column(Integer, nullable=True, default=0)
    
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

