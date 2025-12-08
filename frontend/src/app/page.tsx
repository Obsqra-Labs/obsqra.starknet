'use client';

import { Dashboard } from '@/components/Dashboard';
import { DemoModeToggle } from '@/components/DemoModeToggle';
import { DemoModeProvider } from '@/contexts/DemoModeContext';
import { useAccount, useConnect, useDisconnect } from '@starknet-react/core';
import { useEffect, useMemo, useState } from 'react';

const DOCS_URL = 'https://github.com/obsqra-labs/obsqra.starknet/tree/main/docs';

export default function Home() {
  const { address, status } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();
  const [mounted, setMounted] = useState(false);
  type ConnectorType = ReturnType<typeof useConnect>['connectors'][number];
  const defaultConnector = useMemo<ConnectorType | undefined>(() => {
    return connectors.find((connector) => connector.available()) ?? connectors[0];
  }, [connectors]);
  const isConnected = status === 'connected';
  const connecting = status === 'connecting' || status === 'reconnecting';

  const handleLaunch = () => {
    if (defaultConnector) {
      connect({ connector: defaultConnector });
    }
  };

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

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

  if (connecting) {
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
          defaultConnector={defaultConnector}
          onConnect={connect}
          onLaunch={handleLaunch}
        />
      )}
    </DemoModeProvider>
  );
}

type Accent = 'mint' | 'lagoon' | 'ink';

