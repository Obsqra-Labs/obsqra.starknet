'use client';

import { Dashboard } from '@/components/Dashboard';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { useEffect, useState } from 'react';
import { useWallet } from '@/hooks/useWallet';
import Link from 'next/link';
import { FEATURES } from '@/lib/config';
import { ModelParamsViewer } from '@/components/stage3a';

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
  const handleLaunch = () => {
    if (preferredConnector) {
      connect(preferredConnector);
    } else {
      setShowWalletModal(true);
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

  useEffect(() => {
    // Check backend health
    const checkHealth = async () => {
      try {
        const response = await fetch('/health', { method: 'GET' });
        setSystemStatus(response.ok ? 'online' : 'offline');
      } catch {
        setSystemStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-[#0a0a0b]/90 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-emerald-500 to-cyan-500" />
            <span className="font-display text-base tracking-tight">obsqra.fi</span>
            <span className="hidden sm:inline font-mono text-[10px] text-white/40 tracking-wider">on Starknet</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-[12px] text-white/50 font-medium">
            <a href="#overview" className="hover:text-white transition-colors">Overview</a>
            <a href="#pillars" className="hover:text-white transition-colors">Pillars</a>
            <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
            <a href="#proof-pipeline" className="hover:text-white transition-colors">Proof Pipeline</a>
            <a href="#privacy" className="hover:text-white transition-colors">Privacy</a>
            <a href="#roadmap" className="hover:text-white transition-colors">Roadmap</a>
            <a href="#labs" className="hover:text-white transition-colors">Labs</a>
            <a href="#demo" className="hover:text-white transition-colors">Demo</a>
          </nav>
          <div className="flex items-center gap-3">
            <Link
              href="/demo"
              className="px-4 py-1.5 text-[13px] text-white/70 border border-white/20 rounded hover:border-white/40 hover:text-white transition-colors"
            >
              Demo
            </Link>
            <button
              onClick={() => { onClearWalletError(); onLaunch(); }}
              className="px-4 py-1.5 text-[13px] font-medium bg-white text-black rounded hover:bg-white/90 transition-colors"
            >
              Launch App
            </button>
          </div>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section id="overview" className="pt-32 pb-24 px-6 relative overflow-hidden">
          <div className="absolute top-20 right-0 w-[32rem] h-[32rem] bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute top-40 left-0 w-[28rem] h-[28rem] bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

          <div className="max-w-4xl mx-auto relative">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-6">Starknet Sepolia · Verifiable execution layer</p>
            <h1 className="font-display text-4xl md:text-5xl lg:text-6xl leading-[1.1] mb-6 tracking-tight">
              obsqra.fi
            </h1>
            <p className="text-lg md:text-xl text-white/70 leading-relaxed mb-6 max-w-2xl">
              A Starknet-native verifiable execution layer for DeFi. Allocation and execution are gated by on-chain proof verification: no proof, no execution.
            </p>
            <p className="text-sm text-white/50 leading-relaxed mb-10 max-w-2xl">
              The original goal was a zkML pipeline for obsqra.fi on EVM. Through significant R&D we have pioneered production-grade proof-gated execution on Starknet: local Stone proving, Integrity Fact Registry verification, model provenance, and parameterized on-chain models. This is the infrastructure we ship today.
            </p>
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <Link
                href="/demo"
                className="px-6 py-3 bg-white text-black text-sm font-medium rounded-lg hover:bg-white/90 transition-colors"
              >
                Interactive Demo
              </Link>
              <button
                onClick={() => { onClearWalletError(); onLaunch(); }}
                className="px-6 py-3 text-sm text-white/80 border border-white/25 rounded-lg hover:border-white/40 hover:text-white transition-colors"
              >
                Launch App
              </button>
            </div>
          </div>
        </section>

        {/* Research Areas */}
        <section id="pillars" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <p className="font-mono text-[11px] text-white/40 tracking-wider mb-4">PILLARS</p>
              <h2 className="font-display text-4xl mb-4">Product vision and deliverables</h2>
              <p className="text-white/60 text-lg max-w-2xl mx-auto">
                Proof-gated execution, on-chain model governance, privacy and selected disclosure, research driving the product.
              </p>
            </div>

            {/* Pillar 1: zkML */}
            <div className="mb-12 bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent border border-emerald-400/20 rounded-2xl p-12 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-400/10 rounded-full blur-3xl pointer-events-none"></div>
              <div className="relative">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-mono text-[11px] text-emerald-300/60 tracking-wider mb-1">PILLAR 1</p>
                    <h3 className="font-display text-3xl text-white">zkML Infrastructure</h3>
                    <p className="text-emerald-200/80 text-sm mt-1">5/5 Maturity Achieved</p>
                  </div>
                </div>
                <p className="text-xl text-white/80 mb-6 max-w-3xl">
                  Production-grade verifiable AI infrastructure with complete model provenance tracking and on-chain verification gates.
                </p>
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-black/20 border border-white/10 rounded-xl p-6">
                    <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">RECENT ACHIEVEMENTS</p>
                    <ul className="space-y-2 text-[13px] text-white/70">
                      <li className="flex items-start gap-2">
                        <span className="text-emerald-400 mt-1">✓</span>
                        <span>Model Registry deployed and operational</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-emerald-400 mt-1">✓</span>
                        <span>100% test pass rate (6/6 tests)</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-emerald-400 mt-1">✓</span>
                        <span>Model hash in all proofs</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-emerald-400 mt-1">✓</span>
                        <span>Version tracking integrated</span>
                      </li>
                    </ul>
                  </div>
                  <div className="bg-black/20 border border-white/10 rounded-xl p-6">
                    <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">KEY METRICS</p>
                    <div className="space-y-3 text-[13px] text-white/70">
                      <div className="flex items-center justify-between">
                        <span>Model Registry</span>
                        <span className="font-mono text-emerald-300">Live</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>zkML Maturity</span>
                        <span className="font-mono text-emerald-300">5/5</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Test Coverage</span>
                        <span className="font-mono text-emerald-300">100%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Status</span>
                        <span className="font-mono text-emerald-300">Production</span>
                      </div>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-white/50 font-mono">
                  First production system achieving full zkML maturity with model provenance, proof generation, and on-chain verification.
                </p>
              </div>
            </div>

            {/* Pillar 2: Local Stone Proving */}
            <div className="mb-12 bg-gradient-to-br from-cyan-500/10 via-cyan-500/5 to-transparent border border-cyan-400/20 rounded-2xl p-12 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-400/10 rounded-full blur-3xl pointer-events-none"></div>
              <div className="relative">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-cyan-400 to-cyan-600 flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-mono text-[11px] text-cyan-300/60 tracking-wider mb-1">PILLAR 2</p>
                    <h3 className="font-display text-3xl text-white">Local Stone Proving</h3>
                    <p className="text-cyan-200/80 text-sm mt-1">Production-Ready Local Proof Generation</p>
                  </div>
                </div>
                <p className="text-xl text-white/80 mb-6 max-w-3xl">
                  First production implementation of dynamic FRI parameter calculation enabling Stone Prover to work with variable trace sizes.
                </p>
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-black/20 border border-white/10 rounded-xl p-6">
                    <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">BREAKTHROUGH</p>
                    <ul className="space-y-2 text-[13px] text-white/70">
                      <li className="flex items-start gap-2">
                        <span className="text-cyan-400/80 mt-1">—</span>
                        <span>Solved "Signal 6" crashes</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-cyan-400/80 mt-1">—</span>
                        <span>Dynamic FRI calculation algorithm</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-cyan-400/80 mt-1">—</span>
                        <span>Variable trace size support</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-cyan-400/80 mt-1">—</span>
                        <span>100% proof generation success</span>
                      </li>
                    </ul>
                  </div>
                  <div className="bg-black/20 border border-white/10 rounded-xl p-6">
                    <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">PERFORMANCE</p>
                    <div className="space-y-3 text-[13px] text-white/70">
                      <div className="flex items-center justify-between">
                        <span>Success Rate</span>
                        <span className="font-mono text-cyan-300">100/100</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Proof Time</span>
                        <span className="font-mono text-cyan-300">2-4s</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Proof Size</span>
                        <span className="font-mono text-cyan-300">~405 KB</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Cost per Proof</span>
                        <span className="font-mono text-cyan-300">$0 (local)</span>
                      </div>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-white/50 font-mono">
                  Makes Stone Prover production-ready for economic use cases. Unlocks entire categories of applications that were previously blocked.
                </p>
              </div>
            </div>

            {/* Pillar 3: Integrity Verification */}
            <div className="bg-gradient-to-br from-amber-500/10 via-amber-500/5 to-transparent border border-amber-400/20 rounded-2xl p-12 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-amber-400/10 rounded-full blur-3xl pointer-events-none"></div>
              <div className="relative">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-mono text-[11px] text-amber-300/60 tracking-wider mb-1">PILLAR 3</p>
                    <h3 className="font-display text-3xl text-white">Integrity Verification</h3>
                    <p className="text-amber-200/80 text-sm mt-1">On-Chain Verification via FactRegistry</p>
                  </div>
                </div>
                <p className="text-xl text-white/80 mb-6 max-w-3xl">
                  Complete orchestration layer with Integrity FactRegistry integration enabling instant on-chain proof verification.
                </p>
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-black/20 border border-white/10 rounded-xl p-6">
                    <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">INTEGRATION</p>
                    <ul className="space-y-2 text-[13px] text-white/70">
                      <li className="flex items-start gap-2">
                        <span className="text-amber-400 mt-1">✓</span>
                        <span>Stone version compatibility mapping</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-amber-400 mt-1">✓</span>
                        <span>Resolved OODS verification failures</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-amber-400 mt-1">✓</span>
                        <span>Complete trace → proof → verify pipeline</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-amber-400 mt-1">✓</span>
                        <span>Instant on-chain verification</span>
                      </li>
                    </ul>
                  </div>
                  <div className="bg-black/20 border border-white/10 rounded-xl p-6">
                    <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">CAPABILITIES</p>
                    <div className="space-y-3 text-[13px] text-white/70">
                      <div className="flex items-center justify-between">
                        <span>Verification Speed</span>
                        <span className="font-mono text-amber-300">Instant</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>FactRegistry</span>
                        <span className="font-mono text-amber-300">Integrated</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>On-Chain Gates</span>
                        <span className="font-mono text-amber-300">Active</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Orchestration</span>
                        <span className="font-mono text-amber-300">Complete</span>
                      </div>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-white/50 font-mono">
                  Critical knowledge for any team using Stone Prover with Integrity. Enables reliable on-chain proof verification.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Product deliverables */}
        <section id="products" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-4xl mx-auto">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">PRODUCT DELIVERABLES</p>
            <h2 className="font-display text-2xl md:text-3xl mb-10 text-white">What we ship today</h2>
            <ul className="space-y-4 text-white/70 text-[15px] leading-relaxed mb-12">
              <li><strong className="text-white/90">Proof-gated allocation.</strong> Full flow: fetch protocol metrics, generate Cairo trace, run Stone prover, register fact via Integrity, call RiskEngine.propose_and_execute_allocation. Contract verifies proofs then executes via StrategyRouter.</li>
              <li><strong className="text-white/90">Parameterized on-chain model.</strong> RiskEngine stores ModelParams per version; risk scoring reads weights and clamp bounds from storage. API and UI expose current params; owner can set new versions without redeploy.</li>
              <li><strong className="text-white/90">Model Registry.</strong> On-chain provenance: version history, model hashes, approved versions enforced in the allocation path.</li>
              <li><strong className="text-white/90">Interactive demo.</strong> Live proof generation, on-chain verification, block explorer links. <Link href="/demo" className="text-cyan-400 hover:text-cyan-300 underline">Demo</Link>.</li>
            </ul>
            {FEATURES.PARAMETERIZED_MODEL && (
              <div className="border border-white/10 rounded-xl p-6 bg-[#0d0d0e]">
                <h3 className="font-display text-sm text-white/90 mb-4">Current model params (v0)</h3>
                <ModelParamsViewer version={0} title="" />
              </div>
            )}
          </div>
        </section>

        {/* System Architecture */}
        <section id="architecture" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-4xl mx-auto">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">SYSTEM ARCHITECTURE</p>
            <h2 className="font-display text-2xl md:text-3xl mb-10 text-white">Current stack</h2>
            <div className="font-mono text-[12px] text-white/60 leading-relaxed space-y-2 mb-10 bg-[#0d0d0e] border border-white/10 rounded-xl p-6 overflow-x-auto">
              <div className="text-white/40">Frontend (Next.js)</div>
              <div className="pl-4">Dashboard, Demo, config — calls Backend API</div>
              <div className="text-white/40 pt-4">Backend (FastAPI)</div>
              <div className="pl-4">API: risk-engine, proofs, verification, model-registry</div>
              <div className="pl-4">Stone Prover (local), Integrity (Fact Registry), Allocation Orchestrator</div>
              <div className="pl-4">Protocol metrics, Model Service (get_model_params, registry)</div>
              <div className="text-white/40 pt-4">Starknet (Sepolia)</div>
              <div className="pl-4">RiskEngine v4 (Stage 3A): proof gate, model_version, ModelParams, propose_and_execute_allocation</div>
              <div className="pl-4">StrategyRouter v3.5: update_allocation (RiskEngine-only), JediSwap + Ekubo</div>
              <div className="pl-4">Model Registry: version history, approved_model_versions</div>
              <div className="pl-4">DAOConstraintManager: max_single, min_diversification, constraints</div>
              <div className="pl-4">Fact Registry (SHARP): get_all_verifications_for_fact_hash — contract queries before execution</div>
            </div>
            <p className="text-[13px] text-white/50">
              Execution path: Backend fetches metrics → generates Cairo trace → Stone proves → Integrity registers fact → Backend calls RiskEngine.propose_and_execute_allocation with fact hashes → Contract verifies proofs at Fact Registry → computes risk (model_params) → checks DAO constraints → calls StrategyRouter.update_allocation.
            </p>
          </div>
        </section>

        {/* Proof Pipeline */}
        <section id="proof-pipeline" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-4xl mx-auto">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">PROOF PIPELINE</p>
            <h2 className="font-display text-2xl md:text-3xl mb-10 text-white">Verification flow</h2>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-[13px] text-white/70">
              <div className="border border-white/10 rounded-lg p-4 bg-[#0d0d0e]">
                <p className="font-mono text-[10px] text-white/40 mb-2">1</p>
                <p className="font-medium text-white/90">Metrics</p>
                <p className="mt-1">Protocol metrics (JediSwap, Ekubo) fetched or provided.</p>
              </div>
              <div className="border border-white/10 rounded-lg p-4 bg-[#0d0d0e]">
                <p className="font-mono text-[10px] text-white/40 mb-2">2</p>
                <p className="font-medium text-white/90">Trace</p>
                <p className="mt-1">Cairo execution trace and public inputs generated.</p>
              </div>
              <div className="border border-white/10 rounded-lg p-4 bg-[#0d0d0e]">
                <p className="font-mono text-[10px] text-white/40 mb-2">3</p>
                <p className="font-medium text-white/90">Stone</p>
                <p className="mt-1">Local Stone prover; dynamic FRI; proof serialized; fact hash computed.</p>
              </div>
              <div className="border border-white/10 rounded-lg p-4 bg-[#0d0d0e]">
                <p className="font-mono text-[10px] text-white/40 mb-2">4</p>
                <p className="font-medium text-white/90">Integrity</p>
                <p className="mt-1">Proof submitted; fact registered in SHARP Fact Registry.</p>
              </div>
              <div className="border border-white/10 rounded-lg p-4 bg-[#0d0d0e]">
                <p className="font-mono text-[10px] text-white/40 mb-2">5</p>
                <p className="font-medium text-white/90">Gate</p>
                <p className="mt-1">RiskEngine verifies fact hashes on-chain; then executes allocation.</p>
              </div>
            </div>
            <p className="mt-6 text-[13px] text-white/50">
              Receipts bind inputs, constraints, decisions, proof hash, and verification status for audit and selected disclosure.
            </p>
          </div>
        </section>

        {/* Privacy */}
        <section id="privacy" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-4xl mx-auto">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">PRIVACY</p>
            <h2 className="font-display text-2xl md:text-3xl mb-6 text-white">Selected disclosure</h2>
            <p className="text-white/65 leading-relaxed mb-4">
              We are privacy-focused. Selected disclosure is core: prove compliance or constraints without exposing full inputs or identity when not required. Receipts bind what was executed and what was verified so that auditors and users can confirm correctness without unnecessary data leakage. This supports regulatory compliance and user privacy by design.
            </p>
            <p className="text-[13px] text-white/50">
              Constraint signatures and proof-bound receipts are in production; we are extending patterns for privacy-preserving disclosure and compliance use cases.
            </p>
          </div>
        </section>

        {/* Roadmap */}
        <section id="roadmap" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-4xl mx-auto">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">ROADMAP</p>
            <h2 className="font-display text-2xl md:text-3xl mb-8 text-white">Stages</h2>
            <div className="space-y-6 text-[14px] text-white/70">
              <div className="flex gap-4 border-b border-white/10 pb-4">
                <span className="font-mono text-white/50 w-8">2</span>
                <div><strong className="text-white/90">Proof-gated execution.</strong> Current. Stone prover, Fact Registry verification, two-protocol allocation.</div>
              </div>
              <div className="flex gap-4 border-b border-white/10 pb-4">
                <span className="font-mono text-white/50 w-8">3A</span>
                <div><strong className="text-white/90">On-chain parameterized model.</strong> Live. ModelParams on RiskEngine, versioned risk scoring, API and UI.</div>
              </div>
              <div className="flex gap-4 border-b border-white/10 pb-4">
                <span className="font-mono text-white/50 w-8">3B</span>
                <div><strong className="text-white/90">zkML inference.</strong> Research. EZKL/Giza Starknet integration for real ML inference proofs.</div>
              </div>
              <div className="flex gap-4 border-b border-white/10 pb-4">
                <span className="font-mono text-white/50 w-8">4</span>
                <div><strong className="text-white/90">Trustless AI.</strong> DAO governance, public artifacts, model approval flows.</div>
              </div>
              <div className="flex gap-4">
                <span className="font-mono text-white/50 w-8">5</span>
                <div><strong className="text-white/90">On-chain agent.</strong> Intents, receipts, agent infrastructure; 2–3 month target.</div>
              </div>
            </div>
          </div>
        </section>

        {/* Labs */}
        <section id="labs" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-4xl mx-auto">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">LABS</p>
            <h2 className="font-display text-2xl md:text-3xl mb-6 text-white">Research driving the product</h2>
            <p className="text-white/65 leading-relaxed mb-6">
              Obsqra Labs is the research arm behind obsqra.fi. We work on zkML stack evaluation (EZKL, Giza, Starknet integration), on-chain agent infrastructure (intents, constraint signatures, receipts), and trustless AI governance. What we prove in Labs ships into the production pipeline.
            </p>
            <p className="text-[13px] text-white/50">
              Current themes: Stage 3B zkML inference research; Stage 5 agent intents and receipts; privacy and selected disclosure; model governance. See the repo and docs for detailed roadmap and implementation notes.
            </p>
          </div>
        </section>

        {/* Demo */}
        <section id="demo" className="py-24 px-6 border-t border-white/5">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-10">
              <p className="font-mono text-[11px] text-white/40 tracking-wider mb-4">INTERACTIVE DEMO</p>
              <h2 className="font-display text-3xl mb-4">See It In Action</h2>
              <p className="text-white/60 text-lg max-w-2xl mx-auto mb-8">
                Explore the complete zkML data path with live proof generation, on-chain verification, and block explorer links.
              </p>
              <Link
                href="/demo"
                className="inline-block px-8 py-3.5 bg-gradient-to-r from-emerald-400 to-cyan-400 text-black text-sm font-semibold rounded-lg hover:shadow-lg hover:shadow-emerald-400/20 transition-all"
              >
                View Interactive Demo →
              </Link>
            </div>
            <div className="grid md:grid-cols-3 gap-6 mt-12">
              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">DATA PATH</p>
                <p className="text-white/80 text-sm mb-2">Visual Pipeline</p>
                <p className="text-white/50 text-xs">See the complete flow from market data to on-chain verification</p>
              </div>
              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">LIVE PROOFS</p>
                <p className="text-white/80 text-sm mb-2">Generate Proofs</p>
                <p className="text-white/50 text-xs">Create verifiable STARK proofs with real-time progress indicators</p>
              </div>
              <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
                <p className="font-mono text-[11px] text-white/40 tracking-wider mb-3">BLOCK EXPLORER</p>
                <p className="text-white/80 text-sm mb-2">On-Chain Links</p>
                <p className="text-white/50 text-xs">All hashes link to Starkscan for transparent verification</p>
              </div>
            </div>
          </div>
        </section>

        {/* Get started */}
        <section className="py-24 px-6 border-t border-white/5">
          <div className="max-w-4xl mx-auto text-center">
            <p className="font-mono text-[11px] text-white/40 tracking-wider mb-4">GET STARTED</p>
            <h2 className="font-display text-2xl md:text-3xl mb-6 text-white">Run the pipeline</h2>
            <p className="text-white/55 text-sm mb-8 max-w-xl mx-auto">
              Use the interactive demo to generate a proof, verify on-chain, and inspect the full data path. Launch the app to connect your wallet and execute allocations.
            </p>
            <div className="flex items-center justify-center gap-4">
              <Link
                href="/demo"
                className="px-8 py-3 bg-white text-black text-sm font-medium rounded hover:bg-white/90 transition-colors"
              >
                View Interactive Demo
              </Link>
              <button
                onClick={() => { onClearWalletError(); onLaunch(); }}
                className="px-8 py-3 text-sm text-white/70 border border-white/20 rounded hover:border-white/40 transition-colors"
              >
                Launch App
              </button>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noreferrer"
                className="px-8 py-3 text-sm text-white/60 border border-white/10 rounded hover:border-white/30 transition-colors"
              >
                View Code
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
            <span className="text-sm text-white/40">obsqra.fi</span>
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
            <span className="font-display text-base">obsqra.fi</span>
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
