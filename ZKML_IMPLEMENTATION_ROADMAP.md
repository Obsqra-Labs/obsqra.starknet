# 🧠 zkML Layer Implementation Roadmap

## What We're Building

Converting your sklearn risk/yield calculations into **verifiable Cairo constraints** that can be proven with SHARP.

```
Current:  sklearn model → result (opaque)
Goal:     sklearn model → Cairo proof → SHARP verification
```

---

## Phase 1: Settlement (6-8 hours) - PREREQUISITE

You can't test zkML without this working:
- Frontend → calls contract
- Contract updates allocation
- Data saved on-chain
- Now you have a real system to add proofs to

**Do this first. zkML depends on it.**

---

## Phase 2: zkML Implementation (20-40 hours)

### What Is zkML?

Your backend ML model does this:
```python
def calculate_allocation(nostra_metrics, zklend_metrics, ekubo_metrics, apys):
    # Secret sauce: proprietary algorithm
    nostra_risk = predict_risk(nostra_metrics)
    zklend_risk = predict_risk(zklend_metrics)
    ekubo_risk = predict_risk(ekubo_metrics)
    
    # Returns allocation percentages
    return {
        "nostra": 45.2,
        "zklend": 32.8,
        "ekubo": 22.0
    }
```

**Problem:** Users trust you. No way to verify.

**Solution:** Create Cairo constraint system that proves:
```cairo
// Cairo contract
// "I have inputs X, Y, Z"
// "I computed allocation A, B, C"
// "The computation is correct"
// PROVE THIS WITH ZERO KNOWLEDGE
```

### The Architecture

```
┌─────────────────────────────────────────┐
│  User deposits STRK                     │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  Risk Engine        │
        │  (Backend ML)       │
        │                     │
        │  • Input: Metrics   │
        │  • Output: Alloc    │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  Cairo Constraints  │
        │                     │
        │  • Verify metrics   │
        │  • Check math       │
        │  • Prove output     │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  SHARP Verification │
        │                     │
        │  "This proof is     │
        │   valid"            │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  Frontend Display   │
        │                     │
        │  "Allocation proven │
        │   by SHARP"         │
        └─────────────────────┘
```

---

## Step 1: Understand Cairo Math (4-6 hours)

### Learn Cairo Constraints

```cairo
// Example: Prove a < b
fn verify_less_than(a: u256, b: u256) {
    // Cairo constraint: assert a < b
    assert a < b;
}

// Example: Prove sum = a + b + c
fn verify_sum(a: u256, b: u256, c: u256, sum: u256) {
    assert a + b + c == sum;
}

// Example: Prove percentage math
fn verify_percentage(part: u256, whole: u256, percent: u256) {
    // part / whole == percent / 100
    assert part * 100 == percent * whole;
}
```

### Your Risk Calculation in Cairo

