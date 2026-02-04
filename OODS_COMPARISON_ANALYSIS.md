# OODS Comparison Analysis

**Date**: 2026-01-26  
**Status**: Comparing our proof structure with Integrity's examples

---

## Proof Serialization Structure

From `integrity/serializer/src/main.rs`:

The `proof_serializer` converts Stone proof JSON to calldata by serializing in this order:
1. **config** - Verifier configuration
2. **public_input** - Public input (segments, builtins, memory)
3. **unsent_commitment** - Commitments including OODS values
4. **witness** - Witness data for decommitment

### UnsentCommitment Structure

From `integrity/src/stark.cairo`:

```cairo
struct StarkUnsentCommitment {
    traces: TracesUnsentCommitment,
    composition: felt252,
    oods_values: Span<felt252>,  // n_oods_values = mask_size + constraint_degree
    fri: FriUnsentCommitment,
    proof_of_work: ProofOfWorkUnsentCommitment,
}
```

**Key**: `oods_values` contains evaluations of mask item polynomials at the OODS point.

---

## OODS Verification Process

From `integrity/src/stark/stark_commit.cairo`:

1. **Read OODS values**: `channel.read_felt_vector_from_prover(*unsent_commitment.oods_values)`
2. **Verify OODS**: Calls `verify_oods()` which checks:
   - Reconstructs composition polynomial from trace values
   - Compares with claimed composition from proof
   - If mismatch → "Invalid OODS" error

---

## Comparison Checklist

### Our Proof vs Integrity Example

- [ ] Proof structure matches (config, public_input, unsent_commitment, witness)
- [ ] `unsent_commitment.oods_values` exists and has correct length
- [ ] OODS values format matches Integrity's expectations
- [ ] Public input structure matches
- [ ] Config structure matches

---

## Next Steps

1. **Compare Proof Structures**: Check if our proof has the same structure as Integrity's examples
2. **Verify OODS Values**: Check if `oods_values` are present and correctly formatted
3. **Check Public Input**: Verify public input structure matches Integrity's format
4. **Test Small Layout**: Try small layout to see if OODS validation passes

---

**Status**: Investigating proof structure differences that could cause OODS mismatch.
