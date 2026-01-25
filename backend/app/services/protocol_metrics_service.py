"""
Protocol metrics service (read-only mainnet data -> proxy metrics).

This is a pragmatic adapter for demo purposes. It maps live market data
to the risk-engine input schema using transparent heuristics.
"""
from dataclasses import dataclass
from typing import Optional, Dict

from app.services.protocol_apy_service import get_apy_service
from app.services.ekubo_api_service import EkuboApiService
from app.config import get_settings


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
        self.ekubo_api = EkuboApiService()
        self.settings = get_settings()

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
        jedi_metrics = self._proxy_metrics(
            apy=float(apys.get("jediswap", 0.0)),
            source=apys.get("source", "default"),
        )

        ekubo_metrics = self._proxy_metrics(
            apy=float(apys.get("ekubo", 0.0)),
            source=apys.get("source", "default"),
        )

        # Try Ekubo API for real pool-derived proxies
        try:
            stats = await self.ekubo_api.get_pair_top_pool(
                chain_id=self.settings.EKUBO_CHAIN_ID,
                token_a=self.settings.EKUBO_TOKEN_A,
                token_b=self.settings.EKUBO_TOKEN_B,
                min_tvl_usd=1000,
            )
            if stats:
                tvl_total = stats.tvl0_total + stats.tvl1_total
                volume_total = stats.volume0_24h + stats.volume1_24h
                delta_total = abs(stats.tvl0_delta_24h) + abs(stats.tvl1_delta_24h)

                utilization = 0
                if tvl_total > 0:
                    utilization = min(10000, int(volume_total * 10000 / tvl_total))

                volatility = 0
                if tvl_total > 0:
                    volatility = min(10000, int(delta_total * 10000 / tvl_total))
                if volatility == 0:
                    volatility = 2000

                # depth_percent -> liquidity tier
                depth = stats.depth_percent or 0.0
                if depth >= 0.08:
                    liquidity = 0
                elif depth >= 0.04:
                    liquidity = 1
                elif depth >= 0.01:
                    liquidity = 2
                else:
                    liquidity = 3

                ekubo_metrics = ProtocolMetricsSnapshot(
                    utilization=utilization,
                    volatility=volatility,
                    liquidity=liquidity,
                    audit_score=92,
                    age_days=365,
                    source="ekubo_api",
                    apy=float(apys.get("ekubo", 0.0)),
                    tvl_usd=None,
                    apy_mean_30d=None,
                )
        except Exception:
            pass

        return {
            "jediswap": jedi_metrics,
            "ekubo": ekubo_metrics,
        }


_metrics_service: Optional[ProtocolMetricsService] = None


def get_protocol_metrics_service() -> ProtocolMetricsService:
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = ProtocolMetricsService()
    return _metrics_service
