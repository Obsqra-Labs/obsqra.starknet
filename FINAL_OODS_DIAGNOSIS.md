# Final OODS Diagnosis - Actual Failing Proof

**Date**: 2026-01-26  
**Status**: Found actual failing proof, diagnosing OODS mismatch

---

## ✅ Actual Failing Proof Found

### Proof Details
- **Directory**: `/tmp/risk_stone_nttstalm` (23:12:34)
- **Layout**: `recursive` ✅
- **Builtins**: `bitwise, execution, output, pedersen, program, range_check` ✅
- **n_steps**: `65536`
- **public_memory**: `281` entries

### Why This is the Failing Proof
- Has `recursive + bitwise` (passes builtin validation)
- Reached OODS validation (passed builtin gate)
- Failed at OODS (composition polynomial mismatch)

---

## Comparison with Integrity Example

### ✅ Structure Matches
- Layout: `recursive` ✅
- Builtin set: `bitwise, pedersen, range_check, output, program, execution` ✅
- Field presence: All required fields present ✅

### ⚠️ Values Differ (Expected for Different Program)
- `n_steps`: `65536` (ours) vs `16384` (example)
- `rc_min/rc_max`: `0/32778` (ours) vs `32762/32769` (example)
- `memory_segments` ranges: All different
- `public_memory`: `281` entries (ours) vs `46` (example)

**These diffs are NOT proof of failure** - they should differ for different programs.

---

## OODS Mismatch Root Cause

**The verifier reconstructs a different composition polynomial from our public input than what the proof claims.**

This means:
1. **Stone generated proof** using one AIR configuration
2. **Integrity verifier expects** a different AIR configuration
3. **AIR mismatch** → Different composition polynomial → OODS mismatch

---

## Possible Causes (User's Assessment)

### 1. AIR Mismatch (Most Likely)
- Stone's AIR doesn't match Integrity's canonical recursive AIR
- Different constraint degrees, interaction elements, or AIR parameters

### 2. Public Input Structure Mismatch (Still Likely)
- Even though structure looks correct, subtle differences in:
  - Segment ordering
  - Field ordering
  - Memory segment structure
  - Can cause verifier to reconstruct differently

### 3. Serialization Mismatch (Less Likely)
- Proof serializer may not match Integrity's expected format exactly

---

## Next Steps (User's Recommendations)

### Step 1: Verify Canonical Recursive Proof ✅
- Test Integrity's recursive example through our FactRegistry
- If fails → deployment/config issue
- If passes → our proof/public input issue

### Step 2: Compare Public Input Schema ✅
- Diff our public input against Integrity example
- Check field-by-field for subtle differences
- Verify segment ordering, field ordering

### Step 3: Align Cairo Toolchain Version
- Check Cairo version used by Integrity examples
- Align our toolchain version
- Version mismatch can cause OODS

---

**Status**: ✅ Found actual failing proof. It has `recursive + bitwise` as expected. The OODS mismatch is a deeper AIR/public_input consistency issue, not a layout/builtin mismatch.
