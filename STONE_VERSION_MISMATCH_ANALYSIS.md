# Stone Version Mismatch Analysis

**Date**: 2026-01-27  
**Status**: Investigating stone5 vs stone6 mismatch in public input hashing

---

## User's Critical Correction ✅

### ❌ Wrong Claim
"Stone recursive ≠ Integrity recursive, so they're incompatible"
- **FALSE**: Canonical recursive proof DOES verify on our registry
- Fact hash: `0x32fc402a33e11316a8be5fbc6094e388bf2804969753715bcbc9b783b1e1156`
- Stone + Integrity recursive CAN verify

### ✅ Correct Understanding
- OODS = composition polynomial mismatch ✅
- Structure/builtins/layout are correct ✅
- Failure is deeper than layout mismatch ✅

---

## The Real Mismatch (Most Likely Cause)

### Stone Version / Channel Hash Mismatch

**Key Difference:**
- **Stone6**: Includes `n_verifier_friendly_commitment_layers` in public input hash
- **Stone5**: Does NOT include it in public input hash

**Impact:**
- If proof generated with Stone6 behavior but verified as Stone5:
  - Channel seed changes
  - OODS point selection changes
  - Composition polynomial reconstruction differs
  - **→ OODS mismatch**

---

## Evidence

### Proof Parameters Differences
- `n_verifier_friendly_commitment_layers`: `1000` (ours) vs `9999` (example)
- Different FRI step list (expected with different n_steps)
- Different n_queries / PoW bits

**These shouldn't matter if verifier reads them from proof, UNLESS stone version mismatch changes hashing.**

---

## Diagnostic Steps

### Step 1: Run Local Stone Verifier ✅
**Goal**: Test if proof is internally consistent

**Action**: Run `cpu_air_verifier` on our failing proof
- If fails locally → proof/public input mismatch
- If passes locally → stone version mismatch or serializer/config mismatch

### Step 2: Check Stone Version Mismatch ✅
**Goal**: Verify if proof was generated with Stone6 but verified as Stone5

**Action**: 
- Check what stone version was used to generate proof
- Check what stone version we're using for verification
- If mismatch → flip stone version to match prover output

### Step 3: Verify Canonical Proof ✅
**Already done**: Canonical recursive proof verifies on our registry

---

## Next Actions

1. **Run local Stone verifier** → Test proof consistency
2. **Check stone version** → Verify if mismatch exists
3. **Flip stone version** → Match prover output if needed

---

**Status**: Investigating stone version mismatch as the likely root cause of OODS failure.
