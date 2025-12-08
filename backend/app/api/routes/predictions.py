"""ML Predictions and Optimization endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.database import get_db
from app.models import User, Prediction
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/risk-forecast")
async def get_risk_forecast(
    protocol: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get risk forecasts for protocols."""
    query = select(Prediction).where(
        (Prediction.user_id == current_user.id) &
        (Prediction.prediction_type == "risk_forecast")
    ).order_by(desc(Prediction.created_at)).limit(10)
    
    if protocol:
        query = query.where(Prediction.protocol == protocol)
    
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    return [
        {
            "protocol": p.protocol,
            "predicted_risk": p.predicted_value,
            "confidence": p.confidence_score,
            "timestamp": p.created_at,
        }
        for p in predictions
    ]


@router.get("/yield-forecast")
async def get_yield_forecast(
    protocol: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get yield forecasts for protocols."""
    query = select(Prediction).where(
        (Prediction.user_id == current_user.id) &
        (Prediction.prediction_type == "yield_forecast")
    ).order_by(desc(Prediction.created_at)).limit(10)
    
    if protocol:
        query = query.where(Prediction.protocol == protocol)
    
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    return [
        {
            "protocol": p.protocol,
            "predicted_yield": p.predicted_value,
            "confidence": p.confidence_score,
            "timestamp": p.created_at,
        }
        for p in predictions
    ]


@router.get("/rebalance-suggestions")
async def get_rebalance_suggestions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get rebalancing suggestions from ML model."""
    query = select(Prediction).where(
        (Prediction.user_id == current_user.id) &
        (Prediction.prediction_type == "rebalance_suggestion")
    ).order_by(desc(Prediction.created_at)).limit(5)
    
    result = await db.execute(query)
    suggestions = result.scalars().all()
    
    return [
        {
            "allocation": s.details.get("suggested_allocation") if s.details else None,
            "reason": s.details.get("reason") if s.details else None,
            "expected_improvement": s.predicted_value,
            "confidence": s.confidence_score,
            "timestamp": s.created_at,
        }
        for s in suggestions
    ]


@router.post("/run-optimization")
async def run_optimization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger optimization run for user."""
    # This would call the ML optimization service
    return {
        "message": "Optimization scheduled",
        "status": "queued",
    }

