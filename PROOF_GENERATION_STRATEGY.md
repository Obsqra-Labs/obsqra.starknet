# Proof Generation Strategy: Dual Pipeline Lab

**Mission:** Build both Stone local + Atlantic managed service. Understand which wins on what metrics. Own your proving while having fallback.

---

## Part 1: Strategic Rationale

### Why Build Stone Local Pipeline?

**Independence**
- Own the full proving stack
- No API dependency (Atlantic outages = your app breaks)
- Control over proof generation latency
- Testable in isolation

**Cost Optimization**
- Stone: $0 per proof (binary cost: already built)
- Atlantic: ~$X per proof on Sepolia, $$$X on mainnet
- At scale (1000s of allocations/day), Stone saves real money

**Technology Understanding**
- Learn how STARK proofs actually work (not black box)
- Debug proof generation failures locally (full trace visibility)
- Customize proof parameters for your specific constraints
- Future-proof: Starknet's native prover will look like Stone (you'll already know it)

**Research Value**
- Data on how Cairo trace serialization affects proof size/latency
- Understanding of stone_version compatibility with different Integrity deployments
- Benchmarks for allocation decision latency (critical for real-time DeFi)
- Insights into what makes proofs fail/pass Integrity verifier

### Why Keep Atlantic?

**Fallback Mechanism**
- If Stone pipeline has issues, Atlantic is production-ready
- Hybrid: Stone for testing, Atlantic for critical allocations
- Safety net while learning Stone

**Managed Complexity**
- Someone else maintains Stone binary compatibility with Starknet
- Someone else handles proof deserialization format changes
- Lower operational burden for critical path

**Benchmarking**
- Atlantic is the "gold standard" (known working)
- Compare Stone against it: latency, proof size, verification success rate
- Validates that Stone output is correct

**Mainnet Ready**
- Atlantic can handle mainnet from day 1
- Stone might need tuning for higher security parameters
- Use Atlantic for mainnet while Stone is in "lab" phase

---

## Part 2: Benchmarking Matrix

### What We're Measuring

#### Latency (Speed)
```
LuminAIR (current):
  - Proof generation: ~2-3s ✅
  - Verification: Fails (RPC issue)
  - Total allocation time: ~10s (gated by Cairo execution)

Stone Local:
  - Compile Cairo → Sierra: ~200ms
  - Execute + trace dump: ??? (depends on allocation complexity)
  - Proof generation: ??? (depends on trace size)
  - Serialization: ??? 
  - Verification: ???
  - TOTAL: ??? (need to benchmark)

Atlantic:
  - API roundtrip: ~5-10s
  - Proof generation (server-side): 5-10s
  - Deserialization: ~500ms
  - Verification: ??? (same as Stone)
  - TOTAL: ~10-20s
```

**Question:** Can Stone match or beat Atlantic's 10-20s?
**Why it matters:** Real-time allocation decisions need <5s latency

#### Cost (Economics)
```
LuminAIR: $0 (doesn't verify)

Stone Local:
  - Initial setup: ~30h engineer time
  - Operational: $0/proof
  - Maintenance: Update Stone binary when Starknet changes (low)
  - Failure rate: Unknown (need to measure)
  
Atlantic Sepolia:
  - Initial setup: 1 hour (API key)
  - Operational: ~$0.01-0.10 per proof (need to confirm)
  - Maintenance: $0 (managed service)
  - Failure rate: Unknown (Herodotus manages it)

Atlantic Mainnet:
  - Operational: ~$1-10 per proof (need to confirm)
  - At 100 allocations/day: $100-1000/day
  - At 1000 allocations/day: $1000-10000/day
```

**Question:** At what volume does Stone breakeven vs Atlantic?
**Why it matters:** DeFi business model fundamentals

#### Correctness (Proof Quality)
```
What we're checking:
1. Proof deserializes into VerifierConfiguration + StarkProofWithSerde
2. Integrity verifier accepts proof (returns success)
3. Proof can be submitted on-chain (serializes to calldata)
4. Fact registration succeeds (l2_verified_at populated)
5. No spurious failures (random failures = bad)

Metrics:
- Success rate: What % of proofs verify? (goal: 100%)
- Error distribution: Serialization? Verification? Integrity timeout?
- Proof validity: Can same allocation use Stone vs Atlantic proof interchangeably?
```

