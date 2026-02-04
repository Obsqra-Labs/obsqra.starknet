# AIR Mismatch Analysis - User's Corrected Assessment

**Date**: 2026-01-26  
**Status**: Following user's corrected analysis

---

## User's Key Insight

**The OODS mismatch is NOT because of structure differences** - it's because:
- The verifier reconstructs a different composition polynomial from our public input
- Than what the proof claims

**Root Cause**: The AIR in Integrity's recursive verifier is **NOT the same AIR** that Stone used to generate our proof.

---

## What We Found (Concrete Diffs)

### ✅ Structure Matches
- Same top-level keys
- Same public_input keys  
- Same builtin set: `bitwise, pedersen, range_check, output`

### ⚠️ Values Differ (Expected for Different Program)
- `n_steps`: 65536 (ours) vs 16384 (example)
- `rc_min/rc_max`: 0/32778 (ours) vs 32762/32769 (example)
- `memory_segments` ranges: All different
- `public_memory` length: 281 vs 46
- `proof_parameters`: Different FRI step list, n_queries, PoW bits

**These diffs are NOT proof of failure** - they should differ for different programs.

---

## What OODS Mismatch Actually Means

If the Stone proof is internally valid, OODS should pass.

**OODS mismatch means one of these is wrong**:
1. **Verifier doesn't match the AIR your proof assumes** (most likely)
2. **Public input is structurally different than what verifier expects** (still likely)
3. **Serialization mismatch** (less likely, but possible)

---

## Likely Root Cause

**We're proving a Cairo0 program with recursive layout, but the AIR in Integrity's recursive verifier is not the same AIR that Stone used to generate our proof.**

This yields OODS mismatch even though the proof "looks" fine.

---

## Diagnostic Plan (User's Recommendations)

### Step 1: Verify Canonical Recursive Proof ✅
**Goal**: Test if our deployment/config/verifier is correct

**Action**: Register and verify Integrity's recursive example proof through our FactRegistry
- If it fails → deployment/config/verifier is wrong
- If it passes → our proof/public input is wrong

### Step 2: Run Stone's Local Verifier ✅
**Goal**: Test if our proof/public input is internally consistent

**Action**: Run Stone's local verifier on our proof
- If it fails locally → proof/public input mismatch
- If it passes locally but fails on-chain → serializer or verifier mismatch

### Step 3: Compare Public Input Schema ✅
**Goal**: Ensure our public input matches Integrity's expected schema

**Action**: Compare our `cairo-run` output public input against the example's public input schema for recursive
- Confirm ordering/segments exactly match

### Step 4: Align Cairo Toolchain Version ✅
**Goal**: Ensure we're using the same Cairo version as Integrity examples

**Action**: Check and align Cairo toolchain version
- A mismatch here is enough to cause OODS

---

## Next Actions

1. **Test canonical proof** → Verify deployment/config
2. **Run Stone verifier** → Test proof consistency
3. **Compare schemas** → Verify public input structure
4. **Check versions** → Align Cairo toolchain

---

**Status**: Following user's corrected analysis. The issue is likely AIR mismatch, not structure differences.
