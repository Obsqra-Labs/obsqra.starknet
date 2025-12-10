"""
Protocol APY Service

Fetches real APY rates from JediSwap and Ekubo protocols on Starknet.
Uses DefiLlama API as primary source, with on-chain queries as future enhancement.
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from starknet_py.net import RpcClient
from starknet_py.net.client import Client
from starknet_py.contract import Contract
import os
import httpx

logger = logging.getLogger(__name__)


class ProtocolAPYService:
    """Service for fetching APY rates from DeFi protocols"""
    
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or os.getenv(
            "STARKNET_RPC_URL",
            "https://starknet-sepolia-rpc.publicnode.com"
        )
        self._client: Optional[Client] = None
        
        # Cache for APY data (5 minute TTL)
        self._cache: Optional[Dict] = None
        self._cache_expiry: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
    
    async def _get_client(self) -> Client:
        """Get or create RPC client"""
        if self._client is None:
            self._client = await RpcClient.create(self.rpc_url)
        return self._client
    
    async def _fetch_defillama_apy(self, protocol_id: str) -> Optional[float]:
        """
        Fetch APY from DefiLlama API for a given protocol.
        
        Args:
            protocol_id: DefiLlama protocol identifier (e.g., 'jediswap', 'ekubo')
        
        Returns:
            APY as float percentage, or None if fetch fails
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # DefiLlama API endpoint for protocol yields
                url = "https://yields.llama.fi/pools"
                
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Search for Starknet pools matching our protocol
                    pools = data.get("data", [])
                    for pool in pools:
                        chain = pool.get("chain", "").lower()
                        project = pool.get("project", "").lower()
                        
                        # Match JediSwap on Starknet
                        if protocol_id == "jediswap" and chain == "starknet" and "jedi" in project:
                            apy = pool.get("apy", None)
                            if apy is not None:
                                logger.info(f"JediSwap APY from DefiLlama: {apy}%")
                                return float(apy)
                        
                        # Match Ekubo on Starknet
                        if protocol_id == "ekubo" and chain == "starknet" and "ekubo" in project:
                            apy = pool.get("apy", None)
                            if apy is not None:
                                logger.info(f"Ekubo APY from DefiLlama: {apy}%")
                                return float(apy)
                    
                    logger.warning(f"No {protocol_id} pool found in DefiLlama data")
                    return None
                else:
                    logger.warning(f"DefiLlama API returned status {response.status_code}")
                    return None
                        
        except httpx.TimeoutException:
            logger.warning(f"DefiLlama API timeout for {protocol_id}")
            return None
        except Exception as e:
            logger.error(f"DefiLlama API error for {protocol_id}: {e}")
            return None
    
    async def get_jediswap_apy(self) -> float:
        """
        Fetch current APY from JediSwap protocol.
        
        Strategy:
        1. Try DefiLlama API (most reliable)
        2. Fallback to default value
        
        Future enhancement: Query JediSwap pool contracts directly.
        """
        try:
            # Try DefiLlama first
            apy = await self._fetch_defillama_apy("jediswap")
            if apy is not None:
                return apy
            
            # Fallback to default
            logger.warning("JediSwap APY: Using default value (5.2%). DefiLlama fetch failed.")
            return 5.2
            
        except Exception as e:
            logger.error(f"Failed to fetch JediSwap APY: {e}")
            return 5.2  # Default fallback
    
    async def get_ekubo_apy(self) -> float:
        """
        Fetch current APY from Ekubo protocol.
        
        Strategy:
        1. Try DefiLlama API (most reliable)
        2. Fallback to default value
        
        Future enhancement: Query Ekubo core/pool contracts directly.
        """
        try:
            # Try DefiLlama first
            apy = await self._fetch_defillama_apy("ekubo")
            if apy is not None:
                return apy
            
            # Fallback to default
            logger.warning("Ekubo APY: Using default value (8.5%). DefiLlama fetch failed.")
            return 8.5
            
        except Exception as e:
            logger.error(f"Failed to fetch Ekubo APY: {e}")
            return 8.5  # Default fallback
    
    async def get_all_apys(self, use_cache: bool = True) -> Dict[str, float]:
        """
        Fetch APY rates for all protocols.
        
        Args:
            use_cache: Whether to use cached data if available
        
        Returns:
            Dictionary with protocol names and APY rates
        """
        # Check cache first
        if use_cache and self._cache and self._cache_expiry:
            if datetime.utcnow() < self._cache_expiry:
                logger.debug("Returning cached APY data")
                return self._cache
        
        try:
            jediswap_apy, ekubo_apy = await asyncio.gather(
                self.get_jediswap_apy(),
                self.get_ekubo_apy(),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(jediswap_apy, Exception):
                logger.error(f"JediSwap APY fetch failed: {jediswap_apy}")
                jediswap_apy = 5.2
            if isinstance(ekubo_apy, Exception):
                logger.error(f"Ekubo APY fetch failed: {ekubo_apy}")
                ekubo_apy = 8.5
            
            # Determine source
            jedi_is_real = not isinstance(jediswap_apy, Exception) and jediswap_apy != 5.2
            ekubo_is_real = not isinstance(ekubo_apy, Exception) and ekubo_apy != 8.5
            
            if jedi_is_real or ekubo_is_real:
                source = "defillama"
            else:
                source = "default"
            
            result = {
                "jediswap": float(jediswap_apy),
                "ekubo": float(ekubo_apy),
                "source": source,
            }
            
            # Update cache
            self._cache = result
            self._cache_expiry = datetime.utcnow() + self._cache_ttl
            
            return result
        except Exception as e:
            logger.error(f"Failed to fetch APY rates: {e}")
            result = {
                "jediswap": 5.2,
                "ekubo": 8.5,
                "source": "default",
            }
            # Cache even defaults to avoid repeated failures
            self._cache = result
            self._cache_expiry = datetime.utcnow() + timedelta(minutes=1)  # Shorter cache for errors
            return result


# Global instance
_apy_service: Optional[ProtocolAPYService] = None


def get_apy_service() -> ProtocolAPYService:
    """Get or create global APY service instance"""
    global _apy_service
    if _apy_service is None:
        _apy_service = ProtocolAPYService()
    return _apy_service

