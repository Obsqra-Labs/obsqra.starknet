# LuminAIR Integration Plan

## What is LuminAIR?

**Source**: https://luminair.gizatech.xyz/contribute/add-ops

**LuminAIR** is Giza's low-level framework for verifiable ML computation using STARK proofs.

### Key Features

1. **AIR (Arithmetic Intermediate Representation)**
   - Defines mathematical constraints for operations
   - Verified by STARK proofs using Stwo prover

2. **Fixed-Point Arithmetic**
   - Uses Q12 scale (2^12 = 4096) by default
   - Built-in NumerAIR library
   - Exactly what our Cairo implementation uses (Q16)

3. **Operator System**
   - Each ML operation (Add, Mul, etc.) is an AIR component
   - Generates execution traces
   - Lookup arguments for verification

4. **Graph Computation**
   - Based on Luminal framework
   - Represents ML models as directed graphs
   - Each node is a provable operation

### Architecture

```
ML Model → LuminAIR Graph → AIR Components → Execution Trace → STARK Proof → SHARP
```

## Should We Use LuminAIR?

### YES - Perfect Fit for Our Use Case

**Why**:
1. **We already have the math**: Our Cairo risk model uses fixed-point arithmetic
2. **Lower level control**: Can implement custom risk scoring operator
3. **Direct STARK proofs**: No high-level SDK needed
4. **Starknet native**: Designed for SHARP integration
5. **Production ready**: Used by Giza in production

**Our risk model as a LuminAIR operator**:
- Input: ProtocolMetrics (5 values)
- Computation: Fixed-point risk calculation
- Output: Risk score (5-95)
- Trace: Component breakdown
- Proof: STARK of correct computation

### Implementation Approach

## Option A: Implement Risk Scoring as LuminAIR Operator (Recommended)

**Pros**:
- Full control over computation
- Direct STARK proof generation
- No external API dependencies (except SHARP)
- Perfect match for our fixed-point Cairo math

**Cons**:
- More complex than high-level SDK
- Need to learn AIR constraint system
- Requires Rust for LuminAIR operators

**Effort**: 15-20 hours (but proper solution)

## Option B: Use Pre-built Giza Agents (Simpler)

**Pros**:
- Higher-level abstractions
- Less code to write
- Faster integration

**Cons**:
- Less control
- Still need Giza account/API key
- May not support custom operators

**Effort**: 5-10 hours

## Recommended Path Forward

### Phase 3B: LuminAIR Risk Operator (Current)

**1. Implement Risk Scoring Operator in Rust**

File: `luminair/operators/risk_scoring.rs`

```rust
use luminair::components::{Component, ComponentProver};
use luminair::trace::{TraceTable, TraceTableRow};

pub struct RiskScoringOperator {
    // Utilization, volatility, liquidity, audit_score, age_days
}

impl RiskScoringOperator {
    pub fn new() -> Self {
        // Initialize operator
    }
    
    pub fn calculate(&self, metrics: ProtocolMetrics) -> RiskScore {
        // Our Cairo algorithm in Rust
        // Uses fixed-point arithmetic
        
        let util_component = (metrics.utilization * 35) / 10000;
        let vol_component = (metrics.volatility * 30) / 10000;
        // ... rest of calculation
        
        RiskScore {
            total: clamp(total, 5, 95),
            components: [util_component, vol_component, ...]
        }
    }
}

// Implement AIR constraints
impl Component for RiskScoringOperator {
    fn trace_log_degree(&self) -> u32 {
        // Calculate trace size
    }
    
    fn evaluate_constraint_quotients() {
        // Define AIR constraints
    }
}
```

**2. Generate Execution Trace**

```rust
pub struct RiskTraceTable {
    rows: Vec<RiskTraceRow>
}

pub struct RiskTraceRow {
    // Input metrics
    utilization: BaseField,
    volatility: BaseField,
    liquidity: BaseField,
    audit_score: BaseField,
    age_days: BaseField,
    
    // Intermediate calculations
    util_component: BaseField,
    vol_component: BaseField,
    liq_component: BaseField,
    audit_component: BaseField,
    age_penalty: BaseField,
    
    // Output
    total_score: BaseField,
    
    // Lookup multiplicities
    input_mult: BaseField,
    output_mult: BaseField,
}
```

**3. Define AIR Constraints**

The constraints prove:
- Inputs are in valid ranges
- Each component calculated correctly
- Total equals sum of components
- Clamping applied correctly (5-95)

