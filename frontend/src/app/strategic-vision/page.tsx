'use client';

import Link from 'next/link';

const DOCS_URL = 'https://github.com/obsqra-labs/obsqra.starknet/tree/main/docs';
const GITHUB_URL = 'https://github.com/obsqra-labs/obsqra.starknet';

const SECTION_LINKS = [
  { id: 'executive-summary', label: 'Executive Summary' },
  { id: 'strategic-pivot', label: 'Strategic Pivot' },
  { id: 'architecture', label: 'Architecture' },
  { id: 'examples', label: 'Examples' },
  { id: 'roadmap', label: 'Roadmap' },
  { id: 'comparison', label: 'EVM vs Starknet' },
  { id: 'developer-toolkit', label: 'Developer Toolkit' },
  { id: 'use-cases', label: 'Use Cases' },
];

type PulseColor = 'mint' | 'lagoon' | 'ink';

const STATUS_PULSES: Array<{ title: string; status: string; detail: string; color: PulseColor }> = [
  { title: 'MIST privacy', status: 'Integrated', detail: 'Deposits/withdrawals live via SDK.', color: 'mint' },
  { title: 'Risk engine (Cairo)', status: 'Building now', detail: 'Proofed allocation logic + SHARP wiring.', color: 'lagoon' },
  { title: 'zkML', status: 'Planned', detail: 'Model proving + SDK toolkit — Q1 2026.', color: 'ink' },
];

const ROADMAP = [
  {
    phase: 'Phase 1',
    title: 'MIST + Routing',
    status: 'Complete',
    statusTone: 'success',
    summary: 'Privacy integration and routing baseline.',
    items: [
      'MIST.cash SDK live (deposit/withdraw)',
      'Strategy router deployed on Sepolia',
      'Frontend with wallet + demo mode',
      'Nostra, zkLend, Ekubo routing wired',
    ],
    timeline: 'Done — Dec 2025',
    accent: 'mint',
  },
  {
    phase: 'Phase 2',
    title: 'Risk Engine in Cairo',
    status: 'In progress',
    statusTone: 'warning',
    summary: 'Verifiable risk scoring and constraint enforcement.',
    items: [
      'Volatility/liquidity/correlation in Cairo',
      'SHARP proofs for scoring + allocations',
      'DAO constraint manager enforcement',
      'On-chain proof verification',
    ],
    timeline: '4 weeks — Jan 2026',
    accent: 'lagoon',
  },
  {
    phase: 'Phase 3',
    title: 'Full zkML',
    status: 'Planned',
    statusTone: 'neutral',
    summary: 'Model proving and SDK for strategy builders.',
    items: [
      'Full ML execution in Cairo',
      'Giza/zkML integration for inference',
      'SDK toolkit for third parties',
      'Mainnet deployment',
    ],
    timeline: 'Q1 2026',
    accent: 'ink',
  },
];

const EXAMPLES = [
  {
    badge: 'Example 1',
    accent: 'lagoon',
    title: 'BTCFi yield with private allocation',
    scenario: 'Alice allocates BTC without revealing identity or position size.',
    steps: [
      'Deposit privately via MIST chamber; wallet unlinkable.',
      'Cairo engine computes allocation: 40% Nostra, 60% Ekubo.',
      'SHARP proves the allocation respected DAO constraints.',
      'Private withdrawal preserves unlinkability.',
    ],
    proof: 'Proof covers allocation logic; identity/size/timing stay private.',
  },
  {
    badge: 'Example 2',
    accent: 'mint',
    title: 'Verifiable risk scoring',
    scenario: 'DAO validates the risk engine before treasury deployment.',
    steps: [
      'DAO submits parameters to the Cairo risk model.',
      'Model runs volatility, liquidity, correlation checks.',
      'SHARP generates proof of the computation path.',
      'DAO verifies outputs match approved logic — no oracles.',
    ],
    proof: 'Transparent scoring with cryptographic provenance; audit-ready.',
  },
  {
    badge: 'Example 3',
    accent: 'ink',
    title: 'Cross-protocol rebalancing with proofs',
    scenario: 'Agent rebalances across Nostra, zkLend, Ekubo as yields move.',
    steps: [
      'Agent triggers rebalance from 60/40 Nostra/zkLend.',
      'Cairo logic recalculates: 30% Nostra, 20% zkLend, 50% Ekubo.',
      'SHARP proves the rebalance followed DAO constraints.',
      'Router executes; proofs anchor every transition.',
    ],
    proof: 'Governance-approved guardrails with verifiable enforcement.',
  },
];

