# Two Products on the Stack: Current + On-Chain AI

**Short answer**: Yes. You can have two products on the stack: **current** (formula + proof verification) and **on-chain AI** (parameterized/upgradeable model). They share the same infra; the difference is the contract model and how you position them.

---

## 1. Two Products, One Stack

| Product | What it is | Contract | Proof | Positioning |
|---------|------------|----------|-------|-------------|
| **Current** | Verifiable AI – fixed formula, proof-gated execution | RiskEngine v4 (fixed formula in Cairo) | Stone proof of formula execution | "Verifiable AI infrastructure" |
| **On-Chain AI** | Upgradeable on-chain model – same formula but params from storage | RiskEngine v4 + Option A (parameterized formula, `model_params` map) | Same Stone proof (trace uses params from storage) | "On-chain AI – upgradeable model" |

**Shared stack**:
- Same backend (orchestration, proof generation, Integrity registration)
- Same frontend (demo, dashboard)
- Same Stone prover, same Integrity FactRegistry
- Same RiskEngine contract **codebase** – On-Chain AI is an extension (add `model_params`, read params in `calculate_risk_score_internal`)

**Difference**:
- **Current**: Formula is fixed in code (25, 40, 5, 15, 30, …).
- **On-Chain AI**: Formula is parameterized; params live in storage, keyed by `model_version`; upgrades = governance/owner updates params.

So you don’t run two separate stacks. You have **one stack** with **two product positions**:
1. **Current product**: "Verifiable AI for DeFi" (fixed formula, proof-gated).
2. **On-Chain AI product**: "On-chain AI for DeFi" (upgradeable model, same proof flow).

---

## 2. How to Offer Both

**Option 1: Single deployment, two narratives**

- Deploy **one** RiskEngine (either current fixed formula or, after implementation, parameterized).
- **Current**: Market as "verifiable AI" (proof-gated, transparent formula).
- **On-Chain AI**: After Option A is live, market as "on-chain AI" (upgradeable model, same contract).

**Option 2: Two deployments (optional)**

- **Deployment A**: RiskEngine with fixed formula (current) – for users who want "stable, audited formula."
- **Deployment B**: RiskEngine with parameterized formula (Option A) – for users who want "upgradeable on-chain model."
- Same backend can point at either via config (e.g. `RISK_ENGINE_ADDRESS`).

**Recommendation**: Start with **Option 1**. Implement Option A (parameterize formula) in the same contract; then you have one stack and two product stories (current + on-chain AI). Add a second deployment only if a partner or client explicitly wants a fixed-formula-only instance.

---

## 3. Summary

- **Two products**: Yes – "Current" (verifiable AI, fixed formula) and "On-Chain AI" (upgradeable model).
- **One stack**: Same backend, frontend, Stone, Integrity; On-Chain AI is a contract extension (Option A).
- **What to do**: Implement Option A in RiskEngine; then market the same system as both "verifiable AI" and "on-chain AI" depending on audience.
