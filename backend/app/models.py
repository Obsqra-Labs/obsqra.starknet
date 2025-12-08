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

