'use client';

import { useEffect, useState } from 'react';
import { ProofBadge, type ProofStatus } from './ProofBadge';
import { TableSkeleton } from './LoadingSkeleton';

interface RebalanceRecord {
  id: string;
  timestamp: string;
  jediswap_pct: number;
  ekubo_pct: number;
  jediswap_risk: number;
  ekubo_risk: number;
  proof_hash: string;
  proof_status: ProofStatus;
  tx_hash: string | null;
  fact_hash: string | null;
  l2_fact_hash?: string | null;
  l2_verified_at?: string | null;
  l1_fact_hash?: string | null;
  l1_verified_at?: string | null;
  l1_settlement_enabled?: boolean;
  atlantic_query_id?: string | null;
  network?: string | null;
  submitted_at: string | null;
  verified_at: string | null;
  proof_job_id?: string;
  proof_generation_time?: number | null;
  proof_size_bytes?: number | null;
}

export function RebalanceHistory() {
  const [history, setHistory] = useState<RebalanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/analytics/rebalance-history?limit=10');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.statusText}`);
      }
      
      const data = await response.json();
      setHistory(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching rebalance history:', err);
      setError(err instanceof Error ? err.message : 'Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchHistory, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading && history.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white">Recent Rebalances</h3>
          <div className="text-xs text-gray-500">Loading...</div>
        </div>
        <TableSkeleton rows={5} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
        <p className="text-red-400 text-sm">⚠️ {error}</p>
        <button
          onClick={fetchHistory}
          className="mt-2 px-3 py-1 bg-red-500/20 hover:bg-red-500/30 rounded text-red-400 text-xs"
        >
          Retry
        </button>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <div className="text-4xl mb-2">📊</div>
        <p>No rebalance history yet</p>
        <p className="text-sm text-gray-500 mt-1">Execute your first AI-driven allocation to see it here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-white">Recent Rebalances</h3>
        <button
          onClick={fetchHistory}
          className="px-3 py-1 bg-white/5 hover:bg-white/10 rounded-lg text-xs text-gray-400 hover:text-white transition-colors"
          disabled={loading}
        >
          {loading ? '⏳' : '🔄'} Refresh
        </button>
      </div>

      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-xs font-medium text-gray-400 uppercase">Time</th>
              <th className="text-left py-3 px-4 text-xs font-medium text-gray-400 uppercase">Allocation</th>
              <th className="text-left py-3 px-4 text-xs font-medium text-gray-400 uppercase">Risk Scores</th>
              <th className="text-left py-3 px-4 text-xs font-medium text-gray-400 uppercase">Proof</th>
              <th className="text-left py-3 px-4 text-xs font-medium text-gray-400 uppercase">Transaction</th>
            </tr>
          </thead>
          <tbody>
            {history.map((record) => (
              <tr
                key={record.id}
                className="border-b border-white/5 hover:bg-white/5 transition-colors"
              >
                {/* Time */}
                <td className="py-3 px-4">
                  <div className="text-sm text-white">
                    {formatTimeAgo(record.timestamp)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(record.timestamp).toLocaleTimeString()}
                  </div>
                </td>

                {/* Allocation */}
                <td className="py-3 px-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-blue-400">🔄 Jedi</span>
                      <span className="text-sm font-mono text-white">{record.jediswap_pct.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-orange-400">🌀 Ekubo</span>
                      <span className="text-sm font-mono text-white">{record.ekubo_pct.toFixed(1)}%</span>
                    </div>
                  </div>
                </td>

                {/* Risk Scores */}
                <td className="py-3 px-4">
                  <div className="space-y-1">
                    <div className="text-xs">
                      <span className="text-gray-400">Jedi: </span>
                      <span className={`font-mono ${getRiskColor(record.jediswap_risk)}`}>
                        {record.jediswap_risk}
                      </span>
                    </div>
                    <div className="text-xs">
                      <span className="text-gray-400">Ekubo: </span>
                      <span className={`font-mono ${getRiskColor(record.ekubo_risk)}`}>
                        {record.ekubo_risk}
                      </span>
                    </div>
                  </div>
                </td>

                {/* Proof */}
                <td className="py-3 px-4">
                  <ProofBadge
                    hash={record.proof_hash}
                    status={record.proof_status}
                    txHash={record.tx_hash}
                    factHash={record.fact_hash}
                    l2FactHash={record.l2_fact_hash}
                    l2VerifiedAt={record.l2_verified_at}
                    l1FactHash={record.l1_fact_hash}
                    l1VerifiedAt={record.l1_verified_at}
                    network={record.network}
                    submittedAt={record.submitted_at}
                    verifiedAt={record.verified_at}
                    proofJobId={record.proof_job_id || record.id}
                    generationTime={record.proof_generation_time}
                    proofSize={record.proof_size_bytes}
                  />
                </td>

                {/* Transaction */}
                <td className="py-3 px-4">
                  {record.tx_hash ? (
                    <a
                      href={`https://sepolia.voyager.online/tx/${record.tx_hash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2 py-1 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded text-xs text-purple-300 transition-colors"
                    >
                      View TX ↗
                    </a>
                  ) : (
                    <span className="text-xs text-gray-500">Pending</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-3">
        {history.map((record) => (
          <div
            key={record.id}
            className="bg-white/5 rounded-lg p-4 border border-white/10"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-sm text-white font-medium">
                  {formatTimeAgo(record.timestamp)}
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(record.timestamp).toLocaleString()}
                </div>
              </div>
              <ProofBadge
                hash={record.proof_hash}
                status={record.proof_status}
                txHash={record.tx_hash}
                factHash={record.fact_hash}
                submittedAt={record.submitted_at}
                verifiedAt={record.verified_at}
                proofJobId={record.proof_job_id || record.id}
                generationTime={record.proof_generation_time}
                proofSize={record.proof_size_bytes}
              />
            </div>

            {/* Allocation */}
            <div className="space-y-2 mb-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-blue-400">🔄 JediSwap</span>
                <span className="text-sm font-mono text-white">{record.jediswap_pct.toFixed(1)}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-orange-400">🌀 Ekubo</span>
                <span className="text-sm font-mono text-white">{record.ekubo_pct.toFixed(1)}%</span>
              </div>
            </div>

            {/* Risk Scores */}
            <div className="flex items-center justify-between text-xs mb-3">
              <span className="text-gray-400">Risk Scores:</span>
              <div className="flex gap-3">
                <span>
                  Jedi: <span className={`font-mono ${getRiskColor(record.jediswap_risk)}`}>{record.jediswap_risk}</span>
                </span>
                <span>
                  Ekubo: <span className={`font-mono ${getRiskColor(record.ekubo_risk)}`}>{record.ekubo_risk}</span>
                </span>
              </div>
            </div>

            {/* Transaction */}
            {record.tx_hash && (
              <a
                href={`https://sepolia.voyager.online/tx/${record.tx_hash}`}
                target="_blank"
                rel="noopener noreferrer"
                className="block text-center py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded text-xs text-purple-300 transition-colors"
              >
                View Transaction ↗
              </a>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-gray-500 pt-2">
        Showing {history.length} recent rebalance{history.length !== 1 ? 's' : ''}
        {loading && <span className="ml-2">• Refreshing...</span>}
      </div>
    </div>
  );
}

// Helper functions
function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now.getTime() - then.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
}

function getRiskColor(risk: number): string {
  if (risk < 30) return 'text-green-400';
  if (risk < 70) return 'text-yellow-400';
  return 'text-red-400';
}
