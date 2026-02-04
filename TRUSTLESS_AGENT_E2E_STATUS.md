# Trustless On-Chain Agent - E2E Testing Status

**Date**: January 28, 2026  
**Milestone**: From Verifiable AI → Trustless On-Chain Agent

---

## The Fundamental Shift

### Before: Verifiable AI Infrastructure
- **Trust model**: Owner-controlled execution
- **Verification**: Proofs verified, but only owner can execute
- **Model**: Off-chain, no on-chain enforcement
- **User constraints**: Not represented on-chain

### After: Trustless On-Chain Agent (v4)
- **Trust model**: Permissionless execution (when enabled)
- **Verification**: Proof + Model + User Constraints all on-chain
- **Model**: On-chain version enforcement (STEP 0.5)
- **User constraints**: On-chain attestation (STEP 0.6)
- **Gate**: Proof + approved model + (optional) signed constraints

**Contract Address**: `0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab`

---

## What Was Upgraded (Last 24 Hours)

### 1. RiskEngine v4 Contract
**New Parameters (9-parameter interface)**:
- `model_version` (felt252) - Hash of the model that produced the proof
- `constraint_signature` (struct) - User-signed constraints with ECDSA signature

**New Logic**:
- **STEP 0.5**: Verify `model_version` in `approved_model_versions` map; revert if unapproved (unless 0 for legacy)
- **STEP 0.6**: Accept and attest `constraint_signature`; if `signer ≠ 0`, record that user constraints were supplied
- **Permissionless mode**: When enabled, ANY caller can execute with valid proof + approved model

### 2. Backend Integration
- Detects 9-input ABI automatically
- Constructs 24-element calldata: 10 (metrics) + 5 (proof) + 9 (agent)
- Gets `model_version` from ModelService
- Accepts optional `constraint_signature` in orchestrate-allocation API

### 3. Contract Wiring
- StrategyRouter updated to point to RiskEngine v4 (TX `0x07c14de...`)
- Model hash `3405732...` approved in contract (TX `0x03b7e994...`)

---

## Infrastructure Fixes Completed ✅

| Fix | Status | Evidence |
|-----|--------|----------|
| RPC failover (public Sepolia) | ✅ | `backend/app/utils/rpc.py` |
| Port alignment (8001) | ✅ | `backend/app/config.py`, `frontend/src/lib/config.ts` |
| Backend uses correct RiskEngine v4 | ✅ | `.env.sepolia`, `backend/.env` updated |
| StrategyRouter points to RiskEngine v4 | ✅ | TX `0x07c14de11715ec6dbaa0fbb86cad71312bb75828b67f7442eb5af675c6638355` |
| Script env loading from repo root | ✅ | `scripts/set_strategy_router_risk_engine.py` |
| Documentation updated | ✅ | `integration_tests/dev_log.md`, status docs |

---

## E2E Test Suite Status

### Test Suite Created

**Files**:
- `test_e2e_dao_pass.py` - DAO constraints PASS cases (41/59 allocation)
- `test_e2e_dao_fail.py` - DAO constraints FAIL cases (9/91, 7/93 allocations)
- `find_safe_allocation_metrics.py` - Helper to calculate allocations from metrics

**DAO Constraints** (from on-chain):
- max_single: 6000 (60%)
- min_diversification: 2 protocols
- min per protocol: 1000 (10%)

**On-Chain APYs**:
- JediSwap: 850 bp (8.5%)
- Ekubo: 1210 bp (12.1%)

**Challenge**: APY difference makes it hard to find allocations between 40-60%. Equal metrics produce 41/59 (PASS). Small risk differences push allocation >60% or <40%.

### Test Cases Designed

**DAO PASS Tests**:
1. Equal metrics → 41.3% / 58.7% (PASS)
2. Slight variation → ~42% / 58% (PASS)

**DAO FAIL Tests**:
1. Jedi extreme risk → 8.6% / 91.4% (FAIL - Ekubo >60%)
2. Jedi ultra risk → 6.9% / 93.1% (FAIL - Ekubo >60%)

**Model Version Tests** (to be created):
1. Approved model hash → PASS
2. Legacy (model_version=0) → PASS
3. Unapproved model hash → FAIL (revert code 3)

