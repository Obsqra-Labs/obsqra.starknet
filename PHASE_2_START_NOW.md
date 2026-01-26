# Phase 2 Start: Your Commands

## FIND YOUR TRACE FILE

```bash
# Option 1: Search
find /opt/obsqra.starknet -name "*trace*" -type f -not -path "*/node_modules/*" 2>/dev/null | head -20

# Option 2: Check December logs
grep -i "trace\|execution" /opt/obsqra.starknet/DEV_LOG.md | tail -30

# Option 3: Check common locations
ls -la /tmp/*trace*
ls -la /opt/obsqra.starknet/tmp/*trace*
ls -la /opt/obsqra.starknet/backend/*trace*
```

**When you find it, note the full path.**

---

## RUN THE TEST

Replace `<TRACE_FILE>` with your actual path:

```bash
python3 /opt/obsqra.starknet/test_all_fri_params.py /full/path/to/execution_trace.json
```

**What this does:**
- Tests 17 FRI parameter combinations (one at a time)
- Shows real-time progress for each test
- Captures timing, proof size, error messages
- Saves logs to `/tmp/stone_fri_tests/`
- Prints summary at the end

**Expected runtime:** 5-30 minutes (depends on trace size)

---

## WATCH PROGRESS

In another terminal, monitor resources:

```bash
watch -n 1 'echo "=== MEMORY ===" && free -h && echo "=== DISK ===" && df -h /tmp && echo "=== PROCESSES ===" && top -b -n 1 | grep cpu_air'
```

---

## CHECK RESULTS

While tests run or after:

```bash
# See what's in test directory
ls -lh /tmp/stone_fri_tests/

# See summary (JSON format)
cat /tmp/stone_fri_tests/results.json | jq .

# See specific test log
cat /tmp/stone_fri_tests/test_1.log

# Find errors
grep -i "error\|abort\|signal" /tmp/stone_fri_tests/test_*.log

# Count successes
ls -1 /tmp/stone_fri_tests/proof_*.json | wc -l
```

---

## IF TESTS SUCCEED ✅

You'll see output like:

```
======================================================================
SUMMARY: 17 Tests
======================================================================

✅ Passed: 3/17
❌ Failed: 14/17

📊 WORKING PARAMETER SETS:
  last_layer=  64, fri_steps=[3, 4, 4, 4], time=   8.5s, size=  5.2MB
  last_layer= 128, fri_steps=[3, 3, 4, 4], time=   9.1s, size=  5.8MB
  last_layer= 512, fri_steps=[3, 3, 3, 3], time=   7.2s, size=  4.9MB
```

**Then:** Go to PHASE_3_BUILD_PROVER.md (will be created)

---

## IF ALL TESTS FAIL ❌

Check error logs:

```bash
# Show all unique errors
cat /tmp/stone_fri_tests/test_*.log | grep -i "error\|abort" | sort -u

# Show last few lines of first failure
cat /tmp/stone_fri_tests/test_1.log | tail -20

# Check if it's memory
cat /tmp/stone_fri_tests/test_1.log | grep -i "memory"
```

**Then:** Debug using PHASE_2_QUICK_START.md troubleshooting section

---

## SYSTEM INFO (FOR REFERENCE)

```bash
# Check available RAM (need ~10x trace size)
free -h

# Check trace size
du -h /path/to/execution_trace.json

# Check disk space
df -h /tmp

# Check CPU cores
nproc

# Check Stone binary is executable
/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover --help
```

---

## ABORT DECISION POINT

If after 8 hours (by tomorrow night):

```bash
# Tests still failing? Still debugging?
# Check how much time you've spent:
find /tmp/stone_fri_tests -type f -newer /opt/obsqra.starknet/test_all_fri_params.py
# Shows all files created during testing

# Decision:
# - Give up on Stone? → Use Atlantic instead (1 hour to wire)
# - Keep debugging? → How much time left in your 5-day window?
```

---

## REPORT TEMPLATE (When Done)

Copy this and fill it out:

```
PHASE 2 TEST RESULTS
====================

Trace file used: [path]
Trace size: [MB]
Available RAM: [GB]

Test command: python3 /opt/obsqra.starknet/test_all_fri_params.py [path]

Results:
✅ Passed: [number]/17
❌ Failed: [number]/17

Working parameters:
  - last_layer=???, fri_steps=[?,?,?,?], time=??s, proof=??MB
  - last_layer=???, fri_steps=[?,?,?,?], time=??s, proof=??MB

Fastest: [which combination]
Smallest proof: [which combination]

Decision: [Proceed to Phase 3 / Keep debugging / Abort to Atlantic]

Notes:
[Any patterns, errors, or observations]
```

---

## YOU'RE READY!

1. Find trace file
2. Run tests
3. Come back with results

**Go!**

```bash
python3 /opt/obsqra.starknet/test_all_fri_params.py <trace_file>
```

