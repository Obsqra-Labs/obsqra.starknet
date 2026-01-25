"""
Protocol metrics service (read-only mainnet data -> proxy metrics).

This is a pragmatic adapter for demo purposes. It maps live market data
to the risk-engine input schema using transparent heuristics.
"""
from dataclasses import dataclass
from typing import Optional, Dict

from app.services.protocol_apy_service import get_apy_service


@dataclass
class ProtocolMetricsSnapshot:
    utilization: int
    volatility: int
    liquidity: int
    audit_score: int
    age_days: int
    source: str
    apy: float
    tvl_usd: Optional[float] = None
    apy_mean_30d: Optional[float] = None


class ProtocolMetricsService:
    """
    Convert live market data into proxy risk metrics.
    """

    def __init__(self):
        self.apy_service = get_apy_service()

    @staticmethod
    def _liquidity_tier(tvl_usd: Optional[float]) -> int:
        if tvl_usd is None:
            return 2
        if tvl_usd >= 50_000_000:
            return 0
        if tvl_usd >= 10_000_000:
            return 1
        if tvl_usd >= 1_000_000:
            return 2
        return 3

    @staticmethod
    def _audit_score(tvl_usd: Optional[float]) -> int:
        if tvl_usd is None:
            return 85
        if tvl_usd >= 50_000_000:
            return 95
        if tvl_usd >= 10_000_000:
            return 90
        if tvl_usd >= 1_000_000:
            return 85
        return 80

    @staticmethod
    def _age_days_default() -> int:
        # Conservative default for demo if protocol age isn't available
        return 365

    def _proxy_metrics(self, apy: float, source: str, tvl_usd: Optional[float] = None, apy_mean_30d: Optional[float] = None) -> ProtocolMetricsSnapshot:
        # Utilization proxy: APY percentage -> basis points
        utilization = max(0, min(10000, int(apy * 100)))

        # Volatility proxy: deviation from 30d mean if available, else a mild default
        if apy_mean_30d is not None:
            volatility = max(0, min(10000, int(abs(apy - apy_mean_30d) * 100)))
        else:
            volatility = 2500

        liquidity = self._liquidity_tier(tvl_usd)
        audit_score = self._audit_score(tvl_usd)
        age_days = self._age_days_default()

        return ProtocolMetricsSnapshot(
            utilization=utilization,
            volatility=volatility,
            liquidity=liquidity,
            audit_score=audit_score,
            age_days=age_days,
            source=source,
            apy=apy,
            tvl_usd=tvl_usd,
            apy_mean_30d=apy_mean_30d,
        )

    async def get_protocol_metrics(self) -> Dict[str, ProtocolMetricsSnapshot]:
        apys = await self.apy_service.get_all_apys(force_refresh=False)

        # DefiLlama yields endpoint doesn't always provide tvl/mean data in current call path.
        # For now we return proxies based on APY and a shared source label.
        return {
            "jediswap": self._proxy_metrics(
                apy=float(apys.get("jediswap", 0.0)),
                source=apys.get("source", "default"),
            ),
            "ekubo": self._proxy_metrics(
                apy=float(apys.get("ekubo", 0.0)),
                source=apys.get("source", "default"),
            ),
        }


_metrics_service: Optional[ProtocolMetricsService] = None


def get_protocol_metrics_service() -> ProtocolMetricsService:
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = ProtocolMetricsService()
    return _metrics_service
