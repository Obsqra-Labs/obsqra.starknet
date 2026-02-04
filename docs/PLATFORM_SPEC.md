# Obsqra Platform — Full Specification

**Version:** 1.0  
**Last updated:** January 2026  
**Landing:** https://starknet.obsqra.fi  
**Brand:** Obsqra Labs — pioneering verifiable AI infrastructure for trustless systems.

---

## 1. Overview

### 1.1 Purpose

Obsqra is a **proof-gated execution layer** for DeFi on Starknet. It turns “trust me, the agent respected constraints” into **cryptographically verifiable** decisions: every allocation can come with a STARK proof that it complied with DAO/user-defined constraints. No proof → no execution.

### 1.2 Value Proposition

- **Constraint-proofed decisions**: Allocation and execution are gated by on-chain proof verification (SHARP Fact Registry).
- **Verify before execute**: Proofs can be verified locally before sending the transaction.
- **Audit trail**: Metrics → risk scores → allocation → proof hash → transaction hash.

### 1.3 High-Level Flow

```
Constraints + Inputs
        ↓
Risk engine proposes allocation (deterministic scoring)
        ↓
Generate STARK proof (constraint adherence)
        ↓
Verify (Integrity / Fact Registry)
        ↓
Execute transaction (RiskEngine → StrategyRouter)
        ↓
(Optional) Submit to SHARP → anchor fact on L1
```

### 1.4 Current Maturity

- **Stage 2 (Proof-Gated Execution)**: Production — Stone prover, FactRegistry verification, two-protocol (JediSwap, Ekubo) allocation.
- **Stage 3A (On-Chain Parameterized Model)**: Live — RiskEngine stores per-version `ModelParams`; formula weights and clamp bounds are readable/upgradeable on-chain; API and UI expose model params.

---

## 2. Architecture

### 2.1 Three-Layer Stack

| Layer | Stack | Role |
|-------|--------|------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind, @starknet-react/core | Dashboard, demo, Obsqra Labs landing, Stage 3A model params viewer |
| **Backend** | FastAPI, Python 3.11+, PostgreSQL, starknet.py | API, proof generation (Stone), verification (Integrity), orchestration, wallet signing |
| **Contracts** | Cairo 2, Scarb, Starknet Sepolia | RiskEngine v4, StrategyRouter v3.5, ModelRegistry, DAOConstraintManager, FactRegistry |

### 2.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (Next.js)                                             │
│  • Landing (Obsqra Labs), Demo, Dashboard                       │
│  • ModelParamsViewer, ParamComparisonTool (Stage 3A)             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────────┐
│  Backend (FastAPI)                                               │
│  • Risk Engine API, Proofs, Verification, Model Registry, Demo   │
│  • Stone Prover Service, Integrity Service, Allocation Orchestrator │
│  • Protocol Metrics, Market Data, Analytics                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ Starknet RPC
┌────────────────────────────▼────────────────────────────────────┐
│  Starknet (Sepolia)                                              │
│  • RiskEngine v4 (Stage 3A)  • StrategyRouter v3.5              │
│  • ModelRegistry             • DAOConstraintManager              │
│  • SHARP Fact Registry       • JediSwap / Ekubo                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Repo Structure

```
backend/       FastAPI API, proof jobs, workers, model_service, config
contracts/     Cairo: risk_engine, strategy_router_v3_5, model_registry,
               dao_constraint_manager, sharp_verifier, interfaces
frontend/      Next.js app, config, stage2/ and stage3a/ components
scripts/       Deployment, verification, integration
zkml_roadmap/  Stage 2–5 docs, implementation notes
docs/          Architecture, API reference, contract reference, deployment
```

---

## 3. Smart Contracts

### 3.1 Network and Addresses (Sepolia)

| Contract | Address (default in config) | Purpose |
|----------|-----------------------------|---------|
| **RiskEngine v4** | `0x052fe4c3f3913f6be76677104980bff78d224d5760b91f02700e8c8275ac6e68` | Risk scoring, proof verification gate, allocation proposal, Stage 3A `ModelParams` |
| **StrategyRouter v3.5** | `0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73` | Fund management, protocol execution, only callable by RiskEngine |
| **ModelRegistry** | `0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc` | Model provenance, version history |
| **Fact Registry (SHARP)** | Configured per deployment | On-chain proof verification; RiskEngine queries it before execution |

### 3.2 RiskEngine v4 (Stage 3A)

