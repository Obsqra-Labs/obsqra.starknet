# Stone Version Investigation - Next Steps

**Date**: 2026-01-27  
**Status**: ✅ Canonical proof verifies → Issue confirmed in our pipeline

## Critical Finding

### ✅ Canonical Proof Verifies On-Chain

**Test Result**: Integrity's canonical recursive example proof (`cairo0_stone5_keccak_160_lsb_example_proof.json`) **successfully verifies** on-chain using the public FactRegistry.

**Implications**:
- ✅ Verifier contract is correct
- ✅ FactRegistry is correct  
- ✅ Serializer is correct
- ❌ **Issue is in our proof generation pipeline**

## Current State

### What We've Fixed
1. ✅ FRI parameters: `n_queries: 10`, `proof_of_work_bits: 30` (match canonical)
2. ✅ FactRegistry: Using public FactRegistry with registered verifiers
3. ✅ Layout: Using `recursive` layout
4. ✅ Hasher: Using `keccak_160_lsb`
5. ✅ Stone version config: Using `stone5`

### What's Still Failing
- ❌ Our generated proofs fail with `Invalid OODS` even with correct FRI parameters

## Root Cause Analysis

Since canonical proof verifies but ours doesn't, despite matching FRI parameters, the issue is likely:

### 1. Stone Binary Version Mismatch (Most Likely)

**Our Stone Commit**: `1414a545e4fb38a85391289abe91dd4467d268e1` (Stone v3)

**Canonical Example**: Generated with "stone5" (exact commit unknown)

**Important Context**: 
- Public FactRegistry has stone5 verifiers registered (canonical stone5 proof verifies ✅)
- Stone6 would require stone6 verifiers to be registered in FactRegistry
- **Recommendation**: Stay with stone5 and fix pipeline to match registered stone5 verifier

**Problem**: Even if both are labeled "stone5", different commits can produce incompatible proofs due to:
- Different channel state calculation
- Different OODS point derivation  
- Different AIR constraint evaluation
- Different FRI layer processing

### 2. Proof Generation Differences

Possible subtle differences:
- Cairo-run version differences
- Trace generation differences
- Public input construction differences
- Private input handling differences

## Next Steps

### Priority 1: Find Canonical Example's Stone Commit

**Options**:
1. Check Integrity repository git history for when canonical example was generated
2. Check Integrity documentation/README for Stone version requirements
3. Contact Integrity maintainers or check their GitHub issues
4. Try to reverse-engineer from proof structure (unlikely to reveal commit)

**If commit found and differs**:
- Rebuild Stone with matching commit
- Regenerate proof
- Test on-chain

### Priority 2: Test with Matching n_steps

**Current**: Our proof has `n_steps=65536`, canonical has `n_steps=16384`

**Test**: Generate proof with `n_steps=16384` (same as canonical)

**Purpose**: Eliminate trace size as a variable

**If OODS passes**:
- Issue is trace-size dependent
- May need to adjust trace generation or use smaller traces

**If OODS still fails**:
- Issue is Stone version or AIR config
- Proceed with Priority 1

### Priority 3: Compare OODS Values

Extract and compare:
- OODS evaluation point from both proofs
- OODS values from both proofs
- Channel state at OODS point

**Purpose**: Identify exactly where the cryptographic mismatch occurs

### Priority 4: Test with Integrity's generate.py

**Action**: Run Integrity's `generate.py` script with our risk program

**Purpose**: If this verifies, the issue is in our pipeline implementation, not Stone version

## Conclusion

**Confirmed**: The verifier works correctly. The issue is in our proof generation.

**Most Likely Cause**: Stone binary commit mismatch between our `1414a545...` (Stone v3) and the commit used to generate the canonical example.

**Next Action**: Find the exact Stone commit used for canonical example and rebuild if different.

## Update: Investigation Results

### OODS Comparison
- ✅ Channel/commitment hashes match
- ✅ OODS values count matches (135)
- ❌ OODS points differ (expected for different traces)
- ❌ n_steps differs (16384 vs 65536)

### n_steps Testing
- Attempted to match n_steps=16384 with minimal inputs
- Result: Still n_steps=65536 (determined by program execution)
- Cannot easily control n_steps without changing program

### Stone Commit Research
- Canonical example added in commit `5702c4f` (Nov 2024)
- No Stone commit info found in Integrity repo
- Need to check Stone Prover repo or contact Integrity team

See `NEXT_STEPS_SUMMARY.md` for prioritized action plan.
