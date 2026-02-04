# Landing Page Architecture: Obsqra Labs

**Domain**: starknet.obsqra.fi (primary landing for this server; Obsqra Labs is the research entity).  
**Positioning**: Research lab pioneering proof-gated execution and on-chain AI (not just a product site).

---

## Structure

```
starknet.obsqra.fi/
├── / (Home — Obsqra Labs)
│   ├── Hero: "Obsqra Labs"
│   │   └── "Pioneering verifiable AI infrastructure for trustless systems"
│   ├── Research Areas
│   │   ├── Proof-Gated Execution
│   │   ├── On-Chain AI
│   │   └── Agent Infrastructure
│   ├── Products (showcase)
│   │   ├── Proof-Gated Execution [LIVE]
│   │   ├── On-Chain AI [BETA]
│   │   └── Agent SDK [ROADMAP]
│   └── Research & Open Source (papers, GitHub, blog)
│
├── /demo — Current product + On-Chain AI demo (feature flag) + coming soon
├── /docs — Architecture, integration, research
└── /roadmap — Evolution diagram, stage deep-dives
```

---

## Design Principles

- **Labs first**: Hero and primary message are about Obsqra Labs (research entity).
- **Products as output**: Products and demos are showcased as components/sections, not the only focus.
- **Progressive disclosure**: Teaser → full demo per layer.
- **Feature flags**: Stage 3A (On-Chain AI) section visible when `NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL=true`.

---

## Key Sections (Home Page)

1. **Hero**: Obsqra Labs + one-line tagline + short stats (e.g. proof success rate, zkML maturity).
2. **Research Areas**: Three pillars (Proof-Gated, On-Chain AI, Agent) with status (Production / Development / Research).
3. **Products & Demos**: ProofGatedDemo (live), OnChainAIDemo (if flag), AgentRoadmapTeaser (roadmap).
4. **Research Output**: Papers, GitHub repo, open source links.

---

## Implementation

- Single Next.js app; `page.tsx` implements Obsqra Labs home.
- Components: `ResearchArea`, `ProductShowcase`, `ProofGatedDemo`, `OnChainAIDemo`, `AgentRoadmapTeaser`.
- Config: `FEATURES.PARAMETERIZED_MODEL` for Stage 3A visibility.
