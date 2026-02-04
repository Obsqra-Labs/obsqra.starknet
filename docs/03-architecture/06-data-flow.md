# Data Flow

This document details the end-to-end data flow, request-to-execution flow, event emission, state management, and error handling flows.

## End-to-End Data Flow Diagram

```mermaid
flowchart TD
    A[User Request<br/>Frontend] --> B[Backend API<br/>orchestrate-allocation]
    B --> C[1. Fetch Protocol Metrics]
    C --> C1[JediSwap Metrics<br/>utilization, volatility,<br/>liquidity, audit, age]
    C --> C2[Ekubo Metrics<br/>utilization, volatility,<br/>liquidity, audit, age]
    C1 --> D[2. Generate STARK Proof]
    C2 --> D
    D --> D1[Cairo Trace Generation]
    D --> D2[Stone Prover Execution]
    D --> D3[Proof Serialization]
    D --> D4[Fact Hash Calculation]
    D1 --> E[3. Verify Proof]
    D2 --> E
    D3 --> E
    D4 --> E
    E --> E1[Submit to Integrity Service]
    E --> E2[Register in Fact Registry]
    E --> E3[Get Verification Status]
    E1 --> F[4. Execute On-Chain]
    E2 --> F
    E3 --> F
    F --> F1[Call RiskEngine<br/>propose_and_execute_allocation]
    F1 --> F2[Contract Verifies Proof<br/>Fact Registry Query]
    F2 --> F3[Contract Calculates Risk Scores]
    F3 --> F4[Contract Validates Scores Match Proof]
    F4 --> F5[Contract Calculates Allocation]
    F5 --> F6[Contract Verifies DAO Constraints]
    F6 --> F7[Contract Calls StrategyRouter<br/>update_allocation]
    F7 --> G[5. Return Result]
    G --> G1[Allocation Decision]
    G --> G2[Proof Hash]
    G --> G3[Transaction Hash]
    G --> G4[Verification Status]
    G1 --> H[Frontend Display]
    G2 --> H
    G3 --> H
    G4 --> H
    H --> H1[Show Allocation]
    H --> H2[Display Proof Hash]
    H --> H3[Show Verification Status]
```

## Request → Proof → Verify → Execute Flow

### Phase 1: Request

**Frontend:**
```typescript
// User clicks "Orchestrate Allocation"
const response = await fetch('/api/v1/risk-engine/orchestrate-allocation', {
  method: 'POST',
  body: JSON.stringify({})
});
```

**Backend:**
```python
# Receive request
@app.post("/api/v1/risk-engine/orchestrate-allocation")
async def orchestrate_allocation(request: OrchestrationRequest):
    # Process request
```

### Phase 2: Proof Generation

**Metrics Collection:**
```python
jediswap_metrics = await get_jediswap_metrics()
ekubo_metrics = await get_ekubo_metrics()
```

**Trace Generation:**
```python
trace = generate_cairo_trace(metrics)
memory = extract_memory(trace)
public_inputs = extract_public_inputs(trace)
```

**Proof Generation:**
```python
proof = stone_prover.generate_proof_sync(
    trace=trace,
    memory=memory,
    public_inputs=public_inputs
)
fact_hash = calculate_fact_hash(proof)
```

### Phase 3: Verification

**Integrity Service:**
```python
integrity = IntegrityService(rpc_url, network="sepolia")
verified = await integrity.verify_proof_full_and_register_fact(
    verifier_config=proof.verifier_config,
    stark_proof=proof.proof_json
)
```

**Fact Registry:**
```python
# Fact hash registered in contract
fact_hash = integrity.get_verification_hash(proof_hash)
# Status: verified
```

### Phase 4: Execution

**Transaction Preparation:**
```python
calldata = [
    # Metrics
    jediswap_metrics.utilization,
    jediswap_metrics.volatility,
    # ... more metrics
    # Proof parameters
    jediswap_proof_fact,
    ekubo_proof_fact,
    expected_jediswap_score,
    expected_ekubo_score,
    fact_registry_address
]
```

**Contract Execution:**
```cairo
// RiskEngine.propose_and_execute_allocation()
// STEP 0: Verify proofs
let proofs_valid = verify_allocation_decision_with_proofs(...);
assert(proofs_valid, 0);

// STEP 1: Calculate risk scores
let jediswap_risk = calculate_risk_score(...);
let ekubo_risk = calculate_risk_score(...);

// STEP 2: Validate scores match proof
assert(jediswap_risk == expected_jediswap_score, 1);
assert(ekubo_risk == expected_ekubo_score, 2);

// STEP 3: Calculate allocation
let (jediswap_pct, ekubo_pct) = calculate_allocation(...);

// STEP 4: Verify constraints
let constraints_valid = verify_constraints(...);
assert(constraints_valid, 3);

// STEP 5: Execute
strategy_router.update_allocation(jediswap_pct, ekubo_pct);
```

