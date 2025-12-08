# Zero-Knowledge Machine Learning Implementation Roadmap

## Objective

Implement verifiable AI computation where the risk scoring model runs off-chain but generates zero-knowledge proofs that are verified on-chain via Starknet's SHARP.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Off-Chain Layer                        │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐               │
│  │ Python ML    │──────│ Giza Agent   │               │
│  │ Model        │      │ (Transpiler) │               │
│  └──────────────┘      └──────────────┘               │
│         │                      │                        │
│         └──────────┬───────────┘                        │
│                    ▼                                     │
│         ┌──────────────────────┐                        │
│         │  Cairo ML Model      │                        │
│         │  (Provable Code)     │                        │
│         └──────────────────────┘                        │
│                    │                                     │
│                    ▼                                     │
│         ┌──────────────────────┐                        │
│         │  Proof Generation    │                        │
│         │  (Stone Prover)      │                        │
│         └──────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Starknet L2                             │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           SHARP Verifier                         │  │
│  │  - Verifies proof validity                       │  │
│  │  - Proof fact registered                         │  │
│  └──────────────────────────────────────────────────┘  │
│                     │                                    │
│                     ▼                                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │         RiskEngine Contract                      │  │
│  │  - Checks proof exists                           │  │
│  │  - Validates decision                            │  │
│  │  - Executes allocation                           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Cairo Math Foundation (4-6 hours)

**Goal**: Implement fixed-point math library for Cairo to enable ML computations

**Tasks**:
1. Fixed-point arithmetic library
   - Multiplication/division with scaling
   - Addition/subtraction
   - Comparison operators
   - Overflow protection

2. Statistical functions
   - Mean calculation
   - Standard deviation
   - Weighted averages
   - Normalization

3. Test suite
   - Unit tests for each operation
   - Edge case validation
   - Gas optimization

**Deliverables**:
- `contracts/src/lib/fixed_point.cairo`
- `contracts/src/lib/stats.cairo`
- `contracts/tests/test_math.cairo`

### Phase 2: Risk Scoring Model in Cairo (6-8 hours)

**Goal**: Reimplement risk scoring logic in provable Cairo code

**Current Python Model**:
```python
def calculate_risk_score(metrics):
    # Utilization component (0-35 points)
    util_score = (metrics.utilization / 10000) * 35
    
    # Volatility component (0-30 points)
    vol_score = (metrics.volatility / 10000) * 30
    
    # Liquidity component (0-15 points)
    liq_score = (3 - metrics.liquidity) * 5
    
    # Audit component (0-20 points)
    audit_score = (100 - metrics.audit_score) / 5
    
    # Protocol age penalty (max 10 points)
    age_penalty = max(0, 10 - (metrics.age_days / 100))
    
    return min(95, max(5, util_score + vol_score + liq_score + audit_score + age_penalty))
```

**Cairo Implementation**:
- Translate to fixed-point arithmetic
- Ensure deterministic computation
- Match Python output exactly
- Optimize for proof generation

**Deliverables**:
- `contracts/src/ml/risk_model.cairo`
- `contracts/tests/test_risk_model.cairo`
- Cross-validation script (Python vs Cairo)

### Phase 3: Giza Integration (8-12 hours)

**Goal**: Set up Giza toolchain for proof generation

**Tasks**:
1. Install Giza CLI and dependencies
2. Transpile Cairo model to Giza format
3. Configure proof generation parameters
4. Test proof generation locally
5. Deploy to Giza proving service

**Giza Workflow**:
```bash
# Install Giza
pip install giza-cli

# Transpile Cairo to Giza format
giza transpile contracts/src/ml/risk_model.cairo

# Generate proof
giza prove --model risk_model --input metrics.json

# Verify proof
giza verify --proof proof.json
```

**Deliverables**:
- Giza configuration files
- Proof generation scripts
- Local testing infrastructure
- Documentation for Giza setup

### Phase 4: SHARP Integration (6-8 hours)

**Goal**: Register proofs with Starknet's SHARP verifier

**Tasks**:
1. Understand SHARP proof submission
2. Create proof registration service
3. Monitor proof verification status
4. Handle proof facts in contracts

**SHARP Flow**:
```
1. Generate proof off-chain (Giza/Stone)
2. Submit proof to SHARP
3. Wait for verification (10-60 minutes)
4. Proof fact registered on-chain
5. Contract checks fact exists
6. Decision executed if proof valid
```

**Contract Changes**:
```cairo
#[storage]
struct Storage {
    proof_fact_registry: ContractAddress,
    verified_decisions: LegacyMap<felt252, bool>,
}

fn execute_with_proof(
    decision_id: felt252,
    proof_fact: felt252,
    allocation: AllocationDecision
) {
    // Check proof exists in SHARP registry
    let verified = self.proof_fact_registry.read()
        .is_verified(proof_fact);
    assert(verified, 'Proof not verified');
    
    // Execute decision
    self.execute_allocation(allocation);
}
```

