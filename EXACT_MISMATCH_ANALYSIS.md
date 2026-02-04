# Exact Mismatch Analysis - Embedded Public Input

**Date**: 2026-01-27  
**Status**: Comparing embedded public_input with Integrity example to identify exact OODS mismatch

---

## ✅ Confirmed: Embedded Public Input Structure

### Actual Failing Proof (`/tmp/risk_stone_nttstalm/risk_proof.json`)
- **Layout**: `recursive` ✅
- **Builtins**: `bitwise, execution, output, pedersen, program, range_check` ✅
- **Has bitwise**: `true` ✅
- **Has ecdsa**: `false` ✅

### Structure Matches Integrity Example ✅
- Same field keys: `dynamic_params, layout, memory_segments, n_steps, public_memory, rc_max, rc_min`
- Same memory segments: `bitwise, execution, output, pedersen, program, range_check`
- Same order: Memory segments in same order

---

## ⚠️ Differences (Expected for Different Program)

### Values That Differ
- **n_steps**: `65536` (ours) vs `16384` (example)
- **rc_min/rc_max**: `0/32778` (ours) vs `32762/32769` (example)
- **memory_segments ranges**: All different (different program execution)
- **public_memory**: `281` entries (ours) vs `46` entries (example)

**These differences are EXPECTED** for different programs and should NOT cause OODS.

---

## 🔍 OODS Mismatch Root Cause

Since:
1. ✅ Structure matches perfectly
2. ✅ Builtins match perfectly
3. ✅ Layout matches perfectly
4. ✅ Canonical recursive proof DOES verify on our registry
5. ❌ Our proof fails at OODS

**The issue is NOT structure/builtin/layout mismatch.**

**Most likely causes:**
1. **AIR Mismatch**: Stone's AIR configuration doesn't exactly match Integrity's canonical recursive AIR
   - Different constraint degrees
   - Different interaction elements
   - Different AIR parameters

2. **Public Input Consistency**: Subtle differences in how values are structured/ordered that affect composition polynomial reconstruction
   - Field ordering (though JSON order shouldn't matter)
   - Memory segment structure details
   - Public memory format

3. **Proof/Public Input Pair Inconsistency**: The proof was generated with one public input, but serializer/verifier sees a different one
   - Though embedded public_input looks correct

---

## Next Steps

1. **Verify canonical proof** → Already done (user confirmed it verifies)
2. **Compare AIR configuration** → Check if Stone's AIR matches Integrity's exactly
3. **Check Cairo toolchain version** → Version mismatch can cause OODS
4. **Test with Integrity's exact toolchain** → Use same Cairo version as Integrity examples

---

**Status**: ✅ Embedded public_input structure matches perfectly. OODS mismatch is a deeper AIR/public_input consistency issue, not structure mismatch.
