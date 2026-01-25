"""
Background helpers for Atlantic L1 verification polling.

This is a lightweight stub that can be wired to Celery/APScheduler later.
"""
import logging
from datetime import datetime
from typing import Optional
import asyncio

from app.services.atlantic_service import get_atlantic_service
from app.db.session import SessionLocal
from app.models import ProofJob, ProofStatus

logger = logging.getLogger(__name__)


def enqueue_atlantic_status_check(query_id: str, proof_job_id) -> None:
    """
    Placeholder enqueue hook. Wire this into Celery/APScheduler to poll Atlantic.
    """
    logger.info(f"[Atlantic] Enqueue status check for query_id={query_id}, proof_job_id={proof_job_id}")
    # In production, schedule `check_and_update_atlantic_status` via Celery/APS.


async def check_and_update_atlantic_status(query_id: str, proof_job_id, atlantic=None) -> Optional[ProofJob]:
    """
    Poll Atlantic for L1 verification status and persist results.
    """
    atlantic = atlantic or get_atlantic_service()
    if not atlantic:
        logger.warning("Atlantic service not configured; skipping status check")
        return None

    status = await atlantic.check_query_status(query_id)

    db = SessionLocal()
    try:
        job = db.query(ProofJob).get(proof_job_id)
        if not job:
            logger.warning(f"[Atlantic] Proof job {proof_job_id} not found")
            return None

        job.l1_fact_hash = status.fact_hash or job.l1_fact_hash
        job.l1_block_number = status.l1_block_number

        state = status.state.upper() if status.state else "UNKNOWN"
        if state in ["VERIFIED_ON_L1", "VERIFIED"]:
            job.l1_verified_at = datetime.utcnow()
            job.status = ProofStatus.VERIFIED
            logger.info(f"[Atlantic] Proof {proof_job_id} verified on L1 at block {status.l1_block_number}")
        elif state == "FAILED":
            job.status = ProofStatus.FAILED
            logger.error(f"[Atlantic] Proof {proof_job_id} failed L1 verification: {status.error}")
        else:
            logger.info(f"[Atlantic] Proof {proof_job_id} status={state}")

        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


async def poll_pending_atlantic(interval_seconds: int = 300):
    """
    Periodically poll Atlantic for any outstanding queries and update ProofJobs.
    Intended to be launched as a background task from app startup.
    """
    atlantic = get_atlantic_service()
    if not atlantic:
        logger.info("Atlantic not configured; poller not started")
        return

    logger.info(f"[Atlantic] Poller started (every {interval_seconds}s)")
    while True:
        try:
            db = SessionLocal()
            pending = db.query(ProofJob).filter(
                ProofJob.l1_settlement_enabled.is_(True),
                ProofJob.atlantic_query_id.isnot(None),
                ProofJob.l1_verified_at.is_(None)
            ).all()
            db.close()

            if pending:
                logger.info(f"[Atlantic] Polling {len(pending)} pending queries")
            for job in pending:
                try:
                    await check_and_update_atlantic_status(job.atlantic_query_id, job.id, atlantic=atlantic)
                except Exception as poll_err:
                    logger.warning(f"[Atlantic] Poll failed for job {job.id}: {poll_err}")
        except Exception as e:
            logger.error(f"[Atlantic] Poller error: {e}", exc_info=True)

        await asyncio.sleep(interval_seconds)


def start_atlantic_poller(interval_seconds: int = 300):
    """
    Kick off the async poller in the background. No-op if Atlantic is not configured.
    """
    atlantic = get_atlantic_service()
    if not atlantic:
        return None
    loop = asyncio.get_event_loop()
    return loop.create_task(poll_pending_atlantic(interval_seconds=interval_seconds))
