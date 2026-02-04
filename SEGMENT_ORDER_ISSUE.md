# Segment Order Issue - Index Out of Bounds

**Date**: 2026-01-27  
**Status**: OODS fixed, ecdsa removed, but segment indices broken

---

## Progress! ✅

1. ✅ **OODS fixed** - `n_verifier_friendly_commitment_layers: 1000 → 9999`
2. ✅ **ECDSA removed from proof JSON** - Error changed from "Invalid builtin" to "Index out of bounds"

---

## Current Issue: Index Out of Bounds ❌

**Error**: `Index out of bounds` when Integrity tries to access segments

**Root Cause**:
- Integrity's recursive layout expects segments in specific order:
  - PROGRAM: 0
  - EXECUTION: 1
  - OUTPUT: 2
  - PEDERSEN: 3
  - RANGE_CHECK: 4
  - BITWISE: 5
- cairo-run adds ecdsa segment (possibly at index 5)
- We remove ecdsa, but Integrity expects bitwise at index 5
- Segment indices don't match → Index out of bounds

---

## Possible Solutions

1. **Prevent cairo-run from adding ecdsa** - But how?
2. **Reorder segments after removing ecdsa** - Ensure correct order
3. **Keep ecdsa but mark as unused** - But Integrity rejects it
4. **Use different layout** - But we need recursive for Integrity

---

## Next Steps

1. Check segment order in proof JSON
2. Verify if Integrity uses indices or names for segments
3. Try reordering segments to match Integrity's expectations
4. Or find a way to prevent cairo-run from adding ecdsa

---

**Status**: 🎯 OODS fixed! But segment order issue after removing ecdsa. Need to fix segment indices.
