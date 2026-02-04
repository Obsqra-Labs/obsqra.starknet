# n_verifier_friendly_commitment_layers Fix - Test Status

**Date**: 2026-01-27  
**Status**: Fix applied, testing in progress

---

## Fix Applied ✅

**Updated base params file:**
- File: `integrity/examples/proofs/cpu_air_params.json`
- Change: `n_verifier_friendly_commitment_layers: 1000` → `9999`
- Matches Integrity's canonical recursive example

---

## Proof Generation ✅

**New proof generated with correct value:**
- Proof: `/tmp/risk_stone_xfeoak91/risk_proof.json`
- `n_verifier_friendly_commitment_layers`: `9999` ✅

---

## Testing Status ⚠️

**Issue**: Error handling needs improvement
- Backend catches Integrity errors but doesn't surface actual contract error
- Currently showing generic "No fact hash returned" message
- Need to see actual error (OODS, builtin, etc.)

**Attempted fixes:**
- Updated `integrity_service.py` to capture and re-raise contract errors
- Updated `risk_engine.py` to propagate errors
- Still showing generic error (exception propagation needs refinement)

---

## Next Steps

1. **Check backend logs directly** for actual Integrity contract error
2. **Manually test Integrity contract call** with the new proof
3. **Verify if OODS passes** with `n_verifier_friendly_commitment_layers = 9999`

---

## Expected Result

If the fix works:
- ✅ Public input hash will match Integrity's expectation
- ✅ Channel seed will match
- ✅ OODS point will match
- ✅ **OODS verification should pass!**

If OODS still fails:
- Need to investigate other AIR configuration differences
- Check channel hash, commitment hash, FRI parameters

---

**Status**: 🎯 Fix applied, proof generated with correct value. Need to verify if OODS passes.
