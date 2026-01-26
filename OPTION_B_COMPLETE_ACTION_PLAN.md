# Option B: Debug & Build Stone Pipeline - Complete Action Plan

**Your commitment:** 5+ focused days to own your proving stack  
**Goal:** Solve Signal 6 → implement full Stone pipeline → benchmark against Atlantic  
**Outcome:** Production-ready local proofs + deep STARK knowledge

---

## Phase 1: Understand FRI Parameters (Today + Tomorrow - 8 hours)

### Task 1.1: Understand the FRI Degree Equation

**What you know:**
- Small trace works: `fri_step_list=[3,3,3,2]`, `last_layer_degree_bound=64`
- Full trace fails: Signal 6 during FRI parameter attempts
- Equation: `log2(last_layer_degree_bound) + Σ(fri_step_list) = log2(n_steps) + 4`

**What you need to solve:**
For 131,072 steps (2^17):
```
log2(131072) = 17
So: log2(last_layer_degree_bound) + Σ(fri_step_list) = 17 + 4 = 21
```

**Example valid combinations:**
- `last_layer_degree_bound=32 (log2=5)` + `fri_step_list=[4,4,4,4]` (sum=16) = 5+16 = 21 ✓
- `last_layer_degree_bound=64 (log2=6)` + `fri_step_list=[3,4,4,4]` (sum=15) = 6+15 = 21 ✓
- `last_layer_degree_bound=128 (log2=7)` + `fri_step_list=[3,3,4,4]` (sum=14) = 7+14 = 21 ✓

**Your task:**
1. Verify this equation is correct (search for "STARK FRI" + "degree bound" + "step list")
2. List 5-10 valid parameter combinations for 131,072 steps
3. Understand the tradeoff: bigger last_layer_degree_bound = faster proof generation but higher memory

**Research resources:**
```bash
# Search for:
# - "Stone prover" + "FRI parameters"
# - "STARK" + "last_layer_degree_bound"
# - "cpu_air_prover" + "fri_step_list"
# - Starkware documentation on FRI
# - Cairo/Starknet community forums

# Check Stone repo:
# https://github.com/starkware-libs/stone-prover
# Look for: README, parameters.py, cpu_air_prover help
```

**Expected output:** Document listing 5-10 valid parameter sets to test

**Deliverable:** `STONE_DEBUG_STEP1_FRI_PARAMETERS.md`

---

### Task 1.2: Check Your Stone Binary Version

**Goal:** Confirm cpu_air_prover version and understand Signal 6 error

**Steps:**

1. **Check binary info:**
```bash
cd /opt/obsqra.starknet/stone-prover
file build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover
# Should show: ELF 64-bit executable
```

2. **Try to get help/version:**
```bash
/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover --help 2>&1 | head -50
/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover --version 2>&1
```

3. **Check git history of build:**
```bash
cd /opt/obsqra.starknet/stone-prover
git log --oneline -20
git log --all --grep="FRI" --oneline | head -10
git log --all --grep="Signal 6" --oneline | head -10
git log --all --grep="parameters" --oneline | head -10
```

4. **Look for recent fixes:**
```bash
cd /opt/obsqra.starknet/stone-prover
# Check if there's a newer commit after Dec 12
git log --since="2025-12-12" --until="2026-01-26" --oneline
```

5. **Check if there are known issues:**
```bash
cd /opt/obsqra.starknet/stone-prover
# List all git tags (version markers)
git tag -l | sort -V | tail -20
# Your build was around what tag?
git describe --tags --contains $(git rev-list -1 --before="2025-12-13" HEAD)
```

**Research:**
- Visit Stone prover GitHub issues: search for "Signal 6"
- Look for issues about "FRI parameters"
- Check CHANGELOG for recent fixes

**Expected output:** Binary version, commit hash, any known issues

**Deliverable:** `STONE_DEBUG_STEP2_BINARY_INFO.md`

---

### Task 1.3: Understand Signal 6 Error

**What is Signal 6?**
- SIGABRT: Assertion failure or abort() call
- Means: cpu_air_prover hit an assertion/guard that failed

