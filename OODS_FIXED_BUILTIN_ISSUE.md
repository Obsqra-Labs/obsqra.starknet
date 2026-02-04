# OODS Fixed - Builtin Issue Re-emerged

**Date**: 2026-01-27  
**Status**: OODS fixed, but builtin issue re-emerged

---

## Progress! ✅

**The `n_verifier_friendly_commitment_layers` fix worked!**

- ✅ Error changed from **"Invalid OODS"** to **"Invalid builtin"**
- ✅ This means we **passed the OODS check!**
- ✅ The fix for `n_verifier_friendly_commitment_layers: 1000 → 9999` was successful

---

## New Issue: Invalid Builtin ❌

**Error**: `Invalid builtin - The proof's builtins do not match the verifier's expectations`

**Context**:
- We already fixed this before (changed `ecdsa` → `bitwise` in Cairo program)
- But now it's failing again after the OODS fix

**Possible Causes**:
1. Proof was generated with wrong builtins
2. Verifier expects different builtins for recursive layout with new `n_verifier_friendly_commitment_layers` value
3. Builtin detection/validation mismatch

---

## Timeline of Fixes

1. ✅ **VERIFIER_NOT_FOUND** → Fixed (switched to public FactRegistry)
2. ✅ **Invalid final_pc** → Fixed (switched to recursive layout)
3. ✅ **Invalid builtin (first time)** → Fixed (changed ecdsa → bitwise in Cairo program)
4. ✅ **Invalid OODS** → Fixed (changed n_verifier_friendly_commitment_layers: 1000 → 9999)
5. ❌ **Invalid builtin (again)** → Need to investigate

---

## Next Steps

1. **Check proof builtins** - Verify what builtins are in the generated proof
2. **Check Cairo program** - Verify what builtins are declared in `risk_example_cairo0.cairo`
3. **Check verifier expectations** - Verify what builtins Integrity's recursive layout verifier expects
4. **Compare and fix** - Ensure all three match

---

## Files to Check

- `verification/risk_example_cairo0.cairo` - Cairo program builtins
- Latest proof JSON - Proof builtins
- `integrity/src/air/layouts/recursive/constants.cairo` - Verifier expected builtins

---

**Status**: 🎯 OODS fixed! But builtin issue re-emerged. Need to verify builtin consistency.