```cairo
// Simplified version of your sklearn model
struct ProtocolMetrics {
    utilization: u256,
    volatility: u256,
    liquidity: u256,
    audit_score: u256,
    age_days: u256,
}

struct AllocationProof {
    nostra_pct: u256,
    zklend_pct: u256,
    ekubo_pct: u256,
    proof_inputs: Array<u256>,
}

// Main function that proves allocation
fn prove_allocation(
    nostra: ProtocolMetrics,
    zklend: ProtocolMetrics,
    ekubo: ProtocolMetrics,
    apys: Array<u256>,
) -> AllocationProof {
    // Step 1: Calculate risk scores
    let nostra_risk = calculate_risk(nostra);
    let zklend_risk = calculate_risk(zklend);
    let ekubo_risk = calculate_risk(ekubo);
    
    // Step 2: Calculate risk-adjusted scores
    let nostra_score = apys[0] * (100 - nostra_risk) / 100;
    let zklend_score = apys[1] * (100 - zklend_risk) / 100;
    let ekubo_score = apys[2] * (100 - ekubo_risk) / 100;
    
    // Step 3: Normalize to percentages
    let total = nostra_score + zklend_score + ekubo_score;
    let nostra_pct = nostra_score * 100 / total;
    let zklend_pct = zklend_score * 100 / total;
    let ekubo_pct = ekubo_score * 100 / total;
    
    // Step 4: Prove constraints
    assert nostra_pct + zklend_pct + ekubo_pct == 100;
    assert nostra_pct > 0;
    assert zklend_pct > 0;
    assert ekubo_pct > 0;
    
    // Step 5: Return allocation with proof
    return AllocationProof {
        nostra_pct,
        zklend_pct,
        ekubo_pct,
        proof_inputs: array![
            nostra_risk,
            zklend_risk,
            ekubo_risk,
            nostra_pct,
            zklend_pct,
            ekubo_pct,
        ],
    };
}

// Helper: Calculate risk score in Cairo
fn calculate_risk(metrics: ProtocolMetrics) -> u256 {
    // Simplified version of your sklearn model
    let utilization_factor = metrics.utilization / 2; // 0-50 impact
    let volatility_factor = metrics.volatility / 2;   // 0-50 impact
    let audit_benefit = metrics.audit_score / 3;       // -33 benefit
    
    let risk = utilization_factor + volatility_factor - audit_benefit;
    
    // Clamp to 0-100
    if risk < 0 { 0 }
    else if risk > 100 { 100 }
    else { risk }
}
```

---

## Step 2: Build Cairo Contracts (6-10 hours)

### File Structure
```
contracts/src/
├── risk_engine_verifiable.cairo      (NEW - Verified version)
├── allocation_proof.cairo            (NEW - Proof generation)
├── constraint_system.cairo           (NEW - Constraint helpers)
└── lib.cairo                         (Updated - exports)
```

### Create allocation_proof.cairo
```cairo
// contracts/src/allocation_proof.cairo

use array::ArrayTrait;
use core::option::OptionTrait;

#[derive(Drop, Serde)]
struct ProofInput {
    nostra_utilization: u256,
    nostra_volatility: u256,
    nostra_audit_score: u256,
    zklend_utilization: u256,
    zklend_volatility: u256,
    zklend_audit_score: u256,
    ekubo_utilization: u256,
    ekubo_volatility: u256,
    ekubo_audit_score: u256,
    nostra_apy: u256,
    zklend_apy: u256,
    ekubo_apy: u256,
}

#[derive(Drop, Serde)]
struct AllocationResult {
    nostra_pct: u256,
    zklend_pct: u256,
    ekubo_pct: u256,
}

// Main proof function
fn prove_allocation_is_valid(input: ProofInput) -> AllocationResult {
    // Calculate risk scores
    let nostra_risk = calculate_risk(
        input.nostra_utilization,
        input.nostra_volatility,
        input.nostra_audit_score,
    );
    
    let zklend_risk = calculate_risk(
        input.zklend_utilization,
        input.zklend_volatility,
        input.zklend_audit_score,
    );
    
    let ekubo_risk = calculate_risk(
        input.ekubo_utilization,
        input.ekubo_volatility,
        input.ekubo_audit_score,
    );
    
    // Calculate scores
    let nostra_score = (input.nostra_apy * (100 - nostra_risk)) / 100;
    let zklend_score = (input.zklend_apy * (100 - zklend_risk)) / 100;
    let ekubo_score = (input.ekubo_apy * (100 - ekubo_risk)) / 100;
    
    // Normalize
    let total = nostra_score + zklend_score + ekubo_score;
    let nostra_pct = (nostra_score * 100) / total;
    let zklend_pct = (zklend_score * 100) / total;
    let ekubo_pct = (ekubo_score * 100) / total;
    
    // PROVE: Percentages sum to 100
    assert nostra_pct + zklend_pct + ekubo_pct == 100;
    
    // PROVE: All positive
    assert nostra_pct > 0;
    assert zklend_pct > 0;
    assert ekubo_pct > 0;
    
    // PROVE: Risk bounds
    assert nostra_risk <= 100;
    assert zklend_risk <= 100;
    assert ekubo_risk <= 100;
    
    AllocationResult { nostra_pct, zklend_pct, ekubo_pct }
}

fn calculate_risk(utilization: u256, volatility: u256, audit_score: u256) -> u256 {
    let util_factor = utilization / 2;
    let vol_factor = volatility / 2;
    let audit_benefit = audit_score / 3;
    
    let risk = util_factor + vol_factor;
    
    if risk < audit_benefit { 0 }
    else { risk - audit_benefit }
}
```

