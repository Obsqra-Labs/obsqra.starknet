# OODS Investigation - Next Steps Summary

**Date**: 2026-01-27  
**Status**: Investigation complete, root cause identified

## Executive Summary

### ✅ What We've Confirmed
1. **FRI parameters are correct**: `n_queries: 10`, `proof_of_work_bits: 30` (match canonical)
2. **Canonical proof verifies**: Integrity's example proof successfully verifies on-chain
3. **Verifier is working**: FactRegistry, serializer, and verifier contract are all correct
4. **Issue is in our pipeline**: Our proof generation is producing incompatible proofs

### ❌ What's Still Failing
- Our generated proofs fail with `Invalid OODS` even with correct FRI parameters
- OODS still fails even with minimal inputs (n_steps=65536, not 16384)

## Root Cause Analysis

### Most Likely Cause: Stone Binary Commit Mismatch

**Our Stone Commit**: `1414a545e4fb38a85391289abe91dd4467d268e1` (Stone v3)

**Canonical Example**: Generated with "stone5" (exact commit unknown, added Nov 2024)

**Why This Matters**:
- Even with matching FRI parameters, different Stone commits can produce incompatible proofs
- Different channel state calculation
- Different OODS point derivation
- Different AIR constraint evaluation semantics

### Supporting Evidence

1. **OODS Comparison Results**:
   - Channel/commitment hashes match ✅
   - OODS values count matches (135) ✅
   - OODS points/commitments differ ❌ (expected for different traces)
   - n_steps differs (16384 vs 65536) ❌

2. **Canonical Proof Verification**:
   - Canonical proof verifies ✅
   - Our proof fails ❌
   - Same verifier, same serializer, same FactRegistry
   - → Issue is in proof generation

3. **FRI Parameters**:
   - All FRI parameters now match canonical ✅
   - OODS still fails ❌
   - → Issue is NOT FRI parameters

## What We've Tried

### ✅ Completed
1. Fixed FRI parameters (`n_queries`, `proof_of_work_bits`)
2. Updated to use public FactRegistry
3. Verified canonical proof on-chain
4. Compared OODS values between proofs
5. Tested with minimal inputs (still n_steps=65536)

### ⚠️ Limitations
- Cannot easily match n_steps=16384 (determined by program execution)
- Cannot find exact Stone commit used for canonical example
- Stone commit info not in proof JSON metadata

## Next Steps (Prioritized)

### Priority 1: Find Exact Stone Commit (Manual Research Required)

**Options**:
1. Check Integrity GitHub issues/discussions for Stone version requirements
2. Contact Integrity maintainers (HerodotusDev)
3. Check Stone Prover repository for "stone5" tag/commit
4. Review Integrity commit history around Nov 2024 for Stone version references

**If commit found and differs**:
- Rebuild Stone with matching commit
- Regenerate proof
- Test on-chain

### Priority 2: Test with Integrity's generate.py

**Action**: Modify Integrity's `generate.py` to use our risk program instead of fibonacci

**Purpose**: If this verifies, issue is in our pipeline implementation, not Stone version

**Steps**:
1. Copy `integrity/examples/proofs/generate.py`
2. Replace fibonacci program with our risk program
3. Run generation
4. Test on-chain verification

### Priority 3: Alternative Approach - Use Stone6 ⚠️ NOT RECOMMENDED

**Important Context** (from Integrity documentation):
- Stone6 can work end-to-end, but **only if the verifier side is built+registered for stone6**
- Public FactRegistry likely only has stone5 verifiers registered (since canonical stone5 proof verifies)
- If registry only has stone5 verifiers, stone6 proofs will fail even if valid
- Stone6 requires hasher options: `keccak_160_lsb` or `blake2s_248_lsb`

**Recommendation**: **Stay with stone5** (canonical proof already verifies on public registry)
- Fix pipeline to match stone5 end-to-end
- Once stable, move to stone6 only if you deploy/verify stone6 verifiers

**If Stone5 commit cannot be found**:
- ~~Switch to Stone6 end-to-end~~ ❌ Not viable without stone6 verifier registration
- Continue investigating Stone5 commit mismatch
- Consider contacting Integrity team for exact Stone5 commit

### Priority 4: Contact Integrity Team

**Action**: Reach out to Integrity maintainers to ask:
- What exact Stone commit was used for canonical examples?
- Are there known compatibility issues with Stone v3?
- Recommended Stone version for production use?

## Conclusion

**Current State**: 
- All configurable parameters are correct
- Verifier infrastructure is working
- Issue is in proof generation (likely Stone version mismatch)

**Blocking Issue**: 
- Cannot determine exact Stone commit used for canonical example
- Cannot easily test with matching n_steps (program-dependent)

**Recommended Next Action**: 
- **Stay with Stone5** (public registry has stone5 verifiers, canonical proof verifies)
- Manual research to find exact Stone5 commit used by registered verifier (Priority 1)
- OR test with Integrity's generate.py using our program (Priority 2)
- ~~Switch to Stone6~~ ❌ Not viable without stone6 verifier registration

## Files Created

- `STONE_VERSION_INVESTIGATION.md` - Investigation plan
- `OODS_COMPARISON_RESULTS.md` - OODS values comparison
- `FRI_FIX_TEST_RESULTS.md` - FRI parameter fix results
- `scripts/compare_oods_values.py` - OODS comparison tool
- `scripts/test_matching_n_steps.py` - n_steps testing tool
