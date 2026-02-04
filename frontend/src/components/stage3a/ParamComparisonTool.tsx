'use client';

import { useState, useEffect } from 'react';
import { getConfig } from '@/lib/config';
import type { ModelParamsData } from './ModelParamsViewer';

interface ParamComparisonToolProps {
  versionA?: number;
  versionB?: number;
}

export function ParamComparisonTool({ versionA = 0, versionB = 1 }: ParamComparisonToolProps) {
  const [paramsA, setParamsA] = useState<ModelParamsData | null>(null);
  const [paramsB, setParamsB] = useState<ModelParamsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const cfg = getConfig();
    const apiBase = cfg.backendUrl ? `${cfg.backendUrl}/api/v1` : '';
    const url = (v: number) => apiBase ? `${apiBase}/risk-engine/model-params/${v}` : `/api/v1/risk-engine/model-params/${v}`;
    const fetchOne = (v: number) => fetch(url(v)).then((r) => (r.ok ? r.json() : null));
    setLoading(true);
    setError(null);
    Promise.all([fetchOne(versionA), fetchOne(versionB)])
      .then(([a, b]) => {
        setParamsA(a);
        setParamsB(b);
      })
      .catch((e) => {
        setError(e.message);
      })
      .finally(() => setLoading(false));
  }, [versionA, versionB]);

  if (loading) return <div className="text-sm text-gray-500">Loading...</div>;
  if (error) return <div className="text-sm text-red-500">{error}</div>;

  const keys = paramsA
    ? (Object.keys(paramsA) as (keyof ModelParamsData)[])
    : ['w_utilization', 'w_volatility', 'w_liquidity_0', 'w_liquidity_1', 'w_liquidity_2', 'w_liquidity_3', 'w_audit', 'w_age', 'age_cap_days', 'clamp_min', 'clamp_max'];

  return (
    <div className="overflow-x-auto rounded border border-gray-200 bg-gray-50/50 p-4">
      <h3 className="mb-3 text-sm font-semibold text-gray-700">Compare model versions</h3>
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-200 text-left text-gray-600">
            <th className="py-1 pr-2">Param</th>
            <th className="py-1 pr-2">v{versionA}</th>
            <th className="py-1 pr-2">v{versionB}</th>
          </tr>
        </thead>
        <tbody>
          {keys.map((key) => (
            <tr key={key} className="border-b border-gray-100">
              <td className="py-1 font-mono text-gray-600">{key}</td>
              <td className="py-1 font-mono text-gray-800">{String((paramsA as unknown as Record<string, unknown>)?.[key] ?? '—')}</td>
              <td className="py-1 font-mono text-gray-800">{String((paramsB as unknown as Record<string, unknown>)?.[key] ?? '—')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
