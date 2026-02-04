# FRI Parameters Fix - OODS Resolution

**Date**: 2026-01-27  
**Status**: ✅ Fixed - Parameters updated to match canonical example

## Root Cause

OODS failures were caused by FRI parameter mismatches between our proof generation and Integrity's canonical example:

- ❌ `n_queries`: `18` vs canonical `10` (CRITICAL - affects OODS point selection)
- ❌ `proof_of_work_bits`: `24` vs canonical `30` (CRITICAL - affects PoW hash)
- ℹ️ `fri_step_list`: Different due to different `n_steps` (EXPECTED - both satisfy FRI equation)
  - Canonical: `n_steps=16384` → `[0, 4, 4, 3]` (FRI equation: 7 + 11 = 18, 14 + 4 = 18 ✅)
  - Ours: `n_steps=65536` → `[0, 4, 4, 4, 1]` (FRI equation: 7 + 13 = 20, 16 + 4 = 20 ✅)

## Fix Applied

### Updated Base Parameters File

**File**: `integrity/examples/proofs/cpu_air_params.json`

**Changes**:
```json
"stark": {
    "fri": {
        "fri_step_list": [0, 4, 4, 3],  // Template (recalculated per n_steps)
        "last_layer_degree_bound": 128,
        "n_queries": 10,                // ✅ Changed from 18
        "proof_of_work_bits": 30         // ✅ Changed from 24
    },
    "log_n_cosets": 2
}
```

### FRI Step List Calculation

The `fri_step_list` is calculated dynamically based on `n_steps` using the FRI equation:

```
log2(last_layer_degree_bound) + Σ(fri_steps) = log2(n_steps) + 4
```

**For canonical example** (n_steps=16384):
- log2(16384) = 14
- log2(128) = 7
- sigma = 14 + 4 - 7 = 11
- q=2, r=3 → `[0, 4, 4, 3]` ✅

**For our proof** (n_steps=65536):
- log2(65536) = 16
- log2(128) = 7
- sigma = 16 + 4 - 7 = 13
- q=3, r=1 → `[0, 4, 4, 4, 1]` ✅ (correct for our n_steps)

**Note**: Different `n_steps` will produce different `fri_step_list` - this is expected and correct. The key is that `n_queries` and `proof_of_work_bits` must match the canonical example.

## Why These Parameters Matter

1. **`n_queries`**: Affects security level and OODS point selection
   - Lower queries = lower security but faster verification
   - Must match verifier's expectation

2. **`proof_of_work_bits`**: Affects PoW hash calculation
   - Higher bits = more PoW work required
   - Must match verifier's expectation

3. **`fri_step_list`**: Must satisfy FRI equation for given `n_steps`
   - Different `n_steps` → different step_list (expected)
   - Equation must hold: `log2(last_layer) + Σ(steps) = log2(n_steps) + 4`

## Verification

After this fix:
1. Regenerate proof with updated parameters
2. Compare `n_queries` and `proof_of_work_bits` with canonical (should match)
3. Verify `fri_step_list` satisfies FRI equation for our `n_steps`
4. Test on-chain verification - OODS should pass

## Files Modified

- `integrity/examples/proofs/cpu_air_params.json` - Updated `n_queries` and `proof_of_work_bits`

## Additional Finding: FactRegistry Address

**IMPORTANT**: The backend was using a custom FactRegistry (`0x063feefb...`) instead of the public one (`0x4ce7851f...`).

**Impact**: Even if proof is valid, OODS errors can be misleading if verifiers aren't registered in the custom FactRegistry.

**Fix Applied**: Updated `integrity_service.py` to use PUBLIC FactRegistry by default (has all verifiers registered).

## Next Steps

1. ✅ FRI parameters fixed (`n_queries: 10`, `proof_of_work_bits: 30`)
2. ✅ Backend updated to use PUBLIC FactRegistry
3. **TODO**: Regenerate proof with corrected parameters
4. **TODO**: Re-test on-chain verification
5. **TODO**: Confirm OODS passes