**Question:** Is Stone output byte-for-byte identical to Atlantic, or just semantically equivalent?
**Why it matters:** If proofs are different but both valid, we're measuring implementation robustness

#### Operational Complexity
```
LuminAIR:
  - Running: In-process service (trivial)
  - Failure handling: Graceful (continue without proof)
  - Debugging: Dead end (can't verify)
  
Stone Local:
  - Running: Orchestration of 3 binaries (scarb, cairo-run, cpu_air_prover)
  - Failure handling: Which step fails? (trace? proving? serialization?)
  - Debugging: Full visibility (trace file, proof file, params)
  
Atlantic:
  - Running: HTTP API calls
  - Failure handling: "API returned error" (limited debug info)
  - Debugging: Black box (need Herodotus support)
```

**Question:** Which is easier to debug in production? (Not a joke question - debugging proofs is hard)
**Why it matters:** 3am failure - can you diagnose it?

---

## Part 3: Architecture Comparison

### Current State: LuminAIR (Mock Proofs)
```
User submits allocation proposal
    ↓
allocation_proposal_create() in risk_engine.py
    ├─ Generate LuminAIR proof (in-process, 2-3s)
    ├─ Validate proof structure (recently fixed)
    ├─ Try Integrity verification (FAILS - RPC issue)
    └─ Continue anyway (ALLOW_UNVERIFIED_EXECUTION=True)
    ↓
proof_job_status = "failed" (but execution allowed)
    ↓
Execute allocation (transfer + update constraints)
    ↓
Return: {"proof_job_id": "...", "status": "unverified"}
```

**Database State:**
```python
ProofJob {
  id: "...",
  proof_source: "luminair",
  proof_status: "failed",
  l1_verified_at: None,
  l2_verified_at: None,
  created_at: "2026-01-25T...",
  error_log: "Invalid block id (RPC issue)"
}

Allocation {
  id: "...",
  proof_job_id: "...",
  executed: True,  # ⚠️ Executed despite unverified proof
  status: "active"
}
```

**What the UI shows:**
```
✓ Allocation Created
⚠ Proof Status: UNVERIFIED (red banner)
✓ Execution: SUCCESSFUL
⚠ Risk Engine: NOT FORMALLY VERIFIED
```

---

### Option A: Atlantic (Managed Service)

```
User submits allocation proposal
    ↓
allocation_proposal_create() in risk_engine.py
    ├─ Serialize allocation → calldata
    ├─ Submit to Atlantic API (async)
    │   ├─ Atlantic compiles to trace
    │   ├─ Atlantic runs cpu_air_prover
    │   ├─ Atlantic serializes proof
    │   └─ Returns proof_uuid
    ├─ Poll atlantic_poller.py
    │   ├─ GET /proof/{uuid}
    │   └─ When complete, download proof
    ├─ Store proof in database
    ├─ Call Integrity verifier contract
    ├─ If success: l2_verified_at = now
    └─ If fail: retry with different params (if configured)
    ↓
proof_job_status = "verified" OR "failed"
    ↓
Execute allocation (transfer + update constraints) if verified
    ↓
Return: {"proof_job_id": "...", "status": "verified", "verified_at": "..."}
```

**Database State:**
```python
ProofJob {
  id: "...",
  proof_source: "atlantic",
  proof_status: "verified",
  l1_verified_at: None,
  l2_verified_at: "2026-01-25T...",  # ✅ Set by Integrity contract
  atlantic_uuid: "...",
  created_at: "2026-01-25T...",
}

Allocation {
  id: "...",
  proof_job_id: "...",
  executed: True,  # ✅ Only if proof verified
  proof_verified: True,
  status: "active"
}
```

**What the UI shows:**
```
✓ Allocation Created
✓ Proof Generated (Atlantic)
✓ Proof Verified (Integrity contract)
✓ Execution: SUCCESSFUL
✓ Risk Engine: FORMALLY VERIFIED
```

