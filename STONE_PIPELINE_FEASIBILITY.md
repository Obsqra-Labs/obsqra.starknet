# Stone Local Pipeline: Feasibility Analysis

**TL;DR:** Yes, this is **100% feasible** with what you have. You already have all the tools. Effort: ~2-3 days to wire it properly.

---

## What You Already Have ✅

### 1. Stone CPU AIR Prover Binary
```bash
/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover
```
- Built Dec 12 (20MB)
- Compiled, ready to run
- Takes: trace file + params → outputs proof

### 2. Cairo Execution Environment
```bash
cairo-run (installed)
scarb 2.11.0 (installed)
```
- Can compile `risk_engine.cairo` to Sierra
- Can execute Sierra IR and dump execution traces
- Can feed traces to Stone

### 3. Backend Schema Already Supports It
```python
# models.py line 172:
proof_source = Column(String, nullable=True, index=True)
# Expected values: "luminair", "stone_local", "atlantic"
```

**This means the database is ready for `proof_source="stone_local"`**

### 4. Config Files Ready
```
integrity/examples/proofs/cpu_air_prover_config.json
integrity/examples/proofs/cpu_air_params.json
```

---

## The 4-Step Pipeline

### Step 1: Compile Risk Engine to Sierra
**What:** Convert Cairo contract to IR format Stone understands
**Input:** `contracts/src/contracts/risk_engine.cairo`
**Output:** `risk_engine.sierra`
**Command:**
```bash
cd /opt/obsqra.starknet/contracts
scarb build --target sierra
```
**Effort:** 5 minutes (one command)

### Step 2: Execute Trace Dump
**What:** Run the Sierra IR with test inputs, capture execution trace
**Input:** `risk_engine.sierra` + allocation data (amount, token, etc)
**Output:** `execution_trace.json` (the "proof input")
**Command:**
```bash
cairo-run \
  --proof_mode \
  --program risk_engine.sierra \
  --output execution_trace.json \
  --memory_file memory.bin \
  < allocation_input.json
```
**Effort:** 1 day (need to understand Cairo trace format + input serialization)

### Step 3: Generate Stone Proof
**What:** Feed trace to cpu_air_prover, get cryptographic proof
**Input:** `execution_trace.json` + `cpu_air_prover_config.json`
**Output:** `proof.json` (VerifierConfiguration + StarkProofWithSerde)
**Command:**
```bash
/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover \
  --input_file execution_trace.json \
  --output_file proof.json \
  --parameter_file cpu_air_params.json
```
**Effort:** 30 minutes (just pipe the binary)

### Step 4: Wire Into Backend
**What:** Create `StoneProverService` that orchestrates steps 1-3
**Input:** Allocation context (amount, token, recipient)
**Output:** Proof ready for Integrity verifier
**Where:** `backend/app/services/stone_prover_service.py`
**Effort:** 1 day (implement + test)

---

## Effort Breakdown

| Task | Time | Difficulty | Blocking |
|------|------|-----------|----------|
| Compile risk_engine → Sierra | 5 min | Trivial | None |
| Understand Cairo trace format | 4 hours | Medium | Understanding Stone stdin format |
| Implement trace executor wrapper | 8 hours | Medium | Testing with actual traces |
| Wire to Stone binary | 2 hours | Easy | Binary path, config files |
| Integrate with risk_engine.py | 4 hours | Easy | Proof schema validation |
| End-to-end testing | 4 hours | Medium | Ensure Integrity verifier accepts output |
| **Total** | **27 hours** | **Medium** | **Cairo trace serialization** |

**Real timeline:** 2-3 days if you focus, with one tricky day (understanding Cairo trace format).

---

## Option Comparison: Atlantic vs Stone Local

| Factor | Atlantic | Stone Local |
|--------|----------|-----------|
| **Setup time** | 1 hour (just API key) | 2-3 days (build pipeline) |
| **Recurring cost** | $ per proof | $0 (you own the binary) |
| **Proof latency** | 5-10s (API roundtrip) | 2-5s (local execution) |
| **Proof freshness** | Sepolia block-dependent | Latest Cairo semantics |
| **Operational risk** | Depends on Herodotus API | Depends on cpu_air_prover binary |
| **Debugging** | "Proof failed" (API black box) | Full trace visibility |
| **Maintenance** | None (managed service) | Track Stone updates |

