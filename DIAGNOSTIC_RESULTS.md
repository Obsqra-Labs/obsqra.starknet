# OODS Diagnostic Results

**Date**: 2026-01-26  
**Status**: Comparing our proof/public_input with Integrity's recursive example

---

## Step 1: Canonical Proof Serialization ✅

**Result**: Successfully serialized Integrity's canonical recursive proof
- Example proof: `recursive/cairo0_stone5_keccak_160_lsb_example_proof.json`
- Serialized: **1643 felts**
- Serializer: Working correctly ✅

**Next**: Test this canonical proof with our backend to verify deployment/config.

---

## Step 2: Structure Comparison

### Layout ✅
- Example: `"recursive"`
- Ours: `"recursive"`
- **Match**: ✅

### n_steps
- Example: `16384`
- Ours: `<to be checked>`
- **Status**: Comparing...

### Memory Segments Keys
- Example: `bitwise, execution, output, pedersen, program, range_check`
- Ours: `<to be checked>`
- **Status**: Comparing...

### Public Memory
- Example count: `<to be checked>`
- Our count: `<to be checked>`
- **Status**: Comparing...

---

## Findings

### ✅ What Matches
- Layout: Both use `"recursive"`
- Builtins: Both use `bitwise` (not `ecdsa`)
- Serializer: Working correctly

### ⚠️ What to Check
- `n_steps` value
- `memory_segments` structure and values
- `public_memory` format and content
- Field presence (rc_min, rc_max, dynamic_params)

---

## Next Actions

1. **Complete structure comparison** → Identify exact field differences
2. **Test canonical proof** → Verify deployment/config is correct
3. **Fix mismatches** → Update our public input generation if needed

---

**Status**: Diagnostic in progress. Comparing structures field-by-field.
