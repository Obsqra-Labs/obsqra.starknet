# What the Contract Upgrade Did – On-Chain Agent Explained

**Short answer**: Yes. The upgrade **put the agent on-chain** in the sense that the **policy and verification logic** that used to live only in the backend (or off-chain) now runs **inside the RiskEngine contract**. The contract is the on-chain agent: it orchestrates, verifies, and gates execution. It does **not** run the AI or the prover on-chain; it **verifies** that a valid proof was produced off-chain and then enforces model version and optional user-signed constraints before executing.

---

## 1. What “On-Chain Agent” Means Here

**Before (legacy / proof-gated v4 without agent)**  
- Contract: “I take metrics + proof facts + expected scores + fact registry. I verify proofs, compute allocation, check DAO constraints, then call StrategyRouter.”  
- Who can call: only the **owner**.  
- Model: not checked on-chain.  
- User constraints: not represented on-chain (only DAO constraints).

**After (v4 with on-chain agent)**  
- Contract: “I take the same **plus** `model_version` and `constraint_signature`. I still verify proofs (STEP 0), then I **additionally** check model version (STEP 0.5) and accept optional user-signed constraints (STEP 0.6). I can run in **permissionless mode**: in that case, **anyone** can call me; the only gate is proof + model + constraints.”  
- So the **agent** is the contract itself: it **orchestrates** (one entrypoint: propose_and_execute_allocation), **verifies** (proofs, model, optional user constraints), and **gates** execution (no execution without valid proof; optional model and constraint checks).  
- The “brain” (AI + prover) stays off-chain; the **on-chain agent** is the **gatekeeper and executor** that only acts when the off-chain brain has produced a valid proof and (optionally) the right model and user constraints are supplied.

---

## 2. What the Contract Upgrade Actually Did

### 2.1 New Parameters (9-Parameter Interface)

- **`model_version`** (felt252)  
  - Hash of the model version that produced the proof.  
  - Contract checks it against an **approved list** (`approved_model_versions`).  
  - If not approved and not 0 (legacy), the call reverts (STEP 0.5).  
  - So the **agent** enforces “only approved models can drive allocations” on-chain.

- **`constraint_signature`** (struct)  
  - User-signed constraints: who signed (`signer`), limits (e.g. max_single, min_diversification, max_volatility, min_liquidity), and signature (signature_r, signature_s, timestamp).  
  - If `signer == 0`, “no user signature” – contract still runs (e.g. DAO-only constraints).  
  - If `signer != 0`, the contract records that a user-signed constraint was supplied (STEP 0.6); full ECDSA verification can be added later.  
  - So the **agent** can **enforce and attest** “this execution was allowed under user-signed constraints” on-chain.

### 2.2 New On-Chain Logic (Steps)

- **STEP 0** (unchanged): Verify both proof facts in the SHARP fact registry; verify expected scores match on-chain risk calculation. No proof → revert.  
- **STEP 0.5** (new – on-chain agent): Check `model_version` in `approved_model_versions`; if not approved and not 0, revert.  
- **STEP 0.6** (new – on-chain agent): If `constraint_signature.signer != 0`, treat as “user-signed constraints supplied” (audit trail; full crypto check can be added later).  
- **STEP 1–2**: Compute risk scores, assert they match proof.  
- **STEP 3–4**: Compute allocation, verify DAO constraints.  
- **STEP 5+**: Call StrategyRouter, emit events (including model_version and constraint signer for audit).

So: **policy** (which model, whether user constraints are present) and **verification** (proof + model + optional signature) are now **on-chain**; the agent is the contract doing that.

### 2.3 New State and Admin

- **`approved_model_versions`** (map): Which model hashes are allowed. Owner (or admin) calls `approve_model_version` / `revoke_model_version`.  
- **`permissionless_mode`** (bool): If true, **any** caller can invoke `propose_and_execute_allocation`; the only authorization is “valid proof + approved model + (optional) user constraints”. If false, only the owner can call.  
- **`model_registry`** (address): Reserved for future ModelRegistry integration; approval is currently via the map above.

So the upgrade **put the agent on-chain** by:  
1) Moving **verification** of proof, model, and user constraints into the contract.  
2) Moving **policy** (who can call, which model is allowed) into the contract.  
3) Making the contract the single **orchestrator** that only executes when those checks pass.

---

## 3. What Still Lives Off-Chain

- **AI / risk model**: Runs off-chain (e.g. Python, Stone trace generation).  
- **Prover (Stone)**: Generates STARK proof off-chain.  
- **Fact registry**: Proof is submitted to SHARP/Integrity; the contract only **checks** that the fact is registered and that the scores match.  
- **Backend**: Fetches metrics, runs the prover, builds calldata (including `model_version` and `constraint_signature`), sends the transaction. So the **orchestrator in the large** is backend + contract; the **on-chain agent** is the contract’s role: verify and execute.

