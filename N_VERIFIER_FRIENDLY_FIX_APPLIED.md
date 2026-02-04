# n_verifier_friendly_commitment_layers Fix Applied

**Date**: 2026-01-27  
**Status**: Fix applied, ready for testing

---

## Correction (2026-01-27)

**This only affects Stone6.**  
`integrity/src/air/public_input.cairo` only hashes `n_verifier_friendly_commitment_layers`
when `settings.stone_version == StoneVersion::Stone6`.  
For **Stone5**, this value is **not** included in the public input hash, so mismatching
1000 vs 9999 **does not** change the channel seed or OODS point under Stone5 verification.

**Implication**:
- ✅ Relevant if verifying as Stone6 (or if proof was generated with Stone6 semantics).
- ❌ **Not** the root cause of current Stone5 OODS failures.
- ✅ Still worth aligning for reproducibility.

---

## Root Cause (Stone6 only) ✅

**The `n_verifier_friendly_commitment_layers` value mismatch causes OODS failure when verifying as Stone6:**

1. **Value in public input hash**
   - Integrity's `public_input.cairo` line 81: `hash_data.append(n_verifier_friendly_commitment_layers);`
   - This value is included in public input hash **only for stone6**

2. **The mismatch**
   - **Our base params**: `1000`
   - **Canonical example**: `9999`
   - Different values → Different hash → Different channel seed → Different OODS point → **OODS mismatch!**

---

## Fix Applied ✅

**Updated base params file:**
- File: `integrity/examples/proofs/cpu_air_params.json`
- Change: `n_verifier_friendly_commitment_layers: 1000` → `9999`

---

## Expected Result (Stone6 only)

After regenerating proof with correct value **and verifying as Stone6**:
- ✅ Public input hash will match Integrity's expectation
- ✅ Channel seed will match
- ✅ OODS point will match
- ✅ Composition polynomial reconstruction will match
- ✅ **OODS verification should pass!**

For **Stone5**, this change should **not** affect the public input hash or OODS point.

---

## Next Steps

1. **Regenerate proof** with updated base params
2. **Test verification** through Integrity contract
3. **Verify OODS passes** (should no longer fail)

---

**Status**: 🎯 Fix applied! Ready to regenerate proof and test verification.
