# Critical Discovery: stone5 vs stone6 Public Input Hash Difference

**Date**: 2026-01-27  
**Status**: ⚠️ **ROOT CAUSE IDENTIFIED**

## Critical Finding in Integrity Source Code

### The Key Difference

**File**: `integrity/src/air/public_input.cairo` (lines 80-82)

```cairo
if *settings.stone_version == StoneVersion::Stone6 {
    hash_data.append(n_verifier_friendly_commitment_layers);
}
```

### What This Means

**Stone6**:
- ✅ **Includes** `n_verifier_friendly_commitment_layers` in public input hash
- This affects channel seed
- This affects OODS point selection

**Stone5**:
- ❌ **Does NOT include** `n_verifier_friendly_commitment_layers` in public input hash
- Different channel seed
- Different OODS point selection

## Impact on Our Issue

### The Problem

If our proof was generated with a Stone version that **includes** `n_verifier_friendly_commitment_layers` in the public input hash, but we're verifying as **stone5** (which doesn't include it), then:

1. **Channel seed differs** → Different random elements
2. **OODS point differs** → Different evaluation point
3. **Composition polynomial reconstruction differs** → **OODS mismatch** ❌

### Our Current Situation

- **Our proof**: Generated with Stone v3 (`1414a545...`)
- **Verifying as**: stone5 (doesn't include `n_verifier_friendly_commitment_layers` in hash)
- **Our proof has**: `n_verifier_friendly_commitment_layers: 9999`
- **Question**: Does Stone v3 include this in public input hash?

## Hypothesis

### Hypothesis 1: Stone v3 = stone6 behavior
- Stone v3 might include `n_verifier_friendly_commitment_layers` in hash
- We're verifying as stone5 (doesn't include it)
- **→ OODS mismatch** ✅ **This explains the failure!**

**Test**: Try verifying as **stone6** instead of stone5

### Hypothesis 2: Stone v3 = stone5 behavior
- Stone v3 doesn't include it in hash (matches stone5)
- But there's another difference causing OODS failure
- **→ Different issue**

## Next Steps

### Priority 1: Test with stone6 ⭐ **IMMEDIATE TEST**

**Action**: Change verification to use `stone6` instead of `stone5`

**Why**: If Stone v3 generates proofs with stone6 semantics (includes `n_verifier_friendly_commitment_layers` in hash), verifying as stone6 should work.

**Test**:
1. Update config: `INTEGRITY_STONE_VERSION = "stone6"`
2. Regenerate proof (or use existing)
3. Test on-chain verification with `stone6`
4. **If OODS passes** → Stone v3 = stone6 ✅
5. **If still fails** → Different issue

### Priority 2: Check Stone v3 Source Code

**Action**: Check if Stone v3 includes `n_verifier_friendly_commitment_layers` in public input hash

**Where to check**:
- `stone-prover/src/starkware/air/cpu/board/cpu_air.h`
- `stone-prover/src/starkware/statement/cpu/cpu_air_statement.cc`
- Look for public input hash calculation
- Check if `n_verifier_friendly_commitment_layers` is included

### Priority 3: Test Stone v2

**Action**: If stone6 doesn't work, test Stone v2

**Why**: Stone v2 might be the actual "stone5" (doesn't include in hash)

## Conclusion

**This is likely the root cause!**

The difference in public input hash calculation between stone5 and stone6 explains:
- Why OODS fails even with correct FRI parameters
- Why canonical proof verifies (generated with correct version)
- Why our proof fails (version mismatch)

**Immediate Action**: Test verifying as **stone6** instead of stone5