**Deliverables**:
- Updated RiskEngine contract with proof verification
- Proof submission service
- SHARP monitoring dashboard
- Integration tests

### Phase 5: Backend Proof Pipeline (4-6 hours)

**Goal**: Integrate proof generation into backend orchestration

**Backend Flow**:
```
1. Receive allocation request
2. Calculate risk scores
3. Generate proof of computation
4. Submit proof to SHARP
5. Wait for verification
6. Execute on-chain with proof fact
7. Return decision + proof hash
```

**API Changes**:
```python
@router.post("/orchestrate-with-proof")
async def orchestrate_with_proof(request: OrchestrationRequest):
    # Calculate risk scores
    jediswap_risk = await calculate_risk_with_proof(
        request.jediswap_metrics
    )
    
    # Generate proof
    proof = await generate_proof(
        model="risk_scoring",
        inputs={
            "jediswap": request.jediswap_metrics,
            "ekubo": request.ekubo_metrics
        }
    )
    
    # Submit to SHARP
    proof_fact = await submit_to_sharp(proof)
    
    # Wait for verification
    await wait_for_sharp_verification(proof_fact)
    
    # Execute with proof
    result = await execute_allocation_with_proof(
        proof_fact=proof_fact,
        jediswap_pct=jediswap_pct,
        ekubo_pct=ekubo_pct
    )
    
    return result
```

**Deliverables**:
- Updated backend API with proof generation
- Proof caching layer
- Async proof monitoring
- Error handling for proof failures

### Phase 6: Frontend Proof Display (2-4 hours)

**Goal**: Show proof verification status in UI

**UI Components**:
- Proof generation progress indicator
- SHARP verification status
- Proof hash display
- Verification timestamp
- Link to SHARP explorer

**Update AIProposalDisplay**:
```typescript
interface ProofStatus {
  status: 'generating' | 'submitted' | 'verified' | 'failed';
  proof_hash: string;
  sharp_tx: string;
  verification_time: number;
}
```

**Deliverables**:
- Updated AIProposalDisplay component
- Proof status polling
- SHARP explorer links
- User-friendly proof explanations

## Testing Strategy

### Unit Tests
- Cairo math library functions
- Risk model computation
- Proof generation (mocked)
- Contract proof verification

### Integration Tests
- End-to-end proof generation
- SHARP submission and verification
- Backend orchestration with proofs
- Frontend proof status display

### Cross-Validation
- Python model vs Cairo model
- Known inputs with expected outputs
- Edge cases and boundary conditions
- Gas cost analysis

## Timeline Estimate

| Phase | Hours | Status |
|-------|-------|--------|
| 1. Cairo Math Foundation | 4-6 | Not Started |
| 2. Risk Model in Cairo | 6-8 | Not Started |
| 3. Giza Integration | 8-12 | Not Started |
| 4. SHARP Integration | 6-8 | Not Started |
| 5. Backend Proof Pipeline | 4-6 | Not Started |
| 6. Frontend Proof Display | 2-4 | Not Started |
| **Total** | **30-44** | **0% Complete** |

## Dependencies

### Required Tools
- Giza CLI (pip install giza-cli)
- Stone Prover (for local testing)
- SHARP access (testnet available)
- Cairo 2.0 compiler

### External Services
- Giza proving service
- SHARP verifier contract on Starknet
- RPC endpoints for proof submission

### Knowledge Requirements
- Fixed-point arithmetic
- Zero-knowledge proof systems
- SHARP architecture
- Cairo 2.0 features

## Success Criteria

1. **Correctness**: Cairo model outputs match Python model exactly
2. **Provability**: All computations generate valid proofs
3. **Verifiability**: SHARP successfully verifies all proofs
4. **Performance**: Proof generation < 5 minutes
5. **Integration**: Seamless backend-to-SHARP flow
6. **Transparency**: Frontend clearly shows proof status

## Risk Mitigation

### Proof Generation Failures
- Implement retry logic
- Cache successful proofs
- Fallback to non-proof mode (with warning)

### SHARP Delays
- Async processing with status updates
- Queue management
- User notifications

### Model Drift
- Periodic validation against Python model
- Alert on significant deviations
- Version control for models

## Next Immediate Steps

1. Set up Cairo math library structure
2. Implement fixed-point arithmetic
3. Port risk scoring logic to Cairo
4. Create cross-validation tests
5. Document Cairo model behavior

---

**Ready to begin Phase 1: Cairo Math Foundation**