---

## Step 3: SHARP Integration (4-6 hours)

### How SHARP Works

```
1. Generate proof
2. Send to SHARP API
3. SHARP verifies computation
4. Returns: "This computation is valid"
5. Frontend displays: "Verified by SHARP ✓"
```

### Backend Integration

```python
# backend/app/ml/sharp_integration.py

from typing import Dict, Any
import httpx
import json

class SHARPProofGenerator:
    SHARP_API = "https://api.sharp.starkware.co/positive_out"
    
    async def generate_proof(
        self,
        allocation: Dict[str, float],
        input_hash: str,
    ) -> Dict[str, Any]:
        """
        Generate SHARP proof for allocation
        """
        
        # 1. Prepare proof input
        proof_input = {
            "nostra_pct": int(allocation["nostra"] * 100),
            "zklend_pct": int(allocation["zklend"] * 100),
            "ekubo_pct": int(allocation["ekubo"] * 100),
            "input_hash": input_hash,
        }
        
        # 2. Send to SHARP API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.SHARP_API,
                json=proof_input,
                timeout=60.0,
            )
            
            if response.status_code != 200:
                raise Exception(f"SHARP error: {response.text}")
        
        proof_data = response.json()
        
        # 3. Return proof
        return {
            "proof_hash": proof_data.get("proof_hash"),
            "batch_id": proof_data.get("batch_id"),
            "verified": proof_data.get("verified", False),
            "timestamp": proof_data.get("timestamp"),
        }

# Usage in risk engine
async def calculate_allocation_with_proof(
    metrics: Dict,
    apys: Dict,
) -> Dict[str, Any]:
    # Get allocation
    allocation = optimizer.optimize_allocation(metrics, apys)
    
    # Generate SHARP proof
    sharp = SHARPProofGenerator()
    proof = await sharp.generate_proof(
        allocation,
        input_hash=hash_inputs(metrics, apys),
    )
    
    # Return allocation + proof
    return {
        "allocation": allocation,
        "proof": proof,
        "verified": proof["verified"],
    }
```

### Frontend Integration

```typescript
// frontend/src/components/ProofDisplay.tsx

interface ProofProps {
  proof: {
    hash: string;
    batchId: string;
    verified: boolean;
    timestamp: string;
  };
}

export function VerifiableAllocationDisplay({ proof }: ProofProps) {
  return (
    <div className="bg-gradient-to-br from-green-900/60 to-slate-900/80 border border-green-400/30 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
        <h3 className="text-lg font-bold text-white">
          Verifiable Allocation
        </h3>
      </div>
      
      <div className="space-y-3">
        <div>
          <p className="text-sm text-gray-400 mb-1">Proof Hash</p>
          <code className="bg-slate-800/50 p-2 rounded text-xs text-green-300 break-all">
            {proof.hash}
          </code>
        </div>
        
        <div>
          <p className="text-sm text-gray-400 mb-1">SHARP Batch ID</p>
          <code className="bg-slate-800/50 p-2 rounded text-xs text-green-300">
            {proof.batchId}
          </code>
        </div>
        
        <div className="flex items-center justify-between pt-3 border-t border-green-400/20">
          <span className="text-sm text-gray-400">Verification Status</span>
          {proof.verified ? (
            <span className="text-sm font-bold text-green-400">
              ✓ Verified by SHARP
            </span>
          ) : (
            <span className="text-sm font-bold text-yellow-400">
              ⏳ Pending...
            </span>
          )}
        </div>
      </div>
      
      <p className="text-xs text-gray-500 mt-4">
        This allocation was cryptographically proven and verified by SHARP on {proof.timestamp}
      </p>
    </div>
  );
}
```