---

## 4. One-Sentence Summary

**The contract upgrade put the agent on-chain** by making RiskEngine the on-chain **gatekeeper and executor**: it verifies proofs (STEP 0), enforces approved model version (STEP 0.5), accepts and attests user-signed constraints (STEP 0.6), and can run in permissionless mode where proof + model + constraints are the only gate.

---

## 5. Frontend Flow: “Orchestrate with constraint_signature”

### 5.1 Current vs Desired

- **Current**:  
  - **Propose**: `proposeFromMarket()` or `proposeAllocation(metrics)` → backend generates proof, returns proposal + `proof_job_id`.  
  - **Execute**: `executeAllocation(proof_job_id)` → backend loads ProofJob, builds calldata (with model_version + zero constraint_signature), submits to RiskEngine.  
  - So the UI never sends **custom metrics + optional constraint_signature** in a **single** call to the backend.

- **Desired**:  
  - One flow where the frontend can call **orchestrate-allocation** with **full payload**: metrics + optional **constraint_signature** (and optionally proof_job_id if we want “execute with existing proof but custom constraints”).  
  - Backend already supports this: `POST /api/v1/risk-engine/orchestrate-allocation` with body `{ jediswap_metrics, ekubo_metrics, constraint_signature? }`. So we only need to **use** it from the UI.

### 5.2 Sketch: New Hook Method + Demo/Dashboard Usage

**1) Add `orchestrateAllocation` to the hook** (`useRiskEngineBackendOrchestration.ts`):

- **Signature**:  
  `orchestrateAllocation(payload: { jediswapMetrics: ProtocolMetrics; ekuboMetrics: ProtocolMetrics; constraintSignature?: ConstraintSignaturePayload | null }) => Promise<AllocationDecision | null>`
- **Payload type** (align with backend `ConstraintSignatureRequest`):

```ts
interface ConstraintSignaturePayload {
  signer: string;           // hex address
  max_single: number;
  min_diversification: number;
  max_volatility: number;
  min_liquidity: number;
  signature_r: string;      // hex
  signature_s: string;      // hex
  timestamp: number;
}
```

- **Implementation**:  
  - `POST` to `config.backendUrl + '/api/v1/risk-engine/orchestrate-allocation'`.  
  - Body:  
    `{ jediswap_metrics: payload.jediswapMetrics, ekubo_metrics: payload.ekuboMetrics, constraint_signature: payload.constraintSignature ?? null }`  
  - Backend will: generate proof (or use existing job if we add that later), build 24-element calldata including `model_version` and `constraint_signature`, submit to RiskEngine, return decision + `tx_hash`.  
  - Parse response into existing `AllocationDecision` and return.

**2) Where to call it**

- **Demo page**:  
  - Add a section “One-shot orchestrate (with optional user constraints)”.  
  - Form: JediSwap/Ekubo metrics (reuse existing inputs) + optional “User constraints” (max_single, min_diversification, etc.) + optional “Sign constraints” (future: sign with wallet and set signer + signature_r/s).  
  - Button “Orchestrate allocation” → `orchestrateAllocation({ jediswapMetrics, ekuboMetrics, constraintSignature: signedOrNull })`.  
  - Show `tx_hash`, decision, and any revert message (“DAO constraints violated”, etc.).

- **Dashboard**:  
  - Optional “Advanced” action: “Execute with custom metrics and constraints” that opens a modal/form calling `orchestrateAllocation` with the same shape.  
  - Keeps existing “Propose → Execute” flow as default; this is for power users who want one-shot with custom constraints.

**3) Backend**

- No change needed: `orchestrate-allocation` already accepts `constraint_signature` and builds the 9-parameter calldata. Frontend only needs to pass it through.

**4) Optional: Reuse proof**

- Today, `orchestrate-allocation` always generates a new proof. If we later add “execute with existing proof_job_id but custom constraint_signature”, backend could accept `proof_job_id` + `constraint_signature` and reuse the stored proof while overriding the constraint part of calldata. That would be a small backend extension; the frontend flow above stays the same, just with an optional `proof_job_id` in the payload.

---

## 6. Summary

- **What the contract upgrade did**: It **put the agent on-chain** by making RiskEngine the on-chain orchestrator that verifies proofs (STEP 0), enforces approved model version (STEP 0.5), and accepts user-signed constraints (STEP 0.6), with optional permissionless mode.  
- **Frontend (b)**: Add `orchestrateAllocation(metrics, constraintSignature?)` to the hook and call it from the Demo (and optionally Dashboard) so users can trigger **orchestrate-allocation** with full payload, including optional **constraint_signature**, matching what the on-chain agent already supports.
