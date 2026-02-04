# OODS Error - Next Steps

**Date**: 2026-01-26  
**Status**: Investigation complete, ready for next actions

---

## Summary

### ✅ What We Know

1. **Builtin Fix Successful**: Changed `ecdsa` → `bitwise` in Cairo0 program
2. **Error Progression**: `Invalid builtin` → `Invalid OODS` (progress!)
3. **OODS Understanding**: Composition polynomial mismatch between proof and reconstructed value

### 🔍 Root Cause

OODS validation fails because:
- Integrity reconstructs composition polynomial from trace values at OODS point
- Compares with claimed composition value from proof
- **They don't match** → "Invalid OODS" error

### 📋 Possible Causes (Prioritized)

1. **Proof Serialization** - OODS values may not be serialized correctly
2. **Public Input Format** - Structure may not match Integrity's expectations
3. **AIR Configuration** - Stone's AIR may not match Integrity's exactly
4. **Fiat-Shamir Channel** - OODS point generation may differ

---

## Next Actions

### Option 1: Test Small Layout (Quick Test)

Since our Cairo0 program uses `bitwise` (which matches small layout), try small layout:

```python
# In backend/app/config.py
INTEGRITY_LAYOUT = "small"  # Instead of "recursive"
```

**Why**: Small layout may have different OODS expectations that match our proof better.

### Option 2: Compare Proof Structures

Compare our proof JSON with Integrity's example:
- Check `unsent_commitment.oods_values` length
- Verify structure matches Integrity's format
- Check public input structure

### Option 3: Verify Proof Serialization

Check if `proof_serializer` correctly handles our proof:
- Run serializer on our proof
- Compare output with Integrity's example calldata
- Verify OODS values are included correctly

### Option 4: Check Public Input

Verify public input structure:
- Segments format
- Builtins array
- Memory segments
- Compare with Integrity's format

---

## Recommended Approach

**Start with Option 1 (Small Layout)**:
- Quick test (just config change)
- Our program uses `bitwise` which matches small layout
- May resolve OODS mismatch immediately

**If small layout fails, proceed with Option 2-4**:
- Deep dive into proof structure
- Compare with Integrity examples
- Verify serialization

---

## Documentation

- `OODS_ERROR_ANALYSIS.md` - Deep dive analysis
- `OODS_INVESTIGATION_PLAN.md` - Investigation plan
- `OODS_COMPARISON_ANALYSIS.md` - Comparison checklist
- `integration_tests/dev_log.md` - Logged findings

---

**Status**: Ready to test small layout or continue deep investigation.
