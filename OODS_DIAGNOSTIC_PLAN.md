# OODS Diagnostic Plan - Based on Deep Analysis

**Date**: 2026-01-26  
**Status**: Following user's deep-dive recommendations

---

## Key Insight

We're past structure checks (builtin validation passed) and failing at **cryptographic consistency**. The OODS error means the verifier recomputed the composition polynomial at the OODS point and it didn't match the value claimed in our proof.

---

## Current Setup Analysis

### ✅ What We're Doing Right

1. **Canonical Public Input**: We're using `cairo-run` with `--air_public_input` and `--air_private_input` flags
   - This generates canonical CairoZero format
   - Not manually constructing public input

2. **Correct Cairo Execution**: Using `cairo-run --proof_mode` with proper layout

3. **Stone Prover**: Using `cpu_air_prover` with `--generate_annotations`

### ⚠️ Potential Issues

1. **AIR Mismatch**: Stone's CPU AIR expects canonical CairoZero format
   - Our program uses `bitwise` builtin (matches recursive layout)
   - But we're using `recursive` layout which may have different AIR expectations

2. **Layout Mismatch**: 
   - Config: `INTEGRITY_LAYOUT = "recursive"`
   - Our program: Uses `bitwise` (matches recursive)
   - But Stone's CPU AIR is for CairoZero, which may expect `small` layout

3. **Proof Serializer Version**: Need to verify serializer matches verifier contract version

---

## Diagnostic Steps (User's Recommendations)

### Step 1: Verify with Stone Verifier Locally ✅ (Priority)

**Goal**: If Stone verifier passes, bug is in Integrity serialization/config. If Stone verifier fails, bug is in trace/public input.

**Action**: 
- Find `cpu_air_verifier` binary
- Run it on our proof + public input
- Compare result with Stone's fibonacci example

### Step 2: Compare Public Input Structure ✅

**Goal**: Ensure our public input matches Stone's expected format exactly.

**Action**:
- Compare our `risk_public.json` with Stone's fibonacci public input
- Check field-by-field: layout, builtins, segments, memory_segments

### Step 3: Verify Proof Serializer Version Alignment ✅

**Goal**: Ensure serializer and verifier contract are from same Integrity version + stone version.

**Action**:
- Check `INTEGRITY_STONE_VERSION` in config
- Verify serializer binary matches that version
- Check Integrity contract expects same version

### Step 4: Compare Proof Structure ✅

**Goal**: Ensure our proof JSON structure matches Integrity's expected format.

**Action**:
- Compare our proof JSON with Integrity's fibonacci example
- Check `unsent_commitment.oods_values` structure
- Verify all required fields present

---

## Hypothesis (User's Assessment)

**Most Likely**: We're generating a valid Stone proof, but the Integrity input structure/config doesn't match the verifier's expected AIR config (layout / builtins / public input structure).

**Why**: 
- Stone's CPU AIR is for CairoZero with specific layout expectations
- We're using `recursive` layout which may have different AIR
- Public input structure may not match exactly

---

## Next Actions

1. **Find Stone Verifier**: Locate `cpu_air_verifier` binary
2. **Test Locally**: Run verifier on our proof + public input
3. **Compare Structures**: Compare our proof/public input with fibonacci example
4. **Check Versions**: Verify serializer/verifier version alignment

---

**Status**: Following user's diagnostic recommendations to isolate the issue.