**Architecture:**
```
┌─────────────────────────────────────────────────┐
│ allocation_proposal_create()                    │
│   ├─ allocation_data_to_calldata()              │
│   └─ Call atlantic_service.submit_proof()       │
└──────────────┬──────────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────────┐
│ AtlanticService (in-process)                    │
│   ├─ POST to Atlantic API                       │
│   ├─ Get proof UUID                             │
│   └─ Return immediately (async)                 │
└──────────────┬──────────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────────┐
│ atlantic_worker.py (background, polls every 5s) │
│   ├─ GET /proof/{uuid}                          │
│   ├─ If ready:                                  │
│   │   ├─ Download proof                         │
│   │   ├─ Store in DB                            │
│   │   ├─ Call Integrity verifier                │
│   │   └─ Update proof_status                    │
│   └─ If not ready: wait 5s, retry               │
└──────────────┬──────────────────────────────────┘
               │
               ↓
         [Proof Verified]
```

**Scaling:**
```
At 1000 allocations/day:
  - 1000 Atlantic API calls
  - atlantic_worker polling every 5s
  - ~3600 GET requests/day
  - Cost: ~$0.01-0.10 per proof × 1000 = $10-100/day
```

---

### Option B: Stone Local (Built Pipeline)

```
User submits allocation proposal
    ↓
allocation_proposal_create() in risk_engine.py
    ├─ Serialize allocation → Stone input format
    ├─ Call stone_prover_service.generate_proof()
    │   ├─ Compile risk_engine.cairo → Sierra
    │   │   $ scarb build --target sierra
    │   │   ↓ risk_engine.sierra (10-100 KB)
    │   │
    │   ├─ Execute with cairo-run
    │   │   $ cairo-run \
    │   │       --proof_mode \
    │   │       --program risk_engine.sierra \
    │   │       --output execution_trace.json
    │   │   ↓ execution_trace.json (10MB-1GB depending on complexity)
    │   │
    │   ├─ Generate proof with cpu_air_prover
    │   │   $ cpu_air_prover \
    │   │       --input_file execution_trace.json \
    │   │       --output_file proof.json
    │   │   ↓ proof.json (0.5-10MB depending on trace size)
    │   │
    │   ├─ Deserialize proof
    │   │   ├─ Parse VerifierConfiguration
    │   │   └─ Parse StarkProofWithSerde
    │   │
    │   └─ Return proof structure
    │
    ├─ Call Integrity verifier contract
    ├─ If success: l2_verified_at = now
    └─ If fail: log + possibly retry with tuning
    ↓
proof_job_status = "verified" OR "failed"
    ↓
Execute allocation (transfer + update constraints) if verified
    ↓
Return: {"proof_job_id": "...", "status": "verified", "verified_at": "..."}
```

**Database State:**
```python
ProofJob {
  id: "...",
  proof_source: "stone_local",
  proof_status: "verified",
  l1_verified_at: None,
  l2_verified_at: "2026-01-25T...",  # ✅ Set by Integrity contract
  stone_trace_size: 245000000,  # 245MB
  stone_proof_size: 5000000,    # 5MB
  stone_latency_ms: 8500,  # 8.5s total
  created_at: "2026-01-25T...",
}

Allocation {
  id: "...",
  proof_job_id: "...",
  executed: True,  # ✅ Only if proof verified
  proof_verified: True,
  status: "active"
}
```

**What the UI shows:**
```
✓ Allocation Created
✓ Proof Generated (Local Stone)
✓ Proof Verified (Integrity contract)
✓ Execution: SUCCESSFUL
✓ Risk Engine: FORMALLY VERIFIED
[INFO] Proof generation: 8.5s, trace: 245MB, proof: 5MB
```

**Architecture:**
```
┌──────────────────────────────────────────────────────┐
│ allocation_proposal_create()                         │
│   ├─ allocation_data_to_cairo_input()                │
│   └─ Call stone_prover_service.generate_proof_sync() │
└──────────────┬───────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────┐
│ StoneProverService (in-process, SYNC)                │
│   ├─ Compile: scarb build --target sierra            │
│   ├─ Trace: cairo-run --proof_mode ...               │
│   ├─ Prove: cpu_air_prover ...                       │
│   ├─ Deserialize proof                               │
│   └─ Return immediately with proof                   │
└──────────────┬───────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────┐
│ Integrity Verification (in-process)                  │
│   ├─ Call IntegrityService.verify_proof()            │
│   ├─ Contract call to Integrity verifier             │
│   └─ Store l2_verified_at                            │
└──────────────┬───────────────────────────────────────┘
               │
               ↓
         [Proof Verified]
```

