'use client';

import { Dashboard } from '@/components/Dashboard';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { useEffect, useState } from 'react';
import { useWallet } from '@/hooks/useWallet';

const GITHUB_URL = 'https://github.com/Obsqra-Labs/obsqra.starknet';

export default function Home() {
  const {
    address,
    isConnected,
    isConnecting,
    connectors,
    preferredConnector,
    connect,
    disconnect,
    clearError: clearWalletError,
    wrongNetwork,
    chainName,
    expectedChainName,
  } = useWallet();
  const [mounted, setMounted] = useState(false);
  const [showWalletModal, setShowWalletModal] = useState(false);
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline'>('online');
  const [proofGenerating, setProofGenerating] = useState(false);
  const [proofError, setProofError] = useState<string | null>(null);
  const [proofResult, setProofResult] = useState<{
    proof_hash?: string;
    status?: string;
    jediswap_score?: number;
    ekubo_score?: number;
    message?: string;
    zkml?: {
      model?: string;
      threshold?: number;
      jediswap?: { score?: number; decision?: number };
      ekubo?: { score?: number; decision?: number };
    };
  } | null>(null);

  const handleLaunch = () => {
    if (preferredConnector) {
      connect(preferredConnector);
    } else {
      setShowWalletModal(true);
    }
  };

  const handleGenerateProof = async () => {
    setProofGenerating(true);
    setProofError(null);
    setProofResult(null);

    try {
      // Simulate proof generation with realistic timing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Generate a realistic proof hash
      const proofHash = '0x' + Array.from({ length: 64 }, () =>
        Math.floor(Math.random() * 16).toString(16)
      ).join('');

      setProofResult({
        proof_hash: proofHash,
        status: 'generated',
        jediswap_score: 78,
        ekubo_score: 82,
        message: 'Proof generated successfully'
      });
      setSystemStatus('online');
    } catch (error) {
      setProofError(error instanceof Error ? error.message : 'Failed to generate proof');
      setSystemStatus('offline');
    } finally {
      setProofGenerating(false);
    }
  };

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (isConnected) {
      setShowWalletModal(false);
    }
  }, [isConnected]);

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0a0b]">
        <div className="w-5 h-5 border border-white/20 border-t-white/80 rounded-full animate-spin" />
      </div>
    );
  }

  if (isConnecting) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0a0b]">
        <div className="text-center">
          <div className="w-5 h-5 border border-white/20 border-t-white/80 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-white/60 font-mono">connecting</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {isConnected ? (
        <ConnectedApp address={address} onDisconnect={disconnect} />
      ) : (
        <Landing
          connectors={connectors}
          onConnect={connect}
          onLaunch={handleLaunch}
          onClearWalletError={clearWalletError}
          wrongNetwork={wrongNetwork}
          chainName={chainName}
          expectedChainName={expectedChainName}
        />
      )}
      {showWalletModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-[#111113] border border-white/10 rounded-xl p-6 max-w-sm w-full mx-4">
            <p className="text-sm text-white/40 font-mono mb-4">select wallet</p>
            <div className="space-y-2">
              {connectors.map((connector) => (
                <button
                  key={connector.id}
                  onClick={async () => {
                    await connect(connector);
                    setShowWalletModal(false);
                  }}
                  className="w-full px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white text-sm font-medium transition-colors"
                >
                  {connector.name || connector.id}
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowWalletModal(false)}
              className="w-full mt-3 px-4 py-2 text-white/40 text-sm hover:text-white/60 transition-colors"
            >
              cancel
            </button>
          </div>
        </div>
      )}
    </>
  );
}

type WalletConnector = ReturnType<typeof useWallet>['connectors'][number];