## Event Emission and Indexing

### Events Emitted

**AllocationProposed:**
```cairo
event AllocationProposed {
    decision_id: felt252,
    jediswap_pct: felt252,
    ekubo_pct: felt252,
    proof_fact_hash: felt252
}
```

**AllocationExecuted:**
```cairo
event AllocationExecuted {
    decision_id: felt252,
    transaction_hash: felt252,
    model_hash: felt252
}
```

**ConstraintsValidated:**
```cairo
event ConstraintsValidated {
    decision_id: felt252,
    constraints: DAOConstraints
}
```

### Event Indexing

**Backend:**
- Listen for events via RPC
- Index events in database
- Update UI in real-time
- Maintain audit trail

**Frontend:**
- Poll for new events
- Display in dashboard
- Update allocation display
- Show transaction history

## State Management

### Contract State

**RiskEngine:**
- `decision_count`: Total decisions
- `current_decision`: Latest allocation
- `current_model_hash`: Active model
- `strategy_router`: Router address

**StrategyRouter:**
- `total_deposited`: Total funds
- `jediswap_pct`: Current allocation
- `ekubo_pct`: Current allocation
- `user_balances`: Per-user balances

**ModelRegistry:**
- `current_version`: Active version
- `model_versions`: Version map
- `version_count`: Total versions

### Backend State

**Database:**
- `ProofJob`: Proof tracking
- `AllocationDecision`: Decision history
- `PerformanceSnapshot`: Performance data

**Cache:**
- Protocol metrics (60s TTL)
- Model hashes (until change)
- Fact Registry status (30s TTL)

## Error Handling Flows

### Proof Generation Failure

```mermaid
flowchart TD
    A[Proof Generation Fails] --> B[Error Logged]
    B --> C[Retry with Backoff]
    C --> D{Still Fails?}
    D -->|Yes| E[Fallback to LuminAIR]
    D -->|Yes| F[Return Error to User]
    D -->|Yes| G[Queue for Retry]
    D -->|No| H[Success]
```

### Verification Failure

```mermaid
flowchart TD
    A[Verification Fails] --> B[Status: Failed]
    B --> C[Error Logged]
    C --> D[User Notified]
    D --> E[Can Retry Allocation]
```

### Transaction Revert

```mermaid
flowchart TD
    A[Transaction Reverts] --> B[Error Code Extracted]
    B --> C[Reason Identified]
    C --> D[User Notified]
    D --> E{Fixable?}
    E -->|Yes| F[Can Retry]
    E -->|No| G[Error Displayed]
```

### Common Error Codes

**0:** Proofs not verified
**1:** JediSwap risk score mismatch
**2:** Ekubo risk score mismatch
**3:** Constraints violated
**4:** Insufficient balance

## Data Transformation

### Input → Output Flow

**Input:**
- Protocol metrics (raw data)
- User request (allocation trigger)

**Processing:**
- Risk calculation (deterministic)
- Proof generation (cryptographic)
- Verification (on-chain)

**Output:**
- Allocation decision
- Proof hash
- Transaction hash
- Verification status

### State Transitions

**ProofJob Status:**
```mermaid
stateDiagram-v2
    [*] --> pending
    pending --> generating
    generating --> generated
    generated --> verifying
    verifying --> verified
    verified --> [*]
    generating --> failed: Error
    verifying --> failed: Error
    failed --> [*]
```

**Allocation Status:**
```mermaid
stateDiagram-v2
    [*] --> requested
    requested --> proof_generating
    proof_generating --> proof_verified
    proof_verified --> executing
    executing --> executed
    executed --> [*]
    proof_generating --> failed: Error
    executing --> failed: Error
    failed --> [*]
```

## Performance Considerations

### Timing

- **Metrics Fetch:** <1 second
- **Proof Generation:** 2-4 seconds
- **Verification:** 1-2 seconds
- **Transaction:** 5-10 seconds
- **Confirmation:** 12+ seconds
- **Total:** ~20-30 seconds

### Optimization

- **Parallel Processing:** Metrics and proof generation
- **Caching:** Protocol metrics, model hashes
- **Async Operations:** Non-blocking verification
- **Batch Operations:** Multiple proofs

## Next Steps

- **[System Overview](01-system-overview.md)** - Component architecture
- **[Smart Contracts](02-smart-contracts.md)** - Contract details
- **[Backend Services](03-backend-services.md)** - Service layer

---

**Data Flow Summary:** Complete end-to-end flow from user request through proof generation, verification, and on-chain execution, with comprehensive error handling and state management.
