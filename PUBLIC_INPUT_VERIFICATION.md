# Public Input Verification - User's Critical Check

**Date**: 2026-01-26  
**Status**: Verifying actual public input from failing proof

---

## User's Critical Insight

**If public input was `small + ecdsa`, Integrity recursive would fail at builtin gate, not OODS.**

Since we passed builtin validation and got to OODS, the verifier must be seeing:
- `recursive + bitwise` (compatible builtin set)

This means either:
1. We're looking at wrong public input (from different run/path)
2. The failing proof is not the one that produced that public input
3. The actual public input IS `recursive + bitwise` and issue is deeper

---

## Verification Steps

### Step 1: Find Failing Proof Directory
- Locate the exact `/tmp/risk_stone_*` directory from the failing run
- Check timestamps to ensure it's the correct run

### Step 2: Check Public Input
- Open `risk_public.json` from that exact run
- Verify:
  - `layout` is really `recursive`
  - `memory_segments` contains `bitwise`, not `ecdsa`

### Step 3: Interpret Results

**If it says `small + ecdsa`:**
- Found the cause: wrong layout/builtin
- Fix: Ensure `--layout recursive` is applied
- Verify running bitwise version of program

**If it says `recursive + bitwise`:**
- Cause is NOT layout/builtin
- Mismatch is deeper: AIR/public_input consistency
- Next: Diff full public_input against Integrity recursive example

---

## Status

Checking actual public input from failing proof run...