function Landing({
  connectors,
  defaultConnector,
  onConnect,
  onLaunch,
}: {
  connectors: ReturnType<typeof useConnect>['connectors'];
  defaultConnector?: ReturnType<typeof useConnect>['connectors'][number];
  onConnect: ReturnType<typeof useConnect>['connect'];
  onLaunch: () => void;
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
              <p className="font-display text-xl text-ink leading-none">Starknet | Phase 3.0</p>
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
              <span className="px-3 py-1 rounded-full bg-lagoon-100 text-ink">Cairo + SHARP Proofs</span>
              <span className="px-3 py-1 rounded-full bg-mint-100 text-ink">MIST Privacy</span>
              <span className="px-3 py-1 rounded-full bg-white border border-ink/10">Verifiable zkML</span>
            </div>
            <h1 className="font-display text-4xl md:text-5xl leading-tight mt-4">
              Verifiable AI<br />
              <span className="text-lagoon-600">Infrastructure for DeFi</span>
            </h1>
            <p className="text-lg text-slate-700 mt-3">
              Prove your AI's logic, intent, and outcomes. On-chain.
            </p>
            <p className="text-base text-slate-600 mt-2">
              On EVM, we built privacy pools. Half the protocol was just privacy infrastructure. It worked, but AI remained a black box. Starknet changes everything: Cairo proves AI logic. SHARP attests outputs. MIST provides privacy natively. We're not building privacy from scratch—we're building the verifiable AI SDK that wraps computation around your logic to prove what matters.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={onLaunch}
                className="px-6 py-3 rounded-full bg-gradient-to-r from-mint-500 to-lagoon-500 text-ink font-semibold shadow-lift hover:translate-y-[-1px] transition transform"
              >
                {defaultConnector ? `Launch - ${defaultConnector.name}` : 'Launch'}
              </button>
              <a
                href="/strategic-vision"
                className="px-6 py-3 rounded-full bg-ink text-white font-semibold hover:opacity-90 transition"
              >
                Read Strategic Vision
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
            <div className="mt-6 grid sm:grid-cols-2 gap-4 text-sm text-slate-600">
              <div className="p-4 rounded-2xl border border-white/70 bg-cloud">
                <p className="font-semibold text-ink">What this is</p>
                <p className="mt-1">
                  An SDK for wrapping verifiable computation around AI logic. Prove your strategy's risk scoring is correct. Prove your allocations are what you claimed. No more black boxes—just Cairo proofs, SHARP attestation, and MIST-native privacy.
                </p>
              </div>
              <div className="p-4 rounded-2xl border border-white/70 bg-cloud">
                <p className="font-semibold text-ink">Why Starknet</p>
                <p className="mt-1">
                  EVM forced us to choose: privacy OR provability. Pick one. Starknet says both—natively. We integrated MIST not because it was easy, but because it's the smartest move: native privacy infrastructure. Now we layer Cairo proofs on top. That's the stack.
                </p>
              </div>
              <div className="p-4 rounded-2xl border border-white/70 bg-cloud">
                <p className="font-semibold text-ink">ZK-RAG (risk model)</p>
                <p className="mt-1">
                  Knowledge graph + ontology feed the risk engine. Graph features and policy constraints are hashed, then proven in Cairo/SHARP so every allocation is grounded in the same data slice and rules.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-b from-white/90 via-cloud to-white/70 border border-white/70 rounded-3xl p-6 shadow-lift backdrop-blur">
            <div className="flex items-center gap-3">
              <span className="px-3 py-1 rounded-full bg-mint-100 text-ink text-xs font-semibold">Strategic Experiment</span>
              <span className="px-3 py-1 rounded-full bg-lagoon-100 text-ink text-xs font-semibold">Starknet Native</span>
            </div>
            <p className="font-display text-2xl text-ink mt-3">The zkML advantage</p>
            <ul className="mt-4 space-y-3 text-sm text-slate-700">
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-mint-500" />
                <div>
                  <p className="font-semibold text-ink">Verifiable AI (Cairo + SHARP)</p>
                  <p>Risk models run in Cairo. SHARP proves the output. No black boxes.</p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-lagoon-500" />
                <div>
                  <p className="font-semibold text-ink">Native privacy (MIST)</p>
                  <p>We didn't rebuild privacy pools. MIST does it better, natively. We integrated their SDK.</p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-ink" />
                <div>
                  <p className="font-semibold text-ink">SDK toolkit for DeFi rails</p>
                  <p>Composable infrastructure: routers, constraints, agents. Build on top of us.</p>
                </div>
              </li>
            </ul>
            {connectors.length > 0 && (
              <div className="mt-6">
                <p className="text-xs uppercase tracking-[0.14em] text-slate-500 mb-2">
                  Connect with
                </p>
                <div className="flex flex-wrap gap-2">
                  {connectors.map((connector) => (
                    <button
                      key={connector.id}
                      onClick={() => onConnect({ connector })}
                      disabled={!connector.available()}
                      className={`px-4 py-2 rounded-full text-sm font-semibold border transition ${
                        connector.available()
                          ? 'bg-white text-ink border-ink/10 hover:border-ink/20'
                          : 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed'
                      }`}
                    >
                      {connector.available()
                        ? `Connect ${connector.name}`
                        : `${connector.name} not installed`}
                    </button>
                  ))}
                </div>
              </div>
            )}
            <div className="mt-6 p-4 rounded-2xl border border-white/70 bg-white/60 text-sm text-slate-700">
              <p className="font-semibold text-ink">Where we are</p>
              <p className="mt-1">EVM Obsqra launches with privacy pools (proven concept). Starknet Obsqra proves verifiable AI can work NOW--Cairo+SHARP enable what EVM fundamentally cannot. MIST integration done. Full zkML coming Q1 2026.</p>
            </div>
          </div>
        </section>

        <section className="mt-10 grid gap-4 md:grid-cols-3">
          <InfoCard
            title="Prove AI Logic"
            body="Your risk model runs in Cairo. Every decision gets a proof. SHARP attests it. DAOs and auditors see the math, not the mystery. Verifiable AI isn't a feature—it's the whole point."
            badge="Cairo"
            accent="lagoon"
          />
          <InfoCard
            title="Privacy as Foundation"
            body="We didn't rebuild privacy pools. MIST already solved that elegantly. Smart move: we integrated it in days instead of spending months. Now privacy is infrastructure, and we layer proofs on top."
            badge="MIST"
            accent="mint"
          />
          <InfoCard
            title="SDK for Builders"
            body="Wrap verifiable computation around your logic. Prove intent. Prove outcomes. Plug into Starknet's DeFi rails. Nostra, zkLend, Ekubo—ready to go. Make your AI trustworthy."
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
            <IntegrationCard title="Nostra" status="Sepolia: pending" role="Lending" accent="ink" />
            <IntegrationCard title="zkLend" status="Sepolia: pending" role="Lending" accent="lagoon" />
            <IntegrationCard title="Ekubo" status="Sepolia: live" role="DEX / LP" accent="mint" />
            <IntegrationCard title="MIST.cash" status="Privacy rails" role="Shielded pools" accent="ink" />
          </div>
        </section>

        <section className="mt-10 grid gap-6 md:grid-cols-[1.4fr_1fr]">
          <div className="bg-gradient-to-r from-mint-500/90 to-lagoon-500/90 text-ink rounded-3xl p-6 shadow-lift">
            <p className="text-xs uppercase tracking-[0.14em] text-ink/80">Ecosystem</p>
            <h3 className="font-display text-2xl mt-1">The verifiable AI layer Starknet was built for</h3>
            <p className="text-sm mt-2 max-w-2xl">
              EVM has privacy pools. Cosmos has cross-chain. Starknet has provable computation. We're building the SDK that ties it all together: verifiable AI infrastructure. Fork the repo. Build your strategy. Prove it works.
            </p>
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
            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Why this matters</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-700">
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-mint-500" />
                <span>EVM proved privacy pools work. Starknet proves verifiable AI works.</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-lagoon-500" />
                <span>Build on existing tools (MIST), not from scratch.</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-ink" />
                <span>SDK toolkit for the Starknet ecosystem.</span>
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
