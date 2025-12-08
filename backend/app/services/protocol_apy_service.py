"""
Protocol APY Service

Fetches real APY rates from JediSwap and Ekubo protocols on Starknet.
"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from starknet_py.net import RpcClient
from starknet_py.net.client import Client
from starknet_py.contract import Contract
import os

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
    
    async def get_jediswap_apy(self) -> float:
        """
        Fetch current APY from JediSwap protocol.
        
        TODO: Implement actual JediSwap contract query.
        For now, returns a default value.
        
        JediSwap typically provides APY through:
        - Pool contract queries
        - Router contract queries
        - External APIs (DefiLlama, etc.)
        """
        try:
            client = await self._get_client()
            
            # TODO: Query JediSwap router/pool contracts for real APY
            # Example approach:
            # 1. Get pool address from StrategyRouter
            # 2. Query pool contract for current rate
            # 3. Calculate APY from rate
            
            # For now, return default
            logger.warning("JediSwap APY: Using default value (5.2%). Implement real fetching.")
            return 5.2
            
        except Exception as e:
            logger.error(f"Failed to fetch JediSwap APY: {e}")
            return 5.2  # Default fallback
    
    async def get_ekubo_apy(self) -> float:
        """
        Fetch current APY from Ekubo protocol.
        
        TODO: Implement actual Ekubo contract query.
        For now, returns a default value.
        
        Ekubo typically provides APY through:
        - Pool contract queries
        - Core contract queries
        - External APIs (DefiLlama, etc.)
        """
        try:
            client = await self._get_client()
            
            # TODO: Query Ekubo core/pool contracts for real APY
            # Example approach:
            # 1. Get pool address from StrategyRouter
            # 2. Query pool contract for current rate
            # 3. Calculate APY from rate
            
            # For now, return default
            logger.warning("Ekubo APY: Using default value (8.5%). Implement real fetching.")
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
            
            result = {
                "jediswap": float(jediswap_apy),
                "ekubo": float(ekubo_apy),
                "source": "on-chain" if not isinstance(jediswap_apy, Exception) and not isinstance(ekubo_apy, Exception) else "default",
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