**Scaling:**
```
At 1000 allocations/day:
  - 1000 Stone proof generations (local)
  - Each uses: scarb (shared), cairo-run (2-4s), cpu_air_prover (2-6s)
  - Total compute: ~4000-10000 CPU-seconds = 2-3 hours total (parallelizable)
  - Cost: $0 (your hardware)
  - Infrastructure: None (self-contained)
```

---

### Comparison Matrix

| Dimension | LuminAIR | Stone Local | Atlantic |
|-----------|----------|-------------|----------|
| **Proof latency** | 2-3s ✅ | ??? | 10-20s |
| **Proof generation latency** | 2-3s | ???+2-4s (compile) | 5-10s |
| **Verification latency** | Fails ❌ | ??? | ??? |
| **Total E2E latency** | ~10s (no proof) | ??? | ~20-30s |
| **Cost per proof** | $0 | $0 | $0.01-0.10 |
| **Cost at scale** | $0 | $0 | $10-100/day |
| **Ownership** | None (mock) | Full | Herodotus |
| **Debuggability** | Low (mock) | High (full trace) | Low (API) |
| **Operational complexity** | Trivial | Medium | Trivial |
| **Failure modes** | Always fails | Unknown | Known (Atlantic SLA) |
| **Research value** | None | High | None |

---

## Part 4: What We're Building - Final Product Comparison

### Scenario: 100 Allocations Submitted (Peak Load)

#### With LuminAIR Only (Current)
```
Allocations submitted: 100
Proof generation latency: 0.2s (parallel, 100 in ~0.2s)
Proof verification: ❌ FAILS (RPC issue)
Status in database:
  - 100 ProofJobs with status="failed"
  - 100 Allocations with executed=True, proof_verified=False
  - ERROR LOG full of "Invalid block id"

UI Display:
  ┌─────────────────────────┐
  │ ALLOCATIONS CREATED: 100 │
  │                         │
  │ ⚠️  UNVERIFIED (100)     │
  │ 🚫 PROOF FAILED (100)   │
  │                         │
  │ ✓ Executed: 100         │
  │                         │
  │ Status: DEMO MODE       │
  └─────────────────────────┘

Risk Profile:
  - All 100 allocations are live but NOT cryptographically verified
  - If Risk Engine logic is buggy, bug affects all 100
  - No audit trail of proof verification
  - Compliance/audit nightmare: "Yes we executed but can't prove risk was assessed"
```

---

#### With Stone Local Only (If Built)
```
Allocations submitted: 100
Proof generation:
  - Compile (cached): 0.2s
  - Trace dump (sequential): 100 × 3s = 300s (parallelize to 30s with 10 workers)
  - Proof generation: 100 × 4s = 400s (parallelize to 40s with 10 workers)
  - Deserialization: 100 × 0.1s = 10s
  - Total time: ~40-50s if parallelized
  
Proof verification:
  - Call Integrity contract 100×: ~50-100s (depends on RPC speed)
  - Success rate: ??? (this is what we need to measure)

Status in database (best case):
  - 100 ProofJobs with status="verified"
  - 100 Allocations with executed=True, proof_verified=True
  - 100 rows with l2_verified_at timestamp
  - Trace size: 100 × 250MB = 25GB (need to decide: keep? compress? delete?)

UI Display:
  ┌──────────────────────────┐
  │ ALLOCATIONS CREATED: 100  │
  │                          │
  │ ✓ VERIFIED (95)          │
  │ ⚠️  UNVERIFIED (5)        │
  │                          │
  │ ✓ Executed: 100          │
  │                          │
  │ Status: PRODUCTION READY │
  │                          │
  │ Proof Gen: 45s (local)   │
  │ Verification: 75s        │
  │ Total latency: 120s      │
  └──────────────────────────┘

Risk Profile:
  - 95 allocations are cryptographically verified
  - 5 failed verification (investigate why: proof generation bug? verifier issue?)
  - Full audit trail: timestamp, proof hash, verification status
  - Compliance: "All allocations verified by Stone proof + Integrity contract"
  - Cost: $0 (local)
  - Operational: manage trace file storage, debug failures locally
```

---

