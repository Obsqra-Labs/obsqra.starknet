# zkML Evolution Roadmap - Executive Summary

**Obsqra Labs**: Pioneering verifiable AI infrastructure for trustless systems.

---

## High-Level Overview

This roadmap documents the evolution from **Proof-Gated Execution** (Stage 2, current) through **On-Chain AI** (Stage 3A/3B), **Trustless AI** (Stage 4), and **On-Chain Agent** (Stage 5).

| Stage | Name | Proof System | Timeline |
|-------|------|--------------|----------|
| **2** | Proof-Gated Execution | Stone only | **Current** |
| **3A** | On-Chain Model (Parameterized) | Stone only | 1-2 weeks |
| **3B** | zkML Inference | EZKL/Giza + Stone | 2-4 months (after research) |
| **4** | Trustless AI | Same as 3A/3B | 3-6 months |
| **5** | On-Chain Agent | Hybrid | 2-3 months (accelerated) |

---

## Key Clarifications

- **No Option C** (tiny NNs in Cairo): Too limited for "true AI"; skip to zkML (Option B) for real ML.
- **zkML is documented**: EZKL/Giza have SDKs; we need **Starknet integration research** (4-6 weeks), not reverse engineering.
- **Stage 5 accelerated**: 2-3 months (not 6-12) — foundations exist (STEP 0.6 = intents, events = receipts).
- **Landing = Labs**: obsqra.xyz is Obsqra Labs (research entity); products are research output.

---

## Proof System Summary

- **LuminAIR**: Deprecated, not Integrity-compatible. Not used.
- **Stone**: Production path. No new proof system for Stage 3A (same flow, parameterized).
- **Stage 3B**: New zkML stack (EZKL/Giza) for real ML inference; Starknet integration research required.

---

## Document Index

| File | Purpose |
|------|---------|
| `01_STAGE_2_CURRENT_STATE.md` | Where we are (4/5 zkML) |
| `02_STAGE_3A_ONCHAIN_MODEL.md` | Option A: Parameterized formula (NEXT) |
| `03_STAGE_3B_ZKML_INFERENCE.md` | Option B: Real ML with zkML proofs |
| `04_STAGE_4_TRUSTLESS_AI.md` | DAO governance + public artifacts |
| `05_STAGE_5_ONCHAIN_AGENT.md` | Hybrid agent infrastructure |
| `06_ZKML_STACK_RESEARCH.md` | EZKL/Giza Starknet evaluation |
| `07_LANDING_PAGE_ARCHITECTURE.md` | starknet.obsqra.fi Obsqra Labs design |
| `08_CODE_STRUCTURE.md` | Monorepo + feature flags |
| `09_IMPLEMENTATION_TIMELINE.md` | Phased rollout |
