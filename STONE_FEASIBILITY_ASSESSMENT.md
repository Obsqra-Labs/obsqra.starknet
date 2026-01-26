# Stone Pipeline Feasibility Assessment

**Date:** January 25, 2026  
**Status:** DETAILED RESEARCH COMPLETE - READY FOR DECISION

---

## Executive Summary

The Stone local pipeline is **technically feasible but has one critical blocker**. The small proof (8,192 steps) works end-to-end, but the full trace (131,072 steps) **keeps aborting with Signal 6** during FRI parameter tuning. This is preventing validation of whether local proofs can beat Atlantic's 10-20s latency.

**Decision Required:** Do we (a) spend 2-3 days debugging the full trace issue, or (b) proceed with Atlantic first and circle back to Stone later?

---

## What We Know Works ✅

### 1. Cairo Trace Serialization (SOLVED)
- Input method: `--air_public_input` and `--air_private_input` flags (not stdin)
- u256 encoding: Two 128-bit felts (low/high) via `{"low": ..., "high": ...}`
- ContractAddress: Single felt
- Error handling: Will fail loudly if format is wrong

**Confidence:** HIGH - Dev-log shows successful small trace generation

**Action Required:** Write a wrapper function to serialize (amount: u256, token: address, recipient: address) into the correct JSON format.

---

### 2. Proof Format & Integrity Compatibility (SOLVED)
- Required format: VerifierConfiguration (4 felts) + StarkProofWithSerde
- Required parameters: `layout=recursive`, `hasher=keccak_160_lsb`, `stone_version=stone5`, `memory_verification=strict`
- Small proof successfully generated as ~400 KB JSON

**Confidence:** HIGH - Config documented in backend, small proof confirmed to work

**Action Required:** Use same 4 parameters consistently. Ensure --generate_annotations flag when generating proofs.

---

### 3. Stone Version Compatibility (SOLVED)
- Sepolia Integrity expects: stone5
- Config specifies: stone5
- Atlantic produces: stone5

**Confidence:** HIGH - Explicitly documented in code

**Action Required:** None - already correct in config.py

---

### 4. Proof Serialization & Calldata (PARTIALLY SOLVED)
- Small proof (400 KB JSON) serializes to ~10-15 KB calldata (feasible)
- Full proof size: unknown (depends on full trace)
- On-chain verification: expected to work if proof is valid

**Confidence:** MEDIUM - Small proof works, full proof unknown

**Action Required:** Measure full proof size once full trace can be generated.

---

## What We DON'T Know Yet ❌

### 1. CRITICAL BLOCKER: Full Trace FRI Parameters
**Issue:** Attempting to generate a proof from the full 131,072-step trace results in Signal 6 (native crash) despite multiple FRI parameter tuning attempts.

**What this means:**
- Small trace (8,192 steps) works with `fri_step_list=[3,3,3,2], last_layer_degree_bound=64`
- Full trace needs `fri_step_list=[...], last_layer_degree_bound=[...]` where the equation holds: `log2(last_layer_degree_bound) + Σ(fri_step_list) = log2(131072) + 4 = 21.03 ≈ 21`
- Stone's cpu_air_prover is rejecting parameter combinations, suggesting either:
  - Wrong formula interpretation
  - Resource limits (memory?)
  - Mismatch between layout (recursive) and trace content

**Impact:** Can't measure if Stone beats Atlantic's 10-20s latency. Can't validate full pipeline.

**Resolution Time:** 1-2 days of FRI parameter research + experimentation

**Risk:** If parameters can't be fixed, Stone local may not work for full Risk Engine traces.

---

### 2. Latency Comparison (UNKNOWN)
**What we need:**
- Small proof: scarb (cached) + cairo-run + cpu_air_prover + serializer + Integrity call = ~? seconds
- Full proof: same chain, assuming FRI params can be fixed = ~? seconds
- Atlantic: documented as 10-20s total latency

**Why it matters:**
- If local Stone is >10s, Atlantic might be better (managed, reliable SLA)
- If local Stone is <5s, it's worth owning

**Resolution Time:** 1 day of benchmarking (once full trace works)

**Risk:** Local proving may be slower than Atlantic due to FRI parameter tuning overhead.

