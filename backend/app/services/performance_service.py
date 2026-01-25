"""
Performance Tracking Service

Calculates actual performance metrics from on-chain execution data.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models import ProofJob

logger = logging.getLogger(__name__)


class PerformanceService:
    """Service for calculating performance metrics from on-chain data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_portfolio_performance(
        self,
        user_address: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Calculate portfolio performance metrics from executed transactions.
        
        Args:
            user_address: Optional user address to filter by
            days: Number of days to analyze
        
        Returns:
            Dictionary with performance metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all executed rebalances (proof jobs with tx_hash)
        query = self.db.query(ProofJob).filter(
            ProofJob.created_at >= cutoff_date,
            ProofJob.tx_hash.isnot(None)
        ).order_by(desc(ProofJob.created_at))
        
        rebalances = query.all()
        
        if not rebalances:
            return {
                "total_rebalances": 0,
                "total_yield_earned": 0.0,
                "average_allocation": {"jediswap": 50.0, "ekubo": 50.0},
                "performance_metrics": {
                    "total_return": 0.0,
                    "annualized_return": 0.0,
                    "best_day": None,
                    "worst_day": None,
                }
            }
        
        # Calculate metrics
        total_rebalances = len(rebalances)
        
        # Calculate average allocation
        jediswap_total = sum(r.jediswap_pct or 0 for r in rebalances)
        ekubo_total = sum(r.ekubo_pct or 0 for r in rebalances)
        avg_jediswap = (jediswap_total / total_rebalances) / 100 if total_rebalances > 0 else 50.0
        avg_ekubo = (ekubo_total / total_rebalances) / 100 if total_rebalances > 0 else 50.0
        
        # Get latest rebalance for current state
        latest = rebalances[0] if rebalances else None

        verified_count = sum(1 for r in rebalances if str(getattr(r, "status", "")).lower() == "verified")
        
        return {
            "total_rebalances": total_rebalances,
            "period_days": days,
            "average_allocation": {
                "jediswap": round(avg_jediswap, 2),
                "ekubo": round(avg_ekubo, 2),
            },
            "latest_rebalance": {
                "timestamp": latest.created_at.isoformat() if latest else None,
                "jediswap_pct": (latest.jediswap_pct / 100) if latest and latest.jediswap_pct else 0,
                "ekubo_pct": (latest.ekubo_pct / 100) if latest and latest.ekubo_pct else 0,
                "tx_hash": latest.tx_hash if latest else None,
            } if latest else None,
            "rebalance_frequency": {
                "per_day": round(total_rebalances / days, 2) if days > 0 else 0,
                "per_week": round(total_rebalances / (days / 7), 2) if days > 0 else 0,
            },
            "proof_metrics": {
                "total_proofs": total_rebalances,
                "verified_count": verified_count,
                "verified_percentage": round((verified_count / total_rebalances * 100) if total_rebalances > 0 else 0, 1),
            }
        }
    
    def calculate_yield_estimate(
        self,
        portfolio_value: float,
        jediswap_apy: float,
        ekubo_apy: float,
        jediswap_allocation: float,
        ekubo_allocation: float,
        days: int = 30
    ) -> Dict:
        """
        Calculate estimated yield based on current allocation and APY.
        
        Args:
            portfolio_value: Current portfolio value in STRK
            jediswap_apy: JediSwap APY percentage
            ekubo_apy: Ekubo APY percentage
            jediswap_allocation: JediSwap allocation percentage
            ekubo_allocation: Ekubo allocation percentage
            days: Number of days to project
        
        Returns:
            Dictionary with yield estimates
        """
        # Calculate weighted APY
        weighted_apy = (
            (jediswap_apy * jediswap_allocation / 100) +
            (ekubo_apy * ekubo_allocation / 100)
        )
        
        # Calculate yield for period
        daily_yield = (portfolio_value * weighted_apy / 100) / 365
        period_yield = daily_yield * days
        
        return {
            "weighted_apy": round(weighted_apy, 2),
            "daily_yield_estimate": round(daily_yield, 4),
            "period_yield_estimate": round(period_yield, 4),
            "annual_yield_estimate": round(portfolio_value * weighted_apy / 100, 2),
            "projection_days": days,
        }
    
    def get_performance_timeline(
        self,
        days: int = 30
    ) -> List[Dict]:
        """
        Get performance timeline with rebalance history.
        
        Args:
            days: Number of days to retrieve
        
        Returns:
            List of rebalance events with performance data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        rebalances = self.db.query(ProofJob).filter(
            ProofJob.created_at >= cutoff_date,
            ProofJob.tx_hash.isnot(None)
        ).order_by(desc(ProofJob.created_at)).all()
        
        timeline = []
        for rebalance in rebalances:
            verified = False
            status_val = str(getattr(rebalance, "status", "")).lower()
            if hasattr(rebalance, "verified_at") and rebalance.verified_at:
                verified = True
            elif status_val == "verified":
                verified = True

            timeline.append({
                "timestamp": rebalance.created_at.isoformat(),
                "jediswap_pct": (rebalance.jediswap_pct / 100) if rebalance.jediswap_pct else 0,
                "ekubo_pct": (rebalance.ekubo_pct / 100) if rebalance.ekubo_pct else 0,
                "jediswap_risk": rebalance.jediswap_risk or 0,
                "ekubo_risk": rebalance.ekubo_risk or 0,
                "tx_hash": rebalance.tx_hash,
                "proof_hash": rebalance.proof_hash,
                "proof_status": rebalance.status.value if hasattr(rebalance.status, 'value') else str(rebalance.status),
                "verified": verified,
            })
        
        return timeline