**4. Generate STARK Proof**

```rust
let prover = LuminairProver::new();
let trace = generate_risk_trace(metrics);
let proof = prover.prove(trace);
let proof_hash = hash(proof);
```

**5. Submit to SHARP**

```rust
let submission = sharp_client.submit(proof);
let fact_hash = submission.fact_hash;
// Wait for verification (10-60 min)
```

### Integration with Our System

**Backend Service** (`backend/app/services/luminair_service.py`):
```python
import subprocess
import json

class LuminAIRService:
    """Wrapper for LuminAIR Rust binary"""
    
    async def generate_risk_proof(self, metrics: dict) -> ProofResult:
        # Call Rust binary
        result = subprocess.run(
            ["./luminair/target/release/risk_prover"],
            input=json.dumps(metrics),
            capture_output=True,
            text=True
        )
        
        return parse_proof_result(result.stdout)
```

**Build Process**:
```bash
# Build LuminAIR with our risk operator
cd luminair
cargo build --release

# Generate proof
./target/release/risk_prover \
  --input risk_metrics.json \
  --output proof.bin

# Submit to SHARP
./target/release/sharp_submitter \
  --proof proof.bin \
  --network sepolia
```

## Timeline

### LuminAIR Implementation

| Task | Hours | Description |
|------|-------|-------------|
| Setup LuminAIR | 2 | Clone, build, understand structure |
| Implement Operator | 6-8 | Rust implementation of risk scoring |
| Define AIR Constraints | 4-6 | Mathematical constraints |
| Generate Traces | 2-3 | Execution trace generation |
| SHARP Integration | 2-3 | Submit and verify |
| Testing | 3-4 | Validate against Cairo/Python |
| **Total** | **19-26** | **Full LuminAIR integration** |

### Alternative: High-Level SDK

| Task | Hours | Description |
|------|-------|-------------|
| Get Giza API Key | 0.5 | Account setup |
| Transpile Model | 2-3 | Cairo to Giza format |
| Test Generation | 1-2 | Validate proofs |
| Backend Integration | 2-3 | API integration |
| **Total** | **5.5-8.5** | **Using existing SDK** |

## Decision Point

### For Your Project

**Question**: Do you want:

**A. Full Control (LuminAIR)**
- Implement risk scoring as custom AIR operator
- Total control over proof generation
- No external API dependencies (except SHARP)
- **Effort**: 20-26 hours
- **Result**: Production-grade verifiable AI

**B. Faster Integration (High-Level)**
- Use Giza's existing proof infrastructure
- Get API key and transpile
- Less control but faster
- **Effort**: 6-9 hours
- **Result**: Working proofs quickly

## My Recommendation

### For Grant Application / V1.2

**Use High-Level Giza SDK**:
- Faster to demonstrate
- Still uses SHARP
- Still verifiable
- Professional result

Then in V1.3/V2:
- Migrate to LuminAIR custom operator
- Optimize performance
- Reduce external dependencies

### Implementation Plan

**Now** (2 hours):
1. Get Giza API key: `python3 scripts/giza_setup_sdk.py`
2. Test proof generation
3. Verify SHARP submission works

**Phase 4** (4-6 hours):
- Integrate proofs into backend orchestration
- Add async job tracking
- Implement proof caching

**Phase 5** (2-4 hours):
- Build frontend proof display
- Show verification status
- Link to SHARP explorer

**Total to complete zkML**: 8-12 hours remaining

**V2 Enhancement**:
- Port to LuminAIR custom operator (20-26 hours)
- Full control and optimization
- Remove external dependencies

## What LuminAIR Gives Us

### Now (with SDK)
- Verifiable proofs via SHARP
- Python/TypeScript integration
- Faster development

### Later (with LuminAIR)
- Custom AIR operator
- Optimized proof generation
- No API key needed
- Full transparency

## Resources

- **LuminAIR Docs**: https://luminair.gizatech.xyz/contribute/add-ops
- **Giza Agents**: https://github.com/gizatechxyz/giza-agents
- **Stwo Prover**: https://github.com/starkware-libs/stwo
- **Our Cairo Model**: `contracts/src/ml/risk_model.cairo` (already compatible!)

---

**Decision**: Start with high-level SDK (fast), migrate to LuminAIR later (optimal)

This gives us:
- Working proofs for V1.2 (next 8-12 hours)
- Path to full optimization in V2 (20-26 hours later)
- Professional grant-ready demonstration

