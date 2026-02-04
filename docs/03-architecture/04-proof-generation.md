# Proof Generation Pipeline

This document details the proof generation pipeline, including LuminAIR integration, Stone prover, proof submission to SHARP, fact hash calculation, and verification workflow.

## Proof Generation Overview

The proof generation pipeline transforms protocol metrics into cryptographically verifiable STARK proofs.

```
Protocol Metrics
    ↓
Cairo Execution Trace
    ↓
STARK Proof Generation
    ↓
Fact Hash Calculation
    ↓
SHARP Registration
    ↓
On-Chain Verification
```

## Proof Generation Pipeline

### Step 1: Input Preparation

**Protocol Metrics:**
- Utilization percentage
- Volatility score
- Liquidity score
- Audit score
- Protocol age (days)

**Format:**
```python
{
    "jediswap_metrics": {
        "utilization": 6500,  # 65%
        "volatility": 3500,   # 35%
        "liquidity": 1,
        "audit_score": 98,
        "age_days": 800
    },
    "ekubo_metrics": {
        "utilization": 5000,
        "volatility": 2500,
        "liquidity": 2,
        "audit_score": 95,
        "age_days": 600
    }
}
```

### Step 2: Cairo Trace Generation

**Process:**
1. Execute risk calculation in Cairo VM
2. Generate execution trace
3. Extract public inputs
4. Extract private inputs
5. Serialize trace data

**Trace Components:**
- **Execution Steps:** Cairo VM instruction trace
- **Memory:** State at each step
- **Public Inputs:** Metrics and risk scores
- **Private Inputs:** Internal calculations

### Step 3: STARK Proof Generation

**Stone Prover (Primary):**
- **Binary:** `cpu_air_prover`
- **Input:** Execution trace, memory, public inputs
- **Output:** STARK proof JSON
- **Time:** 2-4 seconds
- **Cost:** $0 (local)

**LuminAIR (Alternative):**
- **Language:** Rust
- **Input:** Same as Stone
- **Output:** STARK proof JSON
- **Time:** Similar to Stone
- **Fallback:** Used if Stone unavailable

### Step 4: Fact Hash Calculation

**Process:**
1. Extract public inputs from proof
2. Calculate Pedersen hash
3. Generate fact hash
4. Format for SHARP registry

**Fact Hash Format:**
- **Type:** felt252
- **Usage:** SHARP Fact Registry identifier
- **Verification:** On-chain query key

### Step 5: SHARP Registration

**Process:**
1. Submit proof to Integrity Service
2. Integrity Service verifies proof
3. Integrity Service registers fact hash
4. Fact hash stored in Fact Registry contract

**Registration:**
- **Service:** Herodotus Integrity (Atlantic API)
- **Contract:** SHARP Fact Registry
- **Status:** Verified and registered
- **Permanent:** Immutable on-chain record

## LuminAIR Integration

### Overview

LuminAIR is a Rust-based STARK prover alternative to Stone.

**Key Features:**
- Rust implementation
- Similar performance to Stone
- Fallback option
- Compatible proof format

### Integration Points

**Service:** `backend/app/services/luminair_service.py`

**Key Methods:**
- `generate_proof(metrics) -> ProofResult`
- `verify_proof(proof) -> bool`

**Usage:**
- Automatic fallback if Stone unavailable
- Manual selection via configuration
- Performance testing

## Stone Prover (Primary)

### Overview

Stone Prover is StarkWare's C++ STARK prover, used as the primary proof generation method.

**Key Features:**
- Local execution (no cloud costs)
- 2-4 second generation time
- 100% success rate (100/100 tested)
- Dynamic FRI parameter calculation

### FRI Parameters

**Dynamic Calculation:**
```
log2(last_layer) + Σ(fri_steps) = log2(n_steps) + 4
```

**Benefits:**
- Works with variable trace sizes
- No fixed parameter issues
- Automatic calculation
- Proven mathematically

### Integration

**Service:** `backend/app/services/stone_prover_service.py`

**Key Methods:**
- `generate_proof_sync(trace, memory, public_inputs) -> ProofResult`
- `calculate_fri_parameters(trace_size) -> FRIParams`
- `verify_proof_local(proof, public_inputs) -> bool`

## Proof Submission to SHARP

### Process

1. **Proof Generation:**
   - Generate STARK proof (Stone/LuminAIR)
   - Calculate fact hash
   - Serialize proof

2. **Integrity Service:**
   - Submit proof to Atlantic API
   - Verify proof format
   - Register fact hash

3. **Fact Registry:**
   - Fact hash stored on-chain
   - Verification array updated
   - Permanent record created

### SHARP Fact Registry

**Address:** `0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64`

**Interface:**
```cairo
fn get_all_verifications_for_fact_hash(
    fact_hash: felt252
) -> Span<felt252>
```

**Usage:**
- Contracts query registry
- Verify fact hash exists
- Confirm proof validity

## Fact Hash Calculation

### Method

**Pedersen Hash:**
- Hash public inputs
- Generate fact identifier
- Format as felt252

**Calculation:**
```python
fact_hash = pedersen_hash(public_inputs)
```

### Format

**Type:** felt252 (Starknet field element)
**Range:** 0 to 2^251 - 1
**Usage:** SHARP registry key

### Verification

**On-Chain:**
- Query Fact Registry
- Check if fact hash exists
- Verify array is non-empty

**Off-Chain:**
- Calculate expected hash
- Compare with registered hash
- Confirm match

## Verification Workflow

### Backend Verification

1. **Proof Generation:**
   - Generate STARK proof
   - Calculate fact hash

2. **Integrity Service:**
   - Submit to Atlantic API
   - Verify proof
   - Register fact hash

3. **Status Update:**
   - Mark as verified
   - Store fact hash
   - Update database

### On-Chain Verification

1. **Contract Call:**
   - RiskEngine receives fact hash
   - Queries Fact Registry
   - Checks verification array

2. **Verification:**
   - Array non-empty = verified
   - Array empty = not verified
   - Revert if not verified

3. **Execution:**
   - Proceed if verified
   - Revert if not verified
   - Emit events

## Performance Metrics

### Proof Generation

- **Time:** 2-4 seconds (Stone)
- **Success Rate:** 100% (100/100)
- **Size:** 400-500 KB
- **Cost:** $0 (local)

### Verification

- **Backend:** <1 second
- **On-Chain:** <1 second (query)
- **Total:** 2-4 seconds end-to-end

## Error Handling

### Proof Generation Failures

**Causes:**
- Prover unavailable
- Trace generation error
- Resource constraints

**Handling:**
- Automatic retry
- Fallback to alternative prover
- Error logging

### Verification Failures

**Causes:**
- Invalid proof format
- Fact Registry error
- Network issues

**Handling:**
- Queue for retry
- Error notification
- Status tracking

## Next Steps

- **[On-Chain Verification](05-on-chain-verification.md)** - Detailed verification architecture
- **[Data Flow](06-data-flow.md)** - End-to-end data flow
- **[Novel Features: Multi-Prover Support](../04-novel-features/04-multi-prover-support.md)** - Prover abstraction

---

**Proof Generation Summary:** Local Stone prover generates STARK proofs in 2-4 seconds with 100% success rate, registered in SHARP Fact Registry for on-chain verification.
