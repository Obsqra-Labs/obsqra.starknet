"""
Herodotus Atlantic service for L1 proof settlement

Submits execution traces to Atlantic for L1 verification on Ethereum.
This provides L1 settlement for proofs (free on Sepolia, paid on mainnet).
"""
import logging
import httpx
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AtlanticSubmission:
    """Result of Atlantic submission"""
    query_id: str
    status: str  # 'submitted', 'processing'


@dataclass
class AtlanticStatus:
    """Status of Atlantic L1 verification"""
    query_id: str
    state: str  # 'PENDING', 'PROCESSING', 'VERIFIED_ON_L1', 'FAILED'
    fact_hash: Optional[str]
    l1_block_number: Optional[int]
    error: Optional[str]


class AtlanticService:
    """L1 settlement via Herodotus Atlantic (premium feature)"""
    
    def __init__(self, api_key: str, base_url: str = "https://atlantic.api.herodotus.cloud", network: str = "sepolia"):
        """
        Initialize Atlantic Service
        
        Args:
            api_key: Herodotus API key
            base_url: Atlantic API base URL
            network: Network name ('sepolia' or 'mainnet')
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.network = network.lower()
        
        if not self.api_key:
            logger.warning("Atlantic API key not configured - L1 settlement will be disabled")
        else:
            logger.info(f"Atlantic Service initialized for {network}")
    
    async def submit_trace_for_l1_verification(
        self,
        pie_file_path: str,
        declared_job_size: str = "S",  # XS, S, M, L
        cairo_version: str = "cairo1",
        layout: str = "recursive"
    ) -> AtlanticSubmission:
        """
        Submit trace to Atlantic for L1 verification
        
        Args:
            pie_file_path: Path to pie.zip trace file
            declared_job_size: Job size (XS, S, M, L)
            cairo_version: Cairo version (0 or 1)
            layout: Layout type (recursive, dynamic, etc.)
        
        Returns:
            AtlanticSubmission with query_id
        
        Raises:
            ValueError: If API key not configured
            httpx.HTTPError: If submission fails
        """
        if not self.api_key:
            raise ValueError("Atlantic API key not configured. Set ATLANTIC_API_KEY in environment.")
        
        pie_path = Path(pie_file_path)
        if not pie_path.exists():
            raise FileNotFoundError(f"Trace file not found: {pie_file_path}")
        
        try:
            with open(pie_path, "rb") as f:
                pie_data = f.read()
            
            logger.info(f"Submitting trace to Atlantic: {pie_path.name} ({len(pie_data)} bytes)")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/atlantic-query?apiKey={self.api_key}",
                    files={"pieFile": (pie_path.name, pie_data, "application/zip")},
                    data={
                        "declaredJobSize": declared_job_size,
                        "cairoVersion": cairo_version,
                        "layout": layout,
                        "result": "PROOF_VERIFICATION_ON_L1"  # L1 settlement
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                query_id = data.get("id") or data.get("query_id") or str(data.get("job_id", ""))
                
                if not query_id:
                    raise ValueError(f"Invalid response from Atlantic: {data}")
                
                logger.info(f"Trace submitted to Atlantic: query_id={query_id}")
                
                return AtlanticSubmission(
                    query_id=query_id,
                    status="submitted"
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Atlantic submission failed with status {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Atlantic submission failed: {e}", exc_info=True)
            raise
    
    async def check_query_status(self, query_id: str) -> AtlanticStatus:
        """
        Check Atlantic query status
        
        Args:
            query_id: Atlantic query ID from submission
        
        Returns:
            AtlanticStatus with current state
        
        Raises:
            ValueError: If API key not configured
            httpx.HTTPError: If status check fails
        """
        if not self.api_key:
            raise ValueError("Atlantic API key not configured")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/atlantic-query/{query_id}?apiKey={self.api_key}"
                )
                response.raise_for_status()
                data = response.json()
                
                state = data.get("state") or data.get("status", "UNKNOWN")
                fact_hash = data.get("factHash") or data.get("fact_hash")
                l1_block_number = data.get("l1BlockNumber") or data.get("l1_block_number")
                error = data.get("error")
                
                return AtlanticStatus(
                    query_id=query_id,
                    state=state,
                    fact_hash=fact_hash,
                    l1_block_number=l1_block_number,
                    error=error
                )
        except httpx.HTTPStatusError as e:
            logger.error(f"Atlantic status check failed with status {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Atlantic status check failed: {e}", exc_info=True)
            raise
    
    async def wait_for_l1_verification(
        self,
        query_id: str,
        max_wait_seconds: int = 3600,
        poll_interval: int = 30
    ) -> AtlanticStatus:
        """
        Wait for Atlantic L1 verification to complete
        
        Args:
            query_id: Atlantic query ID
            max_wait_seconds: Maximum time to wait (default 1 hour)
            poll_interval: Seconds between status checks (default 30s)
        
        Returns:
            Final AtlanticStatus
        
        Raises:
            TimeoutError: If verification takes too long
        """
        import asyncio
        
        logger.info(f"Waiting for Atlantic L1 verification: {query_id}")
        
        elapsed = 0
        
        while elapsed < max_wait_seconds:
            status = await self.check_query_status(query_id)
            
            if status.state in ["VERIFIED_ON_L1", "VERIFIED"]:
                logger.info(
                    f"Atlantic L1 verification complete: {query_id}, "
                    f"fact={status.fact_hash}, block={status.l1_block_number}"
                )
                return status
            
            elif status.state == "FAILED":
                logger.error(f"Atlantic L1 verification failed: {query_id}, error={status.error}")
                return status
            
            # Still processing, wait and retry
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            if elapsed % 300 == 0:  # Log every 5 minutes
                logger.info(f"Still waiting for Atlantic L1 verification: {query_id} ({elapsed}s elapsed)")
        
        # Timeout
        logger.error(f"Atlantic L1 verification timeout: {query_id} (waited {max_wait_seconds}s)")
        raise TimeoutError(f"Atlantic L1 verification timeout after {max_wait_seconds}s")


# Singleton instance
_atlantic_service_instance = None


def get_atlantic_service() -> Optional[AtlanticService]:
    """
    Get singleton Atlantic Service instance
    
    Returns:
        AtlanticService instance or None if API key not configured
    """
    global _atlantic_service_instance
    
    if _atlantic_service_instance is None:
        from app.config import get_settings
        settings = get_settings()
        
        api_key = settings.ATLANTIC_API_KEY
        base_url = settings.ATLANTIC_BASE_URL
        network = settings.STARKNET_NETWORK
        
        if not api_key:
            logger.warning("Atlantic API key not configured - L1 settlement disabled")
            return None
        
        _atlantic_service_instance = AtlanticService(
            api_key=api_key,
            base_url=base_url,
            network=network
        )
    
    return _atlantic_service_instance


