'use client';

import { useEffect, useState, useCallback } from 'react';

export interface PerformanceTimelineEntry {
  timestamp: string;
  jediswap_pct: number;
  ekubo_pct: number;
  jediswap_risk: number;
  ekubo_risk: number;
  tx_hash: string | null;
  proof_hash: string;
  proof_status: string;
  verified: boolean;
}

export interface PortfolioPerformance {
  total_rebalances: number;
  period_days: number;
  average_allocation: { jediswap: number; ekubo: number };
  latest_rebalance: {
    timestamp: string | null;
    jediswap_pct: number;
    ekubo_pct: number;
    tx_hash: string | null;
  } | null;
  rebalance_frequency: { per_day: number; per_week: number };
  proof_metrics: { total_proofs: number; verified_count: number; verified_percentage: number };
}

export interface RealPerformanceResult {
  portfolio: PortfolioPerformance;
  timeline: PerformanceTimelineEntry[];
  period_days: number;
  source: string;
}

export function useRealPerformance(days: number = 30) {
  const [data, setData] = useState<RealPerformanceResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPerformance = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`/api/v1/analytics/performance/real?days=${days}`, {
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch performance: ${res.status} ${res.statusText}`);
      }
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch real performance', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch real performance');
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    fetchPerformance();
    const interval = setInterval(fetchPerformance, 30000);
    return () => clearInterval(interval);
  }, [fetchPerformance]);

  return {
    data,
    loading,
    error,
    refetch: fetchPerformance,
  };
}