#### With Atlantic Only (If Credits Granted)
```
Allocations submitted: 100
Proof submission:
  - Submit to Atlantic: 100 × 0.1s = 10s (async, returns immediately)
  - Polling latency: 100 × 10-20s (depends on Atlantic queue)
  - Total submission-to-completion: ~30-40s

Proof verification:
  - Call Integrity contract 100×: ~50-100s

Status in database (best case):
  - 100 ProofJobs with status="verified"
  - 100 Allocations with executed=True, proof_verified=True
  - 100 rows with l2_verified_at timestamp
  - atlantic_uuid: stored for debugging

UI Display:
  ┌──────────────────────────┐
  │ ALLOCATIONS CREATED: 100  │
  │                          │
  │ ✓ VERIFIED (100)         │
  │ 🚫 FAILED (0)            │
  │                          │
  │ ✓ Executed: 100          │
  │                          │
  │ Status: PRODUCTION READY │
  │                          │
  │ Proof Gen: 20s (Atlantic)│
  │ Verification: 75s        │
  │ Total latency: 95s       │
  │ Cost: $1.00/batch        │
  └──────────────────────────┘

Risk Profile:
  - 100% of proofs verified (Atlantic's SLA)
  - Zero manual debugging needed (Atlantic handles it)
  - Full audit trail: atlantic_uuid for reference
  - Compliance: "All allocations verified by Atlantic + Integrity contract"
  - Cost: $1/batch at scale
  - Operational: track Atlantic API quota, handle rate limiting
```

---

#### With Stone + Atlantic Hybrid (Both Built)
```
Strategy: Use Stone for testing (fast feedback), Atlantic for critical/mainnet (safe)

Dev/Testing Environment:
  - All allocations: use Stone local
  - Instant feedback: 45s for 100 proofs
  - Deep debugging: see every trace, every proof parameter
  - Cost: $0
  - Learn mode: understand what breaks and why

Production Sepolia:
  - Critical allocations (>10M TVL risk): Stone local (own it, understand it)
  - Regular allocations: Atlantic (managed, 100% SLA)
  - Fallback: if Atlantic API down, switch to Stone

Mainnet (when live):
  - Small allocations: Stone local ($0)
  - Large allocations: Atlantic (managed, insured by Herodotus)
  - Cost optimization: save ~$100/day vs Atlantic-only

UI Display (Sepolia):
  ┌──────────────────────────┐
  │ ALLOCATIONS CREATED: 100  │
  │                          │
  │ ✓ VERIFIED (50)          │
  │   - Stone (local): 30    │
  │   - Atlantic: 20         │
  │ ⚠️  UNVERIFIED (0)        │
  │                          │
  │ ✓ Executed: 100          │
  │                          │
  │ Status: RESEARCH ENABLED │
  │                          │
  │ Latency breakdown:       │
  │  - Stone avg: 45s        │
  │  - Atlantic avg: 30s     │
  │  - Combined: ~40s median │
  └──────────────────────────┘

Risk Profile:
  - 100% of proofs verified (hybrid of both systems)
  - Deep understanding: Stone gives you debugging + learning
  - Cost optimization: Atlantic fallback keeps you safe
  - Research capability: understand performance tradeoffs
  - Compliance: "Allocations verified by Stone + Integrity or Atlantic + Integrity"
  - Future-proof: when Starknet native prover launches, you'll recognize it (Stone-like)
```

---

## Part 5: Research Gaps & Independent Investigation

### What We Need to Discover

#### 1. **Cairo Trace Format & Serialization**
**Gap:** How to serialize allocation context into input that cairo-run accepts?

**Details:**
- Risk Engine expects: `(amount: u256, token: ContractAddress, recipient: ContractAddress)`
- Cairo-run stdin format: ?
- Example input file: ?
- Error handling: what if serialization is wrong?

**Research needed:**
```
From Cairo docs:
- Is there std::io::read() for getting stdin in Cairo?
- How do u256 and ContractAddress get serialized to bytes?
- Can we use cairo_test! macros to test this locally?
- Is there a cairo-run flag to dump serialization format?
```

**Who should research:**
> Independent research agent should:
> - Search Cairo 2.11 stdlib documentation for I/O module
> - Find examples of cairo-run with stdin input
> - Check Starknet SDK (starknet.py) for serialization patterns
> - Look at Herodotus integration tests (how do they serialize?)

**Blocks:** Everything in Stone pipeline depends on this

---

#### 2. **Proof Size vs Trace Size Relationship**
**Gap:** How does trace complexity affect proof output?

