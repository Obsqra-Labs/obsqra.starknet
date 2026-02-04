# Contract Upgrade & Frontend Integration – Status and Audit

**Date**: 2026-01-28  
**Scope**: RiskEngine v4 with on-chain agent, frontend integration, tests, fuzz/audit and E2E.

---

## 1. Where We Are

### Contract Upgrade (RiskEngine v4)

| Item | Status | Notes |
|------|--------|------|
| **Deployed contract** | OK | `0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab` (Sepolia) |
| **9-parameter interface** | OK | `propose_and_execute_allocation` with `model_version` + `ConstraintSignature` |
| **Proof gate (STEP 0)** | OK | Fact registry verification; reverts if proofs invalid |
| **Model version (STEP 0.5)** | OK | Check against `approved_model_versions`; model hash approved |
| **Constraint signature (STEP 0.6)** | OK | Accepts user-signed constraints; `signer=0` = not provided |
| **Permissionless mode** | OK | Configurable; when on, proof verification is the gate |
| **DAO constraint check** | OK | Reverts with "DAO constraints violated" when allocation violates policy |

### Backend Integration

| Item | Status | Notes |
|------|--------|------|
| **ABI detection** | OK | Detects 9 inputs; builds 24-element calldata |
| **Calldata construction** | OK | 10 metrics + 5 proof + 9 on-chain agent (model_version + ConstraintSignature) |
| **Model version** | OK | From model service; 0 if unavailable |
| **Constraint signature** | OK | From request or zeroed (signer=0) |
| **orchestrate-allocation** | OK | One-shot proof + execute; used by tests and API |
| **execute-allocation** | OK | Execute using existing `proof_job_id` |

### Frontend Integration

| Item | Status | Notes |
|------|--------|------|
| **Propose (propose-allocation / propose-from-market)** | OK | Demo + Dashboard; no `constraint_signature` in body yet |
| **Execute (execute-allocation)** | OK | Dashboard calls with `proof_job_id` |
| **Demo generate-proof** | OK | Sends `constraint_signature` to **demo** endpoint only |
| **Risk-engine orchestrate-allocation from UI** | Gap | No UI path that POSTs full payload (including `constraint_signature`) to `/api/v1/risk-engine/orchestrate-allocation` |
| **Display tx_hash / revert errors** | OK | Hook and UI handle `tx_hash` and errors |

**Summary**: Backend and contract are aligned with v4. Frontend uses propose then execute and demo proof generation; the only missing piece is a UI that calls **orchestrate-allocation** with full payload (including optional `constraint_signature`).

---

## 2. How Tests Went

### E2E / Step 6

| Test | Result | Notes |
|------|--------|------|
| **Step 6 (on-chain execution)** | PASS | `test_step6_only.py`: proposal created, orchestration with 9 params, tx submitted; revert = constraint enforcement |
| **Full 6-step E2E** | Partial | Step 1, 5, 6 pass; Step 2 (proof generation) often times out; 3–4 skipped when 2 fails |
| **ABI detection** | PASS | Backend correctly detects 9-input interface |
| **Calldata** | PASS | 24 elements; model_version and ConstraintSignature included |
| **Revert handling** | PASS | "DAO constraints violated" treated as expected contract behavior |

### Contract Unit Tests (snforge)

- `test_calculate_risk_score_*` (low/medium/high): PASS  
- `test_calculate_allocation_*` (balanced, prefer_low_risk): PASS  
- `test_verify_constraints_*` (pass, fail_max_single, fail_min_protocols): PASS  
- `test_age_factor_rewards_maturity`: PASS  

**Gap**: No unit test for `propose_and_execute_allocation` (needs mocks for StrategyRouter, DAO, fact registry, proof hashes). Current tests cover pure logic (risk, allocation, constraints).

---

## 3. Deeper Fuzz Testing We Can Do

### Contract (Cairo / snforge)

1. **Metric ranges**: Fuzz `ProtocolMetrics` (utilization, volatility, liquidity, audit_score, age_days) in valid and boundary ranges. Assert risk score in [5, 95]; allocation sums to 10000; no panic.
2. **Constraint boundary**: Fuzz allocation triple and constraint params (max_single, min_diversification). Assert `verify_constraints` pass/fail.
3. **Division / overflow**: Fuzz inputs to `calculate_risk_score` and `calculate_allocation` (e.g. very large values, zero where allowed). Ensure no overflow/underflow and no division by zero.
4. **propose_and_execute_allocation**: Once mocks exist, fuzz metrics + proof facts + expected scores + model_version + constraint_signature (e.g. signer=0 vs non-zero, extreme values). Assert either success or known revert reasons (proof, model, DAO).