- **Proof gate**: `propose_and_execute_allocation` verifies both proof fact hashes via Fact Registry before any execution.
- **Model version**: Enforces `approved_model_versions`; supports `model_version == 0` for legacy.
- **Constraint signature**: Optional user-signed constraints (STEP 0.6).
- **Risk scoring**: `calculate_risk_score_internal(ref self, model_version, utilization, volatility, liquidity, audit_score, age_days)`.
  - If `model_version == 0` or params not set: fixed Stage 2 formula (hardcoded weights).
  - Else: reads `model_params.read(model_version)` (Stage 3A) — weights and clamp bounds.
- **Storage**: `model_params: Map<felt252, ModelParams>`, owner-only `set_model_params(version, params)`, view `get_model_params(version)`.
- **Allocation**: Two-protocol (JediSwap, Ekubo) risk-adjusted allocation; then DAO constraints check; then `StrategyRouter.update_allocation`.

### 3.3 StrategyRouter v3.5

- **Access**: `update_allocation(jediswap_pct, ekubo_pct)` callable only by RiskEngine.
- **Protocols**: JediSwap (AMM), Ekubo (concentrated liquidity); deposit/withdraw, position tracking.
- **Optional**: MIST.cash privacy (commit/reveal).

### 3.4 ModelRegistry

- **Register**: Owner-only `register_model_version(version, model_hash, description)`.
- **Read**: `get_current_model()`, `get_model_version(version)`, `get_model_history()`.

### 3.5 DAOConstraintManager

- **Storage**: `max_single_protocol`, `min_diversification`, `max_volatility`, `min_liquidity`.
- **Usage**: RiskEngine reads and validates allocation against these before calling StrategyRouter.

### 3.6 Fact Registry (SHARP)

- **Interface**: `get_all_verifications_for_fact_hash(fact_hash) -> Span<felt252>`.
- **Semantics**: Non-empty return ⇒ proof verified; RiskEngine reverts if proofs not verified.

---

## 4. Backend

### 4.1 Configuration (High Level)

- **Server**: `API_HOST`, `API_PORT` (default 8001), `API_BASE_URL`, `CORS_ORIGINS` (include `https://starknet.obsqra.fi`, `http://localhost:3003`, `3004` for dev).
- **Starknet**: `STARKNET_RPC_URL`, `STARKNET_RPC_URLS` (failover), `STARKNET_NETWORK` (sepolia/mainnet), `RISK_ENGINE_ADDRESS`, `STRATEGY_ROUTER_ADDRESS`, `MODEL_REGISTRY_ADDRESS`.
- **Proof**: Stone prover (local); Integrity layout `recursive`, hasher `keccak_160_lsb`, Stone version `stone6`; `INTEGRITY_CAIRO_TIMEOUT`, `ALLOW_UNVERIFIED_EXECUTION` (default false).
- **Stage 3A**: `PARAMETERIZED_MODEL_ENABLED` (default True), `MODEL_PARAMS_TABLE`.
- **Wallet**: `BACKEND_WALLET_ADDRESS`, `BACKEND_WALLET_PRIVATE_KEY` for automated execution.
- **Atlantic**: `ATLANTIC_API_KEY`, `ATLANTIC_BASE_URL` for L1 settlement (optional).

### 4.2 API Routes (Grouped)

**Base path:** `/api/v1`