---

## The Smart Hybrid Approach

**Why not do BOTH?**

1. **Get Atlantic credits NOW** (you're already talking to them)
   - Implement Atlantic integration (1 hour wiring)
   - Test proofs work end-to-end
   - You have real proofs immediately
   
2. **Build Stone local pipeline AFTER** (2-3 day sprint)
   - Once it works, you own your proving
   - Use it as fallback if Atlantic has issues
   - Or use Atlantic for Sepolia (testing), Stone for mainnet (cost savings)

**This is not an "either/or" choice.** The backend schema already supports both:
```python
if proof_source == "atlantic":
    use_atlantic()
elif proof_source == "stone_local":
    use_stone_local()
```

---

## Hidden Complexity: Cairo Trace Format

The **one hard day** is understanding how to serialize allocation data into a format Cairo-run can consume.

**What you need to solve:**
- Risk Engine expects: `(amount: u256, token: ContractAddress, recipient: ContractAddress)`
- Cairo-run stdin needs: Some serialized format of this
- Stone expects: Binary trace file from cairo-run

**The bridge:** Cairo's `std::io` module for reading inputs
```cairo
use core::to_bytes::ToBytes;

fn main() {
    let amount = cairo_read::<u256>();  // Read from stdin
    let token = cairo_read::<ContractAddress>();
    let recipient = cairo_read::<ContractAddress>();
    
    // ... risk_engine logic ...
    
    // Outputs go to trace file automatically
}
```

**You'll need to:**
1. Add I/O wrappers to risk_engine.cairo
2. Serialize allocation context in backend
3. Feed to cairo-run stdin
4. Capture trace output

This is the **knowledge day.** Once you do it once, it's straightforward.

---

## Recommended Path Forward

### Week 1: Get Proofs Working (Atlantic Route - FAST)
```bash
# Day 1: Call with Herodotus
# - Explain: Full-stack DeFi protocol, need proof generation for allocation decisions
# - Ask: "Can we get Sepolia credits for testing?"
# - Expected response: "Yes, here's your API key"

# Day 2: Wire Atlantic
# - Uncomment atlantic_worker.py
# - Add API key to .env
# - Test single proof generation

# Day 3: Test end-to-end
# - Allocation → Atlantic proof → Integrity verification → execution
# - Database should show l2_verified_at timestamp
```

### Week 2-3: Own Your Proving (Stone Local Route - PARALLEL)
```bash
# After Atlantic is working, start Stone pipeline on the side

# Day 1: Trace format research
# - Understand Cairo I/O module
# - Check risk_engine.cairo for natural input points
# - Serialize allocation context

# Day 2: Implement pipeline
# - StoneProverService that orchestrates:
#   - Scarb build (compile to Sierra)
#   - cairo-run (generate trace)
#   - cpu_air_prover (generate proof)

# Day 3: Integration + testing
# - Wire into risk_engine.py
# - Test proof serialization
# - Verify Integrity contract accepts it
```

---

## Why This Hybrid Approach Wins

1. **You're not blocked** - Atlantic gets you running immediately
2. **You own the technology** - Stone pipeline gives you independence
3. **You have options** - Use Atlantic OR Stone depending on situation
4. **You understand proofs** - Building Stone teaches you the full stack
5. **You reduce costs** - Once Stone works, skip Atlantic fees

---

## Files to Create/Modify

```
NEW:
  backend/app/services/stone_prover_service.py (250 lines)
    - cairun runner wrapper
    - cpu_air_prover executor
    - proof serialization
  
MODIFY:
  contracts/src/contracts/risk_engine.cairo
    - Add I/O wrappers for trace input
  
  backend/app/workers/atlantic_worker.py
    - Add fallback to stone_prover_service
  
  backend/.env
    - Add STONE_BINARY_PATH=/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover
```

---

## Bottom Line

**Can you build it?** Yes, absolutely.

**Should you do it now?** No, do Atlantic first (you're already in contact).

**Should you do it after?** Yes, 100% worth it for independence.

**Effort?** 2-3 focused days, with one knowledge day (Cairo traces).

**Risk?** Low - you have all the tools, the schema already supports it, and you can test with simple allocations first.

The Stone binary has been sitting there since Dec 12 waiting for this. Let's use it.

