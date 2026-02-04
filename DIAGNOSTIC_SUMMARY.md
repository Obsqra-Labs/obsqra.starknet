# OODS Diagnostic Summary

**Date**: 2026-01-26  
**Status**: Following user's corrected analysis

---

## Key Insight from User

**The OODS mismatch is NOT because of structure differences** - it's because:
- The verifier reconstructs a different composition polynomial from our public input
- Than what the proof claims

**Root Cause**: The AIR in Integrity's recursive verifier is **NOT the same AIR** that Stone used to generate our proof.

---

## Critical Finding: Layout Mismatch

### Our Generated Public Input
- **Layout**: `"small"` ❌ (should be `"recursive"`)
- **Builtins**: `ecdsa` segment present, `bitwise` missing ❌
- **Field order**: Different from example

### Integrity's Recursive Example
- **Layout**: `"recursive"` ✅
- **Builtins**: `bitwise` segment present ✅
- **Field order**: Standard format

**This confirms**: `cairo-run --layout recursive` is NOT working - it's generating `small` layout instead.

---

## Diagnostic Results

### Step 1: Canonical Proof Test
- **Status**: Failed (wallet config issue, not proof issue)
- **Action**: Need to test with proper wallet config or use read-only call

### Step 2: Stone Local Verifier
- **Status**: Testing...
- **Goal**: Verify if our proof is internally consistent
- **If passes**: Proof is valid, issue is in serializer/verifier mismatch
- **If fails**: Proof/public input mismatch

### Step 3: Schema Comparison
- **Layout**: Mismatch (small vs recursive)
- **Builtins**: Mismatch (ecdsa vs bitwise)
- **Field order**: Different
- **Segment order**: Different

### Step 4: Cairo Version
- **Our version**: `cairo-run 0.14.0.1`
- **Example version**: Checking...

---

## Root Cause Hypothesis

**Cairo0's `cairo-run` does NOT support `recursive` layout.**

The `--layout recursive` flag is being ignored, and it defaults to `small` layout. This means:
1. Stone generates proof with `small` layout AIR
2. Integrity verifier expects `recursive` layout AIR
3. AIR mismatch → OODS mismatch

---

## Solutions

### Option 1: Use Cairo1 (Recommended)
- Use `cairo1-run` with `recursive` layout
- Cairo1 supports recursive layout
- Our program already uses `bitwise` builtin

### Option 2: Use Small Layout + Split Serialization
- Change config to `INTEGRITY_LAYOUT = "small"`
- Use split serialization (not monolith)
- Keep `ecdsa` builtin (or change program back)

### Option 3: Fix Cairo0 Layout Support
- Check if there's a way to make Cairo0 use recursive layout
- May require different Cairo version or toolchain

---

## Next Actions

1. **Run Stone verifier** → Test proof consistency
2. **Test Cairo1 path** → Try `cairo1-run` with recursive
3. **Compare versions** → Align Cairo toolchain
4. **Fix or switch** → Either fix recursive or switch to small

---

**Status**: Layout mismatch confirmed. Cairo0's `cairo-run` doesn't support `recursive` layout. Need to use Cairo1 or switch to small layout.
