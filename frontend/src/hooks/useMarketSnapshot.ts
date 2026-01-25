'use client';

import { useCallback, useEffect, useState } from 'react';

export interface MarketSnapshot {
  block_number: number;
  block_hash: string;
  timestamp: number;
  apys: {
    jediswap: number;
    ekubo: number;
  };
  apy_source: string;
  network: string;
  rpc_url: string;
}

export function useMarketSnapshot(refreshMs: number = 30000) {
  const [data, setData] = useState<MarketSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSnapshot = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/market/snapshot', {
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch snapshot: ${res.status} ${res.statusText}`);
      }
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch market snapshot', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch market snapshot');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSnapshot();
    const interval = setInterval(fetchSnapshot, refreshMs);
    return () => clearInterval(interval);
  }, [fetchSnapshot, refreshMs]);

  return {
    data,
    loading,
    error,
    refetch: fetchSnapshot,
  };
}
