# Actual Failing Proof Found! ✅

**Date**: 2026-01-26  
**Status**: Found the actual failing proof with `recursive + bitwise`

---

## Resolution ✅

**User's logic was correct!** The proof we were looking at (`/tmp/risk_stone_dgpxtm73`) was NOT the failing one.

### Found Actual Failing Proofs
1. **`/tmp/risk_stone_nttstalm`** (23:12:34)
   - `layout: recursive` ✅
   - `bitwise` segment ✅
   - `ecdsa` segment: false ✅

2. **`/tmp/risk_stone_dt_zx2u6`** (23:27:24)
   - `layout: recursive` ✅
   - `bitwise` segment ✅
   - `ecdsa` segment: false ✅

### Wrong Proof (Not the Failing One)
- **`/tmp/risk_stone_dgpxtm73`** (00:44:59) - Most recent but NOT failing
   - `layout: small` ❌
   - `ecdsa` segment ❌
   - This would fail at builtin gate, not OODS

---

## Why This Makes Sense

1. **Actual failing proof** has `recursive + bitwise`
   - Passes builtin validation ✅
   - Reaches OODS validation ✅
   - Fails at OODS (composition polynomial mismatch) ❌

2. **Wrong proof** has `small + ecdsa`
   - Would fail at builtin gate (never reaches OODS)
   - This is from a different run/path

---

## Next Steps

Now that we found the actual failing proof:
1. **Compare with Integrity example** → Field-by-field diff
2. **Check AIR consistency** → Verify public input matches Integrity's expectations
3. **Identify exact mismatch** → Find which field causes OODS failure

---

**Status**: ✅ Found actual failing proof! It has `recursive + bitwise` as expected. Now we can properly diagnose the OODS mismatch.
