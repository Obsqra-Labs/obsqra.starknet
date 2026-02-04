# Full zkML Roadmap: 3.5/5 → 5/5

**Current Status:** 3.5/5 - Real zkML-Infra, Not Yet Full zkML Product  
**Target:** 5/5 - Full zkML Product with On-Chain Verification Gate

---

## Phase 1: Reach 4/5 - On-Chain Verification Gate ⚡ **PRIORITY**

### The Critical Gap
**Current:** Backend verifies proofs, but contract doesn't enforce it  
**Needed:** Contract must verify proofs **before** executing allocations

### Implementation Steps

#### 1.1 Update `RiskEngine.propose_and_execute_allocation()` Signature

**File:** `contracts/src/risk_engine.cairo`

Add proof verification parameters:

```cairo
fn propose_and_execute_allocation(
    ref self: ContractState,
    jediswap_metrics: ProtocolMetrics,
    ekubo_metrics: ProtocolMetrics,
    // NEW: Proof verification parameters
    jediswap_proof_fact: felt252,      // SHARP fact hash for JediSwap risk proof
    ekubo_proof_fact: felt252,         // SHARP fact hash for Ekubo risk proof
    expected_jediswap_score: felt252,  // Risk score from proof
    expected_ekubo_score: felt252,     // Risk score from proof
    fact_registry_address: ContractAddress,  // SHARP fact registry
) -> AllocationDecision
```

#### 1.2 Add Proof Verification as STEP 0

**Location:** Before STEP 1 (risk score calculation)

```cairo
// ============================================
// STEP 0: VERIFY PROOFS (NEW - CRITICAL)
// ============================================
use super::super::sharp_verifier::{verify_allocation_decision_with_proofs, IFactRegistryDispatcher};

// Verify both proofs are valid in SHARP registry
let proofs_valid = verify_allocation_decision_with_proofs(
    (jediswap_metrics.utilization, jediswap_metrics.volatility, 
     jediswap_metrics.liquidity, jediswap_metrics.audit_score, 
     jediswap_metrics.age_days),
    (ekubo_metrics.utilization, ekubo_metrics.volatility,
     ekubo_metrics.liquidity, ekubo_metrics.audit_score,
     ekubo_metrics.age_days),
    jediswap_proof_fact,
    ekubo_proof_fact,
    expected_jediswap_score,
    expected_ekubo_score,
    fact_registry_address
);

assert(proofs_valid, 'Proofs not verified in SHARP registry');

// Verify on-chain calculation matches proven scores
let jediswap_risk = calculate_risk_score_internal(...);
assert(jediswap_risk == expected_jediswap_score, 'JediSwap risk score mismatch');

let ekubo_risk = calculate_risk_score_internal(...);
assert(ekubo_risk == expected_ekubo_score, 'Ekubo risk score mismatch');

// NOW proceed with allocation (existing steps 1-6)...
```

#### 1.3 Get SHARP Fact Registry Address

**File:** `contracts/src/sharp_verifier.cairo`

Update the constant with actual Sepolia address:

```cairo
// Starknet Sepolia SHARP Fact Registry
// Source: https://docs.starknet.io/documentation/architecture_and_concepts/Network_Architecture/fact-registry/
const SHARP_FACT_REGISTRY_SEPOLIA: ContractAddress = 0x...; // TODO: Get actual address
```

**How to get it:**
- Check Starknet docs for Sepolia fact registry address
- Or query from Integrity service (Herodotus uses SHARP)

#### 1.4 Update Backend to Pass Proof Facts

**File:** `backend/app/api/routes/risk_engine.py` (or wherever contract is called)

```python
# After proof generation and Integrity verification
fact_hash = await integrity_service.get_verification_hash(proof_hash)

# Call contract with proof facts
await risk_engine.propose_and_execute_allocation(
    jediswap_metrics=...,
    ekubo_metrics=...,
    jediswap_proof_fact=fact_hash,  # NEW
    ekubo_proof_fact=fact_hash,     # NEW (or separate if separate proofs)
    expected_jediswap_score=risk_scores['jediswap'],
    expected_ekubo_score=risk_scores['ekubo'],
    fact_registry_address=SHARP_FACT_REGISTRY_SEPOLIA,
)
```

#### 1.5 Update Interface

**File:** `contracts/src/risk_engine.cairo`

Update `IRiskEngine` trait to include new parameters.

---

## Phase 2: Reach 5/5 - Model Upgradeability + Provenance + UX

### 2.1 Model Upgradeability System

**Add to `RiskEngine` contract:**

```cairo
#[storage]
struct Storage {
    // ... existing storage ...
    current_model_version: felt252,
    model_versions: Map<felt252, ModelMetadata>,
}

#[derive(Drop, Copy, Serde, starknet::Store)]
struct ModelMetadata {
    version: felt252,
    model_hash: felt252,      // Hash of model code/weights
    deployed_at: u64,
    is_active: bool,
}

fn upgrade_model(
    ref self: ContractState,
    new_version: felt252,
    model_hash: felt252,
) {
    // Only owner can upgrade
    assert(self.owner.read() == get_caller_address(), 'Not owner');
    
    // Store new model version
    let metadata = ModelMetadata {
        version: new_version,
        model_hash,
        deployed_at: get_block_timestamp(),
        is_active: true,
    };
    
    // Deactivate old model
    let old_metadata = self.model_versions.read(self.current_model_version.read());
    let old_metadata_updated = ModelMetadata {
        is_active: false,
        ..old_metadata
    };
    self.model_versions.write(self.current_model_version.read(), old_metadata_updated);
    
    // Activate new model
    self.model_versions.write(new_version, metadata);
    self.current_model_version.write(new_version);
}
```

