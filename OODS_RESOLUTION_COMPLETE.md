# OODS Resolution - Complete

**Date**: 2026-01-27  
**Status**: ✅ **RESOLVED**

## Root Cause Identified

**Issue**: Proofs failed with "Invalid OODS" even with correct FRI parameters.

**Root Cause**: **Stone version mismatch**

- **Stone v3** (`1414a545e4fb38a85391289abe91dd4467d268e1`) generates proofs with **stone6 semantics**
- **stone6 semantics**: Includes `n_verifier_friendly_commitment_layers` in public input hash
- **stone5 semantics**: Does NOT include it in public input hash
- **We were verifying as stone5** → Public input hash mismatch → OODS failure

## Solution Applied

**Changed**: `INTEGRITY_STONE_VERSION = "stone5"` → `"stone6"`

**Result**: ✅ **OODS now passes**

## Verification Results

### Phase 1: Test stone6 Verification
- ✅ Updated config to `stone6`
- ✅ Generated proof with Stone v3
- ✅ **Preflight call passed** → Proof verifies with stone6

### Phase 2: Verify stone6 Verifier Registration
- ✅ Canonical stone6 example verifies on-chain
- ✅ stone6 verifier IS registered in public FactRegistry
- ✅ Public FactRegistry supports both stone5 and stone6

## Key Discovery

**Integrity Source Code** (`integrity/src/air/public_input.cairo`):
```cairo
if *settings.stone_version == StoneVersion::Stone6 {
    hash_data.append(n_verifier_friendly_commitment_layers);
}
```

**Impact**:
- Different public input hash → Different channel seed
- Different channel seed → Different OODS point
- Different OODS point → OODS validation fails if version mismatch

## Stone Version Mapping

**Confirmed**:
- **Stone v3** (`1414a545...`, Sept 2024) = **stone6** behavior
- **Stone v2** (`7ac17c8b...`, March 2024) = Likely **stone5** behavior (not tested, not needed)

**Note**: Stone Prover uses "Stone v2/v3" naming, Integrity uses "stone5/stone6" runtime settings. These are different naming schemes.

## Files Modified

1. **`backend/app/config.py`**:
   - Line 96: `INTEGRITY_STONE_VERSION: str = "stone6"` (was "stone5")

## Test Results

### Our Proof with stone6
- ✅ Preflight call: **PASSED**
- ✅ OODS validation: **PASSED**
- ✅ Proof structure: Valid
- ✅ FRI parameters: Correct (n_queries: 10, proof_of_work_bits: 30)

### Canonical Examples
- ✅ stone5 example verifies with stone5 setting
- ✅ stone6 example verifies with stone6 setting
- ✅ Both verifiers registered in public FactRegistry

## Conclusion

**OODS issue resolved** by matching Stone version:
- Stone v3 generates stone6 proofs
- Verifying as stone6 → OODS passes ✅

**Action**: Keep `INTEGRITY_STONE_VERSION = "stone6"` in production.

## Next Steps (Optional)

1. **Document Stone version mapping** for future reference
2. **Update any documentation** that references stone5
3. **Consider testing Stone v2** if you need stone5 compatibility (not required)

---

**Resolution Time**: ~10 minutes (Phase 1 + Phase 2)
**Status**: ✅ Complete
