# Trustless On-Chain Agent - Testing Execution Guide

## What We've Built: Verifiable → Trustless

**The Shift**: In the last 24 hours, you upgraded from **verifiable AI infrastructure** (owner-controlled, proofs verified but trust in owner) to **trustless on-chain agent** (permissionless capable, proof + model + user constraints on-chain).

---

## Contract Upgrade Summary

### RiskEngine v4 with On-Chain Agent
**Address**: `0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab`

**New Capabilities**:
1. **STEP 0.5** - Model version enforcement: Only approved model hashes can drive allocations
2. **STEP 0.6** - User constraint signatures: Accept and attest user-signed constraints on-chain
3. **Permissionless mode**: Anyone can execute with valid proof + approved model (when enabled)

**What This Means**:
- **Before**: Trust the owner to run the right model and respect user constraints
- **After**: Contract enforces model version and records user constraints; proof + model are the gate

---

## All Infrastructure Issues Fixed ✅

| Issue | Status | Fix |
|-------|--------|-----|
| RPC unavailable | ✅ | Public Sepolia fallback, 3 retries |
| Port confusion (8000 vs 8001) | ✅ | Aligned to 8001 everywhere |
| Backend using wrong RiskEngine | ✅ | Updated `.env.sepolia` and `backend/.env` |
| StrategyRouter wiring | ✅ | Called `set_risk_engine` via sncast |
| Scripts fail from repo root | ✅ | Load backend/.env before get_settings() |
| Stale documentation | ✅ | Updated all status docs |

**Current State**: All infrastructure working; ready for comprehensive E2E testing.

---

## Comprehensive Test Suite Created

### Test Files

| File | Purpose | Proof Time | Status |
|------|---------|------------|--------|
| `test_e2e_dao_pass.py` | DAO constraints PASS (41/59, 42/58) | ~6-10 min | ✅ Ready |
| `test_e2e_dao_fail.py` | DAO constraints FAIL (9/91, 7/93) | ~6-10 min | ✅ Ready |
| `test_e2e_model_version.py` | Model version enforcement (STEP 0.5) | ~3-5 min | ✅ Ready |
| `test_e2e_constraint_signature.py` | Constraint signatures (STEP 0.6) | ~6-10 min | ✅ Ready |
| `find_safe_allocation_metrics.py` | Helper: calculate allocations | 0s (no proof) | ✅ Ready |
| `RUN_ALL_E2E_TESTS.sh` | Master test runner | ~30-40 min | ✅ Ready |

---

## Test Coverage

### 1. DAO Constraint Tests

**Goal**: Verify both sides of constraint enforcement work.

**DAO Limits** (from on-chain):
- max_single: 6000 (60%)
- min_diversification: 2 protocols
- min per protocol: 1000 (10%)

**On-Chain APYs**:
- JediSwap: 850 bp (8.5%)
- Ekubo: 1210 bp (12.1%)

**PASS Cases** (`test_e2e_dao_pass.py`):
- Equal metrics → 41.3% / 58.7% allocation
- Slight variation → ~42% / 58% allocation
- Both allocations <= 60% and >= 10%
- Expected: Transaction succeeds, tx_hash returned

**FAIL Cases** (`test_e2e_dao_fail.py`):
- Jedi extreme risk → 8.6% / 91.4% allocation (Ekubo >60%)
- Jedi ultra risk → 6.9% / 93.1% allocation (Ekubo >60%)
- Expected: Transaction reverts with "DAO constraints violated"

### 2. Model Version Tests

**Goal**: Verify STEP 0.5 (model version enforcement).

**Current Approved Model**: `3405732080517192222953041591819286874024339569620541729716512060767324490654`

**Test Cases** (`test_e2e_model_version.py`):
1. Approved model hash → PASS
2. Legacy mode (model_version=0) → PASS (bypasses check) [requires backend mod to test]
3. Unapproved model → FAIL (revert code 3) [requires backend mod to test]

**Note**: Tests 2-3 require temporary backend modifications to send different model_version values. Test 1 verifies approved model works.

### 3. Constraint Signature Tests

**Goal**: Verify STEP 0.6 (constraint signature support).

**Test Cases** (`test_e2e_constraint_signature.py`):
1. Zero signature (signer=0) → PASS (current default)
2. Provided signature (signer≠0) → PASS + verify event has constraint_signer

### 4. Event Verification

