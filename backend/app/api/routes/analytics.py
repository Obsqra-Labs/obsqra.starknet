"""Analytics endpoints - Historical data and trends"""

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.db.session import get_db as get_sync_db
from app.models import User, RiskHistory, AllocationHistory, ProofJob
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


@router.get("/rebalance-history")
async def get_rebalance_history(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_sync_db)
):
    """
    Get recent rebalance history with proof verification status.
    
    Returns list of rebalances with:
    - Allocation percentages
    - Proof hash and status
    - Transaction hash
    - Timestamp
    """
    # Query proof jobs ordered by creation time (most recent first)
    proof_jobs = db.query(ProofJob).order_by(
        desc(ProofJob.created_at)
    ).limit(limit).all()
    
    return [
        {
            "id": str(job.id),
            "timestamp": job.created_at.isoformat() if job.created_at else None,
            # Try new columns first, fallback to metrics JSON if not available (for in-memory DB)
            "jediswap_pct": (
                (getattr(job, 'jediswap_pct', None) / 100.0) 
                if hasattr(job, 'jediswap_pct') and getattr(job, 'jediswap_pct', None) is not None 
                else (job.metrics.get("jediswap", {}).get("utilization", 0) / 100.0 if job.metrics else 50)
            ),
            "ekubo_pct": (
                (getattr(job, 'ekubo_pct', None) / 100.0)
                if hasattr(job, 'ekubo_pct') and getattr(job, 'ekubo_pct', None) is not None
                else (job.metrics.get("ekubo", {}).get("utilization", 0) / 100.0 if job.metrics else 50)
            ),
            "jediswap_risk": (
                getattr(job, 'jediswap_risk', None)
                if hasattr(job, 'jediswap_risk') and getattr(job, 'jediswap_risk', None) is not None
                else (job.metrics.get("jediswap_risk", 0) if job.metrics else 0)
            ),
            "ekubo_risk": (
                getattr(job, 'ekubo_risk', None)
                if hasattr(job, 'ekubo_risk') and getattr(job, 'ekubo_risk', None) is not None
                else (job.metrics.get("ekubo_risk", 0) if job.metrics else 0)
            ),
            "proof_hash": job.proof_hash,
            "proof_status": job.status.value if hasattr(job.status, 'value') else str(job.status),
            "tx_hash": job.tx_hash,
            "fact_hash": job.fact_hash,
            "submitted_at": job.submitted_at.isoformat() if job.submitted_at else None,
            "verified_at": job.verified_at.isoformat() if job.verified_at else None,
        }
        for job in proof_jobs
    ]


@router.get("/proof/{proof_job_id}/download")
async def download_proof(
    proof_job_id: str,
    db: Session = Depends(get_sync_db)
):
    """
    Download proof binary data for a specific proof job
    
    Returns the STARK proof binary file for verification or archival purposes.
    """
    
    try:
        job_uuid = uuid.UUID(proof_job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proof job ID format")
    
    job = db.query(ProofJob).filter(ProofJob.id == job_uuid).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Proof job not found")
    
    if not job.proof_data:
        raise HTTPException(status_code=404, detail="Proof data not available for this job")
    
    return Response(
        content=job.proof_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="proof_{job.proof_hash[:16]}.bin"',
            "X-Proof-Hash": job.proof_hash,
            "X-Proof-Status": job.status.value if hasattr(job.status, 'value') else str(job.status),
        }
    )


@router.get("/proof-performance")
async def get_proof_performance(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_sync_db)
):
    """
    Get proof generation performance metrics
    
    Returns statistics about proof generation times, sizes, and success rates.
    """
    from sqlalchemy import func
    
    # Get recent proof jobs
    proof_jobs = db.query(ProofJob).order_by(
        desc(ProofJob.created_at)
    ).limit(limit).all()
    
    if not proof_jobs:
        return {
            "total": 0,
            "average_generation_time": 0,
            "average_proof_size": 0,
            "verified_count": 0,
            "verified_percentage": 0
        }
    
    # Calculate metrics
    generation_times = []
    proof_sizes = []
    verified_count = 0
    
    for job in proof_jobs:
        if job.metrics:
            gen_time = job.metrics.get("proof_generation_time_seconds")
            if gen_time:
                generation_times.append(gen_time)
            
            proof_size = job.metrics.get("proof_data_size_bytes")
            if proof_size:
                proof_sizes.append(proof_size)
        
        if job.status.value == "verified" if hasattr(job.status, 'value') else str(job.status) == "verified":
            verified_count += 1
    
    avg_gen_time = sum(generation_times) / len(generation_times) if generation_times else 0
    avg_proof_size = sum(proof_sizes) / len(proof_sizes) if proof_sizes else 0
    verified_percentage = (verified_count / len(proof_jobs)) * 100 if proof_jobs else 0
    
    return {
        "total": len(proof_jobs),
        "average_generation_time_seconds": round(avg_gen_time, 2),
        "average_proof_size_bytes": int(avg_proof_size),
        "average_proof_size_kb": round(avg_proof_size / 1024, 2),
        "verified_count": verified_count,
        "verified_percentage": round(verified_percentage, 1),
        "min_generation_time": round(min(generation_times), 2) if generation_times else 0,
        "max_generation_time": round(max(generation_times), 2) if generation_times else 0,
    }


@router.get("/protocol-apys")
async def get_protocol_apys():
    """
    Get current APY rates for protocols.
    
    TODO: Fetch from actual protocol contracts or external APIs.
    For now, returns default values.
    """
    # TODO: Implement real APY fetching from:
    # - JediSwap: Query pool contracts for current rates
    # - Ekubo: Query pool contracts for current rates
    # - Or: Use external APIs (DefiLlama, etc.)
    
    return {
        "jediswap": 5.2,  # Default, replace with real data
        "ekubo": 8.5,     # Default, replace with real data
        "source": "default",  # Will be "on-chain" or "api" when implemented
        "last_updated": datetime.utcnow().isoformat(),
    }

