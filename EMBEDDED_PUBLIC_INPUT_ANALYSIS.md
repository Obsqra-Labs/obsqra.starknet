# Embedded Public Input Analysis - Actual Failing Proof

**Date**: 2026-01-27  
**Status**: Comparing embedded public_input in actual failing proof with Integrity example

---

## User's Key Points ✅

1. **Canonical recursive proof DOES verify** on our registry
   - Fact hash: `0x32fc402a33e11316a8be5fbc6094e388bf2804969753715bcbc9b783b1e1156`
   - This means Integrity recursive is NOT broken
   - Stone recursive is NOT inherently incompatible

2. **Actual failing proofs ARE recursive + bitwise**
   - `/tmp/risk_stone_nttstalm`
   - `/tmp/risk_stone_dt_zx2u6`
   - These passed builtin validation → reached OODS

3. **Root cause is NOT layout/builtin mismatch**
   - Builtins are correct ✅
   - Layout is correct ✅
   - OODS still fails → AIR or public input mismatch ❌

---

## Most Likely Issue

**Proof/public_input pair inconsistency:**
- Wrong file pairing
- Stale artifacts
- proof_serializer fed a different proof than the public input inspected

This produces OODS while still passing builtins.

---

## Verification Steps

1. **Check embedded public_input** in `risk_proof.json` (not standalone `risk_public.json`)
2. **Compare with Integrity example** field-by-field
3. **Identify exact mismatch** causing OODS

---

## Status

Checking embedded public_input in actual failing proof file...
