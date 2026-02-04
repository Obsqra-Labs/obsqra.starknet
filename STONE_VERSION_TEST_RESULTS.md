# Stone Version Test Results

**Date**: 2026-01-27  
**Status**: Stone6 verification test completed

---

## Test Results

### Stone6 Verification Test
- **Result**: ❌ FAILED
- **Error**: `Invalid builtin` (not OODS)
- **Conclusion**: Stone version mismatch is NOT the issue

---

## Error Comparison

### Stone5 Verification
- ✅ Passed builtin validation
- ❌ Failed at OODS

### Stone6 Verification
- ❌ Failed at builtin validation
- Error: `Invalid builtin`

---

## Analysis

### What This Means
1. **Proof was likely generated with stone5**
   - Stone5 verification passes builtin gate
   - Stone6 verification fails at builtin gate
   - This suggests proof uses stone5 semantics

2. **Stone version mismatch is NOT the issue**
   - If it were, stone6 verification would pass OODS
   - Instead, stone6 fails earlier (builtin validation)

3. **Different issue remains**
   - Stone5 passes builtin but fails OODS
   - This indicates AIR/public_input consistency issue
   - Not related to stone version mismatch

---

## Next Steps

Since stone version mismatch is ruled out:
1. **Investigate AIR configuration differences**
   - Compare Stone's AIR with Integrity's canonical recursive AIR
   - Check if AIR parameters match exactly

2. **Check public input consistency**
   - Verify subtle differences in public input structure
   - Check field ordering, memory segment details

3. **Run local Stone verifier**
   - Test if proof is internally consistent
   - If passes locally but fails on-chain → serializer/config issue

---

**Status**: Stone version mismatch hypothesis ruled out. Need to investigate deeper AIR/public_input consistency issue.
