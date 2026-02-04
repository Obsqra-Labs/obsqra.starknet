# OODS Investigation Plan

**Date**: 2026-01-26  
**Status**: Builtin fix successful, investigating OODS validation failure

---

## Current Status

### ✅ What's Working
- Proof generation: SUCCESS (65.47s)
- Builtin configuration: Matches recursive layout ✅
- Builtin validation: PASSED ✅

### ⚠️ Current Issue
- **Error**: `Invalid OODS`
- **Meaning**: Composition polynomial from proof doesn't match reconstructed value from trace

---

## Understanding OODS Validation

From [STARK Verifier documentation](https://docs.starknet.io/learn/S-two-book/how-it-works/stark_proof/verify#step-by-step-breakdown):

### OODS Validation Process

1. **Draw OODS Point**: Randomly selected from Fiat-Shamir channel
2. **Reconstruct Composition**: Evaluates composition polynomial from sampled trace values
3. **Compare Values**: Checks reconstructed value matches claimed value from proof
4. **Error if Mismatch**: Returns `OodsNotMatching` error

### Integrity's Implementation

From `integrity/src/oods.cairo`:

```cairo
fn verify_oods(...) {
    // Reconstruct from trace
    let composition_from_trace = AIRComposition::eval_composition_polynomial(...);
    
    // Get claimed from proof
    let claimed_composition = *oods[oods.len() - 2] + *oods[oods.len() - 1] * oods_point;
    
    // Verify match
    assert(composition_from_trace == claimed_composition, 'Invalid OODS');
}
```

**Our Error**: `composition_from_trace != claimed_composition`

---

## Investigation Steps

### Step 1: Verify Proof Serialization ✅
- Check if `proof_serializer` correctly includes OODS values
- Verify OODS values are in the correct format
- Compare with Integrity's example proofs

### Step 2: Check Public Input Format
- Verify public input structure matches Integrity's format
- Check segments, builtins, memory serialization
- Compare with Integrity's example public inputs

### Step 3: Compare with Integrity Examples
- Use Integrity's fibonacci example as reference
- Compare proof structure, OODS values, format
- Identify differences

### Step 4: Check AIR Configuration
- Verify AIR configuration matches Integrity's expectations
- Check constraint degrees, interaction elements
- Ensure Stone's AIR matches Integrity's AIR

### Step 5: Test with Small Layout
- Try small layout (may have different OODS expectations)
- See if it works as fallback

---

## Likely Causes (Prioritized)

### 1. Proof Serialization Issue (Most Likely)
- `proof_serializer` may not be serializing OODS values correctly
- Format mismatch between Stone proof and Integrity's expected format
- **Action**: Compare serialized proof with Integrity's example

### 2. Public Input Format Mismatch
- Public input structure may not match Integrity's expectations
- Segments, builtins, memory may be serialized incorrectly
- **Action**: Verify public input structure

### 3. AIR Configuration Mismatch
- Stone's AIR configuration may not match Integrity's exactly
- Constraint degrees, interaction elements may differ
- **Action**: Compare AIR configurations

### 4. Fiat-Shamir Channel State
- Channel state used to generate OODS point may not match
- Commitment order or interaction elements may differ
- **Action**: Verify channel state matches

---

## Next Actions

1. **Compare Proof Structure**
   - Check Integrity's fibonacci example proof
   - Compare OODS values format
   - Identify differences

2. **Verify Serialization**
   - Check `proof_serializer` output
   - Verify OODS values are included
   - Compare with expected format

3. **Test Small Layout**
   - Try small layout (matches our program's builtins)
   - See if OODS validation passes
   - Use as fallback if recursive fails

4. **Check Public Input**
   - Verify public input structure
   - Check all required fields
   - Compare with Integrity's format

---

**Status**: OODS validation is the next hurdle. The composition polynomial mismatch suggests a proof format or AIR configuration issue. Investigation in progress.
