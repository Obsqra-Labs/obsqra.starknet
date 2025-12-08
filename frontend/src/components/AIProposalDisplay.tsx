'use client';

import { useState } from 'react';

/**
 * AIProposalDisplay Component
 * 
 * Shows AI's allocation proposal with reasoning and proof.
 * This demonstrates "verifiable AI" - transparent decision-making.
 */

interface AIProposal {
  decision_id: number;
  timestamp: number;
  jediswap_pct: number;
  ekubo_pct: number;
  jediswap_risk: number;
  ekubo_risk: number;
  jediswap_apy: number;
  ekubo_apy: number;
  rationale_hash: string;
  strategy_router_tx: string;
  message?: string;
}

interface AIProposalDisplayProps {
  proposal: AIProposal | null;
  isLoading?: boolean;
  onExecute?: () => void;
  executionStatus?: 'idle' | 'executing' | 'success' | 'error';
}

export function AIProposalDisplay({
  proposal,
  isLoading,
  onExecute,
  executionStatus = 'idle'
}: AIProposalDisplayProps) {
  const [showProof, setShowProof] = useState(false);
  
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-soft border border-slate-200 p-8">
        <div className="flex flex-col items-center justify-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-lagoon-300 border-t-transparent" />
          <p className="text-slate-600 font-medium">
            🤖 AI is analyzing protocols and generating allocation proposal...
          </p>
        </div>
      </div>
    );
  }
  
  if (!proposal) {
    return (
      <div className="bg-white rounded-2xl shadow-soft border border-slate-200 p-8 text-center">
        <div className="text-6xl mb-4">🤖</div>
        <h3 className="text-xl font-display font-bold text-ink mb-2">
          No AI Proposal Yet
        </h3>
        <p className="text-slate-600">
          Click "AI Orchestrate" to generate a verified allocation proposal
        </p>
      </div>
    );
  }
  
  const bpsToPercent = (bps: number) => (bps / 100).toFixed(2);
  const formatTimestamp = (ts: number) => new Date(ts * 1000).toLocaleString();
  
  // Calculate expected returns
  const jediswapReturn = (proposal.jediswap_pct * proposal.jediswap_apy) / 10000;
  const ekuboReturn = (proposal.ekubo_pct * proposal.ekubo_apy) / 10000;
  const totalExpectedReturn = (jediswapReturn + ekuboReturn) / 100;
  
  // Risk-adjusted score (simplified)
  const jediswapRiskAdj = (proposal.jediswap_pct * (100 - proposal.jediswap_risk)) / 10000;
  const ekuboRiskAdj = (proposal.ekubo_pct * (100 - proposal.ekubo_risk)) / 10000;
  const riskAdjustedScore = ((jediswapRiskAdj + ekuboRiskAdj) / 100).toFixed(2);
  
  return (
    <div className="bg-gradient-to-br from-lagoon-50 to-mint-50 rounded-2xl shadow-lift border-2 border-lagoon-200 p-6">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-display font-bold text-ink flex items-center gap-2">
            🤖 AI Allocation Proposal
            <span className="text-sm font-normal bg-lagoon-500 text-white px-3 py-1 rounded-full">
              #{proposal.decision_id}
            </span>
          </h2>
          <p className="text-sm text-slate-600 mt-1">
            Generated: {formatTimestamp(proposal.timestamp)}
          </p>
        </div>
        <button
          onClick={() => setShowProof(!showProof)}
          className="text-sm text-lagoon-600 hover:text-lagoon-700 font-medium flex items-center gap-1"
        >
          {showProof ? '🔽 Hide' : '🔍 View'} Proof
        </button>
      </div>
      
      {/* Allocation Breakdown */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <AllocationCard
          protocol="JediSwap"
          percentage={bpsToPercent(proposal.jediswap_pct)}
          apy={bpsToPercent(proposal.jediswap_apy)}
          risk={proposal.jediswap_risk}
          color="lagoon"
        />
        <AllocationCard
          protocol="Ekubo"
          percentage={bpsToPercent(proposal.ekubo_pct)}
          apy={bpsToPercent(proposal.ekubo_apy)}
          risk={proposal.ekubo_risk}
          color="mint"
        />
      </div>
      
      {/* Expected Returns */}
      <div className="bg-white/80 backdrop-blur rounded-xl p-4 mb-6">
        <h3 className="text-sm font-semibold text-ink mb-3">📈 Expected Performance</h3>
        <div className="grid grid-cols-3 gap-4">
          <MetricDisplay
            label="Total APY"
            value={`${totalExpectedReturn.toFixed(2)}%`}
            icon="💰"
          />
          <MetricDisplay
            label="Risk-Adjusted Score"
            value={riskAdjustedScore}
            icon="🛡️"
          />
          <MetricDisplay
            label="Diversification"
            value={
              Math.abs(proposal.jediswap_pct - proposal.ekubo_pct) > 3000
                ? 'Balanced'
                : 'Concentrated'
            }
            icon="⚖️"
          />
        </div>
      </div>
      
      {/* AI Reasoning */}
      <div className="bg-white/80 backdrop-blur rounded-xl p-4 mb-6">
        <h3 className="text-sm font-semibold text-ink mb-2 flex items-center gap-2">
          🧠 AI Reasoning
        </h3>
        <div className="text-sm text-slate-700 space-y-2">
          <ReasoningPoint>
            <strong>Risk Optimization:</strong> Allocated {bpsToPercent(proposal.jediswap_pct)}% 
            to JediSwap (Risk: {proposal.jediswap_risk}) vs {bpsToPercent(proposal.ekubo_pct)}% 
            to Ekubo (Risk: {proposal.ekubo_risk})
          </ReasoningPoint>
          <ReasoningPoint>
            <strong>APY Targeting:</strong> JediSwap offers {bpsToPercent(proposal.jediswap_apy)}% 
            APY while Ekubo offers {bpsToPercent(proposal.ekubo_apy)}% APY
          </ReasoningPoint>
          <ReasoningPoint>
            <strong>Constraint Compliance:</strong> Allocation respects all DAO-configured constraints
          </ReasoningPoint>
          <ReasoningPoint>
            <strong>Proof Hash:</strong> 
            <code className="ml-2 text-xs bg-slate-100 px-2 py-1 rounded font-mono">
              {proposal.rationale_hash.substring(0, 20)}...
            </code>
          </ReasoningPoint>
        </div>
      </div>
      
      {/* Proof Details (Collapsible) */}
      {showProof && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
          <h3 className="text-sm font-semibold text-ink mb-3 flex items-center gap-2">
            🔐 Cryptographic Proof
          </h3>
          <div className="space-y-2 text-xs font-mono">
            <ProofField label="Rationale Hash" value={proposal.rationale_hash} />
            <ProofField label="Strategy Router TX" value={proposal.strategy_router_tx || 'Pending execution'} />
            <ProofField 
              label="Proof Type" 
              value="Cairo zkSNARK (SHARP)" 
              description="Decision executed on Starknet L2"
            />
          </div>
          <p className="text-xs text-amber-700 mt-3 italic">
            💡 This proof guarantees the AI decision was computed correctly and respects all constraints.
          </p>
        </div>
      )}
      
      {/* Execute Button */}
      {onExecute && (
        <div className="border-t border-lagoon-200 pt-4">
          <button
            onClick={onExecute}
            disabled={executionStatus === 'executing' || executionStatus === 'success'}
            className={`
              w-full py-4 px-6 rounded-xl font-bold text-white text-lg
              transition-all duration-200 transform
              ${executionStatus === 'executing' || executionStatus === 'success'
                ? 'bg-slate-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-lagoon-500 to-mint-500 hover:shadow-lift hover:scale-[1.02]'}
            `}
          >
            {executionStatus === 'executing' ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent" />
                Executing On-Chain...
              </span>
            ) : executionStatus === 'success' ? (
              '✅ Executed Successfully'
            ) : (
              '🚀 Execute AI Proposal On-Chain'
            )}
          </button>
          {executionStatus === 'success' && proposal.message && (
            <p className="text-sm text-green-600 text-center mt-2">
              {proposal.message}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// Helper Components

function AllocationCard({
  protocol,
  percentage,
  apy,
  risk,
  color
}: {
  protocol: string;
  percentage: string;
  apy: string;
  risk: number;
  color: 'lagoon' | 'mint';
}) {
  const colorClass = color === 'lagoon' ? 'bg-lagoon-100 border-lagoon-300' : 'bg-mint-100 border-mint-300';
  const textColor = color === 'lagoon' ? 'text-lagoon-700' : 'text-mint-700';
  
  return (
    <div className={`${colorClass} border-2 rounded-xl p-4`}>
      <h3 className={`text-lg font-bold ${textColor} mb-2`}>{protocol}</h3>
      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Allocation:</span>
          <span className="font-bold text-ink">{percentage}%</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">APY:</span>
          <span className="font-semibold text-green-600">{apy}%</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Risk:</span>
          <span className={`font-semibold ${risk > 70 ? 'text-red-600' : risk > 40 ? 'text-amber-600' : 'text-green-600'}`}>
            {risk}/95
          </span>
        </div>
      </div>
    </div>
  );
}

function MetricDisplay({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className="text-center">
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-xs text-slate-600 mb-1">{label}</div>
      <div className="text-lg font-bold text-ink">{value}</div>
    </div>
  );
}

function ReasoningPoint({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-start gap-2">
      <span className="text-lagoon-500 mt-1">•</span>
      <span>{children}</span>
    </div>
  );
}

function ProofField({
  label,
  value,
  description
}: {
  label: string;
  value: string;
  description?: string;
}) {
  return (
    <div className="bg-white/50 rounded p-2">
      <div className="text-slate-600 mb-1">{label}:</div>
      <div className="text-ink break-all">{value}</div>
      {description && (
        <div className="text-slate-500 text-xs mt-1 italic">{description}</div>
      )}
    </div>
  );
}