| Domain | Method | Path | Purpose |
|--------|--------|------|---------|
| **Risk Engine** | POST | `/risk-engine/calculate-risk` | Compute risk scores (body: metrics) |
| | GET | `/risk-engine/model-params/{version}` | Get Stage 3A model params (weights, clamp) |
| | POST | `/risk-engine/calculate-allocation` | Compute allocation (legacy) |
| | POST | `/risk-engine/orchestrate-allocation` | Full flow: metrics → proof → verify → execute |
| | POST | `/risk-engine/propose-allocation` | Propose only (no execute) |
| | POST | `/risk-engine/propose-from-market` | Propose using live market metrics |
| | POST | `/risk-engine/execute-allocation` | Execute existing proposal (by proof_job_id) |
| | POST | `/risk-engine/orchestrate-from-market` | Orchestrate using live market metrics |
| **Proofs** | POST | `/proofs/generate` | Generate proof (metrics → proof hash) |
| **Verification** | GET | `/verification/verification-status/{proof_job_id}` | Verification status for job |
| | GET | `/verification/verify-fact-hash/{fact_hash}` | Verify fact hash on registry |
| **Model Registry** | GET | `/model-registry/current` | Current model version |
| | GET | `/model-registry/history` | Version history |
| | GET | `/model-registry/version/{version}` | Specific version |
| | POST | `/model-registry/register` | Register model (body) |
| **Demo** | POST | `/demo/generate-proof` | Demo proof generation |
| | GET | `/demo/cost-comparison` | Cost comparison data |
| **Analytics** | GET | `/analytics/risk-history`, `/allocation-history`, `/dashboard`, `/rebalance-history`, `/proof-summary`, `/proof/{id}/download`, `/proof-performance`, `/protocol-apys`, `/performance/real` | Analytics and history |
| **Market** | GET | `/market/snapshot`, `/market/metrics` | Market snapshots and metrics |
| **Admin** | POST | `/admin/update-strategy-router-risk-engine` | Wire StrategyRouter to RiskEngine (admin) |
| **Auth / Users** | POST | `/auth/register`, `/auth/login`; GET `/auth/me`; POST `/auth/connect-wallet` | Auth and wallet |
| **MIST** | POST | `/mist/commit`, `/mist/reveal`; GET `/mist/commitments/{hash}`; POST `/mist/chamber` | MIST.cash integration |
| **zkML** | POST | `/zkml/infer`, `/zkml/verify-demo` | zkML inference (demo) |
| **Predictions** | GET | `/predictions/risk-forecast`, `/yield-forecast`, `/rebalance-suggestions`; POST `/predictions/run-optimization` | Forecasts and optimization |
| **Transactions** | POST | `/transactions/`; GET `/transactions/`, `/transactions/{tx_hash}` | Transaction submit and lookup |

### 4.3 Key Services

- **Stone Prover Service**: Local STARK proof generation from Cairo execution trace; output serialized for Integrity.
- **Integrity Service**: Submit proof, get fact hash; verification against Fact Registry.
- **Allocation Proof Orchestrator**: Coordinates metrics → trace → proof → verify → RiskEngine call.
- **Model Service**: `get_model_params(version)` (call RiskEngine `get_model_params`), `set_model_params` (returns guidance for admin/sncast); model hash / registry helpers.
- **Protocol Metrics / Market Data**: JediSwap, Ekubo metrics (utilization, volatility, liquidity, audit_score, age_days) and APY.

### 4.4 Data Flow (Orchestrate)

1. Client POSTs to `/risk-engine/orchestrate-allocation` (optional body with metrics, or use live market).
2. Backend fetches protocol metrics (if not provided).
3. Backend generates Cairo execution trace for risk + allocation.
4. Stone prover produces proof; backend serializes and submits to Integrity; obtains fact hash.
5. Backend calls RiskEngine `propose_and_execute_allocation` with metrics, proof fact hashes, expected scores, fact registry address, model_version, constraint_signature.
6. Contract: STEP 0 verify proofs (Fact Registry), STEP 0.5 model version, STEP 0.6 constraint signature, STEP 1–2 risk scores (with `model_version` and Stage 3A params if set), STEP 3 allocation, STEP 4 DAO constraints, STEP 5 StrategyRouter.update_allocation.
7. Backend returns proof_job_id, decision_id, allocation percentages, proof_hash, fact_hash, transaction_hash, verification_status.

---

## 5. Frontend

### 5.1 Stack

- **Framework**: Next.js 14 (App Router), TypeScript, Tailwind CSS.
- **Starknet**: @starknet-react/core.
- **Config**: `frontend/src/lib/config.ts` — RPC, backend URL, strategy router / risk engine / model registry addresses, network, feature flags.

### 5.2 Feature Flags (config)

- `PROOF_GATED_EXECUTION`: true.
- `PARAMETERIZED_MODEL`: `NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL === 'true'` (default true in next.config).
- `MODEL_GOVERNANCE`, `ZKML_INFERENCE`, `DAO_MODEL_APPROVAL`, `AGENT_INTENTS`: optional future stages.

### 5.3 Key Pages / Sections

- **Landing (Obsqra Labs)**: Hero “Obsqra Labs”, tagline, Research Areas, Products & Demos (Proof-Gated LIVE, On-Chain AI BETA when `PARAMETERIZED_MODEL`, Agent SDK ROADMAP), System Architecture, Get Started.
- **Products**: Proof-Gated Execution (link to demo); On-Chain AI (Stage 3A) — ModelParamsViewer “Current model params (v0)”, ParamComparisonTool; Agent SDK (roadmap).
- **Demo**: Interactive proof generation, on-chain verification, block explorer links.
- **Dashboard**: When wallet connected; allocation and risk views.

