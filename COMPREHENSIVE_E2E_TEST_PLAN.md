# Comprehensive E2E Test Plan - On-Chain Agent v4

## Vision: Trustless zkML Infrastructure

**What changed**: From "verifiable AI" (owner-controlled, off-chain trust) to **trustless on-chain agent** (permissionless, proof + model gates, user-signed constraints on-chain).

**Two major upgrades (last 24 hours)**:
1. **STEP 0.5**: Model version enforcement (`approved_model_versions`)
2. **STEP 0.6**: User constraint signatures (on-chain attestation)

---

## Test Strategy: Both Sides of the Coin

For each feature, test **success path** AND **failure path** to verify both sides work.

---

## 1. Infrastructure Tests ✅ (DONE)

| Test | Status | Evidence |
|------|--------|----------|
| RPC failover (public Sepolia) | ✅ Fixed | `backend/app/utils/rpc.py` |
| Port alignment (8001) | ✅ Fixed | `backend/app/config.py`, `frontend/src/lib/config.ts` |
| Backend config (RiskEngine v4) | ✅ Fixed | `.env.sepolia`, `backend/.env` |
| StrategyRouter wiring | ✅ Fixed | TX `0x07c14de...` (set_risk_engine) |

---

## 2. Contract Interface Tests

### 2a. ABI Detection & Calldata

| Test | Expected | Status |
|------|----------|--------|
| Backend detects 9 inputs | 9-input ABI with model_version + ConstraintSignature | ✅ Verified |
| Calldata has 24 elements | 10 metrics + 5 proof + 9 agent | ✅ Verified |
| Model version from ModelService | Non-zero model hash | ✅ Verified |
| Constraint signature (zero) | signer=0, all other fields=0 | ✅ Verified |

---

## 3. DAO Constraint Tests ⚠️ (NEEDS DUAL TESTS)

**DAO Constraints** (from on-chain):
- max_single: 6000 (60%)
- min_diversification: 2 protocols
- min per protocol: 1000 (10%)

### Test Cases

| # | JediSwap | Ekubo | Expected | Reason |
|---|----------|-------|----------|--------|
| 1 | 5000 (50%) | 5000 (50%) | **PASS** | Both <= 60%, both >= 10%, count=2 |
| 2 | 4000 (40%) | 6000 (60%) | **PASS** | Both <= 60%, both >= 10%, count=2 |
| 3 | 3000 (30%) | 7000 (70%) | **FAIL** | Ekubo > 60% (max_single violated) |
| 4 | 2000 (20%) | 8000 (80%) | **FAIL** | Ekubo > 60% (max_single violated) |
| 5 | 500 (5%) | 9500 (95%) | **FAIL** | Jedi < 10% (not diversified), Ekubo > 60% |

**Implementation**: Create `test_e2e_dao_constraints.py` with 5 test functions (one per case).

Each test:
1. Build metrics that produce the target allocation
2. Call `orchestrate-allocation` (generates proof + executes)
3. For PASS cases: assert tx_hash returned, verify on Starkscan
4. For FAIL cases: assert error contains "DAO constraints violated"

---

## 4. Model Version Enforcement Tests ⚠️ (NEEDS TESTS)

**Current State**: Model hash `3405732080517192222953041591819286874024339569620541729716512060767324490654` is approved.

### Test Cases

| # | Model Version | Expected | Reason |
|---|---------------|----------|--------|
| 1 | Approved hash | **PASS** | Model in approved_model_versions |
| 2 | 0 (legacy) | **PASS** | model_version=0 bypasses check |
| 3 | Unapproved hash | **FAIL** | Revert code 3 "Model version not approved" |

**Implementation**: Create `test_e2e_model_version.py` with 3 test functions.

Test 1 & 2: Use backend's current model hash and 0; expect success (may fail on DAO constraints, but not model).
Test 3: Temporarily set a fake model hash in backend, call orchestrate; expect revert code 3.

---

## 5. Constraint Signature Tests ⚠️ (NEEDS TESTS)

**Current State**: Backend sends zero signature (signer=0) by default.

### Test Cases

| # | Constraint Signature | Expected | Reason |
|---|---------------------|----------|--------|
| 1 | None (signer=0) | **PASS** | Zero signature accepted |
| 2 | Provided (signer≠0) | **PASS** | Contract records signer (no ECDSA yet) |

**Implementation**: Create `test_e2e_constraint_signature.py`.

Test 1: Call orchestrate with no constraint_signature (backend uses zero); expect pass (may fail on DAO, but not signature).
Test 2: Call orchestrate with `constraint_signature: {signer: "0x123...", ...}`; expect pass and verify AllocationExecuted event has constraint_signer.

---

## 6. Permissionless Mode Tests ⚠️ (NOT TESTED YET)

**Current State**: Permissionless mode likely OFF (owner-only).

### Test Cases

| # | Mode | Caller | Expected | Reason |
|---|------|--------|----------|--------|
| 1 | Owner-only | Backend wallet (owner) | **PASS** | Owner authorized |
| 2 | Owner-only | Random address | **FAIL** | Unauthorized |
| 3 | Permissionless | Random address + valid proof | **PASS** | Proof is gate |

**Implementation**: Check current permissionless_mode; if OFF, test 1 (done implicitly); optionally call set_permissionless_mode and test 2/3.

---

## 7. Full Proof Flow Tests ⚠️ (PARTIAL)

### 7a. Propose + Execute (2-step)

**Status**: Working but slow (~2 min proof generation).

