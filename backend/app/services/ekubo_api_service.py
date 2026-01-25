"""
Ekubo API integration for read-only pool metrics.

Uses Ekubo's public API to fetch top pool stats for a given token pair.
"""
from dataclasses import dataclass
from typing import Optional
import logging
import httpx

logger = logging.getLogger(__name__)


EKUBO_API_BASE = "https://prod-api.ekubo.org"


@dataclass
class EkuboPoolStats:
    tvl0_total: int
    tvl1_total: int
    tvl0_delta_24h: int
    tvl1_delta_24h: int
    volume0_24h: int
    volume1_24h: int
    fees0_24h: int
    fees1_24h: int
    depth_percent: Optional[float]


class EkuboApiService:
    def __init__(self, base_url: str = EKUBO_API_BASE):
        self.base_url = base_url.rstrip("/")

    async def get_pair_top_pool(
        self,
        chain_id: str,
        token_a: str,
        token_b: str,
        min_tvl_usd: Optional[float] = None,
    ) -> Optional[EkuboPoolStats]:
        params = {}
        if min_tvl_usd is not None:
            params["minTvlUsd"] = str(min_tvl_usd)

        url = f"{self.base_url}/pair/{chain_id}/{token_a}/{token_b}/pools"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    logger.warning(f"Ekubo API status {resp.status_code}: {resp.text[:200]}")
                    return None
                data = resp.json()
        except Exception as e:
            logger.warning(f"Ekubo API error: {e}")
            return None

        pools = data.get("topPools") or []
        if not pools:
            return None

        top = pools[0]
        try:
            return EkuboPoolStats(
                tvl0_total=int(top.get("tvl0_total", "0")),
                tvl1_total=int(top.get("tvl1_total", "0")),
                tvl0_delta_24h=int(top.get("tvl0_delta_24h", "0")),
                tvl1_delta_24h=int(top.get("tvl1_delta_24h", "0")),
                volume0_24h=int(top.get("volume0_24h", "0")),
                volume1_24h=int(top.get("volume1_24h", "0")),
                fees0_24h=int(top.get("fees0_24h", "0")),
                fees1_24h=int(top.get("fees1_24h", "0")),
                depth_percent=top.get("depth_percent"),
            )
        except Exception as e:
            logger.warning(f"Ekubo API parse error: {e}")
            return None