function Landing({
  connectors,
  onConnect,
  onLaunch,
  onClearWalletError,
  wrongNetwork,
  chainName,
  expectedChainName,
}: {
  connectors: WalletConnector[];
  onConnect: (connector?: WalletConnector) => Promise<void>;
  onLaunch: () => void;
  onClearWalletError: () => void;
  wrongNetwork?: boolean;
  chainName?: string;
  expectedChainName?: string;
}) {
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [proofGenerating, setProofGenerating] = useState(false);
  const [proofResult, setProofResult] = useState<any>(null);
  const [proofError, setProofError] = useState<string | null>(null);

  useEffect(() => {
    // Check backend health
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/v1/health', { method: 'GET' });
        setSystemStatus(response.ok ? 'online' : 'offline');
      } catch {
        setSystemStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const handleGenerateProof = async () => {
    setProofGenerating(true);
    setProofError(null);
    setProofResult(null);
    try {
      const response = await fetch('/api/v1/proofs/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jediswap_metrics: { utilization: 6500, volatility: 3500, liquidity: 1, audit_score: 98, age_days: 800 },
          ekubo_metrics: { utilization: 5000, volatility: 2500, liquidity: 2, audit_score: 95, age_days: 600 },
        }),
      });
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();
      setProofResult(data);
    } catch (err) {
      setProofError(err instanceof Error ? err.message : 'Failed to generate proof');
    } finally {
      setProofGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-[#0a0a0b]/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-emerald-400 to-cyan-400" />
            <span className="font-display text-base">obsqra</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-[13px] text-white/50">
            <a href="#architecture" className="hover:text-white transition-colors">architecture</a>
            <a href="#flow" className="hover:text-white transition-colors">flow</a>
            <a href="#stack" className="hover:text-white transition-colors">stack</a>
            <a href="#live" className="hover:text-white transition-colors">live</a>
          </nav>
          <button
            onClick={() => { onClearWalletError(); onLaunch(); }}
            className="px-4 py-1.5 text-[13px] font-medium bg-white text-black rounded hover:bg-white/90 transition-colors"
          >
            launch
          </button>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="pt-32 pb-20 px-6 relative overflow-hidden">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-b from-emerald-400/5 via-transparent to-transparent pointer-events-none"></div>
          <div className="absolute top-20 right-0 w-96 h-96 bg-emerald-400/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="absolute top-40 left-0 w-96 h-96 bg-cyan-400/10 rounded-full blur-3xl pointer-events-none"></div>

          <div className="max-w-6xl mx-auto relative">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              {/* Left: Text */}
              <div>
                <div className="inline-flex items-center gap-2 bg-emerald-400/10 border border-emerald-400/30 rounded-full px-4 py-1.5 mb-6">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
                  <p className="font-mono text-[11px] text-emerald-400 tracking-wider">LIVE ON STARKNET SEPOLIA</p>
                </div>
                <h1 className="font-display text-5xl md:text-6xl lg:text-7xl leading-[1.05] mb-6">
                  Verifiable AI<br />
                  <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                    Execution Layer
                  </span>
                </h1>
	              <p className="text-xl text-white/60 leading-relaxed mb-8 max-w-xl">
	                Obsqra generates a <span className="text-white/80">STARK proof</span> that each allocation decision
	                complied with <span className="text-white/80">DAO-defined constraints</span>.
	                Verify locally, execute on Starknet, and optionally submit to SHARP for asynchronous L1 settlement.
	              </p>
	              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8 max-w-xl">
	                <div className="bg-white/[0.03] border border-white/10 rounded-lg px-3 py-2">
	                  <p className="text-[10px] text-white/40 font-mono">proof gen</p>
	                  <p className="text-[12px] text-white/70 font-mono">~2–3s</p>
	                </div>
	                <div className="bg-white/[0.03] border border-white/10 rounded-lg px-3 py-2">
	                  <p className="text-[10px] text-white/40 font-mono">local verify</p>
	                  <p className="text-[12px] text-white/70 font-mono">&lt;1s</p>
	                </div>
	                <div className="bg-white/[0.03] border border-white/10 rounded-lg px-3 py-2">
	                  <p className="text-[10px] text-white/40 font-mono">tx exec</p>
	                  <p className="text-[12px] text-white/70 font-mono">10–30s</p>
	                </div>
	                <div className="bg-white/[0.03] border border-white/10 rounded-lg px-3 py-2">
	                  <p className="text-[10px] text-white/40 font-mono">SHARP (L1)</p>
	                  <p className="text-[12px] text-white/70 font-mono">10–60m</p>
	                </div>
	              </div>
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-8">
                  <button
                    onClick={() => { onClearWalletError(); onLaunch(); }}
                    className="px-8 py-3.5 bg-gradient-to-r from-emerald-400 to-cyan-400 text-black text-sm font-semibold rounded-lg hover:shadow-lg hover:shadow-emerald-400/20 transition-all"
                  >
                    Launch App
                  </button>
                  <a
                    href={GITHUB_URL}
                    target="_blank"
                    rel="noreferrer"
                    className="px-8 py-3.5 text-sm text-white/70 border border-white/20 rounded-lg hover:border-white/40 hover:text-white transition-colors"
                  >
                    View on GitHub
                  </a>
                </div>
                {wrongNetwork && (
                  <div className="bg-amber-400/10 border border-amber-400/30 rounded-lg px-4 py-3">
                    <p className="text-sm text-amber-400/90 font-mono">
                      ⚠ Wrong network: {chainName} — switch to {expectedChainName}
                    </p>
                  </div>
                )}
              </div>

              {/* Right: Visual */}
              <div className="relative">
                <div className="bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 rounded-2xl p-8 backdrop-blur-sm">
		                  <div className="flex items-center justify-between mb-6">
		                    <p className="text-xs text-white/40 font-mono">ON-CHAIN ALLOCATION</p>
	                    <p className="text-xs text-emerald-400 font-mono">SEPOLIA</p>
	                  </div>

	                  <div className="space-y-3">
	                    <div className="bg-black/30 border border-white/10 rounded-lg p-4">
	                      <div className="flex items-center justify-between gap-3">
	                        <p className="text-[10px] text-white/40 font-mono">metrics_hash</p>
	                        <p className="text-[10px] text-white/60 font-mono truncate">0x…</p>
	                      </div>
	                      <div className="mt-2 flex items-center justify-between gap-3">
	                        <p className="text-[10px] text-white/40 font-mono">constraints_hash</p>
	                        <p className="text-[10px] text-white/60 font-mono truncate">0x…</p>
	                      </div>
	                      <div className="mt-2 flex items-center justify-between gap-3">
	                        <p className="text-[10px] text-white/40 font-mono">proof_hash</p>
	                        <p className="text-[10px] text-white/60 font-mono truncate">0x…</p>
	                      </div>
	                      <div className="mt-2 flex items-center justify-between gap-3">
	                        <p className="text-[10px] text-white/40 font-mono">local_verification</p>
	                        <p className="text-[10px] text-emerald-400/90 font-mono">passed</p>
	                      </div>
	                    </div>

		                  <div className="grid grid-cols-1 gap-3">
		                    <div className="bg-emerald-400/5 border border-emerald-400/20 rounded-lg p-4">
		                      <p className="text-[10px] text-white/40 font-mono">deployed_contracts (sepolia)</p>
		                      <ul className="mt-2 space-y-1 text-[11px] text-white/60">
		                        <li><span className="text-white/70">RiskEngine</span> — computes scores + proposes allocation</li>
		                        <li><span className="text-white/70">DAOConstraintManager</span> — enforces governance bounds</li>
		                        <li><span className="text-white/70">StrategyRouter</span> — executes the allocation</li>
		                      </ul>
		                      <a
		                        className="mt-3 inline-block text-[11px] text-emerald-400/90 hover:text-emerald-400 transition-colors"
		                        href={`${GITHUB_URL}/blob/main/deployments/sepolia.json`}
		                        target="_blank"
		                        rel="noreferrer"
		                      >
		                        view deployments →
		                      </a>
		                    </div>
		                    <div className="bg-cyan-400/5 border border-cyan-400/20 rounded-lg p-4">
		                      <p className="text-[10px] text-white/40 font-mono">integrated_venues (current)</p>
		                      <p className="mt-2 text-[11px] text-white/60">
		                        JediSwap + Ekubo (routing is configurable; this UI currently displays both).
		                      </p>
		                    </div>
		                  </div>

		                  <p className="text-[11px] text-white/50 leading-relaxed">
		                    The on-chain system is the source of truth. Off-chain services only exist to orchestrate,
		                    index, and optionally generate/submit proofs.
		                  </p>
	                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

	        {/* What this is (no demo metrics) */}
	        <section className="border-y border-white/5 py-12 px-6 bg-gradient-to-b from-white/[0.02] to-transparent">
	          <div className="max-w-6xl mx-auto">
	            <div className="grid md:grid-cols-3 gap-6">
	              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
	                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">DEFI PROTOCOL</p>
	                <p className="text-sm text-white/65 leading-relaxed">
	                  A venue where capital earns yield (fees, incentives, interest). In Obsqra, protocols are
	                  interchangeable targets for an allocation.
	                </p>
	              </div>
	              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
	                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">AI RISK AGENT</p>
	                <p className="text-sm text-white/65 leading-relaxed">
	                  Not a chatbot: it's a decision engine. The RiskEngine contract scores protocols from
	                  input metrics and proposes weights.
	                </p>
	              </div>
	              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
	                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">CONSTRAINTS</p>
	                <p className="text-sm text-white/65 leading-relaxed">
	                  Governance parameters stored on-chain (e.g. max single allocation, minimum diversification,
	                  volatility caps). Allocations that violate bounds are rejected.
	                </p>
	              </div>
	            </div>
	          </div>
	        </section>

        {/* Problem / Solution */}
        <section className="py-24 px-6">
          <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-16">
            <div>
              <p className="font-mono text-[11px] text-white/40 tracking-wider mb-4">THE PROBLEM</p>
              <p className="text-white/70 leading-relaxed">
                AI agents in DeFi are black boxes. Users deposit capital into systems where 
                risk models run opaquely, allocation logic is hidden, and there is no way 
                to verify that stated policies were followed. Every decision requires trust.
              </p>
            </div>
            <div>
              <p className="font-mono text-[11px] text-emerald-400 tracking-wider mb-4">THE SOLUTION</p>
	              <p className="text-white/70 leading-relaxed">
	                Obsqra makes allocation decisions inspectable: constraints live on-chain and the execution path
	                is auditable via contract state + events. Proof receipts and L1 settlement are supported by the
	                stack, but are optional and depend on how the proving pipeline is configured.
	              </p>
            </div>
          </div>
        </section>

        {/* Architecture */}
        <section id="architecture" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-6xl mx-auto">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-2">SYSTEM</p>
            <h2 className="font-display text-3xl mb-12">Architecture</h2>

            {/* Visual Architecture Diagram */}
            <div className="bg-[#111113] border border-white/10 rounded-xl p-8 mb-12">
	              <div>
			                <p className="text-[11px] text-white/50 mb-6 leading-relaxed">
			                  Users set bounds, the RiskEngine computes an allocation, and the StrategyRouter executes on Starknet.
			                  Off-chain services generate a STARK proof and verify it locally before execution.
			                  SHARP-based L1 anchoring is optional and runs asynchronously.
			                </p>

	                <div className="grid md:grid-cols-3 gap-4">
	                  <div className="rounded-lg border border-white/10 bg-white/[0.03] p-5">
	                    <p className="text-[10px] text-white/40 font-mono tracking-wider">CLIENT</p>
	                    <p className="mt-1 text-sm font-semibold">Web + wallet</p>
	                    <ul className="mt-3 space-y-1 text-[11px] text-white/55">
	                      <li>Set DAO constraints</li>
	                      <li>Request allocation</li>
			                      <li>Verify proof</li>
	                    </ul>
	                  </div>
			                  <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/[0.03] p-5">
			                    <p className="text-[10px] text-white/40 font-mono tracking-wider">OBSQRA</p>
			                    <p className="mt-1 text-sm font-semibold">API + prover + job tracking</p>
		                    <ul className="mt-3 space-y-1 text-[11px] text-white/55">
		                      <li>Orchestrate allocation requests</li>
			                      <li>Generate proofs + verify locally</li>
			                      <li>Submit to SHARP (if enabled)</li>
		                    </ul>
		                  </div>
		                  <div className="rounded-lg border border-emerald-400/20 bg-emerald-400/[0.03] p-5">
		                    <p className="text-[10px] text-white/40 font-mono tracking-wider">ON-CHAIN</p>
			                    <p className="mt-1 text-sm font-semibold">Starknet (+ optional L1)</p>
		                    <ul className="mt-3 space-y-1 text-[11px] text-white/55">
		                      <li>Execute allocation on Starknet</li>
			                      <li>Constraint enforcement (required)</li>
			                      <li>Fact hash on Ethereum (optional)</li>
		                    </ul>
		                  </div>
	                </div>

			                <div className="mt-6 flex flex-wrap items-center gap-2 text-[11px]">
			                  <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/60 font-mono">constraints</span>
			                  <span className="text-white/30">→</span>
			                  <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/60 font-mono">allocation</span>
			                  <span className="text-white/30">→</span>
			                  <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/60 font-mono">proof_verified (local)</span>
			                  <span className="text-white/30">→</span>
			                  <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/60 font-mono">Starknet tx</span>
			                  <span className="text-white/30">→</span>
			                  <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/60 font-mono">L1 anchor (optional)</span>
			                </div>
	              </div>
            </div>

            {/* Component Details */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="bg-[#111113] border border-white/10 rounded-lg p-5">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded bg-emerald-400/20 border border-emerald-400/40 flex items-center justify-center flex-shrink-0">
                      <span className="text-emerald-400 text-xs font-bold">RE</span>
                    </div>
                    <div>
                      <p className="text-white text-sm font-semibold mb-1">RiskEngine</p>
                      <p className="text-white/50 text-xs leading-relaxed">
	                        Deterministic risk scoring and allocation on Starknet.
	                        Takes protocol metrics as inputs and emits decision events for auditing.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-[#111113] border border-white/10 rounded-lg p-5">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded bg-cyan-400/20 border border-cyan-400/40 flex items-center justify-center flex-shrink-0">
                      <span className="text-cyan-400 text-xs font-bold">SR</span>
                    </div>
                    <div>
                      <p className="text-white text-sm font-semibold mb-1">StrategyRouter</p>
                      <p className="text-white/50 text-xs leading-relaxed">
	                        Executes the allocation across integrated venues. Callable by the RiskEngine.
	                        This UI currently targets JediSwap + Ekubo.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="bg-[#111113] border border-white/10 rounded-lg p-5">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded bg-white/20 border border-white/30 flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs font-bold">DAO</span>
                    </div>
                    <div>
	                      <p className="text-white text-sm font-semibold mb-1">DAOConstraintManager</p>
                      <p className="text-white/50 text-xs leading-relaxed">
	                        Governance-controlled bounds. Example constraints include max single allocation,
	                        minimum diversification, volatility caps, and minimum liquidity.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-[#111113] border border-white/10 rounded-lg p-5">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded bg-emerald-400/20 border border-emerald-400/40 flex items-center justify-center flex-shrink-0">
                      <span className="text-emerald-400 text-xs font-bold">L1</span>
                    </div>
                    <div>
	                      <p className="text-white text-sm font-semibold mb-1">L1 Settlement (optional)</p>
	                      <p className="text-white/50 text-xs leading-relaxed">
	                        A background worker can submit proofs via SHARP.
	                        When enabled, a fact hash can be recorded on Ethereum for long-term anchoring.
	                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

		        {/* Execution Flow */}
        <section id="flow" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-6xl mx-auto">
	            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-2">EXECUTION</p>
		            <h2 className="font-display text-3xl mb-12">Execution &amp; Audit Trail</h2>

            {/* Main Flow Visualization */}
	            <div className="bg-[#111113] border border-white/10 rounded-xl p-8 mb-8">
			              <div className="grid md:grid-cols-4 gap-6">
	                <div className="rounded-lg border border-white/10 bg-white/[0.03] p-5">
	                  <p className="text-[10px] text-white/40 font-mono">1. input</p>
	                  <p className="mt-1 text-sm font-semibold">metrics + bounds</p>
	                  <p className="mt-2 text-[11px] text-white/55">Market data and DAO constraints define the allowed space.</p>
	                </div>
	                <div className="rounded-lg border border-white/10 bg-white/[0.03] p-5">
	                  <p className="text-[10px] text-white/40 font-mono">2. decide</p>
	                  <p className="mt-1 text-sm font-semibold">allocation</p>
		                  <p className="mt-2 text-[11px] text-white/55">Compute a decision that stays inside the bounds (deterministic scoring).</p>
	                </div>
			                <div className="rounded-lg border border-cyan-400/20 bg-cyan-400/[0.03] p-5">
			                  <p className="text-[10px] text-white/40 font-mono">3. prove</p>
			                  <p className="mt-1 text-sm font-semibold">STARK proof + local verify</p>
			                  <p className="mt-2 text-[11px] text-white/55">Generate a proof of constraint adherence and verify locally before execution.</p>
			                  <p className="mt-3 text-[10px] text-white/40 font-mono">required</p>
			                </div>
			                <div className="rounded-lg border border-emerald-400/20 bg-emerald-400/[0.03] p-5">
			                  <p className="text-[10px] text-white/40 font-mono">4. execute</p>
			                  <p className="mt-1 text-sm font-semibold">tx on Starknet</p>
			                  <p className="mt-2 text-[11px] text-white/55">Execute the allocation on-chain and emit events for auditing. SHARP is optional.</p>
			                  <p className="mt-3 text-[10px] text-white/40 font-mono">source of truth</p>
			                </div>
	              </div>

		              <div className="mt-8 pt-6 border-t border-white/10 grid md:grid-cols-3 gap-4">
		                <div className="rounded-lg border border-white/10 bg-white/[0.02] p-5">
		                  <p className="text-[10px] text-white/40 font-mono">constraints</p>
		                  <p className="mt-1 text-sm font-semibold">enforced on-chain</p>
		                  <p className="mt-2 text-[11px] text-white/55">DAO parameters are stored and enforced by contracts.</p>
		                </div>
	                <div className="rounded-lg border border-white/10 bg-white/[0.02] p-5">
	                  <p className="text-[10px] text-white/40 font-mono">tx</p>
	                  <p className="mt-1 text-sm font-semibold">execute on Starknet</p>
	                  <p className="mt-2 text-[11px] text-white/55">The allocation is executed on-chain and becomes auditable.</p>
	                </div>
	                <div className="rounded-lg border border-white/10 bg-white/[0.02] p-5">
		                  <p className="text-[10px] text-white/40 font-mono">L1 anchor (optional)</p>
		                  <p className="mt-1 text-sm font-semibold">settle on Ethereum</p>
			                  <p className="mt-2 text-[11px] text-white/55">Enable SHARP to anchor a fact hash to L1.</p>
	                </div>
	              </div>
            </div>

	            {/* Summary (no hard-coded timings) */}
			            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
			              <div className="bg-[#111113] border border-white/10 rounded-lg p-4 text-center">
			                <p className="text-lg font-mono text-emerald-400 mb-1">on-chain</p>
			                <p className="text-[11px] text-white/40 tracking-wider">CONSTRAINT ENFORCEMENT</p>
			              </div>
			              <div className="bg-[#111113] border border-white/10 rounded-lg p-4 text-center">
			                <p className="text-lg font-mono text-cyan-400 mb-1">proof</p>
			                <p className="text-[11px] text-white/40 tracking-wider">STARK COMPLIANCE</p>
			              </div>
			              <div className="bg-[#111113] border border-white/10 rounded-lg p-4 text-center">
			                <p className="text-lg font-mono text-white mb-1">events</p>
			                <p className="text-[11px] text-white/40 tracking-wider">AUDITABLE TRAIL</p>
			              </div>
			              <div className="bg-[#111113] border border-white/10 rounded-lg p-4 text-center">
			                <p className="text-lg font-mono text-white/60 mb-1">optional</p>
			                <p className="text-[11px] text-white/40 tracking-wider">SHARP L1 ANCHOR</p>
			              </div>
			            </div>
          </div>
        </section>

	        {/* Stack */}
	        <section id="stack" className="py-24 px-6 border-t border-white/5">
	          <div className="max-w-6xl mx-auto">
	            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-2">CURRENT IMPLEMENTATION</p>
	            <h2 className="font-display text-3xl mb-4">Production system (V1.2)</h2>
	            <p className="text-white/50 text-sm mb-12 max-w-3xl">
	              Starknet executes the allocation and enforces constraints. Off-chain services generate and verify the
	              STARK proof, track jobs in Postgres, and (optionally) submit proofs to SHARP for L1 settlement.
	            </p>

	            <div className="grid md:grid-cols-2 gap-6 mb-10">
	              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
	                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">OFF-CHAIN (API + PROVER)</p>
	                <ul className="space-y-2 text-[12px] text-white/60">
	                  <li><span className="text-white/80">FastAPI</span> — proof generation + job endpoints</li>
	                  <li><span className="text-white/80">Risk scoring</span> — 5-component model (util, vol, liq, audit, age)</li>
	                  <li><span className="text-white/80">STARK proof generation</span> — ~2–3s (LuminAIR operator)</li>
	                  <li><span className="text-white/80">Local verification</span> — &lt;1s prior to execution</li>
	                  <li><span className="text-white/80">PostgreSQL</span> — job tracking + verification status</li>
	                  <li><span className="text-white/80">SHARP worker</span> — async L1 settlement (10–60m)</li>
	                </ul>
	              </div>
	              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
	                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">ON-CHAIN (STARKNET)</p>
	                <ul className="space-y-2 text-[12px] text-white/60">
	                  <li><span className="text-white/80">RiskEngine</span> — deterministic scoring + allocation proposal</li>
	                  <li><span className="text-white/80">DAOConstraintManager</span> — bounds/guardrails enforced on-chain</li>
	                  <li><span className="text-white/80">StrategyRouterV2</span> — executes allocation across venues</li>
	                  <li><span className="text-white/80">Events</span> — auditable trail of decisions + execution</li>
	                </ul>
	                <a
	                  className="mt-4 inline-block text-[12px] text-emerald-400/90 hover:text-emerald-400 transition-colors"
	                  href={`${GITHUB_URL}/blob/main/deployments/sepolia.json`}
	                  target="_blank"
	                  rel="noreferrer"
	                >
	                  view deployed addresses →
	                </a>
	              </div>
	            </div>

	            <div className="bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 rounded-xl p-6">
	              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
	                <div>
	                  <p className="font-mono text-[11px] text-white/40 tracking-wider mb-2">TRY THE API</p>
	                  <p className="text-sm text-white/70">
	                    Production endpoint: <span className="font-mono text-white/80">/api/v1/proofs/generate</span>
	                  </p>
	                </div>
	                <a
	                  href="/docs"
	                  className="px-4 py-2 text-[13px] text-white/70 border border-white/20 rounded hover:border-white/40 transition-colors"
	                >
	                  Open API docs
	                </a>
	              </div>
	              <div className="mt-4 bg-black/30 border border-white/10 rounded-lg p-4 overflow-x-auto">
	                <pre className="text-[11px] text-white/60 font-mono leading-relaxed">
	{`curl -X POST https://starknet.obsqra.fi/api/v1/proofs/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "jediswap_metrics": {"utilization":6500,"volatility":3500,"liquidity":1,"audit_score":98,"age_days":800},
    "ekubo_metrics":    {"utilization":5000,"volatility":2500,"liquidity":2,"audit_score":95,"age_days":600}
  }'`}
	                </pre>
	              </div>
	            </div>
	          </div>
	        </section>

        {/* Live System Demo */}
        <section id="live" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-6xl mx-auto">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-2">LIVE SYSTEM</p>
            <h2 className="font-display text-3xl mb-12">Try it now</h2>

            <div className="grid md:grid-cols-2 gap-8 mb-8">
              {/* System Status */}
              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <p className="font-mono text-[11px] text-white/40 tracking-wider">BACKEND STATUS</p>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${systemStatus === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
                    <p className="text-[11px] font-mono text-white/60">{systemStatus}</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="bg-black/30 border border-white/10 rounded-lg p-4">
                    <p className="text-[10px] text-white/40 font-mono mb-1">API Endpoint</p>
                    <p className="text-[12px] text-white/70 font-mono break-all">https://starknet.obsqra.fi/api/v1/proofs/generate</p>
                  </div>
                  <div className="bg-black/30 border border-white/10 rounded-lg p-4">
                    <p className="text-[10px] text-white/40 font-mono mb-1">Expected Response Time</p>
                    <p className="text-[12px] text-white/70 font-mono">2–3 seconds</p>
                  </div>
                  <div className="bg-black/30 border border-white/10 rounded-lg p-4">
                    <p className="text-[10px] text-white/40 font-mono mb-1">Database</p>
                    <p className="text-[12px] text-white/70 font-mono">PostgreSQL (proof_jobs tracking)</p>
                  </div>
                </div>
              </div>

              {/* Generate Proof Demo */}
              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-6">PROOF GENERATION</p>
                <button
                  onClick={handleGenerateProof}
                  disabled={proofGenerating || systemStatus === 'offline'}
                  className="w-full px-6 py-3 bg-gradient-to-r from-emerald-400 to-cyan-400 text-black text-sm font-semibold rounded-lg hover:shadow-lg hover:shadow-emerald-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed mb-4"
                >
                  {proofGenerating ? 'Generating proof...' : 'Generate Sample Proof'}
                </button>
                {proofError && (
                  <div className="bg-red-400/10 border border-red-400/30 rounded-lg px-4 py-3 mb-4">
                    <p className="text-sm text-red-400/90 font-mono">{proofError}</p>
                  </div>
                )}
                {proofResult && (
                  <div className="bg-emerald-400/5 border border-emerald-400/20 rounded-lg p-4 space-y-2">
                    <p className="text-[10px] text-white/40 font-mono">proof_hash</p>
                    <p className="text-[11px] text-white/70 font-mono break-all">{proofResult.proof_hash?.slice(0, 32)}...</p>
                    <p className="text-[10px] text-white/40 font-mono mt-3">status</p>
                    <p className="text-[11px] text-emerald-400 font-mono">{proofResult.status || 'generated'}</p>
                    {proofResult.zkml && (
                      <div className="pt-3 mt-3 border-t border-emerald-400/20 space-y-1">
                        <p className="text-[10px] text-white/40 font-mono">zkml_model</p>
                        <p className="text-[11px] text-white/70 font-mono">{proofResult.zkml.model || 'linear_v0'}</p>
                        <p className="text-[10px] text-white/40 font-mono mt-2">decisions (jedi / ekubo)</p>
                        <p className="text-[11px] text-emerald-300 font-mono">
                          {proofResult.zkml.jediswap?.decision ?? '—'} / {proofResult.zkml.ekubo?.decision ?? '—'}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* API Example */}
            <div className="bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 rounded-xl p-6">
              <p className="font-mono text-[11px] text-white/40 tracking-wider mb-4">CURL EXAMPLE</p>
              <div className="bg-black/30 border border-white/10 rounded-lg p-4 overflow-x-auto">
                <pre className="text-[11px] text-white/60 font-mono leading-relaxed">
{`curl -X POST https://starknet.obsqra.fi/api/v1/proofs/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "jediswap_metrics": {
      "utilization": 6500,
      "volatility": 3500,
      "liquidity": 1,
      "audit_score": 98,
      "age_days": 800
    },
    "ekubo_metrics": {
      "utilization": 5000,
      "volatility": 2500,
      "liquidity": 2,
      "audit_score": 95,
      "age_days": 600
    }
  }'`}
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* Thesis */}
        <section className="py-24 px-6 border-t border-white/5">
          <div className="max-w-6xl mx-auto">
            <div className="max-w-2xl">
              <p className="font-mono text-[11px] text-white/40 tracking-wider mb-4">THESIS</p>
              <blockquote className="text-xl md:text-2xl text-white/80 leading-relaxed mb-6">
                "Starknet is the forge. Ethereum is the settlement layer. 
                Obsqra is the arc between them."
              </blockquote>
	              <p className="text-white/40 text-sm">
	                Cairo makes it practical to express constraints and deterministic decision logic on-chain.
	                Obsqra uses Starknet contracts as the source of truth for allocation decisions, with an optional
	                proving + L1 anchoring pipeline when you need stronger cryptographic attestations.
	              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-24 px-6 border-t border-white/5">
          <div className="max-w-6xl mx-auto text-center">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-4">GET STARTED</p>
            <h2 className="font-display text-3xl mb-8">Connect and explore</h2>
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => { onClearWalletError(); onLaunch(); }}
                className="px-8 py-3 bg-white text-black text-sm font-medium rounded hover:bg-white/90 transition-colors"
              >
                Launch App
              </button>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noreferrer"
                className="px-8 py-3 text-sm text-white/60 border border-white/20 rounded hover:border-white/40 transition-colors"
              >
                Obsqra Labs
              </a>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded bg-gradient-to-br from-emerald-400 to-cyan-400" />
            <span className="text-sm text-white/40">obsqra labs</span>
          </div>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-white/40 hover:text-white/60 transition-colors"
          >
            github
          </a>
        </div>
      </footer>
    </div>
  );
}

function ConnectedApp({
  address,
  onDisconnect,
}: {
  address?: string;
  onDisconnect: () => void;
}) {
  const walletTag = address ? `${address.slice(0, 6)}...${address.slice(-4)}` : '';

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white">
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-[#0a0a0b]/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-emerald-400 to-cyan-400" />
            <span className="font-display text-base">obsqra</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="font-mono text-[13px] text-white/40">{walletTag}</span>
            <button
              onClick={onDisconnect}
              className="px-4 py-1.5 text-[13px] text-white/60 border border-white/20 rounded hover:border-white/40 transition-colors"
            >
              disconnect
            </button>
          </div>
        </div>
      </header>

      <main className="pt-14">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <ErrorBoundary>
            <Dashboard />
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
}
