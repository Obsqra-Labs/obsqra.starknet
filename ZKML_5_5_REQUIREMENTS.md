# Requirements for 5/5 zkML Maturity

**Current Status**: 4/5 ✅ (On-chain proof verification enforced)  
**Target**: 5/5 (Full zkML product with provenance & UX)

---

## What We Have (4/5)

✅ **On-chain proof verification gate**
- RiskEngine v4 verifies proofs before execution
- SHARP fact registry integration
- Risk score matching assertions
- Contract-level enforcement

---

## What's Needed for 5/5

### 1. Model Provenance & Upgradeability

**Requirements**:
- Model hash committed on-chain
- Versioned model registry
- Model upgrade function (with governance)
- Track which model version was used for each proof

**Implementation**:
```cairo
// In RiskEngine contract
struct ModelVersion {
    version: felt252,
    model_hash: felt252,
    deployed_at: u64,
    is_active: bool,
}

#[storage]
struct Storage {
    model_versions: Map<felt252, ModelVersion>,
    current_version: felt252,
}

fn upgrade_model(
    ref self: ContractState,
    new_version: felt252,
    new_model_hash: felt252,
) {
    // Only owner can upgrade
    // Deactivate old version
    // Activate new version
    // Emit event
}
```

**Backend Changes**:
- Store model version with each proof
- Pass model version/hash to contract
- Track model upgrades in database

---

### 2. UX Transparency

**Requirements**:
- Display proof hash on frontend
- Display model hash/version
- Show input commitments (metrics hash)
- Show verification status clearly
- Display proof source (Stone vs LuminAIR)

**Frontend Component**:
```tsx
<ZkmlStatusPanel>
  - Proof Hash: 0x...
  - Model Version: v1.2.3
  - Model Hash: 0x...
  - Input Hash: 0x...
  - Verification: ✅ Verified on-chain
  - Proof Source: Stone Prover
  - Generation Time: 2.3s
</ZkmlStatusPanel>
```

**Backend API**:
- Return proof metadata in allocation responses
- Include model version/hash
- Include verification status

---

### 3. Complete Audit Trail

**Requirements**:
- Every allocation decision links to:
  - Proof fact hash
  - Model version used
  - Input metrics hash
  - Verification status
  - Timestamp

**Contract Events**:
```cairo
#[derive(Drop, starknet::Event)]
struct AllocationExecuted {
    decision_id: felt252,
    proof_fact: felt252,
    model_version: felt252,
    model_hash: felt252,
    input_hash: felt252,
    verified: bool,
    timestamp: u64,
}
```

---

## Implementation Plan

### Phase 1: Model Versioning (2-3 days)
1. Add model version storage to RiskEngine
2. Add upgrade_model function (owner-only)
3. Update propose_and_execute_allocation to accept model version
4. Store model version with each decision
5. Emit model version in events

### Phase 2: Backend Integration (1 day)
1. Track model version in ProofJob model
2. Pass model version to contract
3. Store model hash in database
4. API returns model metadata

### Phase 3: Frontend UX (1-2 days)
1. Create ZkmlStatusPanel component
2. Display proof/model metadata
3. Show verification status
4. Add to dashboard

### Phase 4: Testing (1 day)
1. Test model upgrade flow
2. Test provenance tracking
3. Test UX display
4. End-to-end verification

---

## Success Criteria

✅ **5/5 Achievement**:
- [x] All 4/5 criteria met (proof verification)
- [ ] Model versioning system works
- [ ] Model provenance tracked on-chain
- [ ] UX displays all zkML metadata
- [ ] Users can see proof/model/input hashes
- [ ] Complete audit trail available

---

## Estimated Timeline

**Total**: 5-7 days

- Model versioning: 2-3 days
- Backend integration: 1 day
- Frontend UX: 1-2 days
- Testing: 1 day

---

**Status**: Ready to implement after 4/5 is fully tested and working.