**Enhanced Events** (v4):
- `AllocationExecuted` now includes:
  - `jediswap_proof_fact`
  - `ekubo_proof_fact`
  - `constraint_signer`
  - `model_version` (if added to event)

**Verification**: Parse TX receipts from successful tests; assert enhanced fields present.

---

## How to Run Tests

### Option 1: Run All Tests (30-40 minutes)

```bash
cd /opt/obsqra.starknet
./RUN_ALL_E2E_TESTS.sh
```

This runs all tests sequentially and saves results to `test_results/e2e_<timestamp>/`.

### Option 2: Run Individual Tests

```bash
# DAO PASS (2 test cases, ~6-10 min)
python3 test_e2e_dao_pass.py

# DAO FAIL (2 test cases, ~6-10 min)
python3 test_e2e_dao_fail.py

# Model Version (1 test case, ~3-5 min)
python3 test_e2e_model_version.py

# Constraint Signatures (2 test cases, ~6-10 min)
python3 test_e2e_constraint_signature.py
```

### Option 3: Quick Calculation (No Proofs)

```bash
# See what allocations various metrics produce WITHOUT generating proofs
python3 find_safe_allocation_metrics.py
```

---

## Expected Results

### Success Criteria

| Test | Expected Result | Verification |
|------|-----------------|--------------|
| DAO PASS | 2 TXs succeed, allocations 41/59 and 42/58 | Starkscan shows SUCCEEDED |
| DAO FAIL | 2 TXs revert with "DAO constraints violated" | Error message contains expected text |
| Model Version | Approved model executes successfully | TX succeeds with model_version in calldata |
| Constraint Sig | Both zero and provided signatures work | TXs succeed, event has constraint_signer |

### What This Proves

✅ **Infrastructure**: RPC, ports, wiring all working  
✅ **DAO Enforcement**: Contract correctly validates and rejects bad allocations  
✅ **Model Enforcement**: Contract checks approved model versions (STEP 0.5)  
✅ **Signature Support**: Contract accepts user constraint signatures (STEP 0.6)  
✅ **Trustless Agent**: All gates (proof + model + constraints) working on-chain  

---

## Performance Notes

### Proof Generation Time
- **Per proof**: 3-5 minutes (Stone prover + Integrity registration)
- **Per test case**: Depends on number of proofs
- **Full suite**: 30-60 minutes total

### Why It's Slow
1. Stone prover generates STARK proof (~2-3 min)
2. Integrity registration submits to Starknet (~30-60s)
3. Fact verification wait (~30-60s)

### Optimization Options (Future)
- Cache proofs for parameter combinations
- Parallel proof generation
- Pre-generate proofs for test suite
- Use faster prover setup or fewer steps

**For Now**: Accept the time cost; these are full E2E tests with real proofs.

---

## Test Execution Checklist

- [ ] Backend running on port 8001
- [ ] All test files created and executable
- [ ] DAO PASS test completed (or in progress)
- [ ] DAO FAIL test completed (or in progress)
- [ ] Model version test completed
- [ ] Constraint signature test completed
- [ ] Results documented in `test_results/`
- [ ] Final summary created

---

## Next Steps After Tests Complete

1. **Parse Event Data**: Extract `AllocationExecuted` events from successful TXs; verify enhanced fields
2. **Update Docs**: Add test results to `E2E_TEST_COMPLETE.md` and `integration_tests/dev_log.md`
3. **Create Summary**: `TRUSTLESS_AGENT_VERIFICATION_COMPLETE.md` with full results
4. **Frontend Integration** (optional): Add UI for orchestrate-allocation with constraint_signature
5. **Enable Permissionless Mode** (when ready for production): Call `set_permissionless_mode(true)` on RiskEngine

---

## Quick Reference

**Contracts**:
- RiskEngine v4: `0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab`
- StrategyRouter v3.5: `0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73`
- DAO Manager: `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856`

**DAO Constraints**:
- max_single: 6000 (60%)
- min_diversification: 2 protocols

**Approved Model**: `3405732080517192222953041591819286874024339569620541729716512060767324490654`

**Safe Metrics** (produce 41/59 allocation):
```json
{
  "utilization": 500,
  "volatility": 2000,
  "liquidity": 2,
  "audit_score": 85,
  "age_days": 365
}
```

---

**Status**: Test suite complete and ready to run. Execute with `./RUN_ALL_E2E_TESTS.sh` or run individual tests. Estimated time: 30-60 minutes for full coverage.
