"""
Read-only market data service (mainnet-friendly).

Fetches live protocol APYs plus Starknet block metadata for auditability.
This is intentionally read-only and safe for demo environments.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

from starknet_py.net.full_node_client import FullNodeClient

from app.services.protocol_apy_service import get_apy_service

logger = logging.getLogger(__name__)


@dataclass
class MarketSnapshot:
    block_number: int
    block_hash: str
    timestamp: int
    apys: Dict[str, float]
    apy_source: str
    network: str
    rpc_url: str


class MarketDataService:
    """Fetches read-only mainnet metrics for proofs and audit trails."""

    def __init__(self, rpc_url: str, network: str):
        self.rpc_url = rpc_url
        self.network = network
        self.client = FullNodeClient(node_url=rpc_url)

    async def get_snapshot(self, force_refresh: bool = False) -> MarketSnapshot:
        apy_service = get_apy_service()
        apys = await apy_service.get_all_apys(force_refresh=force_refresh)

        # Get latest block info for auditability
        block_info = await self.client.get_block_hash_and_number()
        # Use raw RPC to avoid schema mismatches on older starknet-py
        raw_block = await self.client._client.call(
            method_name="getBlockWithTxHashes",
            params={"block_id": {"block_number": block_info.block_number}},
        )
        timestamp = int(raw_block.get("timestamp", 0))

        return MarketSnapshot(
            block_number=block_info.block_number,
            block_hash=hex(block_info.block_hash),
            timestamp=timestamp,
            apys={
                "jediswap": apys.get("jediswap", 0.0),
                "ekubo": apys.get("ekubo", 0.0),
            },
            apy_source=apys.get("source", "unknown"),
            network=self.network,
            rpc_url=self.rpc_url,
        )


_market_data_service: Optional[MarketDataService] = None


def get_market_data_service(rpc_url: str, network: str) -> MarketDataService:
    global _market_data_service
    if _market_data_service is None or _market_data_service.rpc_url != rpc_url:
        _market_data_service = MarketDataService(rpc_url=rpc_url, network=network)
    return _market_data_service
