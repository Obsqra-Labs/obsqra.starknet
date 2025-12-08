"""
SHARP (Shared Prover) integration service

Handles submission of STARK proofs to SHARP for L1 verification
"""
import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class SHARPSubmission:
    """Result of SHARP submission"""
    job_id: str
    status: str  # 'submitted', 'pending', 'processing'


@dataclass
class SHARPStatus:
    """Status of SHARP verification"""
    job_id: str
    state: str  # 'PENDING', 'PROCESSING', 'VERIFIED', 'FAILED'
    fact_hash: Optional[str]
    block_number: Optional[int]
    error: Optional[str]


class SHARPService:
    """
    Service for submitting proofs to SHARP and monitoring verification
    
    SHARP is StarkWare's shared proving service that batches multiple
    proofs and submits them to Ethereum L1 for verification.
    """
    
    def __init__(self):
        # SHARP gateway URL (Sepolia testnet)
        self.gateway_url = os.getenv(
            "SHARP_GATEWAY_URL",
            "https://sharp-sepolia.starkware.co"
        )
        
        # API key (if required by SHARP)
        self.api_key = os.getenv("SHARP_API_KEY")
        
        # SSL verification (disable for testnet development)
        self.verify_ssl = os.getenv("SHARP_VERIFY_SSL", "false").lower() == "true"
        
        logger.info(f"SHARP Service initialized: {self.gateway_url}")
        if not self.verify_ssl:
            logger.warning("⚠️ SSL verification disabled for SHARP (testnet/dev only)")
    
    async def submit_proof(
        self,
        proof_data: bytes,
        proof_hash: str
    ) -> SHARPSubmission:
        """
        Submit STARK proof to SHARP for L1 verification
        
        Args:
            proof_data: Binary STARK proof
            proof_hash: Hash of the proof for tracking
        
        Returns:
            SHARPSubmission with job ID
        
        Raises:
            httpx.HTTPError: If submission fails
        """
        logger.info(f"Submitting proof to SHARP: {proof_hash[:16]}...")
        
        try:
            # Note: SHARP is StarkWare's internal service, not a public API
            # For now, we'll disable SSL verification for testnet (development only)
            # In production, use proper certificate validation or deploy verifier contract
            async with httpx.AsyncClient(
                timeout=30.0,
                verify=self.verify_ssl  # Configurable SSL verification
            ) as client:
                # Prepare request
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                # Submit proof
                # Note: This endpoint may not exist - SHARP is internal to StarkWare
                # Alternative: Deploy verifier contract on Starknet for on-chain verification
                response = await client.post(
                    f"{self.gateway_url}/add_job",
                    files={"proof": proof_data},
                    data={"proof_hash": proof_hash},
                    headers=headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                job_id = data["job_id"]
                logger.info(f"Proof submitted to SHARP: job_id={job_id}")
                
                return SHARPSubmission(
                    job_id=job_id,
                    status="submitted"
                )
                
        except httpx.HTTPError as e:
            logger.error(f"SHARP submission failed: {e}")
            raise
    
    async def check_status(
        self,
        job_id: str
    ) -> SHARPStatus:
        """
        Check verification status of SHARP job
        
        Args:
            job_id: SHARP job ID from submission
        
        Returns:
            SHARPStatus with current state
        """
        try:
            async with httpx.AsyncClient(
                timeout=10.0,
                verify=self.verify_ssl  # Configurable SSL verification
            ) as client:
                response = await client.get(
                    f"{self.gateway_url}/get_status",
                    params={"job_id": job_id}
                )
                
                response.raise_for_status()
                data = response.json()
                
                return SHARPStatus(
                    job_id=job_id,
                    state=data["status"],
                    fact_hash=data.get("fact"),
                    block_number=data.get("block_number"),
                    error=data.get("error")
                )
                
        except httpx.HTTPError as e:
            logger.error(f"SHARP status check failed for {job_id}: {e}")
            raise
    
    async def wait_for_verification(
        self,
        job_id: str,
        max_wait_seconds: int = 3600,
        poll_interval: int = 30
    ) -> SHARPStatus:
        """
        Wait for SHARP verification to complete
        
        Args:
            job_id: SHARP job ID
            max_wait_seconds: Maximum time to wait (default 1 hour)
            poll_interval: Seconds between status checks (default 30s)
        
        Returns:
            Final SHARPStatus
        
        Raises:
            TimeoutError: If verification takes too long
        """
        logger.info(f"Waiting for SHARP verification: {job_id}")
        
        elapsed = 0
        
        while elapsed < max_wait_seconds:
            status = await self.check_status(job_id)
            
            if status.state == "VERIFIED":
                logger.info(f"SHARP verification complete: {job_id}, fact={status.fact_hash}")
                return status
            
            elif status.state == "FAILED":
                logger.error(f"SHARP verification failed: {job_id}, error={status.error}")
                return status
            
            # Still processing, wait and retry
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            if elapsed % 300 == 0:  # Log every 5 minutes
                logger.info(f"Still waiting for SHARP verification: {job_id} ({elapsed}s elapsed)")
        
        # Timeout
        logger.error(f"SHARP verification timeout: {job_id} (waited {max_wait_seconds}s)")
        raise TimeoutError(f"SHARP verification timeout after {max_wait_seconds}s")


# Singleton instance
_sharp_service_instance = None


def get_sharp_service() -> SHARPService:
    """Get singleton SHARP service instance"""
    global _sharp_service_instance
    if _sharp_service_instance is None:
        _sharp_service_instance = SHARPService()
    return _sharp_service_instance

