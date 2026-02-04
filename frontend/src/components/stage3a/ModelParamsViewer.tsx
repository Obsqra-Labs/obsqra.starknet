'use client';

import { useEffect, useState } from 'react';
import { getConfig } from '@/lib/config';

export interface ModelParamsData {
  w_utilization: number;
  w_volatility: number;
  w_liquidity_0: number;
  w_liquidity_1: number;
  w_liquidity_2: number;
  w_liquidity_3: number;
  w_audit: number;
  w_age: number;
  age_cap_days: number;
  clamp_min: number;
  clamp_max: number;
}

interface ModelParamsViewerProps {
  version?: number;
  title?: string;
}

export function ModelParamsViewer({ version = 0, title = 'Model Parameters (Stage 3A)' }: ModelParamsViewerProps) {
  const [params, setParams] = useState<ModelParamsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const cfg = getConfig();
    const apiBase = cfg.backendUrl ? `${cfg.backendUrl}/api/v1` : '';
const url = apiBase ? `${apiBase}/risk-engine/model-params/${version}` : `/api/v1/risk-engine/model-params/${version}`;
    setLoading(true);
    setError(null);
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText);
        return res.json();
      })
      .then((data: ModelParamsData) => setParams(data))
      .catch((e) => {
        setError(e.message || 'Failed to load model params');
        setParams(null);
      })
      .finally(() => setLoading(false));
  }, [version]);

  if (loading) return <div className="text-sm text-gray-500">Loading model params...</div>;
  if (error) return <div className="text-sm text-red-500">{error}</div>;
  if (!params) return null;

  const rows: { label: string; value: number }[] = [
    { label: 'w_utilization', value: params.w_utilization },
    { label: 'w_volatility', value: params.w_volatility },
    { label: 'w_liquidity_0', value: params.w_liquidity_0 },
    { label: 'w_liquidity_1', value: params.w_liquidity_1 },
    { label: 'w_liquidity_2', value: params.w_liquidity_2 },
    { label: 'w_liquidity_3', value: params.w_liquidity_3 },
    { label: 'w_audit', value: params.w_audit },
    { label: 'w_age', value: params.w_age },
    { label: 'age_cap_days', value: params.age_cap_days },
    { label: 'clamp_min', value: params.clamp_min },
    { label: 'clamp_max', value: params.clamp_max },
  ];

  return (
    <div className="rounded border border-gray-200 bg-gray-50/50 p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">{title}</h3>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs sm:grid-cols-3">
        {rows.map(({ label, value }) => (
          <div key={label} className="flex justify-between gap-2">
            <dt className="text-gray-500">{label}</dt>
            <dd className="font-mono text-gray-800">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