### 5.4 Stage Components

- **stage2**: ProofGenerator, AllocationExecutor, DAOConstraintValidator.
- **stage3a**: ModelParamsViewer (GET `/api/v1/risk-engine/model-params/{version}`), ParamComparisonTool.

### 5.5 Environment

- `NEXT_PUBLIC_BACKEND_URL`: Backend base URL (e.g. `http://localhost:8001` or production).
- `NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL`: Enable Stage 3A UI (default true).
- `NEXT_PUBLIC_RPC_URL`, `NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS`, `NEXT_PUBLIC_RISK_ENGINE_ADDRESS`, `NEXT_PUBLIC_MODEL_REGISTRY_ADDRESS`, `NEXT_PUBLIC_NETWORK`.

---

## 6. Proof and Verification

### 6.1 Prover

- **Production**: Stone prover (local binary); layout compatible with Integrity (recursive, keccak_160_lsb, stone6).
- **Typical**: 2–4 s proof generation; fact hash submitted to Integrity and registered in SHARP Fact Registry.

### 6.2 Verification

- **Integrity (Atlantic)**: Submit proof, receive fact hash; Fact Registry stores verifications.
- **On-chain**: RiskEngine calls Fact Registry `get_all_verifications_for_fact_hash`; non-empty ⇒ verified; else revert.

### 6.3 Formula (Risk Score)

- **Stage 2**: Fixed weights (e.g. utilization 25, volatility 40, liquidity tiers 0/5/15/30, audit 3, age 10, age_cap_days 730, clamp 5–95).
- **Stage 3A**: Same formula structure; weights and clamp bounds read from `model_params(version)`; version 0 or unset ⇒ Stage 2 defaults.

---

## 7. Deployment and Operations

### 7.1 Defaults (Development)

- **Backend**: `cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001`.
- **Frontend**: `cd frontend && npm run dev` (port 3003); set `NEXT_PUBLIC_BACKEND_URL` to backend URL; ensure backend CORS includes frontend origin (e.g. `http://localhost:3004` if using port 3004).
- **Contracts**: Scarb build; deploy with sncast/starkli; set RiskEngine/StrategyRouter/ModelRegistry in backend and frontend env.

### 7.2 Production

- **Landing / API**: `https://starknet.obsqra.fi` (frontend and API base); backend typically behind same host or `api.obsqra.fi`.
- **RPC**: Starknet Sepolia (or mainnet); configurable via `STARKNET_RPC_URL` / `STARKNET_RPC_URLS`.

### 7.3 Verification Script (Stage 3A)

- `scripts/verify_stage3a_api.sh`: GET `/api/v1/risk-engine/model-params/0`; expects JSON with `w_utilization`, `clamp_min`, `clamp_max`. Use `BASE_URL` if backend not on 8001.

---

## 8. Roadmap (zkML Evolution)

| Stage | Name | Status | Proof / Model |
|-------|------|--------|----------------|
| **2** | Proof-Gated Execution | Production | Stone; fixed formula |
| **3A** | On-Chain Parameterized Model | Live | Stone; `ModelParams` on-chain, versioned |
| **3B** | zkML Inference | Research | EZKL/Giza + Stone; Starknet integration |
| **4** | Trustless AI | Planned | DAO governance, public artifacts |
| **5** | On-Chain Agent | Planned | Intents, receipts; 2–3 months target |

---

## 9. Security and Trust Boundaries

- **On-chain**: Execution is gated by proof verification and DAO constraints; no execution without valid proof and satisfied constraints.
- **Backend**: Holds wallet key for automated execution; must be secured; CORS and trusted hosts configured for known origins.
- **Frontend**: No secrets; reads from public API and config; wallet operations via Starknet wallet (user-owned).

---

## 10. References

- **Architecture**: `docs/03-architecture/` (system overview, contracts, backend, proof, verification, data flow).
- **API**: `docs/06-api-reference/` (overview, risk-engine, verification, model-registry).
- **Contracts**: `docs/07-contract-reference/` (RiskEngine, StrategyRouter, ModelRegistry, DAO, FactRegistry).
- **Deployment**: `docs/08-deployment/`.
- **zkML roadmap**: `zkml_roadmap/` (stages 2–5, implementation notes, landing, code structure, timeline).
- **Implementation notes (Stage 3A)**: `zkml_roadmap/10_STAGE_3A_IMPLEMENTATION_NOTES.md`.