---

## Step 4: Connect Settlement + zkML (2-4 hours)

### Updated Settlement Flow

```
User clicks "Update Allocation"
    ↓
Frontend gets allocation from backend
    ↓
Backend:
  1. Calculates allocation (sklearn)
  2. Generates Cairo proof
  3. Gets SHARP verification
  4. Stores proof hash in DB
    ↓
Frontend receives: allocation + proof + verification
    ↓
Frontend calls contract: strategy_router.update_allocation(allocation, proof_hash)
    ↓
Contract:
  1. Checks proof hash against SHARP
  2. Updates user allocation on-chain
  3. Emits event: "Allocation updated with proof"
    ↓
Frontend shows:
  "✓ Allocation verified by SHARP and confirmed on-chain"
```

---

## Timeline & Effort

### Total: 20-40 hours

**Breakdown:**
- Cairo learning (4-6 hours)
- Cairo implementation (6-10 hours)
- SHARP integration (4-6 hours)
- Settlement + zkML connection (2-4 hours)
- Testing & debugging (4-6 hours)

**With 1 developer:** 4-5 weeks  
**With 2 developers:** 2-3 weeks

---

## What You Get After This

### User Experience
```
User: "How do I know this allocation is correct?"
System: "Here's the SHARP proof: 0x1234..."
        "This allocation was cryptographically verified"
        "You can trust the math"
```

### Competitive Advantage
```
EVM chains: "We calculate allocations (trust us)"
Obsqra:     "Here's our allocation + SHARP proof (verify it)"
```

### Regulatory Advantage
```
Regulator: "How do we know your AI is honest?"
Obsqra:    "Every allocation comes with a cryptographic proof"
           "Independent verification via SHARP"
           "No backdoors possible"
```

---

## Risk & Mitigation

### Risk 1: Cairo Learning Curve
- **Mitigation**: Start with simple constraints, build up
- **Fallback**: Use existing Cairo libraries

### Risk 2: SHARP Complexity
- **Mitigation**: SHARP APIs are straightforward
- **Fallback**: Host proofs on Starknet directly

### Risk 3: Performance
- **Mitigation**: Cache proofs, don't regenerate
- **Fallback**: Batch proof generation

---

## Success Criteria

After Phase 2 (zkML), you have:

✅ User allocations come with SHARP proofs  
✅ Frontend displays proof hashes  
✅ Contract accepts allocation only with valid proof  
✅ Users can verify allocation is correct  
✅ You can claim "Verifiable AI" for real  

---

## Next Steps

1. **Settlement first** (6-8 hours)
   - Make contracts work
   - Enable real on-chain updates

2. **Then zkML** (20-40 hours)
   - Build Cairo proof system
   - Integrate SHARP verification
   - Connect to settlement

3. **Then Signup** (3 hours)
   - Users can persist data
   - Now they have something real to persist

---

## Resources

**Cairo Learning:**
- Cairo Book: https://cairo-book.io
- Starknet Docs: https://docs.starknet.io
- Cairo by Example: https://github.com/cairo-lang/cairo

**SHARP:**
- SHARP API Docs: https://api.sharp.starkware.co
- Proof Verification: https://docs.starkware.co/sharp

**zkML:**
- Thinking Machine: https://thinkingmachines.ai
- Lens Protocol (example): https://lens.dev

---

## The Big Picture

After settlement + zkML:

**You can claim:**
```
"Verifiable AI for DeFi

Every allocation decision is:
  ✓ Calculated by our ML
  ✓ Proven with Cairo constraints
  ✓ Verified by SHARP
  ✓ Auditable by anyone

This is what Starknet was built for."
```

**That's your competitive moat.**

Build it right, and you own this space. 🚀