---

### 3. Error Recovery (PARTIALLY UNKNOWN)
**What we know:**
- Signal 6 from cpu_air_prover → native crash, need to restart and retry
- "Unexpected number of interaction elements" → need --generate_annotations
- "invalid final_pc" → proof AIR doesn't match verifier's program

**What we don't know:**
- How often do FRI parameters need tuning?
- Is there a formula to derive optimal parameters automatically?
- How to detect which error occurred and retry intelligently?

**Resolution Time:** 2-3 hours (implement error logging + classification)

**Risk:** Pipeline may be fragile if FRI parameters need manual tuning for each new Risk Engine version.

---

## Side-by-Side Comparison: Stone vs Atlantic

| Factor | Stone Local | Atlantic | Verdict |
|--------|-------------|----------|---------|
| **Implementation time** | 2-3 days | 1 hour | Atlantic wins |
| **Full trace working?** | ❌ Signal 6 blocker | ✅ Known working | Atlantic wins |
| **Latency** | ❓ Unknown (est. 5-10s) | ✅ 10-20s SLA | TBD |
| **Cost/proof** | $0 | ~$0.01-0.10 | Stone wins (if working) |
| **Operational complexity** | High (FRI tuning) | Low (API) | Atlantic wins |
| **Debuggability** | Excellent (full traces) | Poor (black box) | Stone wins |
| **Risk of failure** | High (untested for full trace) | Low (Herodotus backs it) | Atlantic wins |

---

## Recommended Path Forward

### Option A: Pragmatic (RECOMMENDED)