**Constraint Signature Tests** (to be created):
1. Zero signature (signer=0) → PASS
2. Provided signature (signer≠0) → PASS + verify event

**Full Flow Test** (to be created):
- Propose-from-market → Execute with PASS allocation
- Verify enhanced events (proof_facts, constraint_signer, model_version)

---

## Execution Notes

### Proof Generation Performance
- **Time**: ~3-5 minutes per proof
- **Issue**: Stone prover is slow; Integrity registration adds latency
- **Impact**: Each E2E test takes 3-5 min; full suite (6-8 tests) = 20-40 min

### Test Execution Strategy
1. Run DAO PASS test (2 proofs, ~6-10 min total)
2. Run DAO FAIL test (2 proofs, ~6-10 min total)
3. Run Model Version tests (reuse proofs or generate 2-3 new)
4. Run Constraint Signature tests (reuse proofs)
5. Run Full Flow + Event Verification

**Total estimated time**: 30-60 minutes for complete test suite execution.

---

## What Needs to Be Run

### Immediate Tests (proof generation required)

1. **DAO PASS Test**:
   ```bash
   cd /opt/obsqra.starknet
   python3 test_e2e_dao_pass.py
   ```
   Expected: 2 successful transactions with allocations 41/59 and ~42/58.

2. **DAO FAIL Test**:
   ```bash
   python3 test_e2e_dao_fail.py
   ```
   Expected: 2 reverts with "DAO constraints violated".

### Model Version Tests (to be created)

Create `test_e2e_model_version.py`:
- Test 1: Use current approved model → expect PASS
- Test 2: Override model_version=0 in backend → expect PASS (legacy mode)
- Test 3: Use fake unapproved model hash → expect FAIL with revert code 3

### Constraint Signature Tests (to be created)

Create `test_e2e_constraint_signature.py`:
- Test 1: Zero signature (current default) → expect PASS
- Test 2: Provide signature with signer≠0 → expect PASS, verify event has constraint_signer

### Event Verification (to be created)

Create `test_e2e_events.py`:
- Query successful TX receipts from DAO PASS tests
- Parse `AllocationExecuted` event
- Verify enhanced fields:
  - `jediswap_proof_fact`
  - `ekubo_proof_fact`
  - `constraint_signer`
  - `model_version`

---

## Current Blocker

**Backend/Stone Prover Hung**: Orchestrate-allocation requests are timing out (>4 min). Backend process may be stuck in proof generation.

**Resolution**:
1. Restart backend
2. Increase timeout in tests to 360s (6 min)
3. Consider adding progress logging to stone prover service
4. Optionally: create "fast" tests that skip proof generation (test orchestration logic only)

---

## Success Criteria for Trustless Agent Verification

1. ✅ Infrastructure working (RPC, ports, wiring)
2. ⏳ DAO constraints: PASS cases execute successfully on-chain
3. ⏳ DAO constraints: FAIL cases revert correctly with "DAO constraints violated"
4. ⏳ Model version: Approved passes, unapproved fails with code 3
5. ⏳ Constraint signatures: Zero and provided both work
6. ⏳ Events: Enhanced fields present in successful TXs
7. ⏳ Documentation: Comprehensive test results logged

---

## Next Steps

1. **Restart backend** (currently hung)
2. **Run DAO PASS test** - verify allocations within limits execute successfully
3. **Run DAO FAIL test** - verify constraint enforcement works
4. **Create and run** model version + constraint signature tests
5. **Verify events** from successful TXs
6. **Document results** in `TRUSTLESS_AGENT_VERIFICATION_COMPLETE.md`

---

## Files Created

**Test Files**:
- `test_e2e_dao_pass.py` - DAO constraint PASS tests
- `test_e2e_dao_fail.py` - DAO constraint FAIL tests
- `find_safe_allocation_metrics.py` - Helper to find safe allocations

**Documentation**:
- `COMPREHENSIVE_E2E_TEST_PLAN.md` - Full test plan
- `TRUSTLESS_AGENT_E2E_STATUS.md` - This file

**Status**: Infrastructure fixed ✅, test suite created ✅, execution in progress ⏳
