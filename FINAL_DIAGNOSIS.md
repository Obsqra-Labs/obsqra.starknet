# Final OODS Diagnosis

**Date**: 2026-01-26  
**Status**: Root cause confirmed, solution identified

---

## ✅ Root Cause Confirmed

**Cairo0's `cairo-run` does NOT support `recursive` layout.**

### Evidence
1. **Config**: `INTEGRITY_LAYOUT = "recursive"`
2. **Generated public input**: `layout: "small"` (not `recursive`)
3. **Builtin mismatch**: `ecdsa` segment (not `bitwise`)
4. **Cairo version**: `cairo-run 0.14.0.1` (Cairo0)

### Why OODS Fails
- Stone generates proof with `small` layout + `ecdsa` builtin AIR
- Integrity verifier expects `recursive` layout + `bitwise` builtin AIR
- **AIR mismatch** → Different composition polynomial → OODS mismatch

---

## Solution: Use Cairo1 Path

### Current Status
- We have Cairo1 path in code (`INTEGRITY_MEMORY_VERIFICATION == "cairo1"`)
- But it's likely set to `"strict"` (Cairo0 path)
- Need to switch to `"cairo1"` to use `cairo1-run`

### Action Required
1. **Change config**: `INTEGRITY_MEMORY_VERIFICATION = "cairo1"`
2. **Verify Cairo1 program**: Ensure `risk_example.cairo` uses `bitwise`
3. **Test**: Run with Cairo1 path and verify recursive layout is generated

---

## Alternative: Use Small Layout + Split

If Cairo1 doesn't work:
1. **Change config**: `INTEGRITY_LAYOUT = "small"`
2. **Use split serialization**: Not monolith (monolith only supports recursive)
3. **Keep ecdsa**: Or change program back to `ecdsa` builtin

---

## Next Steps

1. **Switch to Cairo1 path** → Test if it generates recursive layout
2. **Verify layout in public input** → Should be `"recursive"` with `bitwise`
3. **Test Integrity verification** → Should pass OODS check

---

**Status**: ✅ Root cause confirmed. Solution: Use Cairo1 path or switch to small layout + split serialization.
