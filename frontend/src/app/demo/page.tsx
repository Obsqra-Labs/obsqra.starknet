'use client';

import { useEffect, useMemo, useState } from 'react';
import { getConfig } from '@/lib/config';
import { useModelRegistry } from '@/hooks/useModelRegistry';
import { useDAOConstraints } from '@/hooks/useDAOConstraints';
import { useConstraintApproval, ConstraintSignature } from '@/hooks/useConstraintApproval';
import { useWallet } from '@/hooks/useWallet';
import { HashLink } from '@/components/HashLink';
import { DataPathVisualization } from '@/components/DataPathVisualization';
import { AllocationDisplay } from '@/components/AllocationDisplay';
import { ProofStatusBadge } from '@/components/ProofStatusBadge';

interface DemoProofResponse {
  proof_hash: string;
  fact_hash?: string;
  proof_job_id?: string;
  proof_source: string;
  generation_time_seconds: number;
  proof_size_kb: number;
  jediswap_pct: number;
  ekubo_pct: number;
  jediswap_risk: number;
  ekubo_risk: number;
  constraints_verified: boolean;
  message: string;
  execution_tx_hash?: string;
}

interface ProofSummaryLatest {
  id?: string;
  proof_hash?: string;
  tx_hash?: string;
  fact_hash?: string;
  l2_fact_hash?: string;
  l2_verified_at?: string;
  l1_fact_hash?: string;
  l1_verified_at?: string;
  atlantic_query_id?: string;
  status?: string;
  created_at?: string;
  network?: string;
  proof_source?: string;
  error?: string;
}

interface ProofSummaryResponse {
  total: number;
  l2_verified: number;
  l1_verified: number;
  pending: number;
  failed: number;
  latest?: ProofSummaryLatest;
}

interface RebalanceHistoryEntry {
  id: string;
  timestamp?: string;
  jediswap_pct?: number;
  ekubo_pct?: number;
  jediswap_risk?: number;
  ekubo_risk?: number;
  proof_hash?: string;
  proof_status?: string;
  tx_hash?: string;
  fact_hash?: string;
  l2_fact_hash?: string;
  l2_verified_at?: string;
  l2_block_number?: number;
  l1_fact_hash?: string;
  l1_verified_at?: string;
  l1_block_number?: number;
  proof_source?: string;
  error?: string;
}

interface VerificationStatusResponse {
  proof_job_id: string;
  fact_hash?: string;
  verified: boolean;
  verified_at?: string;
  fact_registry_address: string;
}

interface MarketSnapshot {
  block_number: number;
  block_hash: string;
  timestamp: number;
  apys: Record<string, number>;
  apy_source?: string;
  network: string;
  rpc_url?: string;
}

interface MarketMetricsEntry {
  utilization: number;
  volatility: number;
  liquidity: number;
  audit_score: number;
  age_days: number;
  source?: string;
  apy?: number;
  tvl_usd?: number;
}

interface MarketMetricsResponse {
  jediswap: MarketMetricsEntry;
  ekubo: MarketMetricsEntry;
}

type ProofGenerationStep = 'idle' | 'fetching_market' | 'generating_proof' | 'verifying' | 'complete' | 'error';

// DAO Constraint Manager address (Sepolia)
const DAO_CONSTRAINT_MANAGER_ADDRESS = '0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856' as `0x${string}`;

