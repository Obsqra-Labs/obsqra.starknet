# Stone Version Mismatch Diagnosis

**Date**: 2026-01-27  
**Status**: Investigating stone5 vs stone6 mismatch in public input hashing

---

## User's Critical Insight ✅

### The Real Mismatch
**Stone Version / Channel Hash Mismatch**

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

## Current Status

### Config
- **Verification**: `INTEGRITY_STONE_VERSION = "stone5"`

### Proof Parameters
- **n_verifier_friendly_commitment_layers**: `1000` (ours) vs `9999` (example)
- **Note**: The VALUE may not matter, but whether it's INCLUDED in hash does!

### Need to Determine
1. **What stone version generated our proof?**
   - Check proof generation logs
   - Check Stone prover version used
   - Check if Stone6 semantics were used

2. **Are we verifying with matching stone version?**
   - Currently verifying as `stone5`
   - If proof was generated with Stone6 → mismatch!

---

## Diagnostic Steps

### Step 1: Determine Proof Generation Stone Version
- Check Stone prover binary version
- Check proof generation logs
- Check if Stone6 semantics were used

### Step 2: Test with Matching Stone Version
- If proof was Stone6 → verify as `stone6`
- If proof was Stone5 → verify as `stone5`

### Step 3: Run Local Stone Verifier
- Test if proof is internally consistent
- If passes locally but fails on-chain → stone version mismatch

---

## Next Actions

1. **Check Stone prover version** → Determine what generated the proof
2. **Test with stone6** → If proof was generated with Stone6
3. **Run local verifier** → Test proof consistency

---

**Status**: Investigating stone version mismatch. Need to determine what stone version generated the proof and match verification accordingly.