| Step | Endpoint | Status |
|------|----------|--------|
| Propose | POST /api/v1/risk-engine/propose-from-market | ✅ Works |
| Generate proof | Backend → Stone → Integrity | ✅ Works (~100-300s) |
| Execute | POST /api/v1/risk-engine/execute-allocation | ⚠️ Tested (hits DAO/dup tx) |

**Test**: `test_e2e_propose_execute.py` with metrics that PASS DAO constraints (50/50).

### 7b. Orchestrate (1-shot)

**Status**: Backend supports; frontend doesn't call it with full payload yet.

| Step | Status |
|------|--------|
| orchestrate-allocation API | ✅ Backend supports |
| Frontend orchestrateAllocation hook | ⚠️ Not implemented |
| Demo/Dashboard UI | ⚠️ No UI path |

**Test**: `test_e2e_orchestrate.py` that calls orchestrate-allocation with various payloads (PASS and FAIL DAO cases).

---

## 8. Event Verification Tests ⚠️ (NOT DONE)

**Enhanced Events** (v4 on-chain agent):
- AllocationExecuted now includes:
  - `jediswap_proof_fact`
  - `ekubo_proof_fact`
  - `constraint_signer`
  - `model_version`

**Test**: Parse transaction receipts from successful executions; assert events have all new fields.

---

## 9. End-to-End Test Suite Structure

```
comprehensive_e2e_tests/
├── test_1_infrastructure.py          ✅ DONE (RPC, ports, wiring)
├── test_2_dao_constraints_pass.py    ⚠️ NEW (50/50, 40/60)
├── test_3_dao_constraints_fail.py    ⚠️ NEW (30/70, 20/80)
├── test_4_model_version.py           ⚠️ NEW (approved, legacy, unapproved)
├── test_5_constraint_signature.py    ⚠️ NEW (zero, provided)
├── test_6_propose_execute_flow.py    ⚠️ NEW (full 2-step with PASS allocation)
├── test_7_orchestrate_flow.py        ⚠️ NEW (1-shot with various scenarios)
├── test_8_event_verification.py      ⚠️ NEW (parse receipts, verify enhanced events)
└── test_9_permissionless_mode.py     ⚠️ OPTIONAL (if enabling permissionless)
```

---

## 10. Implementation Plan

### Phase 1: DAO Constraint Dual Tests (1 hour)
1. Create `test_2_dao_constraints_pass.py`:
   - Test case 1: Metrics that produce 50/50 allocation
   - Test case 2: Metrics that produce 40/60 allocation
   - Assert: tx_hash returned, no revert
   
2. Create `test_3_dao_constraints_fail.py`:
   - Test case 1: Metrics that produce 30/70 allocation
   - Test case 2: Metrics that produce 20/80 allocation
   - Assert: error contains "DAO constraints violated"

### Phase 2: Model Version Tests (45 min)
1. Create `test_4_model_version.py`:
   - Test approved model (current hash)
   - Test legacy model (model_version=0)
   - Test unapproved model (fake hash) - expect revert 3

### Phase 3: Constraint Signature Tests (30 min)
1. Create `test_5_constraint_signature.py`:
   - Test zero signature (signer=0)
   - Test provided signature (signer≠0, fake values for now)

### Phase 4: Full Flow Tests (1.5 hours)
1. Create `test_6_propose_execute_flow.py`:
   - Full 2-step: propose → wait for proof → execute
   - Use PASS allocation (50/50)
   - Verify events
   
2. Create `test_7_orchestrate_flow.py`:
   - 1-shot orchestrate with PASS and FAIL cases
   - Parse receipts
   
3. Create `test_8_event_verification.py`:
   - Query successful tx receipts
   - Parse AllocationExecuted event
   - Verify enhanced fields (proof_facts, constraint_signer, model_version)

### Phase 5: Documentation & Summary (30 min)
1. Update `E2E_TEST_COMPLETE.md` with all test results
2. Update `integration_tests/dev_log.md` with findings
3. Create `TRUSTLESS_AGENT_VERIFICATION.md` summary

---

## Success Criteria

1. ✅ Infrastructure (RPC, ports, wiring)
2. ⚠️ DAO constraints: Both PASS and FAIL cases tested and working as expected
3. ⚠️ Model version: Approved/legacy pass, unapproved fails with code 3
4. ⚠️ Constraint signatures: Zero and provided both work
5. ⚠️ Full proof flow: Propose → execute completes with PASS allocation
6. ⚠️ Events: Enhanced fields verified in tx receipts
7. ⚠️ Documentation: Complete test results logged

---

## Execution Order

1. DAO constraints PASS tests (verify the happy path works)
2. DAO constraints FAIL tests (verify enforcement works)
3. Model version tests (verify STEP 0.5 works)
4. Constraint signature tests (verify STEP 0.6 works)
5. Full flow + event verification
6. Document everything

**Estimated time**: 4-5 hours for full implementation and testing.

---

## Key Files to Create/Modify

**New test files**:
- `test_e2e_dao_pass.py`, `test_e2e_dao_fail.py`
- `test_e2e_model_version.py`, `test_e2e_constraint_sig.py`
- `test_e2e_full_flow.py`, `test_e2e_events.py`

**Modified**:
- `integration_tests/dev_log.md` (test results)
- `E2E_TEST_COMPLETE.md` (update with comprehensive results)

**New summary**:
- `TRUSTLESS_AGENT_VERIFICATION.md` (holistic test summary)
