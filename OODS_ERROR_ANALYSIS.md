# OODS Error Analysis - Deep Dive

**Date**: 2026-01-26  
**Source**: [STARK Verifier Documentation](https://docs.starknet.io/learn/S-two-book/how-it-works/stark_proof/verify#step-by-step-breakdown)  
**Status**: Investigating "Invalid OODS" error after builtin fix

---

## What is OODS?

**OODS** = Out-of-Domain Sampling

From the [STARK Verifier documentation](https://docs.starknet.io/learn/S-two-book/how-it-works/stark_proof/verify#step-by-step-breakdown):

> "An `oods_point` is drawn randomly from the channel. This point is used to bind the prover to a unique low-degree polynomial and prevent ambiguity in the list decoding regime."

### OODS Validation Process

The verifier performs a **sanity check** on the composition polynomial:

1. **Draw OODS Point**: Randomly selected from the Fiat-Shamir channel
2. **Reconstruct Composition**: Evaluates composition polynomial from sampled trace values at OODS point
3. **Compare Values**: Checks that reconstructed value matches the claimed value from proof
4. **Error if Mismatch**: Returns `OodsNotMatching` error if values don't match

---

## Integrity's OODS Verification

From `integrity/src/oods.cairo`:

```cairo
fn verify_oods(
    oods: Span<felt252>,
    interaction_elements: InteractionElements,
    public_input: @PublicInput,
    constraint_coefficients: Span<felt252>,
    oods_point: felt252,
    trace_domain_size: felt252,
    trace_generator: felt252,
    contract_address: ContractAddress,
) {
    // Reconstruct composition polynomial from trace values
    let composition_from_trace = AIRComposition::eval_composition_polynomial(
        interaction_elements,
        public_input,
        oods.slice(0, oods.len() - 2),
        constraint_coefficients,
        oods_point,
        trace_domain_size,
        trace_generator,
        contract_address,
    );

    // Get claimed composition from proof
    let claimed_composition = *oods[oods.len() - 2] + *oods[oods.len() - 1] * oods_point;

    // Verify they match
    assert(composition_from_trace == claimed_composition, 'Invalid OODS');
}
```

**Key Check**: `composition_from_trace == claimed_composition`

If this assertion fails, we get: **"Invalid OODS"**

---

## What Causes "Invalid OODS" Error?

### Possible Causes

1. **Wrong Trace Values**
   - The trace values at the OODS point don't match what the verifier expects
   - Could be due to incorrect Cairo execution or trace generation

2. **Wrong Public Input**
   - Public input (segments, builtins, memory) doesn't match
   - Could be due to layout mismatch or incorrect public input serialization

3. **Wrong Constraint Coefficients**
   - The constraint coefficients used to reconstruct composition don't match
   - Could be due to incorrect interaction elements or Fiat-Shamir channel state

4. **Wrong OODS Point**
   - The OODS point used doesn't match what the verifier expects
   - Could be due to incorrect Fiat-Shamir channel state or proof serialization

5. **Wrong Trace Generator/Domain Size**
   - The trace domain parameters don't match
   - Could be due to incorrect layout configuration or trace generation

6. **Proof Serialization Issue**
   - The proof_serializer may not be serializing OODS values correctly
   - Could be due to format mismatch between Stone proof and Integrity's expected format

---

## Our Specific Case

### Current Configuration
- **Layout**: `recursive`
- **Stone Version**: `stone5`
- **Builtins**: `[output, pedersen, range_check, bitwise]` ✅ (matches)
- **Hasher**: `keccak_160_lsb`
- **Memory Verification**: `strict`

### What We Know
- ✅ Proof generation succeeds (65.47s)
- ✅ Builtin validation passes (no more "Invalid builtin")
- ❌ OODS validation fails ("Invalid OODS")

### Likely Causes (In Order of Probability)

1. **Proof Serialization Mismatch**
   - Stone proof format may not match Integrity's expected format exactly
   - `proof_serializer` may not be handling OODS values correctly
   - **Check**: Compare serialized proof with Integrity's example proofs

2. **Public Input Mismatch**
   - Public input structure may not match Integrity's expectations
   - Could be due to Cairo execution trace format differences
   - **Check**: Verify public input structure matches Integrity's format

3. **AIR Configuration Mismatch**
   - The AIR configuration (constraints, degrees) may not match exactly
   - Could be due to Stone vs Integrity AIR differences
   - **Check**: Compare AIR configuration with Integrity's expectations

4. **Fiat-Shamir Channel State**
   - The channel state used to generate OODS point may not match
   - Could be due to different commitment order or interaction elements
   - **Check**: Verify channel state matches Integrity's expectations

---

## Solutions

### Option 1: Verify Proof Serialization
- Check if `proof_serializer` correctly serializes OODS values
- Compare with Integrity's example proofs (fibonacci)
- Verify calldata format matches Integrity's expectations

### Option 2: Check Public Input Format
- Verify public input structure matches Integrity's format
- Check if segments, builtins, memory are serialized correctly
- Compare with Integrity's example public inputs

### Option 3: Use Integrity's Example as Reference
- Use Integrity's fibonacci example proof as reference
- Compare our proof structure with the example
- Identify differences in OODS values or format

### Option 4: Check AIR Configuration
- Verify AIR configuration matches Integrity's expectations
- Check constraint degrees, interaction elements, etc.
- Ensure Stone's AIR matches Integrity's AIR exactly

### Option 5: Use Small Layout
- Small layout may have different OODS expectations
- Could work as fallback if recursive layout has stricter requirements

---

## Key Insight from Documentation

From the [STARK Verifier docs](https://docs.starknet.io/learn/S-two-book/how-it-works/stark_proof/verify#step-by-step-breakdown):

> "The function checks that the composition polynomial evaluated at the OODS point (as provided in the proof) matches the value reconstructed from the sampled trace values. If not, it returns an `OodsNotMatching` error."

**This means**: The proof's claimed composition value doesn't match what Integrity reconstructs from the trace values. This could be:
- A serialization issue (wrong values in proof)
- A trace issue (wrong trace values)
- A configuration issue (wrong AIR/constraints)

---

## Next Steps

1. **Compare with Integrity Examples**
   - Check Integrity's fibonacci example proof structure
   - Compare OODS values format
   - Identify differences

2. **Verify Proof Serialization**
   - Check `proof_serializer` output
   - Verify OODS values are included correctly
   - Compare with expected format

3. **Check Public Input**
   - Verify public input structure
   - Check if all required fields are present
   - Compare with Integrity's format

4. **Test with Small Layout**
   - Try small layout (may have different OODS expectations)
   - See if it works as fallback

---

**Status**: OODS validation is failing because the composition polynomial value from the proof doesn't match what Integrity reconstructs from trace values. This is likely a proof format/serialization issue or AIR configuration mismatch.
