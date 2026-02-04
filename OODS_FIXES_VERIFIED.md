# OODS Debugging Fixes - Verification Results

**Date**: 2026-01-27  
**Status**: ✅ Both fixes verified and working

---

## Test Results

### ✅ Fix 1: Canonical Pipeline Uses Cairo0 - VERIFIED

**Proof Generated Successfully**:
- ✅ Compiled Cairo0 program with `cairo-compile --proof_mode`
- ✅ Ran with `cairo-run --layout recursive --proof_mode`
- ✅ Generated proof in 67.24 seconds
- ✅ Proof saved to `/tmp/canonical_integrity_*/risk_proof.json`

**Matches Integrity's generate.py**: ✅
- Uses Cairo0 (not Cairo1)
- Uses `cairo-compile` + `cairo-run` workflow
- Uses canonical FRI calculation

### ✅ Fix 2: Proof Parameter Logging Reads Correct Field - VERIFIED

**Proof JSON Structure**:
```json
{
  "proof_parameters": {  // ✅ Correct field (not "config")
    "channel_hash": "poseidon3",
    "commitment_hash": "keccak256_masked160_lsb",
    "n_verifier_friendly_commitment_layers": 9999,
    "stark": {
      "fri": {
        "fri_step_list": [0, 4, 4, 4, 1],
        "n_queries": 18,
        "last_layer_degree_bound": 128
      }
    }
  },
  "public_input": {
    "layout": "recursive",
    "n_steps": 65536
  }
}
```

**Logging Now Reads From**:
- ✅ `proof_parameters` field (correct)
- ✅ Falls back to `config` if needed (defensive)

---

## Current Status

### What's Working ✅

1. **Canonical Pipeline**: Generates proof using Cairo0 (matches Integrity's generate.py)
2. **Proof Structure**: Uses `proof_parameters` field (correct Stone JSON structure)
3. **Parameter Logging**: Reads from correct field and logs all parameters
4. **Layout**: Proof has `recursive` layout (matches verifier)
5. **Parameters**: All canonical parameters present (channel_hash, commitment_hash, n_verifier_friendly=9999)

### What's Still Failing ❌

**OODS Error Persists**:
```
Invalid OODS - The proof's OODS values do not match the verifier's expectations.
```

**This indicates**:
- Proof structure is correct (layout, builtins, parameters)
- But OODS values are cryptographically inconsistent with verifier
- Likely causes:
  1. Stone binary version mismatch (stone5 vs stone6 semantics)
  2. AIR configuration mismatch (despite canonical params)
  3. FRI parameter calculation difference
  4. Serialization format mismatch

---

## Next Steps for OODS Diagnosis

### 1. Compare Proof Parameters with Canonical Example

Compare the generated proof's `proof_parameters` against Integrity's canonical example:
- `integrity/examples/proofs/recursive/cairo0_stone5_keccak_160_lsb_example_proof.json`

**Key fields to compare**:
- `fri_step_list` - Should match canonical calculation
- `channel_hash` - Should be `poseidon3`
- `commitment_hash` - Should be `keccak256_masked160_lsb`
- `n_verifier_friendly_commitment_layers` - Should be `9999`
- `n_queries` - Should match canonical
- `log_n_cosets` - Should match canonical

### 2. Verify Stone Binary Version

```bash
# Check Stone binary version/commit
cd /opt/obsqra.starknet/stone-prover
git log --oneline -1
git describe --tags  # if available

# Verify it's stone5 (not stone6)
# If it's stone6, either:
# - Build stone5 binary, OR
# - Register stone6 verifier and use stone6 end-to-end
```

### 3. Test with Canonical Integrity Example

Run Integrity's canonical example to verify the verifier works:
```bash
cd /opt/obsqra.starknet/integrity/examples/proofs
python3 generate.py  # Generate canonical proof
# Then verify it on-chain
```

If canonical example verifies but ours doesn't, the issue is in our pipeline.

### 4. Check Serialization

Compare proof serialization format:
```bash
# Serialize our proof
integrity/target/release/proof_serializer \
  /tmp/canonical_integrity_*/risk_proof.json \
  > /tmp/our_proof_calldata.txt

# Serialize canonical example
integrity/target/release/proof_serializer \
  integrity/examples/proofs/recursive/cairo0_stone5_keccak_160_lsb_example_proof.json \
  > /tmp/canonical_proof_calldata.txt

# Compare
diff /tmp/our_proof_calldata.txt /tmp/canonical_proof_calldata.txt
```

---

## Summary

✅ **Both fixes are working correctly**:
1. Canonical pipeline uses Cairo0 (matches Integrity's generate.py)
2. Proof parameter logging reads from `proof_parameters` field

❌ **OODS error persists** - This indicates a deeper issue:
- Not a layout mismatch (layout is correct)
- Not a parameter field issue (reading from correct field)
- Likely: Stone binary version, AIR mismatch, or serialization issue

**The diagnostic improvements are now in place to help identify the root cause.**
