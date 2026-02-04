# FRI Parameters Fix - Test Results

**Date**: 2026-01-27  
**Status**: ✅ FRI parameters fixed, but OODS still failing

## Test Execution

### Proof Generation
- ✅ Proof generated successfully with fixed FRI parameters
- ✅ Time: 80.61s
- ✅ Proof path: `/tmp/canonical_integrity_sjz04jjd/risk_proof.json`

### FRI Parameters Verification

**New Proof (with fixes)**:
- ✅ `n_queries`: `10` (matches canonical)
- ✅ `proof_of_work_bits`: `30` (matches canonical)
- ✅ `fri_step_list`: `[0, 4, 4, 4, 1]` (correct for n_steps=65536)
- ✅ `last_layer_degree_bound`: `128` (matches canonical)
- ✅ `log_n_cosets`: `2` (matches canonical)

**All FRI parameters now match canonical example!**

### On-Chain Verification

**Result**: ❌ **OODS still failing**

**Error**: `Invalid OODS` from verifier contract

**Preflight call error**:
```
Contract error: 'Invalid OODS'
Contract: 0x4fef1cabed83adeb23b69e09fbdcf493d6ede214a353c5c08af6696c34c797b
```

## Analysis

### What We Fixed
1. ✅ `n_queries`: `18` → `10`
2. ✅ `proof_of_work_bits`: `24` → `30`
3. ✅ Backend using PUBLIC FactRegistry

### What's Still Failing
- ❌ OODS validation still fails even with correct FRI parameters

### Possible Remaining Causes

1. **Stone Commit Mismatch** (Most Likely)
   - Our Stone commit: `1414a545e4fb38a85391289abe91dd4467d268e1` (Stone v3)
   - Canonical example's Stone commit: Unknown
   - Even with same parameters, different Stone versions can produce incompatible proofs

2. **Channel Hash / Commitment Hash Mismatch**
   - Both match canonical: ✅ `poseidon3`, `keccak256_masked160_lsb`
   - But internal calculation might differ if Stone version differs

3. **OODS Point Selection**
   - Different `n_steps` (65536 vs 16384) → different trace
   - OODS point derived from channel state
   - Channel state depends on FRI parameters AND Stone version semantics

4. **AIR Configuration**
   - AIR constraints might differ between Stone versions
   - Even with same FRI params, constraint evaluation could differ

## Next Steps

### Priority 1: Verify Stone Commit
- Check Integrity documentation for canonical example's Stone commit
- Compare with our commit `1414a545e4fb38a85391289abe91dd4467d268e1`
- If mismatch: Rebuild Stone with matching commit

### Priority 2: Test with Same n_steps
- Generate proof with n_steps=16384 (same as canonical)
- This would eliminate trace size as a variable
- If OODS passes → issue is trace size dependent
- If OODS still fails → issue is Stone version or AIR config

### Priority 3: Compare OODS Values
- Extract OODS values from both proofs
- Compare evaluation points and values
- Check if channel state differs

## Conclusion

**FRI parameters are now correct**, but OODS still fails. This strongly suggests:
- Stone commit/version mismatch (most likely)
- Or AIR configuration differences between Stone versions

The fix was correct, but there's a deeper compatibility issue with the Stone binary version.

## Update: Canonical Proof Verification

**✅ CRITICAL FINDING**: Integrity's canonical example proof **successfully verifies** on-chain.

**Implications**:
- Verifier is working correctly
- Issue is confirmed in our proof generation pipeline
- Most likely cause: Stone binary commit mismatch

See `STONE_VERSION_INVESTIGATION.md` for next steps.
