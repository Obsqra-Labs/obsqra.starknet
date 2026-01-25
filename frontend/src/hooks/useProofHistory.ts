'use client';

import { useEffect, useState, useCallback } from 'react';

export type ProofHistoryRecord = {
  id: string;
  timestamp: string | null;
  jediswap_pct: number;
  ekubo_pct: number;
  jediswap_risk: number;
  ekubo_risk: number;
  proof_hash: string;
  proof_status: string;
  tx_hash: string | null;
  fact_hash: string | null;
  l2_fact_hash?: string | null;
  l2_verified_at?: string | null;
  l1_fact_hash?: string | null;
  l1_verified_at?: string | null;
  network?: string | null;
  atlantic_query_id?: string | null;
  l1_settlement_enabled?: boolean;
};

export function useProofHistory(limit: number = 10) {
  const [data, setData] = useState<ProofHistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`/api/v1/analytics/rebalance-history?limit=${limit}`, {
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch proof history: ${res.status} ${res.statusText}`);
      }
      const json = await res.json();
      setData(json || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch proof history', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch proof history');
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 30000);
    return () => clearInterval(interval);
  }, [fetchHistory]);

  return { data, loading, error, refetch: fetchHistory };
}
