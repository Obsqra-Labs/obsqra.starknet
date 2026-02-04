# ZKML Status Assessment

**Date:** January 26, 2026  
**Assessment Against:** zkML Infrastructure Rubric (1-5 scale)

---

## Current Status: **3.5/5** - Real zkML-Infra, Not Yet Full zkML Product

### ✅ What We Definitely Have (3/5 - Real Proofs + Real Infra)

1. **Proof Generation Pipeline** ✅
   - Stone prover integration (local, free)
   - LuminAIR operators (Rust binaries)
   - 100% success rate (100/100 allocations)
   - Dynamic FRI parameter calculation

2. **Deterministic Model in Cairo/Rust** ✅
   - Risk scoring model in Cairo (`RiskEngine.cairo`)
   - Proof artifacts generated (trace, memory, public inputs)
   - Model computation is provable

3. **Backend Orchestration** ✅
   - Proof job tracking (`ProofJob` model)
   - Proof metadata surfaced (hash, size, generation time, source)
   - Integrity verification integration
   - Database storage with verification status

4. **Contracts That Can Consume Decision Outputs** ✅
   - `StrategyRouterV35` deployed and live
   - `RiskEngine` declared and ready
   - `DAOConstraintManager` for constraint enforcement
   - Contracts execute allocations based on decisions

5. **Deployments** ✅
   - StrategyRouterV35 live on Sepolia
   - RiskEngine declared
   - All contracts compiled and ready

---

## ❌ What's Missing for 4/5 (On-Chain Verification Gate)

### The Critical Gap: **On-Chain Verification Not Enforced**

**Current State:**
- ✅ Backend verifies proofs via Integrity service
- ✅ Backend stores `l2_verified` status in database
- ✅ Backend blocks execution if `proof_job.status != VERIFIED` (with `ALLOW_UNVERIFIED_EXECUTION` bypass)
- ❌ **Contract does NOT verify proofs before executing**

**What `RiskEngine.propose_and_execute_allocation` Does:**
1. Calculates risk scores **on-chain** (not from proof)
2. Calculates allocation **on-chain**
3. Verifies DAO constraints **on-chain**
4. Executes allocation
5. **Does NOT check if proof is verified**

**What It Should Do:**
1. Accept proof fact hashes as parameters
2. Call `verify_risk_proof()` or Integrity verifier
3. **Assert proof is valid before executing**
4. Only then proceed with allocation

**Existing Code (Not Used):**
- `sharp_verifier.cairo` has `verify_risk_proof()` function
- `verify_allocation_decision_with_proofs()` exists
- But `RiskEngine` doesn't call them

---

## Current Architecture

### Backend Flow (Has Verification Gate)
```
1. Generate proof (Stone/LuminAIR)
2. Verify via Integrity service → l2_verified = true/false
3. Store ProofJob with status = VERIFIED/FAILED
4. Execute only if status == VERIFIED
   (unless ALLOW_UNVERIFIED_EXECUTION = True)
```

### Contract Flow (Missing Verification Gate)
```
1. propose_and_execute_allocation() called
2. Calculate risk scores on-chain
3. Calculate allocation on-chain
4. Verify DAO constraints
5. Execute allocation
   ❌ NO PROOF VERIFICATION CHECK
```

---

## What's Needed for 4/5

### Option 1: Add Proof Verification to Contract (Recommended)

**Modify `RiskEngine.propose_and_execute_allocation()`:**