**Details:**
- Simple allocation: trace = 10MB, proof = ?
- Complex allocation: trace = 500MB, proof = ?
- Proof serialization overhead: VerifierConfiguration size?

**Why it matters:**
- Storage cost (if we keep proofs)
- Serialization latency
- Gas cost to submit proof on-chain (calldata size)

**Research needed:**
```
Need to measure:
1. Generate 10 different allocations with Stone
2. Record trace size, proof size, latency for each
3. Plot: trace_size → proof_size (is it linear? exponential?)
4. Measure: proof_size → calldata_size (how much overhead?)
5. Measure: large_proof → Integrity verifier gas cost
```

**Who should research:**
> Independent research agent should:
> - Find Starknet gas cost models for proof verification
> - Check Herodotus docs for proof size ranges
> - Look at Stone prover output examples
> - Calculate approximate on-chain cost (gas × gas_price)

**Blocks:** Cost-per-proof calculation for mainnet

---

#### 3. **Integrity Verifier Compatibility**
**Gap:** Does Stone proof format match Integrity verifier expectations exactly?

**Details:**
- Integrity verifier expects: VerifierConfiguration + StarkProofWithSerde
- Atlantic produces: Known working format
- Stone produces: Unknown if format matches

**Why it matters:**
- If formats don't match, deserialization fails
- If deserialization works but verification fails, proof is wrong
- Need to know: are failures due to format or proof correctness?

**Research needed:**
```
Need to understand:
1. VerifierConfiguration exact schema (fields, types, constraints)
2. StarkProofWithSerde exact schema
3. Where does Atlantic differ from raw Stone output?
4. Does Atlantic add a transformation layer?
5. If so, can we replicate it locally?
```

**Who should research:**
> Independent research agent should:
> - Download Atlantic proof example (if available)
> - Compare with Stone cpu_air_prover raw output
> - Check Herodotus atlanticapi repository (if public)
> - Find Integrity verifier contract source (Herodotus repos)
> - Document exact field mapping

**Blocks:** Proof deserialization step

---

#### 4. **Stone Version Compatibility**
**Gap:** Which stone_version should we use? Will it work with Sepolia Integrity?

**Details:**
- You built: cpu_air_prover (which version? from Dec 12 bazelisk build)
- Integrity expects: "stone_version" in VerifierConfiguration
- Options: stone4? stone5? stone6?
- Sepolia Integrity: deployed with which version?

**Why it matters:**
- Wrong version = proof fails verification
- Need to match Sepolia's deployed Integrity contract

**Research needed:**
```
Need to find:
1. Check Herodotus Integrity contract (Sepolia) for stone_version constant
2. Check stone-prover repo for version numbering
3. Your local build: is it stone5? stone4? How to tell?
4. Compatibility table: which stone_prover produces which stone_version?
5. Can you downgrade/upgrade stone version in params?
```

