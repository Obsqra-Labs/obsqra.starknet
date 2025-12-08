"""
Background worker for SHARP proof submission and monitoring

Handles async submission of proofs to SHARP and monitoring of verification status
"""
import asyncio
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import ProofJob, ProofStatus
from app.services.sharp_service import get_sharp_service

logger = logging.getLogger(__name__)


async def submit_proof_to_sharp(
    job_id: UUID,
    proof_data: bytes,
    proof_hash: str
):
    """
    Background task to submit proof to SHARP and monitor verification
    
    This runs asynchronously and doesn't block the user's request.
    Updates database with status as verification progresses.
    
    Args:
        job_id: Proof job ID in database
        proof_data: Binary STARK proof
        proof_hash: Hash of proof
    """
    sharp_service = get_sharp_service()
    db = SessionLocal()
    
    try:
        # Update status: submitting to SHARP
        job = db.query(ProofJob).filter(ProofJob.id == job_id).first()
        if not job:
            logger.error(f"Proof job {job_id} not found")
            return
        
        # Don't change status if on-chain execution already succeeded
        # Only update SHARP-specific fields
        logger.info(f"Submitting proof {job_id} to SHARP...")
        
        try:
            # Submit to SHARP
            sharp_result = await sharp_service.submit_proof(
                proof_data=proof_data,
                proof_hash=proof_hash
            )
            
            # Update with SHARP job ID (don't change main status)
            job.sharp_job_id = sharp_result.job_id
            # Keep status as SUBMITTED (on-chain success), SHARP verification is separate
            if job.status == ProofStatus.SUBMITTED:
                # Only update if still in submitted state (on-chain succeeded)
                pass  # Keep SUBMITTED status
            db.commit()
        except Exception as e:
            logger.warning(f"SHARP submission failed for {job_id} (non-critical, on-chain tx succeeded): {e}")
            # Don't change status - on-chain execution already succeeded
            return  # Exit early, don't try to monitor
        
        logger.info(f"Proof {job_id} submitted to SHARP: {sharp_result.job_id}")
        
        # Monitor verification (10-60 minutes)
        await monitor_sharp_verification(job_id, sharp_result.job_id)
        
    except Exception as e:
        logger.error(f"SHARP submission failed for {job_id}: {e}", exc_info=True)
        
        # Update job with error
        job = db.query(ProofJob).filter(ProofJob.id == job_id).first()
        if job:
            job.status = ProofStatus.FAILED
            job.error = str(e)
            db.commit()
    
    finally:
        db.close()


async def monitor_sharp_verification(
    job_id: UUID,
    sharp_job_id: str
):
    """
    Monitor SHARP verification status and update database
    
    Polls SHARP every 30 seconds until verification completes
    
    Args:
        job_id: Proof job ID in database
        sharp_job_id: SHARP job ID
    """
    sharp_service = get_sharp_service()
    db = SessionLocal()
    
    max_wait = 3600  # 1 hour
    poll_interval = 30  # 30 seconds
    elapsed = 0
    
    try:
        logger.info(f"Monitoring SHARP verification for {job_id}...")
        
        while elapsed < max_wait:
            try:
                # Check SHARP status
                status = await sharp_service.check_status(sharp_job_id)
                
                if status.state == "VERIFIED":
                    # Success!
                    job = db.query(ProofJob).filter(ProofJob.id == job_id).first()
                    if job:
                        job.status = ProofStatus.VERIFIED
                        job.fact_hash = status.fact_hash
                        job.verified_at = datetime.utcnow()
                        db.commit()
                    
                    logger.info(f"Proof {job_id} verified on SHARP! Fact: {status.fact_hash}")
                    
                    # TODO: Trigger webhook/notification
                    await notify_verification_complete(job_id, status.fact_hash)
                    
                    return
                
                elif status.state == "FAILED":
                    # Verification failed
                    job = db.query(ProofJob).filter(ProofJob.id == job_id).first()
                    if job:
                        job.status = ProofStatus.FAILED
                        job.error = status.error or "SHARP verification failed"
                        db.commit()
                    
                    logger.error(f"SHARP verification failed for {job_id}: {status.error}")
                    return
                
                # Still processing, wait and retry
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
                
                if elapsed % 300 == 0:  # Log every 5 minutes
                    logger.info(
                        f"Still waiting for SHARP verification: {job_id} "
                        f"({elapsed}s elapsed, {max_wait - elapsed}s remaining)"
                    )
            
            except Exception as e:
                logger.error(f"Error checking SHARP status: {e}")
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
        
        # Timeout
        logger.error(f"SHARP verification timeout for {job_id}")
        job = db.query(ProofJob).filter(ProofJob.id == job_id).first()
        if job:
            job.status = ProofStatus.TIMEOUT
            job.error = f"SHARP verification timeout after {max_wait}s"
            db.commit()
    
    finally:
        db.close()


async def notify_verification_complete(
    job_id: UUID,
    fact_hash: str
):
    """
    Notify when SHARP verification completes
    
    TODO: Implement webhook, email, or push notification
    """
    logger.info(f"Verification complete for {job_id}: {fact_hash}")
    
    # Future: Send webhook to frontend
    # Future: Send email notification
    # Future: Trigger smart contract update


def start_sharp_worker():
    """
    Start the SHARP worker process
    
    This should be run in a separate process/thread from the main API
    """
    logger.info("SHARP worker starting...")
    
    # Run async event loop
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("SHARP worker shutting down...")
    finally:
        loop.close()


if __name__ == "__main__":
    # For standalone worker process
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    start_sharp_worker()