```cairo
fn propose_and_execute_allocation(
    ref self: ContractState,
    jediswap_metrics: ProtocolMetrics,
    ekubo_metrics: ProtocolMetrics,
    jediswap_proof_fact: felt252,  // NEW: Proof fact hash
    ekubo_proof_fact: felt252,     // NEW: Proof fact hash
    expected_jediswap_score: felt252,  // NEW: Expected from proof
    expected_ekubo_score: felt252,     // NEW: Expected from proof
    integrity_verifier: ContractAddress,  // NEW: Integrity verifier address
) -> AllocationDecision {
    // STEP 0: VERIFY PROOFS BEFORE ANYTHING ELSE
    let integrity = IIntegrityVerifierDispatcher {
        contract_address: integrity_verifier
    };
    
    // Verify JediSwap proof
    let jedi_verified = integrity.is_valid(jediswap_proof_fact);
    assert(jedi_verified, 'JediSwap proof not verified');
    
    // Verify Ekubo proof
    let ekubo_verified = integrity.is_valid(ekubo_proof_fact);
    assert(ekubo_verified, 'Ekubo proof not verified');
    
    // Verify expected scores match on-chain calculation
    let jediswap_risk = calculate_risk_score_internal(...);
    assert(jediswap_risk == expected_jediswap_score, 'Risk score mismatch');
    
    let ekubo_risk = calculate_risk_score_internal(...);
    assert(ekubo_risk == expected_ekubo_score, 'Risk score mismatch');
    
    // NOW proceed with allocation...
}
```

**Backend Changes:**
- Pass proof fact hashes and expected scores to contract
- Get fact hashes from Integrity verification
- Include in contract call calldata

### Option 2: Two-Phase Execution (Alternative)

**Phase 1: Propose (with proof verification)**
```cairo
fn propose_allocation_with_proof(
    proof_fact: felt252,
    expected_scores: (felt252, felt252),
    metrics: (ProtocolMetrics, ProtocolMetrics)
) -> (bool, AllocationDecision)
```

**Phase 2: Execute (only if verified)**
```cairo
fn execute_verified_allocation(
    proposal_id: felt252
) -> AllocationDecision
```

---

## What's Needed for 5/5

### Beyond 4/5 (The Last 0.5):

1. **Model Upgradeability** ⏳
   - Contract can accept new model versions
   - Model version tracked in proofs
   - Backward compatibility handling

2. **Transparent Model Provenance** ⏳
   - Model hash committed on-chain
   - Model version in proof metadata
   - Model source/audit trail

3. **UX That Shows Proof/Inputs/Constraints Clearly** ⏳
   - Proof verification status visible
   - Input commitments displayed
   - Constraint verification shown
   - Model hash displayed
   - **This is what the "zkML status panel" would address**

---

## Honest Rubric Assessment

### Current Score: **3.5/5**

**Breakdown:**
- ✅ 3/5: Real proofs + real infra (DONE)
- ⚠️ 0.5/5: Partial on-chain verification (backend enforces, contract doesn't)
- ❌ 0/5: Full on-chain verification gate (NOT DONE)
- ❌ 0/5: Model upgradeability + provenance + UX (NOT DONE)

### To Reach 4/5:
**Add on-chain proof verification to `RiskEngine.propose_and_execute_allocation()`**

### To Reach 5/5:
**Add:**
1. On-chain verification gate (4/5 requirement)
2. Model upgradeability system
3. Model provenance tracking
4. UX panel showing proof/inputs/constraints (the "zkML status panel")

---

## The Line That Makes It "Full zkML"

> "On-chain verification actually blocks execution unless the proof is valid"

**Current State:** ❌ **NOT TRUE**
- Backend blocks, but contract doesn't
- Contract can be called directly, bypassing backend
- No cryptographic guarantee at contract level

**What We Need:**
- Contract must verify proof before executing
- No way to execute without valid proof
- Cryptographic enforcement, not operational

---

## Recommendation

**Immediate Priority:** Add proof verification to contract to reach 4/5

**Then:** Build the "zkML status panel" UX to show:
- Proof verification status
- Input commitments (metrics hash)
- Model hash/version
- Constraint verification status
- Proof source (Stone vs LuminAIR)

This would get us to **4.5/5**, with the last 0.5 being model upgradeability and full provenance tracking.

---

**Status:** Ready to implement on-chain verification gate to reach 4/5.