const USE_CASES = [
  {
    title: 'BTCFi Yield Optimization',
    copy: 'Private BTC deposits routed across Starknet DeFi. Verifiable allocation logic with unlinkable exits.',
    accent: 'lagoon',
  },
  {
    title: 'DAO Treasury Management',
    copy: 'Constraints enforced in Cairo with SHARP proofs. Treasury operations are auditable by design.',
    accent: 'mint',
  },
  {
    title: 'Autonomous Strategy Agents',
    copy: 'Agents rebalance with cryptographic receipts. Mandates are enforced, not trusted.',
    accent: 'ink',
  },
  {
    title: 'Privacy-Preserving Strategies',
    copy: 'Positions, sizing, and timing stay private. Logic stays provable. Built-in composability.',
    accent: 'slate',
  },
];

const COMPARISON = [
  { feature: 'Verifiable AI', evm: 'Black box; oracle trust required', starknet: 'Cairo + SHARP proofs native' },
  { feature: 'Privacy', evm: 'Custom privacy pools; heavy lift', starknet: 'MIST SDK — native + fast' },
  { feature: 'Proof attestation', evm: 'Not feasible for AI logic', starknet: 'Shared prover (SHARP) on tap' },
  { feature: 'DAO auditability', evm: 'Trust + monitoring only', starknet: 'Proof-backed constraints' },
  { feature: 'zkML capability', evm: 'Retrofit at best; no native support', starknet: 'Cairo-first model proving' },
  { feature: 'Time to value', evm: 'Months', starknet: 'Weeks (privacy done; proofs underway)' },
];

const TOOLKIT = [
  {
    title: 'Contracts (Cairo)',
    items: ['RiskEngine — scoring and allocation', 'StrategyRouter — multi-protocol routes', 'DAOConstraintManager — guardrails'],
    link: `${GITHUB_URL}/tree/main/contracts`,
  },
  {
    title: 'Frontend (React)',
    items: ['useMistCash — private flows', 'useStrategyRouter — allocations', 'Demo mode for testing'],
    link: `${GITHUB_URL}/tree/main/frontend`,
  },
  {
    title: 'SDK direction',
    items: ['Proof helpers + attestations', 'Constraint templates for DAOs', 'Composable strategy kits'],
    link: DOCS_URL,
  },
];

