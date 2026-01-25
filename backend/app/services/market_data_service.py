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
from app.utils.rpc import get_rpc_urls, with_rpc_fallback

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
        fallback_urls = get_rpc_urls()
        if rpc_url:
            self.rpc_urls = [rpc_url] + [url for url in fallback_urls if url != rpc_url]
        else:
            self.rpc_urls = fallback_urls

    async def get_snapshot(self, force_refresh: bool = False) -> MarketSnapshot:
        apy_service = get_apy_service()
        apys = await apy_service.get_all_apys(force_refresh=force_refresh)

        async def _fetch_block(client: FullNodeClient, _rpc_url: str):
            block_info = await client.get_block_hash_and_number()
            raw_block = await client._client.call(
                method_name="getBlockWithTxHashes",
                params={"block_id": {"block_number": block_info.block_number}},
            )
            return block_info, raw_block

        (block_info, raw_block), rpc_used = await with_rpc_fallback(
            _fetch_block,
            urls=self.rpc_urls,
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
            rpc_url=rpc_used,
        )


_market_data_service: Optional[MarketDataService] = None


def get_market_data_service(rpc_url: str, network: str) -> MarketDataService:
    global _market_data_service
    if _market_data_service is None or _market_data_service.rpc_url != rpc_url:
        _market_data_service = MarketDataService(rpc_url=rpc_url, network=network)
    return _market_data_service