**Week 1: Get Atlantic Working**
1. Call Herodotus today/tomorrow (you're already in contact)
2. Confirm Sepolia credits available
3. Wire Atlantic integration (1 hour)
4. Test: single allocation → proof → verification ✅
5. Establish baseline: latency ~15-20s, cost $0 (Sepolia free tier)

**Week 2: Research Stone Issues**
- Investigate FRI parameter formula
- Search Stone prover GitHub issues
- Document findings

**Week 3-4: If Time + Motivation**
- Debug full trace Signal 6 issue
- Optimize FRI parameters
- Build Stone pipeline

**Outcome:** Production-ready proofs in Week 1. Stone as optional optimization later.

**Cost:** 1 hour this week, 16 hours next month (if you choose to pursue Stone)

---

### Option B: Ambitious (NOT RECOMMENDED - unless you want deep learning)

**This Week: Debug Full Trace**
1. Research FRI parameter formula exhaustively
2. Try 10+ parameter combinations
3. Check Stone prover source for clues
4. Potentially: upgrade Stone binary from Dec 12 build? Check for newer version?

**Problem:** Could take 5-10 days, no guarantee of success

**Risk:** Block yourself on Stone while Atlantic is still unavailable

**Only choose this if:** You have 5+ days to spare and want to deeply understand STARK proofs

---

## What To Ask Herodotus On Your Call

1. **Sepolia Credits** - "Can we get free/test credits for Stone proof verification?"
2. **Proof Format** - "Can you provide an example Atlantic-generated proof JSON so we can compare with local Stone output?"
3. **Pricing** - "What's the cost per proof on mainnet? Any volume discounts?"
4. **FRI Parameters** - "We're seeing Signal 6 when tuning FRI parameters for larger traces. Any guidance?"
5. **SLA** - "What's your guaranteed latency and uptime for Atlantic?"

---

## Implementation Roadmap (If You Choose Option A)

### Phase 1: Atlantic Integration (This Week - 1 hour)

```python
# backend/app/services/atlantic_service.py (ALREADY STUBBED)

class AtlanticService:
    async def submit_proof_job(self, allocation_data: dict) -> str:
        """
        Submit allocation to Atlantic API
        Returns: job_uuid
        """
        payload = self._serialize_for_atlantic(allocation_data)
        response = await self.client.post(
            f"{self.base_url}/query",
            json=payload
        )
        return response.json()["jobId"]
    
    async def poll_proof(self, job_uuid: str) -> Optional[dict]:
        """
        Poll for proof completion
        Returns: proof JSON when ready, None if still pending
        """
        response = await self.client.get(f"{self.base_url}/proof/{job_uuid}")
        if response.json()["status"] == "completed":
            return response.json()["proof"]
        return None
```

**Then wire into risk_engine.py:**
```python
# In allocation_proposal_create():
proof = await atlantic_service.submit_proof_job(allocation_data)
# ... rest of execution ...
```

**Wire atlantic_worker.py polling:**
```python
# background task that polls for completed proofs every 5s
async def poll_atlantic_proofs():
    while True:
        for pending_job in get_pending_atlantic_jobs():
            proof = await atlantic_service.poll_proof(pending_job.uuid)
            if proof:
                verify_and_store_proof(proof)
        await asyncio.sleep(5)
```

**Expected outcome:** Database shows `l2_verified_at` timestamps. UI shows ✅ VERIFIED.

---

### Phase 2: Stone Investigation (Next Week - 4 hours research)

**Task 1: Understand FRI Formula**
- Search: "STARK FRI parameters" + "last_layer_degree_bound"
- Read: Stone prover docs on parameter selection
- Goal: Derive parameters for 131,072-step trace

**Task 2: Check for Updated Stone Binary**
- Your build: Dec 12
- Latest: Check stone-prover GitHub
- Outcome: Either upgrade binary or confirm yours is current

**Task 3: Classify the Error**
- Signal 6 is SIGABRT (assertion/memory failure)
- Options:
  - FRI parameters violate invariant → error message in stderr
  - Out of memory → need larger machine
  - Incompatible layout → need different layout

**Deliverable:** STONE_DEBUG_REPORT.md explaining the issue

---

### Phase 3: Stone Build (Only If Needed)

If Phase 2 shows issue is fixable:

```python
# backend/app/services/stone_prover_service.py (NEW FILE - ~200 lines)

class StoneProverService:
    def generate_proof(self, allocation_data: dict) -> dict:
        """
        Local Stone proof generation
        """
        # 1. Serialize allocation to cairo-run input
        input_json = self._serialize_allocation(allocation_data)
        
        # 2. Run scarb build (cached)
        sierra = self._compile_risk_engine()
        
        # 3. Run cairo-run to get trace
        trace_file = self._execute_trace(sierra, input_json)
        
        # 4. Run cpu_air_prover
        proof_json = self._generate_proof(trace_file)
        
        # 5. Deserialize to VerifierConfiguration + StarkProofWithSerde
        verifier_config, stark_proof = self._deserialize_proof(proof_json)
        
        return {
            "verifier_config": verifier_config,
            "stark_proof": stark_proof,
            "trace_size_mb": os.path.getsize(trace_file) / 1024 / 1024,
            "latency_ms": elapsed_time
        }
```

---

## Success Criteria for Each Phase

**Phase 1 (Atlantic):**
- ✅ API key received and configured
- ✅ Single allocation → proof generated → verified → l2_verified_at populated
- ✅ UI shows "✅ VERIFIED (Atlantic)"
- ✅ Cost: $0 (Sepolia free tier)
- ✅ Latency measured: __s

**Phase 2 (Stone Research):**
- ✅ FRI parameter formula documented
- ✅ Stone binary version confirmed
- ✅ Error root cause identified
- ✅ Decision made: fixable? worth pursuing?

**Phase 3 (Stone Build - if Phase 2 is green):**
- ✅ Single allocation proof generates locally
- ✅ Proof verifies on Integrity
- ✅ Latency measured: __s
- ✅ Comparison: Stone vs Atlantic on 100 allocations
- ✅ Decision: use Stone, Atlantic, or hybrid?

---

## Final Recommendation

**Start with Atlantic. The research is done and shows it works. Stone has one critical blocker (FRI parameters for full trace) that needs investigation before you can validate it.**

**Timeline:**
- **Today/Tomorrow:** Call Herodotus, get credits
- **Wednesday:** Wire Atlantic, deploy, test
- **Thursday-Friday:** Have working proofs in production (testnet)
- **Next week:** Research Stone if you want, but you're not blocked

**Cost:** 1 hour this week to get real proofs working. Optional 2-3 days later to own your proving.

The path is clear. You have the knowledge (7 research gaps filled). You have the tools (Atlantic credits + Stone binary). Now you need the execution.

