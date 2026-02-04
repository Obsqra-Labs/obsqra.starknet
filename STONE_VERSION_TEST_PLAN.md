# Stone Version Mismatch Test Plan

**Date**: 2026-01-27  
**Status**: Testing stone5 vs stone6 mismatch hypothesis

---

## Hypothesis

**Stone Version / Channel Hash Mismatch**

- **Stone6**: Includes `n_verifier_friendly_commitment_layers` in public input hash
- **Stone5**: Does NOT include it in public input hash
- If proof generated with Stone6 but verified as Stone5 → channel seed changes → OODS mismatch

---

## Test Plan

### Test 1: Verify with stone6
**Goal**: Test if stone version mismatch is the issue

**Action**:
1. Change `INTEGRITY_STONE_VERSION = "stone6"` in config
2. Re-run verification with same proof
3. If OODS passes → stone version mismatch confirmed ✅
4. If OODS still fails → different issue

### Test 2: Determine Proof Generation Version
**Goal**: Check what stone version generated the proof

**Action**:
1. Check Stone prover binary version
2. Check proof generation logs
3. Check if Stone6 semantics were used

### Test 3: Run Local Stone Verifier
**Goal**: Test if proof is internally consistent

**Action**:
1. Build/run `cpu_air_verifier` on our proof
2. If passes locally but fails on-chain → stone version mismatch
3. If fails locally → proof/public input mismatch

---

## Current Status

- **Config**: `INTEGRITY_STONE_VERSION = "stone5"`
- **Proof**: `n_verifier_friendly_commitment_layers = 1000`
- **Example**: `n_verifier_friendly_commitment_layers = 9999`

**Note**: The VALUE may not matter, but whether it's INCLUDED in hash does!

---

## Next Action

**Test with stone6**: Change config and re-run verification to test hypothesis.

---

**Status**: Ready to test stone version mismatch hypothesis.