export default function StrategicVisionPage() {
  const toneClasses: Record<PulseColor, { dot: string; badge: string; card: string }> = {
    mint: { dot: 'bg-mint-500', badge: 'bg-mint-500 text-white', card: 'border-mint-100 bg-mint-50' },
    lagoon: { dot: 'bg-lagoon-500', badge: 'bg-lagoon-500 text-white', card: 'border-lagoon-100 bg-lagoon-50' },
    ink: { dot: 'bg-ink', badge: 'bg-ink text-white', card: 'border-slate-900/20 bg-slate-900/80 text-white' },
  };

  return (
    <div className="min-h-screen bg-sand text-ink relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-soft-radial opacity-80" aria-hidden />
      <div
        className="absolute -left-[30%] top-[-10%] h-[520px] w-[520px] rounded-full bg-gradient-to-br from-white/60 via-cloud to-transparent blur-3xl"
        aria-hidden
      />
      <div
        className="absolute right-[-20%] bottom-[10%] h-[420px] w-[420px] rounded-full bg-gradient-to-tr from-mint-200/50 via-white/60 to-transparent blur-3xl"
        aria-hidden
      />

      <header className="sticky top-0 z-50 border-b border-white/60 bg-white/85 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 hover:opacity-85 transition">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-mint-500 to-lagoon-500 shadow-md" />
            <div>
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Obsqra</p>
              <p className="font-display text-xl text-ink leading-tight">Starknet Strategic Vision</p>
            </div>
          </Link>
          <nav className="flex items-center gap-3">
            <a
              href={DOCS_URL}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 rounded-full border border-ink/10 text-sm text-ink hover:bg-white transition"
            >
              Docs
            </a>
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2 rounded-full bg-ink text-white text-sm font-semibold hover:opacity-90 transition"
            >
              GitHub
            </a>
          </nav>
        </div>
      </header>

      <section className="pt-14 pb-8">
        <div className="max-w-6xl mx-auto px-6 grid gap-8 lg:grid-cols-[1.1fr_0.9fr] items-start">
          <div className="rounded-3xl bg-white/90 border border-white/70 shadow-lift backdrop-blur p-8 relative overflow-hidden">
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-br from-white via-transparent to-mint-50 opacity-80" />
            <div className="relative space-y-4">
              <div className="flex flex-wrap gap-2 text-xs font-medium text-ink/80">
                <span className="px-3 py-1 rounded-full bg-lagoon-100 text-ink">Strategic Overview</span>
                <span className="px-3 py-1 rounded-full bg-mint-100 text-ink">Starknet Native</span>
                <span className="px-3 py-1 rounded-full bg-white border border-ink/10">zkML Infrastructure</span>
              </div>
              <h1 className="font-display text-4xl md:text-5xl leading-tight">The Verifiable AI SDK</h1>
              <p className="text-lg text-slate-700 max-w-3xl">
                Starknet lets us prove AI logic, intent, and outcomes. MIST provides native privacy. Cairo + SHARP
                make the computation verifiable. This page is the operating plan.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link
                  href="/"
                  className="px-6 py-3 rounded-full bg-gradient-to-r from-mint-500 to-lagoon-500 text-ink font-semibold shadow-lift hover:translate-y-[-1px] transition transform"
                >
                  Launch App
                </Link>
                <a
                  href={DOCS_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="px-6 py-3 rounded-full bg-white text-ink border border-ink/10 font-semibold hover:border-ink/20 transition"
                >
                  Read Docs
                </a>
                <a
                  href={GITHUB_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="px-6 py-3 rounded-full bg-ink text-white font-semibold hover:opacity-90 transition"
                >
                  View Repo
                </a>
              </div>
              <div className="grid gap-4 md:grid-cols-3 pt-2">
                <div className="rounded-2xl border border-white/70 bg-cloud p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Time to market</p>
                  <p className="font-semibold text-ink mt-1">MIST integrated</p>
                  <p className="text-sm text-slate-600">SDK hooks live. Deposits/withdrawals working now.</p>
                </div>
                <div className="rounded-2xl border border-white/70 bg-cloud p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Risk engine</p>
                  <p className="font-semibold text-ink mt-1">Cairo proof path</p>
                  <p className="text-sm text-slate-600">Volatility, liquidity, correlation logic moving on-chain.</p>
                </div>
                <div className="rounded-2xl border border-white/70 bg-cloud p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Last updated</p>
                  <p className="font-semibold text-ink mt-1">Jan 2026</p>
                  <p className="text-sm text-slate-600">Roadmap + build status refreshed.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4 lg:sticky lg:top-10">
            <div className="rounded-3xl bg-ink text-white p-6 shadow-lift">
              <p className="text-xs uppercase tracking-[0.16em] text-white/60">Strategic signal</p>
              <p className="font-display text-2xl mt-2">Prove AI. Keep it private.</p>
              <p className="text-sm text-white/75 mt-3">
                EVM forced a trade-off between privacy and provability. Starknet removes it. We lean on MIST for
                privacy and Cairo + SHARP for proofs. That stack is the product.
              </p>
              <div className="mt-4 rounded-2xl bg-white/10 border border-white/10 p-4">
                <p className="text-sm font-semibold">Next milestone</p>
                <p className="text-sm text-white/80 mt-1">Risk engine proofs live in staging (4 weeks).</p>
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-1">
              {STATUS_PULSES.map((pulse) => {
                const tones = toneClasses[pulse.color];
                return (
                  <div
                    key={pulse.title}
                    className={`rounded-2xl border ${tones.card} p-4 shadow-sm backdrop-blur`}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`h-2.5 w-2.5 rounded-full ${tones.dot}`} />
                      <p className="text-xs uppercase tracking-[0.14em]">{pulse.title}</p>
                    </div>
                    <p className="font-display text-lg mt-2">{pulse.status}</p>
                    <p className={`text-sm mt-1 ${pulse.color === 'ink' ? 'text-white/80' : 'text-slate-600'}`}>
                      {pulse.detail}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <main className="max-w-6xl mx-auto px-6 pb-16">
        <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_280px] lg:gap-10">
          <div className="space-y-16">
            <section id="executive-summary" className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="h-2 w-8 rounded-full bg-lagoon-500" />
                <h2 className="font-display text-3xl text-ink">Executive Summary</h2>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm">
                  <p className="text-sm text-slate-500">Problem</p>
                  <p className="font-semibold text-ink mt-1">AI in DeFi is a black box</p>
                  <p className="text-sm text-slate-600 mt-2">Risk models run opaquely. Users trust without proof.</p>
                </div>
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm">
                  <p className="text-sm text-slate-500">Move</p>
                  <p className="font-semibold text-ink mt-1">Starknet-native verifiability</p>
                  <p className="text-sm text-slate-600 mt-2">Cairo + SHARP prove AI logic; MIST keeps it private.</p>
                </div>
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm">
                  <p className="text-sm text-slate-500">Why now</p>
                  <p className="font-semibold text-ink mt-1">Infrastructure is ready</p>
                  <p className="text-sm text-slate-600 mt-2">MIST SDK live; router deployed; proofs in flight.</p>
                </div>
              </div>

              <div className="rounded-3xl bg-gradient-to-r from-lagoon-50 to-mint-50 border border-lagoon-100 p-6 shadow-sm">
                <p className="text-lg font-medium text-ink mb-2">
                  Obsqra is the verifiable AI SDK for DeFi on Starknet.
                </p>
                <p className="text-slate-600">
                  We stopped rebuilding privacy. MIST solves it natively. Now we wrap Cairo proofs around AI logic,
                  validate via SHARP, and route capital with verifiable constraints. Proofs replace trust.
                </p>
              </div>
            </section>

            <section id="strategic-pivot" className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="h-2 w-8 rounded-full bg-mint-500" />
                <h2 className="font-display text-3xl text-ink">The Strategic Pivot</h2>
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm">
                  <p className="font-semibold text-ink">What we learned on EVM</p>
                  <p className="text-sm text-slate-600 mt-2">
                    Privacy pools worked but consumed half the build. AI stayed opaque; proofs and privacy conflicted.
                  </p>
                </div>
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm">
                  <p className="font-semibold text-ink">Starknet advantage</p>
                  <p className="text-sm text-slate-600 mt-2">
                    Cairo computation is provable by default. SHARP attests. MIST provides native privacy. No rebuilds.
                  </p>
                </div>
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm">
                  <p className="font-semibold text-ink">Product focus</p>
                  <p className="text-sm text-slate-600 mt-2">
                    A verifiable AI wrapper: privacy (MIST), proofs (Cairo/SHARP), routing (StrategyRouter).
                  </p>
                </div>
              </div>
              <div className="rounded-2xl bg-ink text-white p-6 shadow-lift">
                <p className="font-semibold">Thesis</p>
                <p className="text-sm text-white/80 mt-2">
                  EVM: choose privacy or provability. Starknet: both natively. This is Starknet&apos;s killer app for AI
                  infrastructure in DeFi.
                </p>
              </div>
            </section>

            <section id="architecture" className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="h-2 w-8 rounded-full bg-ink" />
                <h2 className="font-display text-3xl text-ink">Technical Architecture</h2>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm space-y-3">
                  <p className="font-semibold text-ink">Cairo &gt; Solidity for zkML</p>
                  <p className="text-sm text-slate-600">
                    Cairo is designed for provable computation. AI logic emits proofs without retrofit work. Solidity
                    cannot prove arbitrary AI paths.
                  </p>
                </div>
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm space-y-3">
                  <p className="font-semibold text-ink">SHARP proving</p>
                  <p className="text-sm text-slate-600">
                    Shared prover generates STARK proofs for the risk engine. On-chain verification removes black-box
                    trust.
                  </p>
                </div>
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm space-y-3">
                  <p className="font-semibold text-ink">MIST privacy layer</p>
                  <p className="text-sm text-slate-600">
                    Native privacy on Starknet. SDK integrated; deposits/withdrawals are unlinkable. No custom privacy
                    rebuild.
                  </p>
                </div>
                <div className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm space-y-3">
                  <p className="font-semibold text-ink">Composability</p>
                  <p className="text-sm text-slate-600">
                    StrategyRouter targets Nostra, zkLend, Ekubo. DAOConstraintManager enforces guardrails with proofs.
                  </p>
                </div>
              </div>

              <div className="rounded-2xl bg-slate-900 text-white p-6 font-mono text-sm overflow-x-auto shadow-lift">
                <p className="text-slate-400 mb-3"># Starknet Obsqra Architecture</p>
                <pre className="whitespace-pre leading-6">
{`User Deposit (Private)
    │
    ▼
┌─────────────────────────────┐
│  MIST.cash Chamber          │
│  └─ Unlinkable transaction  │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Risk Engine (Cairo)        │
│  └─ AI logic + constraints  │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  SHARP Prover               │
│  └─ STARK proof + attestor  │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Strategy Router            │
│  └─ Routes to protocols     │
└─────────────────────────────┘
    │      │        │
    ▼      ▼        ▼
  Nostra  zkLend   Ekubo
    │      │        │
    └──────┴────────┘
          ▼
   Verifiable Yields
          ▼
   Private Withdrawal (MIST)`}
                </pre>
              </div>

              <div className="rounded-2xl bg-white/90 border border-white/70 p-6 shadow-sm space-y-3">
                <p className="font-display text-xl text-ink">ZK-RAG: Knowledge graph + ontology</p>
                <p className="text-sm text-slate-600">
                  The risk engine ingests a knowledge graph of protocols, pools, assets, and constraints defined by an ontology. Graph features (exposure paths, liquidity depth, counterparty risk) are precomputed, hashed, and fed into Cairo. SHARP proves the allocation used exactly that data slice and respected DAO policies.
                </p>
                <ul className="text-sm text-slate-700 space-y-2">
                  <li>• Ontology keeps vocab stable: assets, pools, constraints, policy rules.</li>
                  <li>• Graph features are deterministic inputs—easy to audit, easy to prove.</li>
                  <li>• Privacy holds: sensitive positions stay private via MIST; proofs cover logic.</li>
                </ul>
              </div>
            </section>

            <section id="examples" className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="h-2 w-8 rounded-full bg-lagoon-500" />
                <h2 className="font-display text-3xl text-ink">Concrete Examples</h2>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {EXAMPLES.map((example) => (
                  <div key={example.title} className="rounded-2xl bg-white/90 border border-white/70 p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-3">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          example.accent === 'ink'
                            ? 'bg-ink text-white'
                            : example.accent === 'mint'
                              ? 'bg-mint-100 text-ink'
                              : 'bg-lagoon-100 text-ink'
                        }`}
                      >
                        {example.badge}
                      </span>
                      <p className="font-display text-xl text-ink">{example.title}</p>
                    </div>
                    <p className="text-sm text-slate-600 mb-3">{example.scenario}</p>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-slate-700">
                      {example.steps.map((step) => (
                        <li key={step}>{step}</li>
                      ))}
                    </ol>
                    <p className="mt-3 text-sm rounded-xl bg-cloud border border-white/70 p-3 text-slate-700">
                      {example.proof}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            <section id="roadmap" className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="h-2 w-8 rounded-full bg-mint-500" />
                <h2 className="font-display text-3xl text-ink">Ecosystem Development Roadmap</h2>
              </div>
              <div className="grid gap-4">
                {ROADMAP.map((phase) => (
                  <div
                    key={phase.phase}
                    className={`rounded-2xl border p-6 shadow-sm ${
                      phase.accent === 'mint'
                        ? 'bg-mint-50 border-mint-200'
                        : phase.accent === 'lagoon'
                          ? 'bg-lagoon-50 border-lagoon-200'
                          : 'bg-white/85 border-white/70'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3 flex-wrap">
                      <div className="flex items-center gap-3">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            phase.accent === 'ink'
                              ? 'bg-ink text-white'
                              : phase.accent === 'lagoon'
                                ? 'bg-lagoon-500 text-white'
                                : 'bg-mint-500 text-white'
                          }`}
                        >
                          {phase.phase}
                        </span>
                        <h3 className="font-display text-xl text-ink">{phase.title}</h3>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          phase.statusTone === 'success'
                            ? 'bg-green-100 text-green-700'
                            : phase.statusTone === 'warning'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {phase.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-slate-700 mt-3">{phase.summary}</p>
                    <ul className="mt-3 space-y-2 text-sm text-slate-700">
                      {phase.items.map((item) => (
                        <li key={item} className="flex gap-2">
                          <span className="text-green-500">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                    <p className="text-xs text-slate-500 mt-4">{phase.timeline}</p>
                  </div>
                ))}
              </div>
            </section>

            <section id="comparison" className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="h-2 w-8 rounded-full bg-lagoon-500" />
                <h2 className="font-display text-3xl text-ink">Obsqra: EVM vs Starknet</h2>
              </div>
              <div className="rounded-2xl bg-white/90 border border-white/70 shadow-sm overflow-hidden">
                <div className="grid grid-cols-3 bg-cloud border-b border-white/80 text-sm font-semibold text-ink">
                  <p className="py-3 px-4">Feature</p>
                  <p className="py-3 px-4">EVM (Base/Arbitrum)</p>
                  <p className="py-3 px-4">Starknet</p>
                </div>
                <div className="divide-y divide-white/70 text-sm">
                  {COMPARISON.map((row, idx) => (
                    <div
                      key={row.feature}
                      className={`grid grid-cols-3 px-4 py-3 ${
                        idx % 2 === 0 ? 'bg-white' : 'bg-cloud/60'
                      }`}
                    >
                      <p className="text-slate-700">{row.feature}</p>
                      <p className="text-slate-600">{row.evm}</p>
                      <p className="text-green-700 font-medium">{row.starknet}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-2xl bg-ink text-white p-6 shadow-lift">
                <h3 className="font-display text-xl">Implication</h3>
                <p className="text-sm text-white/80 mt-2">
                  EVM launch validated privacy pools. Starknet unlocks verifiable AI — the actual differentiator.
                  Privacy is solved infrastructure; proofs become the product.
                </p>
              </div>
            </section>

            <section id="developer-toolkit" className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="h-2 w-8 rounded-full bg-mint-500" />
                <h2 className="font-display text-3xl text-ink">Developer Toolkit</h2>
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                {TOOLKIT.map((tool) => (
                  <div key={tool.title} className="rounded-2xl bg-white/90 border border-white/70 p-5 shadow-sm">
                    <h4 className="font-semibold text-ink mb-2">{tool.title}</h4>
                    <ul className="space-y-2 text-sm text-slate-600">
                      {tool.items.map((item) => (
                        <li key={item} className="flex gap-2">
                          <span className="mt-1 h-1.5 w-1.5 rounded-full bg-ink/70" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                    <a
                      href={tool.link}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm text-lagoon-600 hover:underline mt-3 inline-block"
                    >
                      View →
                    </a>
                  </div>
                ))}
              </div>
              <div className="rounded-2xl bg-slate-900 text-white p-6 font-mono text-sm overflow-x-auto shadow-lift">
                <p className="text-slate-400 mb-2"># Example: MIST integration snippet</p>
                <pre className="whitespace-pre leading-6 text-green-200">
{`import { useMistCash } from '@/hooks/useMistCash';

function PrivateDeposit() {
  const { mistService, isReady } = useMistCash();
  const handleDeposit = async (amount: bigint) => {
    if (!isReady) return;
    const claimingKey = 'mist_' + Date.now();
    const txHash = await mistService.deposit(amount, recipientAddress, claimingKey);
    return { txHash, claimingKey };
  };
}`}
                </pre>
              </div>
            </section>

            <section id="use-cases" className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="h-2 w-8 rounded-full bg-ink" />
                <h2 className="font-display text-3xl text-ink">Use Cases & Ecosystem Fit</h2>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                {USE_CASES.map((useCase) => (
                  <div
                    key={useCase.title}
                    className={`rounded-2xl border p-6 shadow-sm ${
                      useCase.accent === 'mint'
                        ? 'bg-mint-50 border-mint-100'
                        : useCase.accent === 'lagoon'
                          ? 'bg-lagoon-50 border-lagoon-100'
                          : useCase.accent === 'ink'
                            ? 'bg-slate-900 text-white border-slate-800'
                            : 'bg-white/90 border-white/70'
                    }`}
                  >
                    <h3 className="font-display text-xl">{useCase.title}</h3>
                    <p
                      className={`text-sm mt-2 ${
                        useCase.accent === 'ink' ? 'text-white/80' : 'text-slate-600'
                      }`}
                    >
                      {useCase.copy}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-gradient-to-r from-ink via-slate-800 to-ink text-white rounded-3xl p-8 shadow-lift">
              <div className="flex flex-wrap items-center gap-3 mb-3">
                <span className="px-3 py-1 rounded-full bg-white/10 border border-white/10 text-xs tracking-[0.16em] uppercase">
                  Call to action
                </span>
                <p className="text-sm text-white/70">Join the Starknet-native verifiable AI experiment.</p>
              </div>
              <h2 className="font-display text-3xl mb-3">Build with us</h2>
              <p className="text-slate-200 max-w-2xl mb-6">
                Contribute contracts, build strategies, or plug your protocol into the router. Every action ships with
                proofs and privacy by default.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link
                  href="/"
                  className="px-6 py-3 rounded-full bg-white text-ink font-semibold hover:opacity-90 transition"
                >
                  Launch App
                </Link>
                <a
                  href={GITHUB_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="px-6 py-3 rounded-full bg-transparent text-white border border-white/30 font-semibold hover:bg-white/10 transition"
                >
                  View on GitHub
                </a>
                <a
                  href={`${GITHUB_URL}/discussions`}
                  target="_blank"
                  rel="noreferrer"
                  className="px-6 py-3 rounded-full bg-white/10 text-white font-semibold border border-white/20 hover:bg-white/15 transition"
                >
                  Talk integrations
                </a>
              </div>
            </section>
          </div>

          <aside className="mt-10 lg:mt-0 space-y-4 lg:sticky lg:top-24">
            <div className="rounded-2xl bg-white/90 border border-white/70 shadow-sm p-5">
              <p className="text-xs uppercase tracking-[0.16em] text-slate-500 mb-3">Navigation</p>
              <nav className="space-y-2 text-sm">
                {SECTION_LINKS.map((section) => (
                  <a
                    key={section.id}
                    href={`#${section.id}`}
                    className="flex items-center gap-2 text-slate-700 hover:text-ink transition"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-ink/50" />
                    {section.label}
                  </a>
                ))}
              </nav>
            </div>
            <div className="rounded-2xl bg-ink text-white shadow-lift p-5">
              <p className="font-semibold text-lg">Need a hand?</p>
              <p className="text-sm text-white/80 mt-1">Open an issue or start a discussion.</p>
              <div className="flex flex-col gap-2 mt-3">
                <a
                  href={`${GITHUB_URL}/issues`}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 rounded-full bg-white text-ink font-semibold text-sm text-center hover:opacity-90 transition"
                >
                  Open GitHub issue
                </a>
                <a
                  href={`${GITHUB_URL}/discussions`}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 rounded-full border border-white/30 text-white text-sm text-center hover:bg-white/10 transition"
                >
                  Start discussion
                </a>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
