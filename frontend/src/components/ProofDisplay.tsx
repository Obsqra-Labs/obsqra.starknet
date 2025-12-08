'use client';

import React, { useMemo } from 'react';
import { ProofData } from '@/hooks/useProofGeneration';

interface ProofDisplayProps {
  proof: ProofData | null;
  isLoading?: boolean;
  error?: string | null;
}

export const ProofDisplay: React.FC<ProofDisplayProps> = ({ 
  proof, 
  isLoading = false, 
  error = null 
}) => {
  const displayData = useMemo(() => {
    if (!proof) return null;

    if (proof.computation_type === 'RISK_SCORE') {
      const trace = proof.computation_trace as any;
      return {
        title: '🔐 Risk Score Proof',
        metrics: [
          { label: 'Risk Score', value: `${trace.total_risk}` },
          { label: 'Utilization Risk', value: `${(trace.utilization_risk * 100).toFixed(2)}%` },
          { label: 'Volatility Risk', value: `${(trace.volatility_risk * 100).toFixed(2)}%` },
          { label: 'Liquidity Risk', value: `${trace.liquidity_risk}` },
          { label: 'Audit Risk', value: `${(trace.audit_risk * 100).toFixed(2)}%` },
          { label: 'Age Risk', value: `${(trace.age_risk * 100).toFixed(2)}%` },
        ],
      };
    } else if (proof.computation_type === 'ALLOCATION') {
      const trace = proof.computation_trace as any;
      const outputs = trace.outputs || {};
      return {
        title: '🎯 Allocation Proof',
        metrics: [
          { label: 'Nostra %', value: `${(outputs.nostra_pct / 100).toFixed(2)}%` },
          { label: 'ZkLend %', value: `${(outputs.zklend_pct / 100).toFixed(2)}%` },
          { label: 'Ekubo %', value: `${(outputs.ekubo_pct / 100).toFixed(2)}%` },
          { label: 'Computation Hash', value: trace.computation_hash?.slice(0, 16) + '...' },
        ],
      };
    }

    return null;
  }, [proof]);

  if (isLoading) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-blue-700">
          <div className="animate-spin">⟳</div>
          <span>Generating proof...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="text-red-700 font-medium">Proof Error</div>
        <div className="text-red-600 text-sm mt-1">{error}</div>
      </div>
    );
  }

  if (!proof || !displayData) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-gray-500 text-sm">
        No proof generated yet
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
      <div className="space-y-4">
        {/* Title */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800">{displayData.title}</h3>
          <div className="flex items-center gap-2">
            {proof.verified && (
              <span className="inline-block px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                ✓ Verified
              </span>
            )}
            <span className="text-xs text-gray-500 font-mono">
              {proof.proof_id.slice(0, 12)}...
            </span>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-4">
          {displayData.metrics.map((metric, idx) => (
            <div key={idx} className="bg-white rounded-lg p-3 border border-gray-100">
              <div className="text-xs text-gray-600 font-medium">{metric.label}</div>
              <div className="text-lg font-mono font-bold text-gray-900 mt-1">
                {metric.value}
              </div>
            </div>
          ))}
        </div>

        {/* Proof Hash */}
        <div className="bg-white rounded-lg p-3 border border-gray-100">
          <div className="text-xs text-gray-600 font-medium mb-1">Proof Hash</div>
          <div className="text-xs font-mono text-gray-700 break-all bg-gray-50 p-2 rounded">
            {proof.proof_hash}
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Generated: {new Date(proof.timestamp).toLocaleString()}
          </div>
        </div>

        {/* Starkscan Link */}
        <div>
          <a
            href={`https://sepolia.starkscan.co/tx/${proof.proof_hash}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            View on Starkscan →
          </a>
        </div>
      </div>
    </div>
  );
};