**Who should research:**
> Independent research agent should:
> - Read Sepolia Integrity contract source (find stone_version)
> - Check stone-prover git tags / releases (what's the latest?)
> - Your Dec 12 build: git log to find commit, what version is it?
> - Herodotus docs for version compatibility matrix

**Blocks:** Proof generation parameters

---

#### 5. **Benchmark Latency Breakdown**
**Gap:** How much time in each step? Where's the bottleneck?

**Details:**
- Compile: 200ms? 2s? depends on build cache
- Trace: 2-4s? depends on allocation complexity
- Proof: 2-6s? depends on trace size
- Serialize: 100ms? 1s?

**Why it matters:**
- If compile takes 3s, that's a blocker (parallelize or cache)
- If trace takes 10s, that's slow (optimize allocation code?)
- If proof takes 1s but serialize takes 8s, different solution
- Need to know: is Stone faster than Atlantic's 10-20s?

**Research needed:**
```
Need to measure (with simple test allocation):
1. Time: scarb build --target sierra (measure 10x, use min)
2. Time: cairo-run --proof_mode (measure variability)
3. Time: cpu_air_prover (measure variability)
4. Time: deserialization (parse JSON to VerifierConfiguration)
5. Time: Integrity contract call
6. Trace size, proof size (correlate with time)
```

**Who should research:**
> Independent research agent should:
> - Find Stone prover performance benchmarks (if published)
> - Look at Cairo execution performance notes
> - Check Starknet docs for typical execution times
> - Find any published latency measurements for similar proofs

**Blocks:** Latency predictions for UI/UX

---

#### 6. **Failure Mode Analysis**
**Gap:** When Stone pipeline fails, what are the common causes?

**Details:**
- Serialization wrong: cairo-run returns error
- Trace malformed: cpu_air_prover crashes
- Proof invalid: Integrity verifier rejects it
- Deserialization bug: our code crashes

**Why it matters:**
- Need graceful error handling
- Need to distinguish: user error vs system error vs infrastructure error
- Need monitoring/alerting

**Research needed:**
```
Need to understand:
1. What does cpu_air_prover do when given bad input?
2. What does cairo-run do when given bad input?
3. What does Integrity contract return on bad proof?
4. Can we mock failures locally for testing?
5. How to serialize error telemetry?
```

**Who should research:**
> Independent research agent should:
> - Check Stone prover CLI help / error messages
> - Find Cairo error handling patterns
> - Look at Integrity contract revert reasons (if available)
> - Search GitHub for Stone+Starknet integration issues

**Blocks:** Production error handling

---

#### 7. **Atlantic Cost & Quota Model**
**Gap:** What's the actual cost? Are there quotas? Rate limits?

**Details:**
- Herodotus pricing: per-proof? monthly? usage-based?
- Sepolia quota: unlimited? per-day limit?
- Rate limits: 1000 proofs/sec? 10 proofs/sec?

**Why it matters:**
- Budget planning for testnet
- Budget planning for mainnet
- Rate limiting strategy
- Fallback strategy (if Atlantic quota exceeded)

**Research needed:**
```
Need to know:
1. Herodotus pricing page (official)
2. Call notes: what did they quote?
3. Sepolia free tier limits
4. Mainnet cost per proof
5. Rate limiting for Atlantic API
```

**Who should research:**
> Independent research agent should:
> - Visit https://herodotus.cloud/pricing
> - Check Atlantic API documentation
> - Look for published rate limits
> - Find any public benchmarks/cost comparisons

**Blocks:** Cost-per-proof estimation

---

## Part 6: Implementation Order

### Phase 1: Get Atlantic Working (Week 1)
**Objective:** Have fallback path, establish baseline

**Tasks:**
1. Call Herodotus (you're already doing this)
2. Get API key + Sepolia credits
3. Uncomment atlantic_worker.py
4. Test single allocation → Atlantic proof → Integrity verification
5. Document: latency, success rate, any failures

**Research during Phase 1:**
- Atlantic cost & quota model (from call)
- Integrity verifier stone_version (from contract)

---

### Phase 2: Stone Pipeline Research (Week 2)
**Objective:** Answer research questions before building

**Tasks:**
1. Investigate Cairo trace serialization (independent research)
2. Find Integrity verifier schema (independent research)
3. Understand Stone version compatibility (independent research)
4. Document findings in separate doc: STONE_RESEARCH_FINDINGS.md

**What you do:** 
- Review research findings
- Decide: is Stone feasible? (if no, abandon; if yes, proceed)
- Decide: which optimizations to try first?

---

### Phase 3: Stone Pipeline Build (Week 3)
**Objective:** Build & benchmark Stone local

**Tasks:**
1. Implement StoneProverService
2. Add Cairo I/O wrappers to risk_engine.cairo
3. Implement trace executor wrapper
4. Integrate with risk_engine.py
5. Test 10 allocations: measure latency, success rate

**Research during Phase 3:**
- Benchmark latency breakdown (from testing)
- Failure mode analysis (what breaks? how often?)

---

### Phase 4: Hybrid Lab (Week 4+)
**Objective:** Compare Stone vs Atlantic on real workload

**Tasks:**
1. Run 100 allocations with Atlantic only → measure metrics
2. Run 100 allocations with Stone only → measure metrics
3. Run 100 allocations with hybrid (50/50) → measure metrics
4. Create comparison table: latency, cost, success rate, complexity

**Output:**
- BENCHMARKING_RESULTS.md (detailed metrics)
- RECOMMENDATIONS.md (which to use when)
- DECISION_MATRIX.md (for future roadmap)

---

## Part 7: Documentation Artifacts We're Creating

```
For Strategic Planning:
  ✓ THIS FILE: PROOF_GENERATION_STRATEGY.md
    - Why both? What are we measuring? What does the app look like?
  □ STONE_RESEARCH_FINDINGS.md
    - Answers to all research gaps (filled in by research agent)

For Implementation:
  □ STONE_PIPELINE_IMPLEMENTATION.md
    - Step-by-step guide to building it
    - Code snippets for each component
    - Testing strategy
  
For Operations:
  □ BENCHMARKING_RESULTS.md
    - Latency tables, cost tables, success rates
    - Failure analysis
    - Recommendations

For Decision Making:
  □ RECOMMENDATIONS.md
    - "Use Stone for: ___"
    - "Use Atlantic for: ___"
    - "Hybrid strategy: ___"
```

---

## Part 8: Success Criteria

**Phase 1 Success (Atlantic):**
- ✅ API key received and stored
- ✅ Single allocation: submit → proof generated → verified in Integrity → execution succeeds
- ✅ Latency measured: __s (Atlantic expects 10-20s, we'll see)
- ✅ Success rate: ___ % (expect 100%)
- ✅ Database: ProofJob has l2_verified_at timestamp

**Phase 2 Success (Research):**
- ✅ Cairo trace serialization documented (input format found)
- ✅ Integrity verifier schema documented (VerifierConfiguration + StarkProofWithSerde)
- ✅ Stone version compatibility documented (which stone_version for Sepolia)
- ✅ Decision made: build Stone or not? (if research says it's blocked, we skip)

**Phase 3 Success (Stone Building):**
- ✅ StoneProverService compiles, runs, generates proof
- ✅ 10 test allocations: ___ % verified successfully
- ✅ Latency measured: __s (can it beat or match Atlantic's 10-20s?)
- ✅ Failure mode documented: why do 10-20% fail (if applicable)?
- ✅ Database: ProofJob has stone_latency_ms, stone_trace_size, stone_proof_size

**Phase 4 Success (Benchmarking):**
- ✅ 100× Atlantic: latency __s, cost $__, success ___%, failures analyzed
- ✅ 100× Stone: latency __s, cost $0, success ___%, failures analyzed
- ✅ 100× Hybrid: latency __s, cost calculated, all verified
- ✅ Recommendation: "In production, use ___"
- ✅ Cost/benefit documented: breakeven point at ___ allocations/day

---

## Key Questions to Answer With Herodotus

When you call them:

1. **Sepolia Credits**
   - "Can we get free Sepolia credits for testing proof generation?"
   - How many credits? Any limits?

2. **Proof Format**
   - "What format do your proofs output in? (VerifierConfiguration + StarkProofWithSerde?)"
   - "Is this compatible with Herodotus Integrity verifier contract on Sepolia?"
   - "Can you provide an example proof JSON we can examine?"

3. **Stone Compatibility**
   - "Which stone_version does your Atlantic service generate?"
   - "Is it compatible with your Integrity contract on Sepolia?"

4. **Cost Structure**
   - "What's the cost per proof on Sepolia?"
   - "What's the cost per proof on mainnet?"
   - "Any volume discounts?"

5. **Operational**
   - "What's your SLA for proof generation latency?"
   - "Do you have rate limits?"
   - "What's your uptime SLA?"

6. **Technical Debugging**
   - "If a proof fails to verify, what debugging info do you provide?"
   - "Can you help diagnose if the issue is format vs correctness?"

---

## TL;DR: Why Both?

**Stone Local:**
- Ultimate independence (own your proving)
- Zero cost per proof (own hardware)
- Full debugging visibility (traces + proofs)
- Learning opportunity (understand STARK proofs)
- Future-proof (matches Starknet native prover architecture)
- Risky: unproven in your specific setup

**Atlantic:**
- Immediately working (just API key)
- Managed complexity (Herodotus handles it)
- Known SLA (they guarantee it works)
- Safe fallback (if Stone breaks, use this)
- Cost-justified early (while learning)
- Not risky: proven service

**Hybrid:**
- Best of both
- Use Atlantic while building Stone
- Use Stone for development (fast feedback, full visibility)
- Use Atlantic for production (safety, SLA)
- Use whichever is faster/cheaper for each tier
- Research-driven: understand proofs, optimize costs

**The plan:** Get Atlantic working today, build Stone this month, decide next month which to use for each environment.

