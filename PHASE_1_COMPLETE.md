# Phase 1: Complete - Ready for Phase 2 Testing

**Status:** ✅ All Phase 1 analysis complete  
**Date:** January 25, 2026  
**Next Action:** Run FRI parameter tests against your execution trace

---

## What We Learned in Phase 1

### 1.1: FRI Parameters Equation ✅
- **For 131,072 steps:** `log2(last_layer) + Σ(fri_steps) = 21`
- **Created:** 17 valid parameter combinations to test
- **File:** `STONE_DEBUG_STEP1_FRI_PARAMETERS.md`

**Key insight:** Signal 6 likely occurs when parameters don't satisfy this equation. Your task: find which combinations work.

### 1.2: Stone Binary Analysis ✅
- **Binary:** 20 MB, built Dec 12 @ 20:10, ready to use
- **Version:** Stone v3.0 (HEAD commit: 1414a54)
- **Latest:** No newer version available (repo up-to-date)
- **Status:** No FRI/Signal 6 fixes since your December build
- **File:** `STONE_DEBUG_STEP2_BINARY_INFO.md`

**Key insight:** Your binary is current. The issue isn't an old version - it's likely FRI parameter tuning or trace content.

### 1.3: Testing Tools Ready ✅
Created two testing scripts:

**Option A: Python harness (recommended)**
```bash
python3 /opt/obsqra.starknet/test_all_fri_params.py <trace_file>
```
- Tests all 17 valid FRI combinations automatically
- Captures timing, proof size, errors
- Saves detailed logs to `/tmp/stone_fri_tests/`
- Outputs summary: which combinations work

**Option B: Bash script (for manual testing)**
```bash
chmod +x /opt/obsqra.starknet/test_fri_params.sh
/opt/obsqra.starknet/test_fri_params.sh <trace_file>
```
- Simpler, useful for debugging specific cases
- Direct access to error messages

---

## Phase 2: Next Steps (Today/Tomorrow)

### Before You Run Tests

1. **Find your execution trace file from December**
   - Should be named something like: `execution_trace.json`, `risk_engine_trace.json`, `trace.bin`, etc.
   - Search:
     ```bash
     find /opt/obsqra.starknet -name "*trace*" -o -name "*execution*" 2>/dev/null
     ```
   - Or check your December work logs for where it was saved

2. **Have 2-4 hours available**
   - Each test takes 5-30 seconds (depending on trace size)
   - 17 tests total = 5-10 minutes if all pass quickly
   - Could take longer if many fail (debugging time)

3. **Monitor system resources**
   - Check available RAM: `free -h`
   - Check disk space: `df -h /tmp`

### Run the Tests

```bash
# Replace with your actual trace file path
python3 /opt/obsqra.starknet/test_all_fri_params.py /path/to/execution_trace.json
```

The script will:
1. Validate the FRI equation for each parameter set
2. Run cpu_air_prover for each valid combination
3. Capture success/failure + error messages
4. Show summary: which parameters work
5. Save detailed logs to `/tmp/stone_fri_tests/`

### Expected Outcomes

**Best case (1-2 hours of work):**
- ✅ Find 1+ FRI parameter combinations that work
- ✅ Get proof JSON files
- ✅ Proceed to Phase 3 (build StoneProverService)

**Moderate case (1 day of debugging):**
- ❌ All parameters fail with same error
- ✅ Error message gives clue (memory? layout? version?)
- ✅ Implement fix or workaround
- ✅ Retry tests

**Worst case (abort after 2 days):**
- ❌ No working parameters despite troubleshooting
- ✅ Root cause unknown (could be: unfixable layout issue, binary incompatibility, trace corruption)
- → Switch to Atlantic (you have it as fallback)
- → You learned about STARK proofs anyway

---

## Decision Tree During Phase 2

```
Run python3 test_all_fri_params.py <trace_file>
    ↓
At least 1 parameter works?
    ├─ YES (✅):
    │   ├─ Proceed to Phase 3
    │   └─ Build StoneProverService with working parameters
    │
    └─ NO (❌): All parameters fail with Signal 6
        ├─ Check error message in /tmp/stone_fri_tests/test_*.log
        ├─ Error mentions: "memory"?
        │   └─ Increase swap / run on larger machine
        ├─ Error mentions: "assertion failed"?
        │   └─ Check trace file validity (might be corrupted)
        ├─ Error is silent (just exit code 134)?
        │   └─ Try with strace: see what breaks
        └─ Still stuck after 8 hours?
            └─ ABORT: Switch to Atlantic instead
```

---

## Files Created for Phase 1

| File | Purpose |
|------|---------|
| `STONE_DEBUG_STEP1_FRI_PARAMETERS.md` | FRI equation + 17 valid parameter combinations |
| `STONE_DEBUG_STEP2_BINARY_INFO.md` | Binary analysis + git history |
| `test_all_fri_params.py` | Automated test harness (recommended) |
| `test_fri_params.sh` | Bash testing script (alternative) |
| `OPTION_B_COMPLETE_ACTION_PLAN.md` | Full 5-day roadmap |
| `STONE_FEASIBILITY_ASSESSMENT.md` | Strategic comparison: Stone vs Atlantic |

---

## What You'll Report Back

After running Phase 2 tests, report:

1. **Which FRI parameters worked?**
   - Example: "last_layer=128, fri=[3,3,4,4] succeeded"

2. **Any patterns in failures?**
   - Example: "Smaller last_layer always fails, larger ones succeed"

3. **Timing data?**
   - Example: "Proof generation took 8.5 seconds, proof size 5 MB"

4. **Error messages?**
   - If any failures: paste the error from logs

5. **Ready to proceed?**
   - Can we build Phase 3 (StoneProverService)?
   - Or do we need to debug deeper?

---

## Commands You'll Need

**Phase 2 (Testing):**
```bash
# Main test
python3 /opt/obsqra.starknet/test_all_fri_params.py <trace_file>

# Check results
cat /tmp/stone_fri_tests/results.json

# Inspect specific test log
cat /tmp/stone_fri_tests/test_1.log
```

**If needed (debugging):**
```bash
# Check available memory
free -h

# Check trace file size
du -h <trace_file>

# Monitor CPU during test
watch -n 1 'top -b -n 1 | head -15'

# See test directory contents
ls -lh /tmp/stone_fri_tests/
```

---

## Timeline

- **Phase 1 (Today):** ✅ Complete - You're reading this
- **Phase 2 (Today/Tomorrow):** 1-4 hours of testing
  - If successful → 1 day debugging (if needed)
  - If stuck → declare abort, use Atlantic
- **Phase 3 (If Phase 2 succeeds):** 1 day building StoneProverService
- **Phase 4 (If all good):** 1 day benchmarking

**Total:** 2-5 days if successful, abort by day 3 if not working

---

## You're Ready!

Go find that execution trace file from December and run:

```bash
python3 /opt/obsqra.starknet/test_all_fri_params.py /your/trace/file.json
```

Come back with results. We'll build from there.

