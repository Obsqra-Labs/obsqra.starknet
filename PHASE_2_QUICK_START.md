# Stone Pipeline Phase 2: Quick Reference Card

## Current Status
- ✅ Phase 1 complete: FRI analysis, binary check, test tools ready
- 📍 You are here: Phase 2 - Run the tests
- ⏱️ Time: 1-4 hours for testing + debugging

---

## IMMEDIATE NEXT STEP

Find your execution trace file from December:

```bash
# Search for it
find /opt/obsqra.starknet -name "*trace*" -type f -not -path "*/node_modules/*" 2>/dev/null

# Or check DEV_LOG for the path
grep -i "trace" /opt/obsqra.starknet/DEV_LOG.md | tail -20
```

**Expected file name:** Something like `execution_trace.json`, `trace.json`, `all_cairo_trace.json`

---

## RUN THE TEST

Once you have the trace file:

```bash
python3 /opt/obsqra.starknet/test_all_fri_params.py /path/to/execution_trace.json
```

**This will:**
- Test 17 FRI parameter combinations
- Take 5 seconds to 5 minutes per test
- Show real-time progress
- Save detailed logs
- Print summary at end

---

## EXPECTED OUTPUT

### Success Case ✅
```
======================================================================
Test 1: last_layer=32, fri_steps=[4, 4, 4, 4]
======================================================================
✅ SUCCESS in 8.5s
   Proof size: 5.2 MB
   Log saved to: /tmp/stone_fri_tests/test_1.log
```

### Failure Case ❌
```
======================================================================
Test 2: last_layer=64, fri_steps=[3, 4, 4, 4]
======================================================================
❌ FAILED (exit code 134) in 2.3s
   Error: error: abort
   Log saved to: /tmp/stone_fri_tests/test_2.log
```

---

## IF TESTS SUCCEED ✅

You'll see output like:
```
SUMMARY
======================================================================
✅ Passed: 3/17
❌ Failed: 14/17

📊 WORKING PARAMETER SETS:
----------------------------------------------------------------------
  last_layer=  64, fri_steps=[3, 4, 4, 4], time=   8.5s, size=  5.2MB
  last_layer= 128, fri_steps=[3, 3, 4, 4], time=   9.1s, size=  5.8MB
  last_layer= 512, fri_steps=[3, 3, 3, 3], time=   7.2s, size=  4.9MB
```

**Next:** Proceed to Phase 3 - Build StoneProverService

---

## IF TESTS FAIL ❌

All 17 combinations fail with Signal 6 or same error:

1. **Check the logs:**
   ```bash
   ls -lh /tmp/stone_fri_tests/
   cat /tmp/stone_fri_tests/test_*.log | grep -i "error\|signal\|abort"
   ```

2. **Common issues & fixes:**

   **Error: "Unexpected number of interaction elements"**
   - This is expected (proof without annotations)
   - Our script uses `--generate_annotations`, should work
   - Check if flag is being passed correctly

   **Error: "memory" or "out of memory"**
   - Trace too large for available RAM
   - Check available: `free -h`
   - Check trace size: `du -h /path/to/trace.json`
   - Workaround: Use smaller trace or larger machine

   **Exit code 134 (SIGABRT):**
   - Assertion failure in cpu_air_prover
   - Could be FRI params, could be trace corruption
   - Try: `strace -e write /opt/obsqra.starknet/stone-prover/.../cpu_air_prover ... 2>&1 | tail -50`

   **Exit code 1 (generic error):**
   - Check stderr in log file for hints
   - Could be anything - need to read the error message carefully

3. **Decision point (after 4-8 hours of debugging):**
   ```
   Give up on Stone?
   → YES: Switch to Atlantic (1-hour wiring)
   → NO: Debug deeper (need specific understanding of error)
   ```

---

## IF YOU GET STUCK

Debug steps:

1. **Is the trace file valid?**
   ```bash
   file /path/to/trace.json
   python3 -c "import json; json.load(open('/path/to/trace.json'))" && echo "Valid JSON"
   ```

2. **Do you have enough memory?**
   ```bash
   free -h
   # Need at least: 10x trace file size in RAM
   ```

3. **Is the prover binary working at all?**
   ```bash
   /opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover --help
   # Should show some output or help message
   ```

4. **Check if trace generation itself failed**
   ```bash
   # Look in your December logs for how the trace was generated
   grep -i "cairo-run\|proof_mode" /opt/obsqra.starknet/DEV_LOG.md | tail -10
   # Retrace if needed: cairo-run --proof_mode ...
   ```

---

## ABORT CONDITION

If after **8 hours of Phase 2** (by tomorrow night):
- ❌ No working FRI parameters found
- ❌ Unable to diagnose root cause
- ❌ Error is fundamental (not a quick fix)

Then:
```
ABORT Stone pipeline
→ Switch to Atlantic (you have Herodotus call scheduled)
→ 1 hour to wire Atlantic API
→ Have real proofs next week
```

**You'll have learned:** How STARK proofs work, FRI folding, Cairo tracing. Worth it!

---

## WHAT TO REPORT BACK

Run the test and come back with:

1. **Command you ran:**
   ```
   python3 /opt/obsqra.starknet/test_all_fri_params.py <your_trace_file>
   ```

2. **Results summary:**
   ```
   Working parameters: [list them]
   Fastest: [which one was quickest]
   Proof sizes: [ranges]
   Any patterns in failures: [what you noticed]
   ```

3. **Decision:**
   ```
   Proceed to Phase 3? (YES/NO)
   Abort and switch to Atlantic? (YES/NO)
   ```

---

## KEY FILES

- `test_all_fri_params.py` - Main test script ← **RUN THIS**
- `test_fri_params.sh` - Alternative bash script
- `STONE_DEBUG_STEP1_FRI_PARAMETERS.md` - Valid parameter combos
- `STONE_DEBUG_STEP2_BINARY_INFO.md` - Binary analysis
- `PHASE_1_COMPLETE.md` - Detailed Phase 1 summary
- `/tmp/stone_fri_tests/` - Test results & logs ← **CHECK THESE**

---

## TIME ESTIMATE

| Activity | Time |
|----------|------|
| Find trace file | 10 min |
| Run tests | 5-10 min (if all fast) to 30 min (if slow) |
| Review results | 5 min |
| Quick debugging (if needed) | 30 min to 4 hours |
| **Total** | **1-4 hours** |

**Abort point:** If still failing at 8-hour mark, stop and use Atlantic.

---

## GO!

```bash
python3 /opt/obsqra.starknet/test_all_fri_params.py <trace_file>
```

Let me know the results. We'll build from there.