**Update proof verification to check model version:**

```cairo
fn verify_proof_with_model_version(
    proof_fact: felt252,
    model_version: felt252,
    expected_score: felt252,
    registry_address: ContractAddress
) -> bool {
    // Verify proof
    let proof_valid = verify_risk_proof(...);
    if !proof_valid {
        return false;
    }
    
    // Verify model version matches current
    assert(self.current_model_version.read() == model_version, 'Model version mismatch');
    
    true
}
```

### 2.2 Model Provenance Tracking

**Add events:**

```cairo
#[derive(Drop, starknet::Event)]
struct ModelUpgraded {
    old_version: felt252,
    new_version: felt252,
    model_hash: felt252,
    upgraded_by: ContractAddress,
    timestamp: u64,
}

#[derive(Drop, starknet::Event)]
struct ProofGenerated {
    proof_fact: felt252,
    model_version: felt252,
    model_hash: felt252,
    computation_hash: felt252,
    output_score: felt252,
    generated_at: u64,
}
```

**Store provenance in proof metadata:**

```cairo
fn record_proof_provenance(
    ref self: ContractState,
    proof_fact: felt252,
    model_version: felt252,
    computation_hash: felt252,
    output_score: felt252,
) {
    let metadata = self.model_versions.read(model_version);
    
    self.emit(ProofGenerated {
        proof_fact,
        model_version,
        model_hash: metadata.model_hash,
        computation_hash,
        output_score,
        generated_at: get_block_timestamp(),
    });
}
```

### 2.3 zkML Status Panel (UX)

**Create new component:** `frontend/src/components/ZkmlStatusPanel.tsx`

**Display:**
- ✅ Proof verification status (on-chain)
- 📊 Input commitments (metrics hash)
- 🔐 Model hash/version
- ✅ Constraint verification status
- ⚡ Proof source (Stone vs LuminAIR)
- 📈 Proof generation time
- 💰 Cost savings (Stone vs cloud)

**Example:**

```tsx
export function ZkmlStatusPanel({ proofData, allocationData }) {
  return (
    <div className="zkml-status-panel">
      <h3>🔐 zkML Verification Status</h3>
      
      <div className="status-grid">
        <StatusBadge 
          label="Proof Verified"
          status={proofData.onChainVerified ? "verified" : "pending"}
          icon="✅"
        />
        
        <StatusBadge 
          label="Model Version"
          value={proofData.modelVersion}
          icon="📊"
        />
        
        <StatusBadge 
          label="Model Hash"
          value={proofData.modelHash.slice(0, 16) + "..."}
          icon="🔐"
        />
        
        <StatusBadge 
          label="Proof Source"
          value={proofData.proofSource}
          icon="⚡"
        />
        
        <StatusBadge 
          label="Constraints"
          status={allocationData.constraintsVerified ? "verified" : "failed"}
          icon="✅"
        />
      </div>
      
      <div className="proof-details">
        <div>Input Hash: {proofData.computationHash}</div>
        <div>Generation Time: {proofData.generationTime}s</div>
        <div>Cost Savings: ${proofData.costSavings}</div>
      </div>
    </div>
  );
}
```

**Add to Dashboard:**

```tsx
// In Dashboard.tsx
import { ZkmlStatusPanel } from './ZkmlStatusPanel';

// Show when proof is generated
{latestProof && (
  <ZkmlStatusPanel 
    proofData={latestProof}
    allocationData={allocation}
  />
)}
```

---

## Implementation Priority

1. **Phase 1 (4/5)** - **CRITICAL** - Do this first
   - Add proof verification to contract
   - Update backend to pass proof facts
   - Test end-to-end
   - **Timeline:** 1-2 days

2. **Phase 2.3 (UX)** - **HIGH** - Makes it user-visible
   - Build zkML status panel
   - Add to dashboard
   - **Timeline:** 1 day

3. **Phase 2.1-2.2 (Upgradeability)** - **MEDIUM** - Nice to have
   - Model versioning system
   - Provenance tracking
   - **Timeline:** 2-3 days

---

## Testing Checklist

### Phase 1 (4/5)
- [ ] Contract rejects allocation if proof fact is invalid
- [ ] Contract rejects allocation if risk scores don't match proof
- [ ] Contract accepts allocation when proofs are valid
- [ ] Backend correctly passes proof facts to contract
- [ ] End-to-end test: Generate proof → Verify → Execute allocation

### Phase 2 (5/5)
- [ ] Model upgrade function works
- [ ] Old models are deactivated
- [ ] Proof provenance is recorded
- [ ] zkML status panel displays all data correctly
- [ ] UX shows proof verification status clearly

---

## Success Criteria

### 4/5 Achievement:
✅ Contract verifies proofs before executing  
✅ No way to execute without valid proof  
✅ Cryptographic enforcement at contract level  

### 5/5 Achievement:
✅ All 4/5 criteria met  
✅ Model upgradeability system works  
✅ Model provenance is tracked  
✅ UX clearly shows proof/inputs/constraints  

---

## Next Steps

1. **Start with Phase 1.1** - Update contract signature
2. **Get SHARP fact registry address** - Research or query Integrity service
3. **Implement STEP 0 verification** - Add proof check before allocation
4. **Update backend** - Pass proof facts to contract
5. **Test end-to-end** - Verify it works
6. **Deploy updated contract** - Deploy new RiskEngine with verification
7. **Build UX panel** - Make it visible to users

---

**Status:** Ready to implement Phase 1 (4/5) immediately.
