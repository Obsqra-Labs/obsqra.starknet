# Deep AIR Investigation - After Stone Version Ruled Out

**Date**: 2026-01-27  
**Status**: Investigating deeper AIR/public_input consistency issue

---

## Test Results Summary

### Stone Version Mismatch: RULED OUT ❌
- Stone6 verification: Failed at builtin (not OODS)
- Stone5 verification: Passed builtin → Failed at OODS
- Conclusion: Proof was generated with stone5, stone version mismatch is NOT the issue

---

## Remaining Issue

**Stone5 OODS Failure Despite Correct Structure**

- ✅ Structure matches perfectly
- ✅ Builtins match perfectly
- ✅ Layout matches perfectly
- ❌ OODS still fails

**This indicates deeper AIR/public_input consistency issue.**

---

## Investigation Focus

### 1. AIR Configuration Differences
- Compare Stone's AIR parameters with Integrity's expectations
- Check if AIR parameters match exactly
- Verify FRI configuration, channel hash, commitment hash

### 2. Public Input Consistency
- Check for subtle differences in structure
- Verify field ordering, memory segment details
- Check public_memory format consistency

### 3. n_verifier_friendly_commitment_layers Impact
- Example: `9999`
- Actual: `1000`
- Even with stone5, this VALUE difference might affect:
  - Commitment structure
  - How Integrity reconstructs commitments
  - Channel state (if used in channel seed)

### 4. Local Stone Verifier
- Test if proof is internally consistent
- If passes locally but fails on-chain → serializer/config issue

---

## Next Steps

1. **Compare public input field-by-field** → Find subtle differences
2. **Check AIR parameter impact** → Verify if differences matter
3. **Investigate n_verifier_friendly_commitment_layers** → Check if value affects verification
4. **Run local Stone verifier** → Test proof consistency

---

**Status**: Investigating deeper AIR/public_input consistency issue after ruling out stone version mismatch.
