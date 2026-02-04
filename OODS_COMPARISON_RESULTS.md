# OODS Comparison Results

**Date**: 2026-01-27  
**Status**: OODS values compared between canonical and our proof

## Comparison Summary

### ✅ Matches
- **Channel hash**: `poseidon3` (both)
- **Commitment hash**: `keccak256_masked160_lsb` (both)
- **OODS values count**: 135 values (both)

### ❌ Differences
- **n_steps**: Canonical=16384, Ours=65536
- **OODS evaluation point**: Different (expected if channel state differs)
- **OODS commitment hash**: Different (indicates different trace/constraints)

## Analysis

### Expected Differences
1. **OODS evaluation point differs**: This is expected because:
   - OODS point is derived from channel state
   - Channel state depends on trace commitments
   - Different traces → different channel state → different OODS point

2. **OODS commitment differs**: This indicates:
   - Different trace structure (different n_steps: 16384 vs 65536)
   - Different constraint evaluations
   - Different composition polynomial

### Key Insight

**OODS values count matches (135)**: This suggests the proof structure is correct, but the actual values differ due to:
- Different trace (n_steps: 16384 vs 65536)
- Potentially different Stone version semantics
- Different channel state progression

## Conclusion

The OODS differences are **expected** given:
1. Different trace sizes (n_steps: 16384 vs 65536)
2. Different program execution (our risk program vs canonical fibonacci)

**The critical question**: Would our proof verify if we used the same n_steps (16384)?

**Next step**: Test with matching n_steps to eliminate trace size as a variable.
