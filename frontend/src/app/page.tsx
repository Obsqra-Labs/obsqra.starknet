'use client';

import { Dashboard } from '@/components/Dashboard';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { useEffect, useState } from 'react';
import { useWallet } from '@/hooks/useWallet';

const DOCS_URL = 'https://github.com/obsqra-labs/obsqra.starknet/tree/main/docs';

export default function Home() {
  const {
    address,
    isConnected,
    isConnecting,
    connectors,
    preferredConnector,
    connect,
    disconnect,
    error: walletError,
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

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Close modal on successful connection
  useEffect(() => {
    if (isConnected) {
      setShowWalletModal(false);
    }
  }, [isConnected]);

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-sand text-ink">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-mint-500 border-t-transparent mx-auto mb-4" />
          <p className="text-sm text-slate-500">Preparing Obsqra for Starknet...</p>
        </div>
      </div>
    );
  }

  if (isConnecting) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-sand text-ink">
        <div className="p-8 rounded-3xl bg-white/80 shadow-lift border border-white/60 backdrop-blur">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-lagoon-300 border-t-transparent mx-auto mb-4" />
          <p className="text-base font-display text-ink">Connecting to your Starknet wallet...</p>
          <p className="text-sm text-slate-500 mt-1">Argent X and Braavos supported.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {isConnected ? (
        <ConnectedApp
          address={address}
          onDisconnect={disconnect}
        />
      ) : (
        <Landing
          connectors={connectors}
          preferredConnector={preferredConnector}
          onConnect={connect}
          onLaunch={handleLaunch}
          onOpenWalletModal={() => {
            clearWalletError();
            setShowWalletModal(true);
          }}
          walletError={walletError}
          onClearWalletError={clearWalletError}
          isConnecting={isConnecting}
          wrongNetwork={wrongNetwork}
          chainName={chainName}
          expectedChainName={expectedChainName}
        />
      )}
      {showWalletModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 shadow-lg max-w-sm">
            <h2 className="text-lg font-semibold mb-4 text-ink">Connect Wallet</h2>
            <div className="space-y-2">
              {connectors.map((connector) => (
                <button
                  key={connector.id}
                  onClick={async () => {
                    await connect(connector);
                    setShowWalletModal(false);
                  }}
                  className="w-full px-4 py-2 bg-mint-500 text-white rounded hover:bg-mint-600 transition"
                >
                  {connector.name || connector.id}
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowWalletModal(false)}
              className="w-full mt-4 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </>
  );
}

type Accent = 'mint' | 'lagoon' | 'ink';
type WalletConnector = ReturnType<typeof useWallet>['connectors'][number];

function Landing({
  connectors,
  preferredConnector,
  onConnect,
  onLaunch,
  onOpenWalletModal,
  walletError,
  onClearWalletError,
  isConnecting,
  wrongNetwork,
  chainName,
  expectedChainName,
}: {
  connectors: WalletConnector[];
  preferredConnector?: WalletConnector;
  onConnect: (connector?: WalletConnector) => Promise<void>;
  onLaunch: () => void;
  onOpenWalletModal: () => void;
  walletError?: string | null;
  onClearWalletError: () => void;
  isConnecting: boolean;
  wrongNetwork?: boolean;
  chainName?: string;
  expectedChainName?: string;
}) {
  return (
    <div className="min-h-screen bg-sand text-ink relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none opacity-70 bg-soft-radial" />
      <div className="absolute top-[-10%] left-[50%] -translate-x-1/2 w-[1200px] h-[1200px] rounded-full bg-gradient-to-br from-white via-cloud to-transparent blur-3xl opacity-70" />
      <header className="relative z-10 border-b border-white/60 bg-white/70 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-mint-500 to-lagoon-500 shadow-md" />
            <div>
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Obsqra</p>
              <p className="font-display text-xl text-ink leading-none">Risk-Managed Vaults</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a
              className="px-4 py-2 rounded-full border border-ink/10 text-sm text-ink hover:bg-white transition"
              href="/strategic-vision"
            >
              Strategic Vision
            </a>
            <a
              className="px-4 py-2 rounded-full border border-ink/10 text-sm text-ink hover:bg-white transition"
              href={DOCS_URL}
              target="_blank"
              rel="noreferrer"
            >
              Docs
            </a>
            <button
              onClick={onLaunch}
              className="px-4 py-2 rounded-full bg-mint-500 text-ink font-medium hover:brightness-95 transition border border-mint-300 shadow-sm"
            >
              Connect wallet
            </button>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-6xl mx-auto px-6 pb-16 pt-10">
        {/* Hero Section - More Compelling */}
        <section className="relative overflow-hidden bg-gradient-to-br from-white via-cloud to-white/90 border border-white/70 rounded-3xl p-8 md:p-12 shadow-lift backdrop-blur mb-16">
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-lagoon-200/30 to-mint-200/30 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
          <div className="relative z-10">
            <div className="flex flex-wrap gap-3 items-center text-xs font-medium text-ink/80 mb-6">
              <span className="px-3 py-1.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200 font-semibold">Prototype</span>
              <span className="px-3 py-1.5 rounded-full bg-lagoon-100 text-ink font-semibold">Starknet Native</span>
              <span className="px-3 py-1.5 rounded-full bg-mint-100 text-ink font-semibold">Verifiable AI</span>
            </div>
            <h1 className="font-display text-5xl md:text-6xl lg:text-7xl leading-tight text-ink mb-6">
              Trust through
              <br />
              <span className="text-lagoon-600">Verifiable Computation</span>
            </h1>
            <p className="text-xl md:text-2xl text-slate-700 mb-2 max-w-3xl leading-relaxed">
              Obsqra brings transparency to DeFi risk management. Every allocation decision is provable, every risk score is auditable, every strategy is verifiable—not just claimed.
            </p>
            <p className="text-base text-slate-600 mb-8 max-w-3xl">
              Built on Starknet&apos;s Cairo + SHARP infrastructure, Obsqra turns AI-driven allocation logic into cryptographic proofs. DAOs, compliance teams, and users can verify that capital stayed within policy bounds, without trusting black-box algorithms.
            </p>
            <div className="flex flex-wrap gap-4 mb-6">
              <button
                onClick={() => {
                  onClearWalletError();
                  onLaunch();
                }}
                className="px-8 py-4 rounded-full bg-gradient-to-r from-mint-500 to-lagoon-500 text-ink font-semibold text-lg shadow-lift hover:translate-y-[-2px] transition transform"
              >
                {preferredConnector ? `Launch on Starknet (${preferredConnector.name})` : 'Launch on Starknet'}
              </button>
              <a
                href={DOCS_URL}
                target="_blank"
                rel="noreferrer"
                className="px-8 py-4 rounded-full bg-ink text-white font-semibold text-lg hover:opacity-90 transition"
              >
                Read Whitepaper
              </a>
              <a
                href="https://github.com/obsqra-labs/obsqra.starknet"
                target="_blank"
                rel="noreferrer"
                className="px-8 py-4 rounded-full bg-white text-ink border-2 border-ink/20 font-semibold text-lg hover:border-ink/40 transition"
              >
                View on GitHub
              </a>
            </div>
            {wrongNetwork && (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800">
                You&apos;re on {chainName || 'another network'}. Please switch to {expectedChainName || 'Starknet Sepolia'} to continue.
              </div>
            )}
          </div>
        </section>

        {/* The Problem & Solution - Holistic Story */}
        <section className="mb-16 grid lg:grid-cols-2 gap-8">
          <div className="bg-gradient-to-br from-slate-50 to-white border border-slate-200 rounded-3xl p-8 shadow-lift">
            <div className="text-5xl mb-4">🔍</div>
            <h2 className="font-display text-3xl text-ink mb-4">The Problem</h2>
            <p className="text-lg text-slate-700 mb-4">
              DeFi yield strategies are black boxes. You see an APY claim, but you can&apos;t verify:
            </p>
            <ul className="space-y-3 text-slate-600">
              <li className="flex items-start gap-3">
                <span className="mt-1 text-red-500">✗</span>
                <span>Whether risk limits were actually respected</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 text-red-500">✗</span>
                <span>If the allocation logic followed stated policies</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 text-red-500">✗</span>
                <span>How decisions were made—it&apos;s all off-chain and opaque</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 text-red-500">✗</span>
                <span>If compliance requirements were met without manual audits</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-gradient-to-br from-lagoon-50 to-mint-50 border border-lagoon-200 rounded-3xl p-8 shadow-lift">
            <div className="text-5xl mb-4">✓</div>
            <h2 className="font-display text-3xl text-ink mb-4">The Obsqra Solution</h2>
            <p className="text-lg text-slate-700 mb-4">
              Every decision is provable on-chain:
            </p>
            <ul className="space-y-3 text-slate-700">
              <li className="flex items-start gap-3">
                <span className="mt-1 text-green-600">✓</span>
                <span><strong>Proof of computation:</strong> Cairo constraints + SHARP proofs verify the math</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 text-green-600">✓</span>
                <span><strong>Transparent risk scoring:</strong> On-chain metrics, visible weightings, auditable decisions</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 text-green-600">✓</span>
                <span><strong>Policy enforcement:</strong> Smart contracts enforce limits—can&apos;t be bypassed</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 text-green-600">✓</span>
                <span><strong>Compliance-ready:</strong> Regulators and DAOs can verify without trusting us</span>
              </li>
            </ul>
          </div>
        </section>

        {/* How It Works - Integrated Flow */}
        <section id="how-it-works" className="mb-16">
          <div className="text-center mb-12">
            <h2 className="font-display text-4xl text-ink mb-4">From Data to Proof to Action</h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              A seamless flow that turns protocol metrics into verifiable allocations, all on Starknet
            </p>
          </div>
          <div className="bg-gradient-to-r from-mint-500/90 via-lagoon-500/90 to-mint-500/90 text-ink rounded-3xl p-8 md:p-12 shadow-lift relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),transparent)]" />
            <div className="relative z-10">
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 border border-white/30">
                  <div className="text-5xl mb-4">📊</div>
                  <div className="text-xs font-semibold text-ink/70 mb-2 uppercase tracking-wider">Step 1</div>
                  <h3 className="font-display text-xl mb-3">Ingest Metrics</h3>
                  <p className="text-sm text-ink/90 leading-relaxed">
                    Real-time data from Nostra, zkLend, Ekubo. APYs, utilization, liquidity depth—everything the risk engine needs.
                  </p>
                </div>
                <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 border border-white/30">
                  <div className="text-5xl mb-4">🧠</div>
                  <div className="text-xs font-semibold text-ink/70 mb-2 uppercase tracking-wider">Step 2</div>
                  <h3 className="font-display text-xl mb-3">Compute Risk</h3>
                  <p className="text-sm text-ink/90 leading-relaxed">
                    Cairo-based risk engine weighs metrics transparently. Risk scores and allocations computed with visible logic.
                  </p>
                </div>
                <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 border border-white/30">
                  <div className="text-5xl mb-4">🔐</div>
                  <div className="text-xs font-semibold text-ink/70 mb-2 uppercase tracking-wider">Step 3</div>
                  <h3 className="font-display text-xl mb-3">Generate Proof</h3>
                  <p className="text-sm text-ink/90 leading-relaxed">
                    SHARP proves the computation. Proof hash settles on L1. Anyone can verify the decision was correct.
                  </p>
                </div>
                <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 border border-white/30">
                  <div className="text-5xl mb-4">✅</div>
                  <div className="text-xs font-semibold text-ink/70 mb-2 uppercase tracking-wider">Step 4</div>
                  <h3 className="font-display text-xl mb-3">Execute & Track</h3>
                  <p className="text-sm text-ink/90 leading-relaxed">
                    Router deploys capital. Positions tracked on-chain. Every action emits verifiable events. Full transparency.
                  </p>
                </div>
              </div>
              <div className="text-center">
                <a
                  href={DOCS_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-block px-8 py-4 rounded-full bg-white text-ink font-semibold hover:bg-white/90 transition shadow-lg"
                >
                  Explore the Architecture →
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Ecosystem Integration - Holistic View */}
        <section id="integrations" className="mb-16">
          <div className="text-center mb-12">
            <h2 className="font-display text-4xl text-ink mb-4">Built for the Starknet Ecosystem</h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Obsqra integrates seamlessly with Starknet&apos;s leading DeFi protocols. As the ecosystem grows (193+ projects and counting), verifiable risk management becomes essential infrastructure.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8 mb-12">
            <div className="bg-white/80 border border-white/70 rounded-3xl p-8 shadow-lift backdrop-blur">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-full bg-lagoon-100 flex items-center justify-center">
                  <span className="text-2xl">🔗</span>
                </div>
                <div>
                  <h3 className="font-display text-xl text-ink">Live Integrations</h3>
                  <p className="text-sm text-slate-500">Prototype Status</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 rounded-xl bg-cloud">
                  <span className="text-green-600 font-bold">✓</span>
                  <div>
                    <p className="font-semibold text-ink">JediSwap V2</p>
                    <p className="text-sm text-slate-600">NFT position management, fee collection live</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-xl bg-cloud">
                  <span className="text-green-600 font-bold">✓</span>
                  <div>
                    <p className="font-semibold text-ink">Ekubo</p>
                    <p className="text-sm text-slate-600">Concentrated liquidity, lock/callback pattern</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-xl bg-cloud">
                  <span className="text-green-600 font-bold">✓</span>
                  <div>
                    <p className="font-semibold text-ink">Strategy Router v3.5</p>
                    <p className="text-sm text-slate-600">Dual-protocol routing on Sepolia</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white/80 border border-white/70 rounded-3xl p-8 shadow-lift backdrop-blur">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-full bg-mint-100 flex items-center justify-center">
                  <span className="text-2xl">🚧</span>
                </div>
                <div>
                  <h3 className="font-display text-xl text-ink">Coming Soon</h3>
                  <p className="text-sm text-slate-500">Next Integrations</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 rounded-xl bg-cloud">
                  <span className="text-amber-600 font-bold">→</span>
                  <div>
                    <p className="font-semibold text-ink">Nostra</p>
                    <p className="text-sm text-slate-600">Lending with proof-gating</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-xl bg-cloud">
                  <span className="text-amber-600 font-bold">→</span>
                  <div>
                    <p className="font-semibold text-ink">zkLend</p>
                    <p className="text-sm text-slate-600">Allocation feed integration</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 rounded-xl bg-cloud">
                  <span className="text-amber-600 font-bold">→</span>
                  <div>
                    <p className="font-semibold text-ink">More Strategies</p>
                    <p className="text-sm text-slate-600">Delta-neutral, basis trading, RWAs</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-lagoon-50 to-mint-50 border border-lagoon-200 rounded-3xl p-8 shadow-lift">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-full bg-lagoon-200 flex items-center justify-center">
                  <span className="text-2xl">🌱</span>
                </div>
                <div>
                  <h3 className="font-display text-xl text-ink">Ecosystem Growth</h3>
                  <p className="text-sm text-slate-600">Starknet DeFi Momentum</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-3xl font-bold text-ink mb-1">193+</p>
                  <p className="text-sm text-slate-600">DeFi projects on Starknet (Nov 2024)</p>
                </div>
                <div className="pt-4 border-t border-lagoon-200">
                  <p className="text-sm text-slate-700 mb-2">
                    <strong>Hackathon winners</strong> like Splyce (AI-managed ETFs) and Overtrade (OTC) show the demand for AI-driven DeFi. Obsqra provides the verifiable infrastructure they need.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Why Starknet - Holistic Value Prop */}
        <section id="why-now" className="mb-16 bg-gradient-to-br from-white via-cloud to-white rounded-3xl p-8 md:p-12 shadow-lift border border-white/70">
          <div className="text-center mb-12">
            <h2 className="font-display text-4xl text-ink mb-4">Why Starknet Changes Everything</h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Starknet&apos;s native capabilities make verifiable AI not just possible, but practical
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-lagoon-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⚡</span>
              </div>
              <h3 className="font-display text-2xl text-ink mb-3">Native Proof-of-Computation</h3>
              <p className="text-slate-600 leading-relaxed">
                Cairo constraints and SHARP verification are first-class on Starknet. No need to bolt on proof systems—it&apos;s built into the chain. This makes verifiable AI cost-effective and practical.
              </p>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-mint-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🔐</span>
              </div>
              <h3 className="font-display text-2xl text-ink mb-3">Account Abstraction</h3>
              <p className="text-slate-600 leading-relaxed">
                Starknet&apos;s account abstraction means better UX and lower costs. Users sign once, transactions batch efficiently. Perfect for complex multi-protocol strategies.
              </p>
            </div>
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-ink/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🌐</span>
              </div>
              <h3 className="font-display text-2xl text-ink mb-3">Growing Ecosystem</h3>
              <p className="text-slate-600 leading-relaxed">
                With 193+ DeFi projects and accelerating innovation (Layer Akira, Raize Club), Starknet needs verifiable risk infrastructure. Obsqra fills that gap.
              </p>
            </div>
          </div>
        </section>

        {/* Roadmap - Integrated Story */}
        <section id="roadmap" className="mb-16">
          <div className="text-center mb-12">
            <h2 className="font-display text-4xl text-ink mb-4">Where We Are, Where We&apos;re Going</h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              This prototype validates the core architecture. The roadmap extends to a unified audit layer across chains.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-8 mb-8">
            <div className="bg-gradient-to-br from-green-50 to-white border border-green-200 rounded-3xl p-8 shadow-lift">
              <div className="flex items-center gap-3 mb-6">
                <span className="text-4xl">✅</span>
                <h3 className="font-display text-2xl text-ink">Live Now (Prototype)</h3>
              </div>
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-white border border-green-100">
                  <p className="font-semibold text-ink mb-2">Strategy Router v3.5 on Sepolia</p>
                  <p className="text-sm text-slate-600">Dual-protocol integration (JediSwap V2 + Ekubo) with automated yield collection, position tracking, and on-chain events.</p>
                </div>
                <div className="p-4 rounded-xl bg-white border border-green-100">
                  <p className="font-semibold text-ink mb-2">Cairo + SHARP Infrastructure</p>
                  <p className="text-sm text-slate-600">Proof generation and verification system ready. Risk calculations can be proven on-chain.</p>
                </div>
                <div className="p-4 rounded-xl bg-white border border-green-100">
                  <p className="font-semibold text-ink mb-2">Proof Display UI</p>
                  <p className="text-sm text-slate-600">Users can see proof hashes, decision IDs, and verifiable event trails in the dashboard.</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-amber-50 to-white border border-amber-200 rounded-3xl p-8 shadow-lift">
              <div className="flex items-center gap-3 mb-6">
                <span className="text-4xl">🚧</span>
                <h3 className="font-display text-2xl text-ink">Coming Next</h3>
              </div>
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-white border border-amber-100">
                  <p className="font-semibold text-ink mb-2">More Protocol Integrations</p>
                  <p className="text-sm text-slate-600">Nostra, zkLend, and additional strategies (delta-neutral, basis trading, RWAs).</p>
                </div>
                <div className="p-4 rounded-xl bg-white border border-amber-100">
                  <p className="font-semibold text-ink mb-2">Enhanced zk Proofs</p>
                  <p className="text-sm text-slate-600">Full zkML constraint sets with comprehensive compliance proofs.</p>
                </div>
                <div className="p-4 rounded-xl bg-white border border-amber-100">
                  <p className="font-semibold text-ink mb-2">Privacy Layer (Optional)</p>
                  <p className="text-sm text-slate-600">Integration with EVM privacy pools for shadow vaults. Provability first, privacy at the edges.</p>
                </div>
                <div className="p-4 rounded-xl bg-white border border-amber-100">
                  <p className="font-semibold text-ink mb-2">Unified Proof Graph</p>
                  <p className="text-sm text-slate-600">Connect Starknet risk engine with EVM privacy pools to form a cross-chain audit layer.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center">
            <a
              href={DOCS_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-block px-8 py-4 rounded-full bg-ink text-white font-semibold text-lg hover:opacity-90 transition shadow-lift"
            >
              View Full Roadmap & Whitepaper →
            </a>
          </div>
        </section>

        {/* Final CTA - Holistic Call to Action */}
        <section id="cta" className="mb-16">
          <div className="relative overflow-hidden bg-gradient-to-br from-mint-500 via-lagoon-500 to-mint-500 text-ink rounded-3xl p-12 md:p-16 shadow-2xl">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.2),transparent)]" />
            <div className="relative z-10 text-center max-w-4xl mx-auto">
              <h2 className="font-display text-4xl md:text-5xl mb-6">Join the Verifiable DeFi Movement</h2>
              <p className="text-xl md:text-2xl text-ink/90 mb-4 leading-relaxed">
                Obsqra is building the infrastructure for trustless, verifiable AI in DeFi. Whether you&apos;re deploying capital, building protocols, or auditing strategies, verifiable computation changes everything.
              </p>
              <p className="text-lg text-ink/80 mb-10">
                This prototype demonstrates what&apos;s possible. The future is transparent, provable, and built on Starknet.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <button
                  onClick={() => {
                    onClearWalletError();
                    onLaunch();
                  }}
                  className="px-10 py-5 rounded-full bg-white text-ink font-bold text-lg shadow-2xl hover:translate-y-[-3px] transition transform hover:shadow-3xl"
                >
                  Launch App →
                </button>
                <a
                  href={DOCS_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="px-10 py-5 rounded-full bg-ink text-white font-bold text-lg hover:opacity-90 transition shadow-xl"
                >
                  Read Whitepaper
                </a>
                <a
                  href="https://github.com/obsqra-labs/obsqra.starknet"
                  target="_blank"
                  rel="noreferrer"
                  className="px-10 py-5 rounded-full bg-white/20 text-ink border-2 border-white/40 font-bold text-lg hover:bg-white/30 transition backdrop-blur"
                >
                  View on GitHub
                </a>
              </div>
              <div className="mt-12 pt-8 border-t border-white/30">
                <p className="text-sm text-ink/70">
                  Built for builders, designed for transparency, powered by Starknet
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-16 border-t border-white/60 pt-8 pb-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-mint-500 to-lagoon-500 shadow-md" />
              <p className="text-sm text-slate-600">Obsqra — The Verifiable AI SDK</p>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <a href="/strategic-vision" className="text-slate-600 hover:text-ink transition">Strategic Vision</a>
              <a href={DOCS_URL} target="_blank" rel="noreferrer" className="text-slate-600 hover:text-ink transition">Documentation</a>
              <a href="https://github.com/obsqra-labs/obsqra.starknet" target="_blank" rel="noreferrer" className="text-slate-600 hover:text-ink transition">GitHub</a>
            </div>
          </div>
          <p className="text-center text-xs text-slate-400 mt-6">
            Verifiable AI Risk Engine for Starknet DeFi. Built with Cairo + SHARP. Prototype demonstrating dual-protocol integration. Part of the growing Starknet DeFi ecosystem.
          </p>
        </footer>
      </main>
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
  const walletTag = address ? `${address.slice(0, 6)}...${address.slice(-4)}` : 'Starknet wallet';

  return (
    <div className="min-h-screen bg-gradient-to-br from-ink via-slate-900 to-ink text-white relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none opacity-40 bg-soft-radial" />
      <div className="absolute top-[-10%] left-[50%] -translate-x-1/2 w-[1200px] h-[1200px] rounded-full bg-gradient-to-br from-indigo-900/40 via-blue-900/20 to-transparent blur-3xl opacity-60" />
      <header className="relative z-10 border-b border-white/10 bg-slate-900/70 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-mint-500 to-lagoon-500 shadow-lg ring-2 ring-white/10" />
            <div>
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Obsqra</p>
              <p className="font-display text-xl leading-none text-white">Starknet</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-4 py-2 rounded-full bg-white/10 text-sm text-white border border-white/15">
              {walletTag}
            </span>
            <a
              className="px-4 py-2 rounded-full border border-white/15 text-sm text-white hover:bg-white/10 transition"
              href="/strategic-vision"
            >
              Vision
            </a>
            <a
              className="px-4 py-2 rounded-full border border-white/15 text-sm text-white hover:bg-white/10 transition"
              href={DOCS_URL}
              target="_blank"
              rel="noreferrer"
            >
              Docs
            </a>
            <button
              onClick={onDisconnect}
              className="px-4 py-2 rounded-full bg-white text-ink text-sm font-medium hover:opacity-90 transition"
            >
              Disconnect
            </button>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-6xl mx-auto px-6 py-10" id="dashboard">
        <div className="mb-4 flex items-center gap-3">
          <span className="px-3 py-1 rounded-full bg-mint-500/20 text-mint-100 text-xs font-semibold border border-mint-400/30">Live</span>
          <h3 className="font-display text-2xl text-white">Your Obsqra dashboard</h3>
        </div>
        <div className="bg-slate-900/80 border border-white/10 rounded-3xl shadow-lift backdrop-blur-lg p-4">
          <ErrorBoundary>
            <Dashboard />
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
}

function InfoCard({
  title,
  body,
  badge,
  accent,
}: {
  title: string;
  body: string;
  badge: string;
  accent: Accent;
}) {
  const accentClasses: Record<Accent, string> = {
    mint: 'from-mint-100 to-white border-mint-100',
    lagoon: 'from-lagoon-100 to-white border-lagoon-100',
    ink: 'from-slate-100 to-white border-slate-200',
  };

  return (
    <div className={`rounded-3xl p-5 shadow-lift bg-gradient-to-br ${accentClasses[accent]} border`}>
      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-white/80 text-ink border border-white/70">
        {badge}
      </span>
      <h3 className="font-display text-xl text-ink mt-3">{title}</h3>
      <p className="text-sm text-slate-700 mt-2">{body}</p>
    </div>
  );
}

function IntegrationCard({
  title,
  status,
  role,
  accent,
}: {
  title: string;
  status: string;
  role: string;
  accent: Accent;
}) {
  const dotColor: Record<Accent, string> = {
    mint: 'bg-mint-500',
    lagoon: 'bg-lagoon-500',
    ink: 'bg-ink',
  };

  return (
    <div className="rounded-2xl border border-white/70 bg-cloud p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${dotColor[accent]}`} />
          <p className="font-display text-lg text-ink">{title}</p>
        </div>
        <span className="text-[11px] uppercase tracking-[0.12em] text-slate-500">{role}</span>
      </div>
      <p className="text-sm text-slate-600 mt-1">{status}</p>
    </div>
  );
}
