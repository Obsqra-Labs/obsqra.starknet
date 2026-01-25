'use client';

import { useCallback, useEffect, useState } from 'react';

export interface ProtocolMetricsSnapshot {
  utilization: number;
  volatility: number;
  liquidity: number;
  audit_score: number;
  age_days: number;
  source: string;
  apy: number;
  tvl_usd: number | null;
  apy_mean_30d: number | null;
}

export interface MarketMetricsResponse {
  jediswap: ProtocolMetricsSnapshot;
  ekubo: ProtocolMetricsSnapshot;
}

export function useMarketMetrics(refreshMs: number = 60000) {
  const [data, setData] = useState<MarketMetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/market/metrics', {
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch metrics: ${res.status} ${res.statusText}`);
      }
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch market metrics', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch market metrics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshMs);
    return () => clearInterval(interval);
  }, [fetchMetrics, refreshMs]);

  return {
    data,
    loading,
    error,
    refetch: fetchMetrics,
  };
}
