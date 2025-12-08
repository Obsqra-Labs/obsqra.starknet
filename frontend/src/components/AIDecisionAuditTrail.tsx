'use client';

import { useState, useEffect } from 'react';
import { Contract, RpcProvider } from 'starknet';
import { getConfig } from '@/lib/config';

/**
 * AIDecisionAuditTrail Component
 * 
 * Displays historical AI allocation decisions from the RiskEngine contract.
 * This provides full transparency and auditability of AI actions.
 */

interface AIDecision {
  decision_id: number;
  block_number: number;
  timestamp: number;
  jediswap_pct: number;
  ekubo_pct: number;
  jediswap_risk: number;
  ekubo_risk: number;
  jediswap_apy: number;
  ekubo_apy: number;
  rationale_hash: string;
  strategy_router_tx: string;
}

export function AIDecisionAuditTrail() {
  const [decisions, setDecisions] = useState<AIDecision[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDecision, setSelectedDecision] = useState<AIDecision | null>(null);
  
  useEffect(() => {
    fetchDecisions();
  }, []);
  
  const fetchDecisions = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const config = getConfig();
      const provider = new RpcProvider({
        nodeUrl: config.rpcUrl
      });
      
      const contract = new Contract(
        [], // We'll use a minimal ABI
        config.riskEngineAddress,
        provider
      );
      
      // Get decision count
      const countResult = await contract.call('get_decision_count');
      const count = Number(countResult);
      
      if (count === 0) {
        setDecisions([]);
        setIsLoading(false);
        return;
      }
      
      // Fetch last 10 decisions
      const decisionsToFetch = Math.min(count, 10);
      const fetchedDecisions: AIDecision[] = [];
      
      for (let i = count; i > count - decisionsToFetch; i--) {
        try {
          const result = await contract.call('get_decision', [i]);
          const decision = (result as any)[0];
          
          fetchedDecisions.push({
            decision_id: Number(decision.decision_id),
            block_number: Number(decision.block_number),
            timestamp: Number(decision.timestamp),
            jediswap_pct: Number(decision.jediswap_pct),
            ekubo_pct: Number(decision.ekubo_pct),
            jediswap_risk: Number(decision.jediswap_risk),
            ekubo_risk: Number(decision.ekubo_risk),
            jediswap_apy: Number(decision.jediswap_apy),
            ekubo_apy: Number(decision.ekubo_apy),
            rationale_hash: String(decision.rationale_hash),
            strategy_router_tx: String(decision.strategy_router_tx),
          });
        } catch (err) {
          console.warn(`Failed to fetch decision #${i}:`, err);
        }
      }
      
      setDecisions(fetchedDecisions);
    } catch (err) {
      console.error('Failed to fetch decisions:', err);
      setError(err instanceof Error ? err.message : 'Failed to load audit trail');
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-soft border border-slate-200 p-8">
        <div className="flex flex-col items-center justify-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-lagoon-300 border-t-transparent" />
          <p className="text-slate-600 font-medium">
            Loading AI decision history from chain...
          </p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
        <h3 className="text-lg font-bold text-red-800 mb-2">
          ❌ Failed to Load Audit Trail
        </h3>
        <p className="text-red-600 text-sm">{error}</p>
        <button
          onClick={fetchDecisions}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }
  
  if (decisions.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-soft border border-slate-200 p-8 text-center">
        <div className="text-6xl mb-4">📜</div>
        <h3 className="text-xl font-display font-bold text-ink mb-2">
          No AI Decisions Yet
        </h3>
        <p className="text-slate-600">
          AI allocation decisions will appear here once executed
        </p>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-2xl shadow-soft border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-display font-bold text-ink">
            📜 AI Decision Audit Trail
          </h2>
          <p className="text-sm text-slate-600 mt-1">
            {decisions.length} decision{decisions.length !== 1 ? 's' : ''} recorded on-chain
          </p>
        </div>
        <button
          onClick={fetchDecisions}
          className="text-sm text-lagoon-600 hover:text-lagoon-700 font-medium flex items-center gap-1"
        >
          🔄 Refresh
        </button>
      </div>
      
      <div className="space-y-3">
        {decisions.map((decision) => (
          <DecisionCard
            key={decision.decision_id}
            decision={decision}
            isSelected={selectedDecision?.decision_id === decision.decision_id}
            onClick={() => setSelectedDecision(
              selectedDecision?.decision_id === decision.decision_id ? null : decision
            )}
          />
        ))}
      </div>
      
      {selectedDecision && (
        <DecisionDetailModal
          decision={selectedDecision}
          onClose={() => setSelectedDecision(null)}
        />
      )}
    </div>
  );
}

// Helper Components