### Backend (Python)

1. **Calldata construction**: Random but valid metrics + optional constraint_signature; call internal calldata builder; assert length 24 and types for v4.
2. **API payloads**: Fuzz `orchestrate-allocation` and `execute-allocation` bodies (missing fields, wrong types, huge numbers). Assert 4xx and clear error messages, no 500 on malformed input.

**Suggested next step**: Add a small fuzz target in `contracts/tests/` for `calculate_risk_score` and `verify_constraints` (no external deps), then run with snforge or a Cairo fuzzer if available.

---

## 4. Audit Snapshot (Internal)

Using `docs/audit/SMART_CONTRACT_AUDIT_CHECKLIST.md` and current code:

- **Access control**: RiskEngine owner/permissionless mode; StrategyRouter caller check. Model version and constraint signature are data checks, not substitute for owner/permissionless policy.
- **Input validation**: Metrics used in fixed-point style math; overflow/division guarded in current logic; fuzz will help. Proof facts / fact registry checked in STEP 0; invalid proof reverts. Model version STEP 0.5; unapproved and non-zero reverts. Constraint signature STEP 0.6 accepts signer=0; non-zero signer accepted (crypto verification can be tightened later).
- **Proof verification**: STEP 0 verifies both proof facts against fact registry; scores must match on-chain calculation (STEP 1–2). No "demo mode" or bypass when contract is v4.
- **Invariants**: Allocation (2-protocol) sums to 10000 basis points; risk score clamped to [5, 95]; DAO constraints enforced before StrategyRouter call.
- **Known gaps**: No formal verification of arithmetic (overflow/underflow) or of proof-gate logic. Constraint signature: on-chain we only check signer != 0; no ECDSA/curve verification in contract yet. StrategyRouter / DAO / FactRegistry are external; assumptions on their behavior are not re-verified in this doc.

---

## 5. End-to-End: How It's Working

### Happy path (current)

1. **Propose**: Frontend calls `propose-from-market` or `propose-allocation`; backend generates proof, verifies, stores ProofJob, returns proposal + `proof_job_id`.
2. **Execute**: Frontend calls `execute-allocation(proof_job_id)`; backend loads ProofJob, builds 24-element calldata (v4), submits to RiskEngine; tx accepted; if allocation violates DAO, contract reverts ("DAO constraints violated").
3. **Step 6 test**: Same flow via `orchestrate-allocation` (one-shot) with full payload; revert treated as success for "constraint enforcement" check.

### Observed behavior

- **Tx submission**: OK; backend and contract agree on 9-parameter interface.
- **Reverts**: Expected when DAO constraints are violated; UI/backend should show "DAO constraints violated" or similar.
- **Proof generation**: Can be slow; causes Step 2 timeout in full 6-step E2E; not a functional failure.

### Edge cases to keep testing

- Unapproved model_version (expect revert 3).
- Invalid or missing proof facts (expect revert 0).
- Score mismatch (expect revert 1/2).
- DAO constraint violation (expect "DAO constraints violated").
- Permissionless vs owner-only mode (caller check).

---

## 6. Summary Table

| Area | Status | Action |
|------|--------|--------|
| Contract v4 | Deployed and wired | None |
| Backend 9-param + calldata | OK | None |
| Frontend propose/execute | OK | Optional: add UI path that calls orchestrate-allocation with optional constraint_signature |
| E2E Step 6 | OK | None |
| Full 6-step E2E | Step 2 timeout | Increase timeout or optimize proof generation |
| Contract unit tests | Pure logic covered | Add tests for propose_and_execute (with mocks) |
| Fuzz | Not yet | Add fuzz for risk + constraints + calldata |
| Audit | Checklist only | Formal audit + optional formal verification later |

---

## 7. Recommended Next Steps

1. **Frontend**: Add a "One-shot orchestrate" (or "Execute with custom constraints") flow that POSTs to `orchestrate-allocation` with full metrics + optional `constraint_signature` so UI matches backend capability.
2. **Fuzz**: Implement at least one fuzz target for `calculate_risk_score` and `verify_constraints` in `contracts/tests/`.
3. **E2E**: Either increase timeout for Step 2 or add a "fast" E2E that mocks/skips proof generation and only checks Step 6.
4. **Audit**: Update audit checklist with v4 address and STEP 0.5/0.6; schedule external audit when ready.
5. **Docs**: Update `docs/audit/SMART_CONTRACT_AUDIT_CHECKLIST.md` with current RiskEngine address and 9-parameter behavior.
