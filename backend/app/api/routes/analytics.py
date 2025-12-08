"""Analytics endpoints - Historical data and trends"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, RiskHistory, AllocationHistory
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/risk-history")
async def get_risk_history(
    protocol: str = Query(None),
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get historical risk scores for user."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(RiskHistory).where(
        (RiskHistory.user_id == current_user.id) &
        (RiskHistory.created_at >= cutoff_date)
    )
    
    if protocol:
        query = query.where(RiskHistory.protocol == protocol)
    
    query = query.order_by(desc(RiskHistory.created_at))
    
    result = await db.execute(query)
    histories = result.scalars().all()
    
    return [
        {
            "protocol": h.protocol,
            "risk_score": h.risk_score,
            "utilization": h.utilization,
            "volatility": h.volatility,
            "timestamp": h.created_at,
        }
        for h in histories
    ]


@router.get("/allocation-history")
async def get_allocation_history(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get historical allocation snapshots."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(AllocationHistory).where(
        (AllocationHistory.user_id == current_user.id) &
        (AllocationHistory.created_at >= cutoff_date)
    ).order_by(desc(AllocationHistory.created_at))
    
    result = await db.execute(query)
    histories = result.scalars().all()
    
    return [
        {
            "nostra_pct": h.nostra_pct,
            "zklend_pct": h.zklend_pct,
            "ekubo_pct": h.ekubo_pct,
            "reason": h.reason,
            "tx_hash": h.tx_hash,
            "timestamp": h.created_at,
        }
        for h in histories
    ]


@router.get("/dashboard")
async def get_dashboard_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics and trends."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get latest allocation
    allocation_query = select(AllocationHistory).where(
        AllocationHistory.user_id == current_user.id
    ).order_by(desc(AllocationHistory.created_at)).limit(1)
    
    allocation_result = await db.execute(allocation_query)
    latest_allocation = allocation_result.scalars().first()
    
    # Get risk scores for each protocol
    risk_query = select(RiskHistory).where(
        (RiskHistory.user_id == current_user.id) &
        (RiskHistory.created_at >= cutoff_date)
    ).order_by(RiskHistory.protocol, desc(RiskHistory.created_at))
    
    risk_result = await db.execute(risk_query)
    risk_histories = risk_result.scalars().all()
    
    return {
        "latest_allocation": {
            "nostra_pct": latest_allocation.nostra_pct if latest_allocation else 0,
            "zklend_pct": latest_allocation.zklend_pct if latest_allocation else 0,
            "ekubo_pct": latest_allocation.ekubo_pct if latest_allocation else 0,
        } if latest_allocation else None,
        "risk_scores": [
            {"protocol": h.protocol, "score": h.risk_score, "timestamp": h.created_at}
            for h in risk_histories
        ],
        "period_days": days,
    }

