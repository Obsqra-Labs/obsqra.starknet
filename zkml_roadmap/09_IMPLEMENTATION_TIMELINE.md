# Implementation Timeline

---

## Phase 1: Immediate (Weeks 1-2) — Stage 3A

**Goal**: Launch "On-Chain AI" narrative + Obsqra Labs site.

- **Week 1**: Contract (ModelParams, storage, set_model_params, calculate_risk_score_internal using params); zkml_roadmap docs.
- **Week 2**: Backend (model params service, feature flag); Frontend (Stage 3A components, feature flags); Landing page (Obsqra Labs hero, research areas, products).

---

## Phase 2: Research (Weeks 3-6) — Stage 3B Evaluation

- EZKL evaluation (export ONNX, proof gen, verifier on Starknet testnet).
- Giza + Orion evaluation (SDK, expressivity, cost).
- Decision: which stack (if any) for production.

---

## Phase 3: Short-term (Months 2-3) — Stage 4 Foundation

- DAO governance contracts (model proposal, voting, execute approval).
- Artifact publishing (IPFS, templates, reproducibility docs).

---

## Phase 4: Medium-term (Months 4-6) — Stage 3B or Stage 5

- **Path A**: If zkML viable — integrate chosen stack, deploy verifier, hybrid pipeline (2-3 months).
- **Path B**: Accelerate Stage 5 — intent registry, reputation, policy marketplace (2-3 months; can run in parallel with zkML research).

---

## Success Metrics

- **Stage 3A**: Model params in storage; governance can update; landing shows Layer 2; demo works (1-2 weeks).
- **Stage 3B research**: EZKL/Giza verifier on testnet; proof &lt; 10s; cost &lt; $0.10 per allocation (4-6 weeks).
- **Stage 4**: DAO votes on model versions; artifacts on IPFS (3-6 months).
- **Stage 5**: Intent submission, agent reputation, policy enforcement (2-3 months).
