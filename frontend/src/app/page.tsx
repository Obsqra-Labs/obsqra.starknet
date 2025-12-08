'use client';

import { Dashboard } from '@/components/Dashboard';
import { DemoModeToggle } from '@/components/DemoModeToggle';
import { DemoModeProvider } from '@/contexts/DemoModeContext';
import { useEffect, useState } from 'react';
import { useWalletKit, WalletModal } from 'obsqra.kit';

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
  } = useWalletKit();
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
    <DemoModeProvider>
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
      <WalletModal
        open={showWalletModal}
        onClose={() => {
          clearWalletError();
          setShowWalletModal(false);
        }}
      />
    </DemoModeProvider>
  );
}

type Accent = 'mint' | 'lagoon' | 'ink';
type WalletConnector = ReturnType<typeof useWalletKit>['connectors'][number];

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
              <p className="font-display text-xl text-ink leading-none">Starknet Lab Build</p>
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
        <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] items-start">
          <div className="bg-white/80 border border-white/70 rounded-3xl p-8 shadow-lift backdrop-blur">
            <div className="flex flex-wrap gap-3 items-center text-xs font-medium text-ink/80">
              <span className="px-3 py-1 rounded-full bg-lagoon-100 text-ink">zkML + SHARP</span>
              <span className="px-3 py-1 rounded-full bg-mint-100 text-ink">MIST-native privacy</span>
              <span className="px-3 py-1 rounded-full bg-white border border-ink/10">Starknet Lab</span>
            </div>
            <h1 className="font-display text-4xl md:text-5xl leading-tight mt-4">
              Proof-first AI allocations
              <br />
              <span className="text-lagoon-600">Built to showcase Starknet</span>
            </h1>
            <p className="text-lg text-slate-700 mt-3">
              Obsqra turns your allocation engine into Cairo constraints so Starknet users, DAOs, and regulators can verify the math—live on-chain.
            </p>
            <p className="text-base text-slate-600 mt-2">
              Starknet lets us do what EVM could not: Cairo constraints + SHARP verification for provable computation, and MIST for privacy without rebuilding pools. The result is a public-facing, verifiable AI layer that makes allocations auditable instead of opaque.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={() => {
                  onClearWalletError();
                  onLaunch();
                }}
                className="px-6 py-3 rounded-full bg-gradient-to-r from-mint-500 to-lagoon-500 text-ink font-semibold shadow-lift hover:translate-y-[-1px] transition transform"
              >
                {preferredConnector ? `Launch with ${preferredConnector.name}` : 'Launch on Starknet'}
              </button>
              <a
                href="#value"
                className="px-6 py-3 rounded-full bg-ink text-white font-semibold hover:opacity-90 transition"
              >
                Why Starknet
              </a>
              <a
                href="https://github.com/obsqra-labs/obsqra.starknet"
                target="_blank"
                rel="noreferrer"
                className="px-6 py-3 rounded-full bg-white text-ink border border-ink/10 font-semibold hover:border-ink/20 transition"
              >
                View repo
              </a>
            </div>
            <div className="mt-6 grid sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm text-slate-600">
              <div className="p-4 rounded-2xl border border-white/70 bg-cloud">
                <p className="font-semibold text-ink">Show the proof</p>
                <p className="mt-1">
                  Every allocation carries Cairo constraints and a SHARP proof hash. Wallets see the proof trail, not just an APY claim.
                </p>
              </div>
              <div className="p-4 rounded-2xl border border-white/70 bg-cloud">
                <p className="font-semibold text-ink">Governance ready</p>
                <p className="mt-1">
                  Deterministic, policy-aware constraints make it trivial for DAOs, risk, and compliance teams to replay and audit decisions.
                </p>
              </div>
              <div className="p-4 rounded-2xl border border-white/70 bg-cloud">
                <p className="font-semibold text-ink">Starknet-first</p>
                <p className="mt-1">
                  MIST handles privacy rails. Cairo + SHARP prove computation. Obsqra stitches them into a Starknet-native SDK and router.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-b from-white/90 via-cloud to-white/70 border border-white/70 rounded-3xl p-6 shadow-lift backdrop-blur">
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 rounded-full bg-mint-100 text-ink text-xs font-semibold">Starknet native</span>
              <span className="px-3 py-1 rounded-full bg-lagoon-100 text-ink text-xs font-semibold">Proof-led</span>
            </div>
            <p className="font-display text-2xl text-ink mt-3">Why this matters now</p>
            {wrongNetwork && (
              <div className="mt-3 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm">
                You&apos;re on {chainName || 'another network'}. Please switch to {expectedChainName || 'the expected Starknet network'} to continue.
              </div>
            )}
            <ul className="mt-4 space-y-3 text-sm text-slate-700">
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-mint-500" />
                <div>
                  <p className="font-semibold text-ink">Cairo + SHARP for allocations</p>
                  <p>Risk and allocation logic run in Cairo with SHARP proofs. Users can verify the computation path, not just the UI.</p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-lagoon-500" />
                <div>
                  <p className="font-semibold text-ink">Privacy is handled</p>
                  <p>MIST gives us shielded rails out-of-the-box. That lets Obsqra focus on provability instead of rebuilding privacy pools.</p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-ink" />
                <div>
                  <p className="font-semibold text-ink">Purpose-built for Starknet</p>
                  <p>Settlement contracts, router, frontend, and proof UI are aligned to Starknet users and tooling.</p>
                </div>
              </li>
            </ul>
            {connectors.length > 0 && (
              <div className="mt-6 rounded-2xl border border-white/70 bg-white/70 p-4">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div>
                    <p className="font-semibold text-ink">Wallets</p>
                    <p className="text-xs text-slate-600">Argent X and Braavos via @starknet-react/core</p>
                  </div>
                  <button
                    onClick={onLaunch}
                    className="px-4 py-2 rounded-full bg-mint-500 text-ink text-sm font-semibold border border-mint-300 shadow-sm hover:brightness-95 transition"
              >
                {preferredConnector ? `Quick connect (${preferredConnector.name})` : 'Quick connect'}
              </button>
            </div>
            <div className="mt-3 grid sm:grid-cols-2 gap-2">
              {connectors.map((connector) => (
                <button
                  key={connector.id}
                  onClick={() => {
                    onClearWalletError();
                    onConnect(connector);
                  }}
                  disabled={!connector.available() || isConnecting}
                  className={`px-4 py-2 rounded-full text-sm font-semibold border transition ${
                    connector.available()
                      ? 'bg-white text-ink border-ink/10 hover:border-ink/20'
                          : 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed'
                      }`}
                    >
                      {connector.available()
                        ? `Use ${connector.name}`
                        : `${connector.name} not installed`}
                    </button>
                  ))}
                </div>
                {walletError && (
                  <div className="mt-3 p-3 rounded-xl border border-red-200 bg-red-50 text-sm text-red-700">
                    {walletError}
                  </div>
                )}
                <p className="text-[11px] text-slate-500 mt-3">
                  We&apos;ll consolidate this into a single wallet modal (Rainbow-style) next so users pick once and stay in flow.
                </p>
              </div>
            )}
            <div className="mt-6 p-4 rounded-2xl border border-white/70 bg-white/60 text-sm text-slate-700">
              <p className="font-semibold text-ink">Shipping status</p>
              <p className="mt-1">
                Settlement layer is live on Sepolia. Proof display UI is wired. zkML constraint set and SHARP verification are in build to ship a public, verifiable allocation demo.
              </p>
            </div>
          </div>
        </section>

        <section id="value" className="mt-10 grid gap-4 md:grid-cols-3">
          <InfoCard
            title="For Starknet protocols"
            body="Ship allocations with Cairo proofs and a proof hash users can inspect. Router + SDK slots into Nostra, zkLend, and Ekubo so strategies are verifiable out of the box."
            badge="Cairo"
            accent="lagoon"
          />
          <InfoCard
            title="For risk & compliance"
            body="Deterministic constraints, policy guardrails, and reproducible metrics keep regulators and risk teams in the loop. Proofs show intent and outcome without exposing user data."
            badge="MIST"
            accent="mint"
          />
          <InfoCard
            title="For users & LPs"
            body="Wallets display the proof trail alongside allocation and APY. Privacy is handled by MIST, provability by Cairo/SHARP, so they can finally trust how capital is routed."
            badge="SDK"
            accent="ink"
          />
        </section>

        <section className="mt-10 bg-white/80 border border-white/70 rounded-3xl p-6 shadow-lift backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Integrations</p>
              <h2 className="font-display text-2xl text-ink mt-1">Starknet-native protocols</h2>
              <p className="text-sm text-slate-600">Plug-and-play slots for Nostra, zkLend, Ekubo, plus MIST for privacy rails.</p>
            </div>
            <a
              href={DOCS_URL}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 rounded-full bg-ink text-white text-sm font-semibold hover:opacity-90 transition"
            >
              Read the docs
            </a>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
            <IntegrationCard title="Nostra" status="Router slot wired; proof gating next" role="Lending" accent="ink" />
            <IntegrationCard title="zkLend" status="Hooked for allocation feed" role="Lending" accent="lagoon" />
            <IntegrationCard title="Ekubo" status="Sepolia routing live" role="DEX / LP" accent="mint" />
            <IntegrationCard title="MIST.cash" status="Shielded rails integrated" role="Privacy pools" accent="ink" />
          </div>
        </section>

        <section className="mt-10 grid gap-6 md:grid-cols-[1.4fr_1fr]">
          <div className="bg-gradient-to-r from-mint-500/90 to-lagoon-500/90 text-ink rounded-3xl p-6 shadow-lift">
            <p className="text-xs uppercase tracking-[0.14em] text-ink/80">How it works</p>
            <h3 className="font-display text-2xl mt-1">From metrics to SHARP proof</h3>
            <ul className="mt-3 space-y-2 text-sm max-w-3xl">
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-ink" />
                <span>Ingest Nostra / zkLend / Ekubo metrics and APYs, run the risk engine, and normalize allocations.</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-ink" />
                <span>Wrap those steps in Cairo constraints; SHARP attests the computation; MIST provides privacy for movements.</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-ink" />
                <span>Frontend shows proof hash + allocation; strategy router accepts updates only with valid proofs.</span>
              </li>
            </ul>
            <div className="mt-4 flex flex-wrap gap-3">
              <a
                className="px-4 py-2 rounded-full bg-white text-ink font-semibold border border-ink/10 hover:-translate-y-[1px] transition transform"
                href="https://github.com/obsqra-labs/obsqra.starknet"
                target="_blank"
                rel="noreferrer"
              >
                GitHub
              </a>
              <a
                className="px-4 py-2 rounded-full bg-ink text-white font-semibold hover:opacity-90 transition"
                href="/strategic-vision"
              >
                Strategic Vision
              </a>
            </div>
          </div>
          <div className="bg-white/80 border border-white/70 rounded-3xl p-6 shadow-lift backdrop-blur">
            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Starknet advantage</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-700">
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-mint-500" />
                <span>Proof-of-computation is native: Cairo constraints and SHARP verification are first-class.</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-lagoon-500" />
                <span>Privacy rails are native: MIST lets users opt into shielded flows without protocol overhead.</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-ink" />
                <span>We package both into an SDK + router so builders can ship verifiable AI without rewriting stacks.</span>
              </li>
            </ul>
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
            Wrap Cairo proofs around AI logic. Built on Starknet. MIST + Cairo + SHARP.
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
            <DemoModeToggle />
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
          <Dashboard />
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
