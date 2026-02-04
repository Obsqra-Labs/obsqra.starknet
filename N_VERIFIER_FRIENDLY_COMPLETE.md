# n_verifier_friendly_commitment_layers Fix - Complete

**Date**: 2026-01-27  
**Status**: Fix applied, ready for verification

---

## Summary

Fixed the `n_verifier_friendly_commitment_layers` value mismatch that was causing OODS verification failures.

---

## Root Cause

The `n_verifier_friendly_commitment_layers` value is included in the public input hash (Integrity's `public_input.cairo` line 81). Our base params file had `1000`, but Integrity's canonical recursive example uses `9999`. This caused:
- Different public input hash
- Different channel seed
- Different OODS point
- **OODS mismatch!**

---

## Fix Applied ✅

**Updated base params file:**
- File: `integrity/examples/proofs/cpu_air_params.json`
- Change: `n_verifier_friendly_commitment_layers: 1000` → `9999`
- Matches Integrity's canonical recursive example

---

## Proof Generated ✅

**New proof with correct value:**
- Proof: `/tmp/risk_stone_xfeoak91/risk_proof.json`
- `n_verifier_friendly_commitment_layers`: `9999` ✅

---

## Error Handling Improvements ✅

**Updated error handling to surface actual contract errors:**
- `backend/app/services/integrity_service.py` - Captures and re-raises contract errors with details
- `backend/app/api/routes/risk_engine.py` - Propagates detailed error messages

**Note**: Backend may need restart to pick up error handling changes.

---

## Expected Result

After regenerating proof with correct value:
- ✅ Public input hash will match Integrity's expectation
- ✅ Channel seed will match
- ✅ OODS point will match
- ✅ Composition polynomial reconstruction will match
- ✅ **OODS verification should pass!**

---

## Next Steps

1. **Restart backend** (if needed) to pick up error handling changes
2. **Run E2E test** to see actual Integrity error (if any)
3. **Verify OODS passes** with `n_verifier_friendly_commitment_layers = 9999`

---

## Files Modified

- `integrity/examples/proofs/cpu_air_params.json` - Updated value to 9999
- `backend/app/services/integrity_service.py` - Improved error handling
- `backend/app/api/routes/risk_engine.py` - Improved error propagation
- Documentation files (various)

---

**Status**: 🎯 Fix applied, proof generated with correct value. Ready for verification testing.