function DecisionCard({
  decision,
  isSelected,
  onClick
}: {
  decision: AIDecision;
  isSelected: boolean;
  onClick: () => void;
}) {
  const bpsToPercent = (bps: number) => (bps / 100).toFixed(1);
  const formatTimestamp = (ts: number) => new Date(ts * 1000).toLocaleString();
  
  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left p-4 rounded-xl border-2 transition-all
        ${isSelected 
          ? 'bg-lagoon-50 border-lagoon-300 shadow-md' 
          : 'bg-slate-50 border-slate-200 hover:border-lagoon-200 hover:bg-lagoon-25'}
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <span className="text-sm font-bold text-ink">
            Decision #{decision.decision_id}
          </span>
          <span className="text-xs text-slate-500 ml-2">
            Block {decision.block_number}
          </span>
        </div>
        <span className="text-xs text-slate-500">
          {formatTimestamp(decision.timestamp)}
        </span>
      </div>
      
      <div className="flex items-center gap-4 text-sm">
        <AllocationBadge
          protocol="JediSwap"
          percentage={bpsToPercent(decision.jediswap_pct)}
          color="lagoon"
        />
        <AllocationBadge
          protocol="Ekubo"
          percentage={bpsToPercent(decision.ekubo_pct)}
          color="mint"
        />
        <span className="text-xs text-slate-500">
          {isSelected ? '🔽 Hide Details' : '🔍 View Details'}
        </span>
      </div>
    </button>
  );
}

function AllocationBadge({
  protocol,
  percentage,
  color
}: {
  protocol: string;
  percentage: string;
  color: 'lagoon' | 'mint';
}) {
  const bgColor = color === 'lagoon' ? 'bg-lagoon-100' : 'bg-mint-100';
  const textColor = color === 'lagoon' ? 'text-lagoon-700' : 'text-mint-700';
  
  return (
    <div className={`${bgColor} ${textColor} px-3 py-1 rounded-full text-xs font-semibold`}>
      {protocol}: {percentage}%
    </div>
  );
}

function DecisionDetailModal({
  decision,
  onClose
}: {
  decision: AIDecision;
  onClose: () => void;
}) {
  const bpsToPercent = (bps: number) => (bps / 100).toFixed(2);
  const formatTimestamp = (ts: number) => new Date(ts * 1000).toLocaleString();
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-2xl font-display font-bold text-ink">
              Decision #{decision.decision_id}
            </h3>
            <p className="text-sm text-slate-600 mt-1">
              {formatTimestamp(decision.timestamp)} • Block {decision.block_number}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700 text-2xl leading-none"
          >
            ×
          </button>
        </div>
        
        {/* Allocation */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-ink mb-3">📊 Allocation</h4>
          <div className="grid grid-cols-2 gap-4">
            <DetailCard label="JediSwap" value={`${bpsToPercent(decision.jediswap_pct)}%`} />
            <DetailCard label="Ekubo" value={`${bpsToPercent(decision.ekubo_pct)}%`} />
          </div>
        </div>
        
        {/* Risk Scores */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-ink mb-3">🛡️ Risk Scores</h4>
          <div className="grid grid-cols-2 gap-4">
            <DetailCard label="JediSwap Risk" value={`${decision.jediswap_risk}/95`} />
            <DetailCard label="Ekubo Risk" value={`${decision.ekubo_risk}/95`} />
          </div>
        </div>
        
        {/* APY */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-ink mb-3">💰 APY at Decision Time</h4>
          <div className="grid grid-cols-2 gap-4">
            <DetailCard label="JediSwap APY" value={`${bpsToPercent(decision.jediswap_apy)}%`} />
            <DetailCard label="Ekubo APY" value={`${bpsToPercent(decision.ekubo_apy)}%`} />
          </div>
        </div>
        
        {/* Proof */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-ink mb-3">🔐 Cryptographic Proof</h4>
          <div className="space-y-2 text-xs font-mono">
            <ProofField label="Rationale Hash" value={decision.rationale_hash} />
            <ProofField label="Strategy Router TX" value={decision.strategy_router_tx || 'N/A'} />
          </div>
        </div>
        
        <div className="mt-6 pt-4 border-t border-slate-200">
          <button
            onClick={onClose}
            className="w-full py-2 px-4 bg-lagoon-500 text-white rounded-lg hover:bg-lagoon-600"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function DetailCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-50 rounded-lg p-3">
      <div className="text-xs text-slate-600 mb-1">{label}</div>
      <div className="text-lg font-bold text-ink">{value}</div>
    </div>
  );
}

function ProofField({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white/50 rounded p-2">
      <div className="text-slate-600 mb-1">{label}:</div>
      <div className="text-ink break-all">{value}</div>
    </div>
  );
}