**Why it happens:**
1. FRI parameters violate invariant (formula wrong or math error)
2. Out of memory (trace too big for parameters)
3. Constraint system mismatch (layout doesn't match trace)
4. Integer overflow (felts don't fit field modulus)

**How to debug:**

1. **Capture stderr (cpu_air_prover prints errors before aborting):**
```bash
# Create test script
cat > /opt/obsqra.starknet/test_fri_params.sh << 'EOF'
#!/bin/bash

PROVER="/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover"
TRACE_FILE="/path/to/execution_trace.json"

# Try parameter combination 1
echo "=== Testing: last_layer=32, fri=[4,4,4,4] ==="
$PROVER \
  --input_file $TRACE_FILE \
  --output_file /tmp/proof1.json \
  --parameter_file /opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json \
  --last_layer_degree_bound 32 \
  --fri_step_list [4,4,4,4] \
  2>&1 | tee /tmp/test1.log

# Try parameter combination 2
echo "=== Testing: last_layer=64, fri=[3,4,4,4] ==="
$PROVER \
  --input_file $TRACE_FILE \
  --output_file /tmp/proof2.json \
  --parameter_file /opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json \
  --last_layer_degree_bound 64 \
  --fri_step_list [3,4,4,4] \
  2>&1 | tee /tmp/test2.log

# Compare errors
echo "=== ERROR ANALYSIS ==="
grep -i "error\|abort\|assert\|out of memory" /tmp/test*.log
EOF

chmod +x /opt/obsqra.starknet/test_fri_params.sh
```

2. **Run with strace to see system calls before abort:**
```bash
strace -e trace=write,abort $PROVER ... 2>&1 | tail -100
# Will show what went wrong at syscall level
```

3. **Check if it's memory:**
```bash
# Get memory info
free -h
# Run with memory limit
ulimit -v 8589934592  # 8GB limit
$PROVER ...
```

**Expected output:** Specific error message from cpu_air_prover or system

**Deliverable:** `STONE_DEBUG_STEP3_SIGNAL6_ANALYSIS.md`

---

## Phase 2: Systematic Testing (Tuesday-Wednesday - 12 hours)

### Task 2.1: Test All Valid FRI Parameter Combinations

Create a systematic test harness:

```bash
cat > /opt/obsqra.starknet/test_all_fri_params.py << 'EOF'
#!/usr/bin/env python3

import subprocess
import json
import time
import sys

PROVER_BIN = "/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover"
PARAMS_FILE = "/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json"
TRACE_FILE = sys.argv[1]  # path to execution trace

# Valid parameter combinations for 131,072 steps (log2=17, target=21)
test_cases = [
    {"last_layer": 32, "fri_steps": [4, 4, 4, 4], "note": "smallest last_layer"},
    {"last_layer": 64, "fri_steps": [3, 4, 4, 4], "note": "balanced"},
    {"last_layer": 128, "fri_steps": [3, 3, 4, 4], "note": "larger last_layer"},
    {"last_layer": 256, "fri_steps": [3, 3, 3, 3], "note": "uniform fri_steps"},
    {"last_layer": 512, "fri_steps": [2, 3, 4, 4], "note": "high last_layer"},
    {"last_layer": 1024, "fri_steps": [2, 3, 3, 4], "note": "very high last_layer"},
]

results = []

for i, test in enumerate(test_cases):
    print(f"\n{'='*60}")
    print(f"Test {i+1}/{len(test_cases)}: {test['note']}")
    print(f"last_layer_degree_bound={test['last_layer']}, fri_step_list={test['fri_steps']}")
    print(f"{'='*60}")
    
    cmd = [
        PROVER_BIN,
        "--input_file", TRACE_FILE,
        "--output_file", f"/tmp/proof_{i}.json",
        "--parameter_file", PARAMS_FILE,
        "--last_layer_degree_bound", str(test['last_layer']),
        "--fri_step_list", json.dumps(test['fri_steps']),
    ]
    
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    
    test['elapsed_seconds'] = elapsed
    test['exit_code'] = result.returncode
    test['success'] = result.returncode == 0
    
    if result.returncode == 0:
        print(f"✅ SUCCESS in {elapsed:.1f}s")
        # Get proof size
        try:
            import os
            proof_size = os.path.getsize(f"/tmp/proof_{i}.json") / (1024*1024)
            test['proof_size_mb'] = proof_size
            print(f"   Proof size: {proof_size:.1f} MB")
        except:
            pass
    else:
        print(f"❌ FAILED (exit code {result.returncode})")
        print("STDERR:", result.stderr[-200:] if result.stderr else "none")
        print("STDOUT:", result.stdout[-200:] if result.stdout else "none")
    
    results.append(test)

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
successful = [r for r in results if r['success']]
print(f"Passed: {len(successful)}/{len(results)}")
if successful:
    print("\nWorking parameter sets:")
    for r in successful:
        print(f"  - last_layer={r['last_layer']}, fri_steps={r['fri_steps']} ({r['elapsed_seconds']:.1f}s, {r.get('proof_size_mb', '?')} MB)")
EOF

chmod +x /opt/obsqra.starknet/test_all_fri_params.py
```

**Run it:**
```bash
python3 /opt/obsqra.starknet/test_all_fri_params.py /path/to/execution_trace.json
# Will test all combinations and show which ones work
```

**Expected output:** Table showing which FRI parameters work, latencies, proof sizes

**Deliverable:** `STONE_DEBUG_STEP4_FRI_TESTING_RESULTS.md`

---

### Task 2.2: If All Parameters Fail

If none of the valid FRI parameters work, the issue is not parameters. Investigate:

1. **Check trace file validity:**
```bash
python3 << 'EOF'
import json
trace_file = "/path/to/execution_trace.json"
with open(trace_file) as f:
    trace = json.load(f)
    
print(f"Trace keys: {trace.keys()}")
print(f"Trace size: {len(json.dumps(trace)) / (1024*1024):.1f} MB")
print(f"Memory rows: {len(trace.get('memory', {}))}")
print(f"Register rows: {len(trace.get('registers', {}))}")
print(f"Number of steps: {len(trace.get('steps', []))}")
EOF
```

2. **Check if layout mismatch:**
```bash
# Try with different layouts
$PROVER ... --layout small   # vs recursive
$PROVER ... --layout all_cairo
```

3. **Check memory limits:**
```bash
# How much RAM is available?
free -h
# How much does trace consume?
du -h /path/to/execution_trace.json
# Rule of thumb: proof generation needs ~10x trace size in RAM
```

4. **Check if it's a version issue:**
```bash
# Maybe newer Stone binary available?
cd /opt/obsqra.starknet/stone-prover
git fetch origin main
git log --oneline main -20
# Is there a newer version? Can you rebuild?
bazelisk build //src/starkware/main/cpu:cpu_air_prover
```

**Expected output:** Root cause identified (layout? memory? version?)

---

## Phase 3: Successful FRI Parameters → Build Pipeline (Wednesday-Thursday - 12 hours)

**Assuming one FRI parameter set works...**

### Task 3.1: Create StoneProverService

```python
# backend/app/services/stone_prover_service.py

import subprocess
import json
import os
import tempfile
import logging
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StoneProof:
    verifier_config: dict
    stark_proof: dict
    trace_size_mb: float
    proof_size_mb: float
    latency_ms: float

class StoneProverService:
    def __init__(self):
        self.prover_bin = Path("/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover")
        self.params_file = Path("/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json")
        
        # These are the FRI parameters you discovered work
        self.fri_step_list = [4, 4, 4, 4]  # CHANGE TO YOUR WORKING PARAMS
        self.last_layer_degree_bound = 32   # CHANGE TO YOUR WORKING PARAMS
    
    def generate_proof(self, allocation_data: dict) -> StoneProof:
        """
        Generate a Stone proof for an allocation
        """
        import time
        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Serialize allocation to cairo-run input
            input_json = self._serialize_allocation(allocation_data)
            input_file = Path(tmpdir) / "input.json"
            input_file.write_text(json.dumps(input_json))
            
            # Step 2: Compile Risk Engine to Sierra
            sierra_file = self._compile_risk_engine()
            
            # Step 3: Generate trace via cairo-run
            trace_file = Path(tmpdir) / "trace.json"
            memory_file = Path(tmpdir) / "memory.bin"
            self._execute_trace(sierra_file, input_file, trace_file, memory_file)
            
            # Step 4: Generate proof via cpu_air_prover
            proof_file = Path(tmpdir) / "proof.json"
            self._run_cpu_air_prover(trace_file, proof_file)
            
            # Step 5: Deserialize proof
            proof_json = json.loads(proof_file.read_text())
            verifier_config, stark_proof = self._deserialize_proof(proof_json)
            
            elapsed = time.time() - start_time
            
            return StoneProof(
                verifier_config=verifier_config,
                stark_proof=stark_proof,
                trace_size_mb=os.path.getsize(trace_file) / (1024*1024),
                proof_size_mb=os.path.getsize(proof_file) / (1024*1024),
                latency_ms=elapsed * 1000
            )
    
    def _serialize_allocation(self, allocation_data: dict) -> dict:
        """
        Serialize (amount, token, recipient) into cairo-run input format
        """
        amount = allocation_data["amount"]  # int
        token = allocation_data["token"]     # hex address
        recipient = allocation_data["recipient"]  # hex address
        
        # Convert to felts
        def to_felt(val):
            if isinstance(val, str):
                val = int(val, 16) if val.startswith("0x") else int(val)
            return val % (2**252 + 27742317884829)  # Cairo field modulus
        
        # u256 as two 128-bit felts
        amount_low = amount & ((1 << 128) - 1)
        amount_high = amount >> 128
        
        token_felt = to_felt(token)
        recipient_felt = to_felt(recipient)
        
        return {
            "amount_low": hex(amount_low),
            "amount_high": hex(amount_high),
            "token": hex(token_felt),
            "recipient": hex(recipient_felt),
        }
    
    def _compile_risk_engine(self) -> Path:
        """
        Compile risk_engine.cairo to Sierra
        Returns: path to sierra file
        """
        sierra_cache = Path("/tmp/risk_engine.sierra")
        if sierra_cache.exists():
            logger.info("Using cached sierra")
            return sierra_cache
        
        logger.info("Compiling risk_engine.cairo to Sierra...")
        result = subprocess.run(
            ["scarb", "build", "--target", "sierra"],
            cwd=Path("/opt/obsqra.starknet/contracts"),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Scarb build failed: {result.stderr}")
        
        # Find generated sierra file
        # (Scarb outputs to target/dev/)
        sierra_files = list(Path("/opt/obsqra.starknet/contracts/target/dev/").glob("*.sierra"))
        if not sierra_files:
            raise RuntimeError("No .sierra file generated")
        
        sierra_file = sierra_files[0]
        sierra_cache.write_text(sierra_file.read_text())
        return sierra_cache
    
    def _execute_trace(self, sierra_file: Path, input_file: Path, trace_file: Path, memory_file: Path):
        """
        Run cairo-run in proof mode to generate execution trace
        """
        logger.info("Running cairo-run to generate execution trace...")
        
        result = subprocess.run([
            "cairo-run",
            "--proof_mode",
            "--program", str(sierra_file),
            "--air_public_input", input_file.read_text(),
            "--trace_file", str(trace_file),
            "--memory_file", str(memory_file),
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"cairo-run failed: {result.stderr}")
        
        logger.info(f"Trace generated: {os.path.getsize(trace_file) / (1024*1024):.1f} MB")
    
    def _run_cpu_air_prover(self, trace_file: Path, proof_file: Path):
        """
        Run cpu_air_prover to generate STARK proof
        """
        logger.info("Running cpu_air_prover...")
        
        result = subprocess.run([
            str(self.prover_bin),
            "--input_file", str(trace_file),
            "--output_file", str(proof_file),
            "--parameter_file", str(self.params_file),
            "--last_layer_degree_bound", str(self.last_layer_degree_bound),
            "--fri_step_list", json.dumps(self.fri_step_list),
            "--generate_annotations",  # IMPORTANT: must annotate
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"cpu_air_prover stderr: {result.stderr}")
            raise RuntimeError(f"cpu_air_prover failed with code {result.returncode}")
        
        logger.info(f"Proof generated: {os.path.getsize(proof_file) / (1024*1024):.1f} MB")
    
    def _deserialize_proof(self, proof_json: dict) -> tuple:
        """
        Parse proof JSON into VerifierConfiguration + StarkProofWithSerde
        """
        # Verifier config: 4 felts (layout, hasher, stone_version, memory_verification)
        verifier_config = {
            "layout": self._string_to_felt("recursive"),
            "hasher": self._string_to_felt("keccak_160_lsb"),
            "stone_version": self._string_to_felt("stone5"),
            "memory_verification": self._string_to_felt("strict"),
        }
        
        # StarkProofWithSerde: complex nested structure from proof_json
        stark_proof = {
            "config": proof_json.get("config", {}),
            "public_input": proof_json.get("public_input", {}),
            "unsent_commitment": proof_json.get("unsent_commitment", {}),
            "witness": proof_json.get("witness", []),
        }
        
        return verifier_config, stark_proof
    
    def _string_to_felt(self, s: str) -> int:
        """Convert ASCII string to felt"""
        return int.from_bytes(s.encode(), byteorder='big')
```

**Then integrate into risk_engine.py:**

```python
# In allocation_proposal_create()

from app.services.stone_prover_service import StoneProverService

stone_service = StoneProverService()
proof = stone_service.generate_proof(allocation_data)

# Verify proof
integrity_result = await integrity_service.verify_proof_full_and_register_fact(
    verifier_config=proof.verifier_config,
    stark_proof=proof.stark_proof
)

# Log metrics
logger.info(f"Stone proof: {proof.latency_ms:.0f}ms, trace={proof.trace_size_mb:.1f}MB, proof={proof.proof_size_mb:.1f}MB")
```

**Deliverable:** Working StoneProverService that generates verified proofs

---

### Task 3.2: Integrate with Backend

```python
# Update backend/app/api/routes/risk_engine.py

@router.post("/allocations/propose")
async def allocation_proposal_create(
    payload: AllocationProposalPayload,
    db: Session = Depends(get_db),
):
    """
    Create allocation proposal with Stone local proof
    """
    allocation_data = {
        "amount": payload.amount,
        "token": payload.token,
        "recipient": payload.recipient,
    }
    
    # Generate proof
    try:
        proof = stone_service.generate_proof(allocation_data)
        proof_status = "generating"
        proof_source = "stone_local"
    except Exception as e:
        logger.error(f"Stone proof generation failed: {e}")
        # Could fallback to Atlantic here
        proof = None
        proof_status = "failed"
        proof_source = "stone_local_failed"
    
    # Create ProofJob
    proof_job = ProofJob(
        allocation_id=allocation.id,
        proof_source=proof_source,
        proof_status=proof_status,
        stone_latency_ms=proof.latency_ms if proof else None,
        stone_trace_size=proof.trace_size_mb if proof else None,
        stone_proof_size=proof.proof_size_mb if proof else None,
    )
    db.add(proof_job)
    db.commit()
    
    # Verify if proof generated
    if proof:
        try:
            result = await integrity_service.verify_proof_full_and_register_fact(
                verifier_config=proof.verifier_config,
                stark_proof=proof.stark_proof,
            )
            proof_job.l2_verified_at = result["verified_at"]
            proof_job.proof_status = "verified"
        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            proof_job.proof_status = "failed"
    
    db.commit()
    
    return {
        "allocation_id": allocation.id,
        "proof_job_id": proof_job.id,
        "proof_status": proof_job.proof_status,
        "latency_ms": proof.latency_ms if proof else None,
    }
```

---

## Phase 4: Benchmarking & Comparison (Friday - 8 hours)

### Task 4.1: Test 100 Allocations with Stone

```python
# test_stone_benchmark.py

import asyncio
import time
import statistics
from app.services.stone_prover_service import StoneProverService

async def benchmark_stone(num_allocations=100):
    service = StoneProverService()
    results = {
        "latencies": [],
        "trace_sizes": [],
        "proof_sizes": [],
        "successes": 0,
        "failures": 0,
    }
    
    for i in range(num_allocations):
        allocation = {
            "amount": (i + 1) * 1000 * 10**18,  # Variable amounts
            "token": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",  # USDC on Starknet
            "recipient": f"0x{(i+1):064x}",
        }
        
        try:
            proof = service.generate_proof(allocation)
            results["latencies"].append(proof.latency_ms)
            results["trace_sizes"].append(proof.trace_size_mb)
            results["proof_sizes"].append(proof.proof_size_mb)
            results["successes"] += 1
            print(f"✓ Allocation {i+1}: {proof.latency_ms:.0f}ms")
        except Exception as e:
            results["failures"] += 1
            print(f"✗ Allocation {i+1}: {e}")
    
    # Analysis
    print("\n" + "="*60)
    print("STONE BENCHMARK RESULTS")
    print("="*60)
    print(f"Success rate: {results['successes']}/{num_allocations}")
    if results['latencies']:
        print(f"Latency: avg={statistics.mean(results['latencies']):.0f}ms, median={statistics.median(results['latencies']):.0f}ms, max={max(results['latencies']):.0f}ms")
        print(f"Trace size: avg={statistics.mean(results['trace_sizes']):.1f}MB")
        print(f"Proof size: avg={statistics.mean(results['proof_sizes']):.1f}MB")
        print(f"Total time: {sum(results['latencies'])/1000:.0f}s for {num_allocations} proofs")
    
    return results

if __name__ == "__main__":
    asyncio.run(benchmark_stone(100))
```

### Task 4.2: Compare with Atlantic Baseline

Once you get Atlantic credentials, run same 100 allocations with Atlantic and compare.

**Comparison table:**

| Metric | Stone Local | Atlantic |
|--------|-------------|----------|
| Avg latency | __ms | __ms |
| Success rate | ___ % | 100% |
| Trace size | __MB | N/A |
| Proof size | __MB | __MB |
| Cost | $0 | $0.001-0.01/proof |
| Debuggability | Excellent | Poor |
| Operational | High (tuning) | Low (managed) |

---

## Decision Tree: When to Stop

```
✅ FRI parameters found + proofs generate?
    ├─ YES:
    │   ├─ Proofs verify on Integrity?
    │   │   ├─ YES: Continue to Phase 3 (full implementation)
    │   │   └─ NO: Debug proof format / verifier mismatch (1 day)
    │   │       ├─ Fixed? Continue to Phase 3
    │   │       └─ Unfixable? ABORT & use Atlantic instead
    │   │
    │   └─ Latency slower than Atlantic (>20s)?
    │       ├─ YES: Still build for learning, but use Atlantic for prod
    │       └─ NO: Build & use Stone as primary
    │
    └─ NO: Can't find working parameters
        └─ ABORT after 3 days max & switch to Atlantic
```

---

## Success Criteria

**Phase 1 (FRI Research):** 
- ✅ Valid FRI parameter combinations documented
- ✅ Binary version confirmed
- ✅ Signal 6 root cause identified

**Phase 2 (Systematic Testing):**
- ✅ At least one FRI parameter set generates proof without Signal 6
- ✅ Full trace produces proof JSON

**Phase 3 (Pipeline Build):**
- ✅ StoneProverService generates proofs from allocations
- ✅ Proofs deserialize to VerifierConfiguration + StarkProofWithSerde
- ✅ Proofs verify on Integrity contract
- ✅ Latency measured: ___ ms (compare to Atlantic's 10-20s)

**Phase 4 (Benchmarking):**
- ✅ 100 allocations tested
- ✅ Comparison table completed
- ✅ Decision made: Stone for production, or Atlantic as primary?

---

## Abort Criteria (When to Switch to Atlantic)

After **3 days of Phase 1-2**, if:
- No FRI parameters work
- Root cause is memory/version incompatibility with no fix
- Stone binary is outdated and can't rebuild

→ Stop, acknowledge it doesn't work for your full trace, switch to Atlantic for the next week

You'll still have learned enormously about STARK proofs and the Stone pipeline.

---

## Resources & References

**FRI Parameter Learning:**
- Search: "STARK FRI folding" + "last layer degree"
- Resource: https://github.com/starkware-libs/stone-prover/blob/main/README.md
- Resource: Starkware Cairo documentation

**Debugging:**
- `strace` to see system calls before abort
- `gdb` to debug cpu_air_prover (if you're advanced)
- Inspect `/tmp/test*.log` for error messages

**Community Help:**
- Starknet Discord #contracts channel
- Herodotus support (mention FRI parameter issues)
- Stone prover GitHub issues

---

## Your Commitment

You're choosing to:
1. Spend 5 focused days understanding STARK proofs deeply
2. Risk that it doesn't work for your full trace
3. Gain independence + $0 proof costs if it works
4. Have a fallback (Atlantic) if it doesn't

**That's a good risk.** The worst case is you learn a ton and use Atlantic. The best case is you own your proving stack.

Let's go build it.