export default function DemoPage() {
  const config = useMemo(() => getConfig(), []);
  const {
    current,
    history,
    loading: registryLoading,
    registering,
    error: registryError,
    fetchCurrent,
    fetchHistory,
    registerModel,
  } = useModelRegistry();

  // DAO Constraints hook (non-blocking - won't prevent page from loading)
  const {
    constraints: daoConstraints,
    isLoading: constraintsLoading,
    error: constraintsError,
  } = useDAOConstraints(DAO_CONSTRAINT_MANAGER_ADDRESS);

  // Wallet connection hook (for connecting wallet)
  const {
    address: walletAddress,
    isConnected: isWalletConnectedFromHook,
    isConnecting: isWalletConnecting,
    connectors,
    connect: connectWallet,
    preferredConnector,
    error: walletError,
  } = useWallet();
  
  const [showWalletModal, setShowWalletModal] = useState(false);

  // Constraint approval hook
  const {
    signConstraints,
    isSigning: isSigningConstraints,
    error: constraintSignError,
    lastSignature: constraintSignature,
    isConnected: isWalletConnectedFromApproval,
  } = useConstraintApproval();

  // Use wallet connection from either hook (prefer useWallet)
  const isWalletConnected = isWalletConnectedFromHook || isWalletConnectedFromApproval;

  const [proof, setProof] = useState<DemoProofResponse | null>(null);
  const [proofLoading, setProofLoading] = useState(false);
  const [proofError, setProofError] = useState<string | null>(null);
  const [proofSummary, setProofSummary] = useState<ProofSummaryResponse | null>(null);
  const [proofSummaryError, setProofSummaryError] = useState<string | null>(null);
  const [proofSummaryLoading, setProofSummaryLoading] = useState(false);
  const [rebalanceHistory, setRebalanceHistory] = useState<RebalanceHistoryEntry[]>([]);
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatusResponse | null>(null);
  const [verificationError, setVerificationError] = useState<string | null>(null);
  const [adminKey, setAdminKey] = useState('');
  const [versionInput, setVersionInput] = useState('1.0.0');
  const [descriptionInput, setDescriptionInput] = useState('Initial risk scoring model');
  const [marketSnapshot, setMarketSnapshot] = useState<MarketSnapshot | null>(null);
  const [marketMetrics, setMarketMetrics] = useState<MarketMetricsResponse | null>(null);
  const [marketError, setMarketError] = useState<string | null>(null);
  const [proofStep, setProofStep] = useState<ProofGenerationStep>('idle');
  const [modelRegistryExpanded, setModelRegistryExpanded] = useState(false);
  const [constraintsApproved, setConstraintsApproved] = useState(false);
  const [constraintApprovalError, setConstraintApprovalError] = useState<string | null>(null);
  // Editable constraint values (user can adjust before signing)
  // Initialize synchronously with defaults to avoid race conditions
  const [editableConstraints, setEditableConstraints] = useState<{
    max_single: number;
    min_diversification: number;
    max_volatility: number;
    min_liquidity: number;
  }>({
    max_single: 4000, // 40% - defaults
    min_diversification: 2, // 2 protocols
    max_volatility: 5000, // 50%
    min_liquidity: 2, // Tier 2
  });

  useEffect(() => {
    fetchCurrent();
    fetchHistory();
  }, [fetchCurrent, fetchHistory]);

  // Close wallet modal when wallet connects
  useEffect(() => {
    if (isWalletConnected) {
      setShowWalletModal(false);
    }
  }, [isWalletConnected]);

  // Update editable constraints when DAO constraints load (no initialization logic)
  useEffect(() => {
    if (daoConstraints && !constraintsLoading) {
      setEditableConstraints({
        max_single: Number(daoConstraints.max_single_protocol),
        min_diversification: Number(daoConstraints.min_protocols),
        max_volatility: Number(daoConstraints.max_volatility),
        min_liquidity: Number(daoConstraints.min_liquidity),
      });
    }
  }, [daoConstraints, constraintsLoading]);

  const apiBase = config.backendUrl ? `${config.backendUrl}/api/v1` : '/api/v1';

  const fetchProofSummary = async () => {
    setProofSummaryLoading(true);
    setProofSummaryError(null);
    try {
      const response = await fetch(`${apiBase}/analytics/proof-summary`);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Failed to fetch proof summary');
      }
      const data: ProofSummaryResponse = await response.json();
      setProofSummary(data);
    } catch (err) {
      setProofSummaryError(err instanceof Error ? err.message : 'Failed to fetch proof summary');
    } finally {
      setProofSummaryLoading(false);
    }
  };

  const fetchRebalanceHistory = async () => {
    try {
      const response = await fetch(`${apiBase}/analytics/rebalance-history?limit=5`);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Failed to fetch rebalance history');
      }
      const data: RebalanceHistoryEntry[] = await response.json();
      setRebalanceHistory(data || []);
    } catch (err) {
      setRebalanceHistory([]);
    }
  };

  const fetchMarketContext = async () => {
    setMarketError(null);
    try {
      const [snapshotRes, metricsRes] = await Promise.all([
        fetch(`${apiBase}/market/snapshot`),
        fetch(`${apiBase}/market/metrics`),
      ]);

      if (!snapshotRes.ok) {
        const text = await snapshotRes.text();
        throw new Error(text || 'Failed to fetch market snapshot');
      }
      if (!metricsRes.ok) {
        const text = await metricsRes.text();
        throw new Error(text || 'Failed to fetch market metrics');
      }

      const snapshot: MarketSnapshot = await snapshotRes.json();
      const metrics: MarketMetricsResponse = await metricsRes.json();

      setMarketSnapshot(snapshot);
      setMarketMetrics(metrics);
    } catch (err) {
      setMarketError(err instanceof Error ? err.message : 'Failed to fetch market context');
    }
  };

  const fetchVerificationStatus = async (proofJobId?: string) => {
    if (!proofJobId) {
      setVerificationStatus(null);
      return;
    }
    setVerificationError(null);
    try {
      const response = await fetch(`${apiBase}/verification/verification-status/${proofJobId}`);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Failed to fetch verification status');
      }
      const data: VerificationStatusResponse = await response.json();
      setVerificationStatus(data);
    } catch (err) {
      setVerificationError(err instanceof Error ? err.message : 'Failed to fetch verification status');
    }
  };

  useEffect(() => {
    fetchProofSummary();
    fetchRebalanceHistory();
    fetchMarketContext();
  }, [apiBase]);

  useEffect(() => {
    fetchVerificationStatus(proofSummary?.latest?.id);
  }, [proofSummary?.latest?.id]);

  const handleApproveConstraints = async () => {
    if (!isWalletConnected) {
      setConstraintApprovalError('Please connect your wallet first');
      return;
    }

    setConstraintApprovalError(null);
    try {
      await signConstraints(editableConstraints);
      setConstraintsApproved(true);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to sign constraints';
      setConstraintApprovalError(errorMessage);
    }
  };

  const handleGenerateProof = async () => {
    setProofLoading(true);
    setProofError(null);
    setProofStep('fetching_market');
    
    try {
      // Step 1: Fetch market data
      await fetchMarketContext();
      setProofStep('generating_proof');

      // Step 2: Generate proof (include constraint signature if available)
      const requestBody: any = {
        source: 'market',
      };

      // Include constraint signature if user has approved constraints
      if (constraintSignature) {
        requestBody.constraint_signature = {
          signature: constraintSignature.signature,
          signer: constraintSignature.signer,
          constraints: constraintSignature.constraints,
          timestamp: constraintSignature.timestamp,
          message_hash: constraintSignature.message_hash,
        };
      }

      const response = await fetch(`${apiBase}/demo/generate-proof`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        const text = await response.text();
        // Try to parse error message
        let errorMsg = text;
        try {
          const errorJson = JSON.parse(text);
          errorMsg = errorJson.detail || errorJson.message || text;
        } catch {
          // Use raw text
        }
        throw new Error(errorMsg || 'Failed to generate proof');
      }
      
      setProofStep('verifying');
      const data = await response.json();
      setProof(data);
      
      // Step 3: Refresh status
      await fetchProofSummary();
      await fetchRebalanceHistory();
      
      setProofStep('complete');
    } catch (err) {
      setProofStep('error');
      const errorMessage = err instanceof Error ? err.message : 'Proof generation failed';
      setProofError(errorMessage);
    } finally {
      setProofLoading(false);
      // Reset step after a delay
      setTimeout(() => {
        if (proofStep === 'complete' || proofStep === 'error') {
          setProofStep('idle');
        }
      }, 3000);
    }
  };

  const handleRegisterModel = async () => {
    await registerModel(
      {
        version: versionInput,
        description: descriptionInput,
      },
      adminKey.trim() || undefined
    );
    await fetchHistory();
  };

  // Data path steps for visualization
  const dataPathSteps = useMemo(() => {
    type StepStatus = 'pending' | 'active' | 'complete' | 'error';
    
    const steps: Array<{
      id: string;
      label: string;
      description: string;
      status: StepStatus;
      data?: string;
    }> = [
      {
        id: 'market',
        label: 'Market Data',
        description: 'Fetch live APYs and protocol metrics from Starknet',
        status: marketSnapshot ? 'complete' : 'pending',
        data: marketSnapshot ? `Block ${marketSnapshot.block_number}` : undefined,
      },
      {
        id: 'model',
        label: 'Risk Model',
        description: 'Cairo model calculates risk scores deterministically',
        status: proofStep === 'generating_proof' || proofStep === 'verifying' || proofStep === 'complete' ? 'complete' : 'pending',
        data: proof ? `Jedi: ${proof.jediswap_risk}, Ekubo: ${proof.ekubo_risk}` : undefined,
      },
      {
        id: 'prover',
        label: 'Stone Prover',
        description: 'Generate STARK proof of computation (2-4 seconds)',
        status: proofStep === 'verifying' || proofStep === 'complete' ? 'complete' : proofStep === 'generating_proof' ? 'active' : 'pending',
        data: proof ? `${proof.generation_time_seconds.toFixed(2)}s, ${proof.proof_size_kb.toFixed(2)} KB` : undefined,
      },
      {
        id: 'verifier',
        label: 'Integrity Verifier',
        description: 'Verify proof on-chain via Fact Registry',
        status: proofStep === 'complete' && proof ? 'complete' : proofStep === 'verifying' ? 'active' : 'pending',
        data: proof?.fact_hash ? 'Verified' : undefined,
      },
      {
        id: 'registry',
        label: 'Fact Registry',
        description: 'Proof fact hash stored on-chain',
        status: verificationStatus?.verified || proofSummary?.latest?.l2_verified_at ? 'complete' : 'pending',
        data: verificationStatus?.fact_hash || proofSummary?.latest?.l2_fact_hash ? 'Registered' : undefined,
      },
      {
        id: 'contract',
        label: 'Smart Contract',
        description: 'Allocation executed autonomously - existing funds rebalanced',
        status: proof?.execution_tx_hash || proofSummary?.latest?.tx_hash ? 'complete' : 'pending',
        data: proof?.execution_tx_hash || proofSummary?.latest?.tx_hash ? 'Executed' : 'Pending execution',
      },
    ];
    return steps;
  }, [marketSnapshot, proof, proofStep, verificationStatus, proofSummary]);

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-[#0a0a0b]/90 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded bg-gradient-to-br from-emerald-400 to-cyan-400" />
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-white/40">Obsqra</p>
              <h1 className="text-lg font-semibold">zkML Demo</h1>
            </div>
          </div>
          <div className="text-xs text-white/40 font-mono px-3 py-1 bg-white/5 rounded-full">
            {config.networkName.toUpperCase()}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10 space-y-10">
        {/* Hero Section */}
        <section className="text-center space-y-4">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            Verifiable AI for DeFi
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            See how zero-knowledge proofs make AI-driven allocation decisions transparent and verifiable on-chain
          </p>
          <div className="flex items-center justify-center gap-4 text-sm text-white/50">
            <span>Native Stone Prover</span>
            <span>•</span>
            <span>On-Chain Verification</span>
            <span>•</span>
            <span>Model Provenance</span>
          </div>
        </section>

        {/* Data Path Visualization */}
        <DataPathVisualization steps={dataPathSteps} currentStep={proofStep} />

        {/* Proof Generation Section */}
        <section className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-white/40">Live Proof Generation</p>
                <h2 className="text-lg font-semibold">Generate Allocation Proof</h2>
              </div>
            </div>

            <p className="text-sm text-white/60 mb-4">
              Generate a verifiable STARK proof for an optimal allocation decision based on live market data
            </p>

            {/* Market Data Preview */}
            <div className="mb-4 border border-white/10 rounded-lg p-4 space-y-3 bg-black/20">
              <div className="flex items-center justify-between">
                <p className="text-xs uppercase tracking-[0.2em] text-white/40">Current Market State</p>
                <button
                  onClick={fetchMarketContext}
                  className="text-xs px-2 py-1 border border-white/20 rounded text-white/70 hover:text-white transition"
                  disabled={proofLoading}
                >
                  refresh
                </button>
              </div>

              {marketError && (
                <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded p-2">
                  {marketError}
                </p>
              )}

              {marketSnapshot ? (
                <div className="space-y-2 text-xs text-white/70">
                  <div className="flex items-center gap-2">
                    <span className="font-mono">Block {marketSnapshot.block_number}</span>
                    <span>•</span>
                    <span>{new Date(marketSnapshot.timestamp * 1000).toLocaleTimeString()}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span>JediSwap APY: <span className="text-emerald-400 font-semibold">{marketSnapshot.apys?.jediswap?.toFixed(2)}%</span></span>
                    <span>•</span>
                    <span>Ekubo APY: <span className="text-cyan-400 font-semibold">{marketSnapshot.apys?.ekubo?.toFixed(2)}%</span></span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-white/50">Loading market data...</p>
              )}
            </div>

            {/* Constraint Approval Section */}
            <div className="mb-4 border border-white/10 rounded-lg p-4 space-y-3 bg-black/20">
              <div className="flex items-center justify-between">
                <p className="text-xs uppercase tracking-[0.2em] text-white/40">DAO Constraints</p>
                {constraintsApproved && constraintSignature && (
                  <span className="text-xs text-emerald-400 flex items-center gap-1">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Approved
                  </span>
                )}
              </div>

              {constraintsLoading ? (
                <p className="text-xs text-white/50">Loading on-chain constraints...</p>
              ) : (
                <div className="space-y-3 text-xs">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-white/70">Max Single Protocol (%):</span>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={editableConstraints.max_single / 100}
                        onChange={(e) => {
                          const value = Math.max(0, Math.min(100, parseFloat(e.target.value) || 0));
                          setEditableConstraints({
                            ...editableConstraints,
                            max_single: Math.round(value * 100), // Convert to basis points
                          });
                        }}
                        className="w-20 px-2 py-1 bg-black/40 border border-white/20 rounded text-white text-xs text-right focus:outline-none focus:border-emerald-400"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-white/70">Min Diversification (protocols):</span>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        value={editableConstraints.min_diversification}
                        onChange={(e) => {
                          const value = Math.max(1, Math.min(10, parseInt(e.target.value) || 1));
                          setEditableConstraints({
                            ...editableConstraints,
                            min_diversification: value,
                          });
                        }}
                        className="w-20 px-2 py-1 bg-black/40 border border-white/20 rounded text-white text-xs text-right focus:outline-none focus:border-emerald-400"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-white/70">Max Volatility (%):</span>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={editableConstraints.max_volatility / 100}
                        onChange={(e) => {
                          const value = Math.max(0, Math.min(100, parseFloat(e.target.value) || 0));
                          setEditableConstraints({
                            ...editableConstraints,
                            max_volatility: Math.round(value * 100), // Convert to basis points
                          });
                        }}
                        className="w-20 px-2 py-1 bg-black/40 border border-white/20 rounded text-white text-xs text-right focus:outline-none focus:border-emerald-400"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-white/70">Min Liquidity (Tier):</span>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={editableConstraints.min_liquidity}
                        onChange={(e) => {
                          const value = Math.max(1, Math.min(5, parseInt(e.target.value) || 1));
                          setEditableConstraints({
                            ...editableConstraints,
                            min_liquidity: value,
                          });
                        }}
                        className="w-20 px-2 py-1 bg-black/40 border border-white/20 rounded text-white text-xs text-right focus:outline-none focus:border-emerald-400"
                      />
                    </div>
                  </div>
                  {!daoConstraints && (
                    <p className="text-xs text-amber-400/80 mt-2">
                      Using default constraints (on-chain constraints unavailable)
                    </p>
                  )}
                  {daoConstraints && (
                    <button
                      onClick={() => {
                        setEditableConstraints({
                          max_single: Number(daoConstraints.max_single_protocol),
                          min_diversification: Number(daoConstraints.min_protocols),
                          max_volatility: Number(daoConstraints.max_volatility),
                          min_liquidity: Number(daoConstraints.min_liquidity),
                        });
                      }}
                      className="text-xs text-white/60 hover:text-white underline mt-2"
                    >
                      Reset to on-chain values
                    </button>
                  )}
                </div>
              )}

              {!constraintsApproved && (
                <button
                  onClick={handleApproveConstraints}
                  disabled={!isWalletConnected || isSigningConstraints}
                  className="w-full mt-3 px-4 py-2 bg-white/10 border border-white/20 text-white text-xs font-medium rounded-lg hover:bg-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isSigningConstraints ? (
                    <>
                      <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Signing...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                      </svg>
                      <span>Approve Constraints</span>
                    </>
                  )}
                </button>
              )}

              {constraintApprovalError && (
                <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded p-2">
                  {constraintApprovalError}
                </p>
              )}

              {constraintSignError && (
                <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded p-2">
                  {constraintSignError}
                </p>
              )}

              {!isWalletConnected && (
                <div className="mt-3 space-y-2">
                  <p className="text-xs text-amber-400/80">
                    Connect wallet to approve constraints
                  </p>
                  {connectors.length > 0 ? (
                    <button
                      onClick={async () => {
                        try {
                          if (preferredConnector) {
                            await connectWallet(preferredConnector);
                          } else if (connectors.length === 1) {
                            await connectWallet(connectors[0]);
                          } else {
                            // Show modal to select wallet if multiple connectors
                            setShowWalletModal(true);
                          }
                        } catch (err) {
                          console.error('Failed to connect wallet:', err);
                          setConstraintApprovalError(err instanceof Error ? err.message : 'Failed to connect wallet');
                        }
                      }}
                      disabled={isWalletConnecting}
                      className="w-full px-4 py-2 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-xs font-medium rounded-lg hover:bg-emerald-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {isWalletConnecting ? (
                        <>
                          <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          <span>Connecting...</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          <span>Connect Wallet</span>
                        </>
                      )}
                    </button>
                  ) : (
                    <p className="text-xs text-red-400/80">
                      No wallet connectors available. Please install ArgentX or Braavos.
                    </p>
                  )}
                  {walletError && (
                    <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded p-2">
                      {walletError}
                    </p>
                  )}
                </div>
              )}
              {isWalletConnected && !constraintsApproved && editableConstraints && (
                <p className="text-xs text-white/60 mt-2">
                  Adjust constraints above, then click "Approve Constraints" to sign
                </p>
              )}
              {isWalletConnected && walletAddress && (
                <p className="text-xs text-emerald-400/80 mt-2 font-mono">
                  {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
                </p>
              )}
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerateProof}
              disabled={proofLoading || !marketSnapshot}
              className="w-full px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-semibold rounded-lg hover:from-emerald-400 hover:to-cyan-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {proofLoading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>
                    {proofStep === 'fetching_market' && 'Fetching market data...'}
                    {proofStep === 'generating_proof' && 'Generating proof...'}
                    {proofStep === 'verifying' && 'Verifying on-chain...'}
                    {proofStep === 'complete' && 'Complete!'}
                  </span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                  <span>Generate Proof</span>
                </>
              )}
            </button>

            {proofError && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-xs text-red-400 font-medium mb-1">Proof Generation Failed</p>
                <p className="text-xs text-red-300/80">{proofError}</p>
                <button
                  onClick={handleGenerateProof}
                  className="mt-2 text-xs text-red-400 hover:text-red-300 underline"
                >
                  Try again
                </button>
              </div>
            )}
          </div>

          {/* Proof Results */}
          <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-white/40">Proof Receipt</p>
                <h3 className="text-lg font-semibold">Allocation Decision</h3>
              </div>
              {proof && (
                <ProofStatusBadge 
                  verified={!!proof.fact_hash} 
                  verifiedAt={verificationStatus?.verified_at || proofSummary?.latest?.l2_verified_at}
                />
              )}
            </div>

            {proof ? (
              <div className="space-y-4">
                {/* Allocation Display */}
                <AllocationDisplay
                  jediswapPct={proof.jediswap_pct}
                  ekuboPct={proof.ekubo_pct}
                  jediswapRisk={proof.jediswap_risk}
                  ekuboRisk={proof.ekubo_risk}
                />

                {/* Proof Details */}
                <div className="border-t border-white/10 pt-4 space-y-3 text-sm">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-xs text-white/40 mb-1">Proof Hash</p>
                      {proof.proof_hash && proof.proof_hash !== '0x0' ? (
                        <HashLink hash={proof.proof_hash} type="search" className="text-xs" />
                      ) : (
                        <span className="text-xs text-white/50">—</span>
                      )}
                    </div>
                    <div>
                      <p className="text-xs text-white/40 mb-1">Fact Hash</p>
                      {proof.fact_hash ? (
                        <HashLink hash={proof.fact_hash || ''} type="fact" className="text-xs" />
                      ) : (
                        <span className="text-xs text-white/50">—</span>
                      )}
                    </div>
                    <div>
                      <p className="text-xs text-white/40 mb-1">Generation Time</p>
                      <p className="text-white/80">{proof.generation_time_seconds.toFixed(2)}s</p>
                    </div>
                    <div>
                      <p className="text-xs text-white/40 mb-1">Proof Size</p>
                      <p className="text-white/80">{proof.proof_size_kb.toFixed(2)} KB</p>
                    </div>
                    <div>
                      <p className="text-xs text-white/40 mb-1">Source</p>
                      <p className="text-white/80 uppercase text-xs">{proof.proof_source}</p>
                    </div>
                    <div>
                      <p className="text-xs text-white/40 mb-1">Constraints</p>
                      <p className={proof.constraints_verified ? 'text-emerald-400' : 'text-amber-400'}>
                        {proof.constraints_verified 
                          ? '✓ Verified (≤40% max)' 
                          : `⚠ Capped at 40% (${proof.jediswap_pct / 100}% / ${proof.ekubo_pct / 100}%)`}
                      </p>
                      {!proof.constraints_verified && (
                        <p className="text-xs text-white/50 mt-1">
                          One protocol exceeds 40% constraint
                        </p>
                      )}
                    </div>
                    {proof.execution_tx_hash && (
                      <div className="col-span-2">
                        <p className="text-xs text-white/40 mb-1">Execution Transaction</p>
                        <HashLink hash={proof.execution_tx_hash} type="transaction" className="text-xs" />
                        <p className="text-xs text-emerald-400/80 mt-1">✓ Allocation executed autonomously</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-white/50">
                <svg className="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                <p className="text-sm">No proof generated yet</p>
                <p className="text-xs mt-1">Click "Generate Proof" to create a verifiable allocation decision</p>
              </div>
            )}
          </div>
        </section>

        {/* Verification Status & Recent Activity */}
        <section className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-white/40">On-Chain Verification</p>
                <h2 className="text-lg font-semibold">Fact Registry Status</h2>
              </div>
              <button
                onClick={async () => {
                  await fetchProofSummary();
                  await fetchVerificationStatus(proofSummary?.latest?.id);
                }}
                className="text-xs px-3 py-1.5 border border-white/20 rounded-full text-white/70 hover:text-white transition"
              >
                refresh
              </button>
            </div>

            <div className="space-y-4">
              {proofSummary?.latest ? (
                <>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-white/40 mb-1">Latest Proof</p>
                      <HashLink hash={proofSummary.latest?.proof_hash || ''} type="search" />
                    </div>
                    <div>
                      <p className="text-xs text-white/40 mb-1">Fact Hash (L2)</p>
                      <HashLink 
                        hash={verificationStatus?.fact_hash || proofSummary.latest?.l2_fact_hash || ''} 
                        type="fact"
                      />
                    </div>
                    <div>
                      <p className="text-xs text-white/40 mb-1">Fact Registry</p>
                      <HashLink 
                        hash={verificationStatus?.fact_registry_address || '0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c'} 
                        type="contract"
                      />
                    </div>
                    <div>
                      <p className="text-xs text-white/40 mb-1">Verification Status</p>
                      <ProofStatusBadge
                        verified={verificationStatus?.verified || !!proofSummary.latest.l2_verified_at}
                        verifiedAt={verificationStatus?.verified_at || proofSummary.latest.l2_verified_at}
                      />
                    </div>
                    {proofSummary.latest.tx_hash && (
                      <div>
                        <p className="text-xs text-white/40 mb-1">Transaction</p>
                        <HashLink hash={proofSummary.latest.tx_hash} type="transaction" />
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <p className="text-sm text-white/50">No proofs verified yet</p>
              )}

              {verificationError && (
                <p className="text-xs text-red-400">{verificationError}</p>
              )}
            </div>
          </div>

          <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
            <p className="text-xs uppercase tracking-[0.3em] text-white/40 mb-4">Recent Activity</p>
            <h3 className="text-lg font-semibold mb-4">Proof Timeline</h3>
            <div className="space-y-3">
              {proofSummaryLoading && (
                <p className="text-xs text-white/50">Loading proofs…</p>
              )}
              {!proofSummaryLoading && rebalanceHistory.length === 0 && (
                <p className="text-xs text-white/50">No proof jobs recorded yet.</p>
              )}
              {rebalanceHistory.map((entry, idx) => (
                <div key={`rebalance-${entry.id || idx}-${entry.timestamp || idx}-${entry.proof_hash || ''}`} className="border border-white/10 rounded-lg p-3 space-y-2 hover:border-white/20 transition">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold">
                      {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : '—'}
                    </p>
                    <ProofStatusBadge
                      verified={entry.proof_status === 'verified' || !!entry.l2_verified_at}
                      verifiedAt={entry.l2_verified_at}
                    />
                  </div>
                  {entry.jediswap_pct !== undefined && entry.ekubo_pct !== undefined && (
                    <div className="text-xs text-white/70">
                      Allocation: JediSwap {entry.jediswap_pct / 100}% • Ekubo {entry.ekubo_pct / 100}%
                    </div>
                  )}
                  <div className="flex items-center gap-3 text-xs">
                    <HashLink hash={entry.proof_hash || ''} type="search" className="text-white/50" />
                    {entry.l2_fact_hash && (
                      <>
                        <span className="text-white/30">•</span>
                        <HashLink hash={entry.l2_fact_hash} type="fact" className="text-white/50" />
                      </>
                    )}
                  </div>
                  {entry.tx_hash && (
                    <div className="pt-2 border-t border-white/10">
                      <HashLink hash={entry.tx_hash || ''} type="transaction" className="text-xs" label="View Transaction" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Model Registry (Collapsible) */}
        <section className="bg-[#111113] border border-white/10 rounded-xl overflow-hidden">
          <button
            onClick={() => setModelRegistryExpanded(!modelRegistryExpanded)}
            className="w-full p-6 flex items-center justify-between hover:bg-white/5 transition"
          >
            <div className="text-left">
              <p className="text-xs uppercase tracking-[0.3em] text-white/40">Model Provenance</p>
              <h3 className="text-lg font-semibold">Model Registry</h3>
            </div>
            {modelRegistryExpanded ? (
              <svg className="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            )}
          </button>

          {modelRegistryExpanded && (
            <div className="px-6 pb-6 space-y-6 border-t border-white/10">
              {/* Current Model */}
              <div className="pt-6">
                <h4 className="text-sm font-semibold mb-4">Current Model</h4>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <p className="text-xs text-white/40 mb-1">Registry Address</p>
                    <HashLink 
                      hash={current?.registry_address || config.modelRegistryAddress} 
                      type="contract"
                    />
                  </div>
                  <div>
                    <p className="text-xs text-white/40 mb-1">Version</p>
                    <p className="text-sm font-semibold">{current?.version || '—'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/40 mb-1">Model Hash</p>
                    <HashLink hash={current?.model_hash || ''} type="search" />
                  </div>
                  <div>
                    <p className="text-xs text-white/40 mb-1">Deployed At</p>
                    <p className="text-sm">
                      {current?.deployed_at
                        ? new Date(current.deployed_at * 1000).toLocaleString()
                        : '—'}
                    </p>
                  </div>
                </div>
                {current?.description && (
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <p className="text-xs text-white/40 mb-1">Description</p>
                    <p className="text-sm text-white/80">{current.description}</p>
                  </div>
                )}
              </div>

              {/* Register New Version (Admin) */}
              <div className="pt-6 border-t border-white/10">
                <h4 className="text-sm font-semibold mb-4">Register New Version</h4>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-white/40 mb-1 block">Version (felt or semver)</label>
                    <input
                      value={versionInput}
                      onChange={(e) => setVersionInput(e.target.value)}
                      className="w-full bg-black/40 border border-white/10 rounded px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/40 mb-1 block">Description</label>
                    <input
                      value={descriptionInput}
                      onChange={(e) => setDescriptionInput(e.target.value)}
                      className="w-full bg-black/40 border border-white/10 rounded px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/40 mb-1 block">Admin Key (optional)</label>
                    <input
                      value={adminKey}
                      onChange={(e) => setAdminKey(e.target.value)}
                      placeholder="X-Admin-Key"
                      className="w-full bg-black/40 border border-white/10 rounded px-3 py-2 text-sm"
                    />
                  </div>
                  <button
                    onClick={handleRegisterModel}
                    disabled={registering}
                    className="w-full px-4 py-2 bg-emerald-500/20 border border-emerald-400/40 rounded text-sm text-emerald-200 hover:bg-emerald-500/30 transition disabled:opacity-50"
                  >
                    {registering ? 'Registering…' : 'Register Model on-Chain'}
                  </button>
                </div>
              </div>

              {/* Version History */}
              {history.length > 0 && (
                <div className="pt-6 border-t border-white/10">
                  <h4 className="text-sm font-semibold mb-4">Version History</h4>
                  <div className="space-y-2">
                    {history.map((entry, idx) => (
                      <div key={`version-${entry.version_felt}-${entry.model_hash || ''}-${idx}-${entry.deployed_at || Date.now()}`} className="flex items-center justify-between gap-3 border border-white/10 rounded-lg px-4 py-3">
                        <div>
                          <p className="text-sm font-semibold">v{entry.version}</p>
                          <HashLink hash={entry.model_hash || ''} type="search" className="text-xs text-white/50" />
                        </div>
                        <div className="text-xs text-white/50">
                          {entry.deployed_at ? new Date(entry.deployed_at * 1000).toLocaleString() : '—'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </main>

      {/* Wallet Selection Modal */}
      {showWalletModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-[#111113] border border-white/10 rounded-xl p-6 max-w-sm w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-white/40 font-mono">Select Wallet</p>
              <button
                onClick={() => setShowWalletModal(false)}
                className="text-white/40 hover:text-white/60 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-2">
              {connectors.map((connector) => (
                <button
                  key={connector.id}
                  onClick={async () => {
                    try {
                      await connectWallet(connector);
                      setShowWalletModal(false);
                    } catch (err) {
                      console.error('Failed to connect wallet:', err);
                      setConstraintApprovalError(err instanceof Error ? err.message : 'Failed to connect wallet');
                    }
                  }}
                  disabled={isWalletConnecting}
                  className="w-full px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {connector.name || connector.id}
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowWalletModal(false)}
              className="w-full mt-3 px-4 py-2 text-white/40 text-sm hover:text-white/60 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
