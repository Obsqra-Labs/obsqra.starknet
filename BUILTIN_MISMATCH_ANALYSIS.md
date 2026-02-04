# Builtin Mismatch Analysis - Root Cause Identified

**Date**: 2026-01-26  
**Status**: Root cause of "Invalid builtin" error identified

---

## Root Cause: Builtin Configuration Mismatch

### The Problem

Integrity's verifier expects specific builtins based on the layout. Our Cairo programs use different builtins than what Integrity's recursive layout expects.

### Integrity's Recursive Layout Expected Builtins

From `integrity/src/air/layouts/recursive/constants.cairo`:

```cairo
fn get_builtins() -> Array<felt252> {
    array!['output', 'pedersen', 'range_check', 'bitwise']
}
```

**Recursive layout expects**: `output`, `pedersen`, `range_check`, `bitwise` (4 builtins)

### Our Cairo Programs' Builtins

#### Cairo0 Program (`risk_example_cairo0.cairo`)
```cairo
%builtins output pedersen range_check ecdsa
```

**Cairo0 uses**: `output`, `pedersen`, `range_check`, `ecdsa` (4 builtins)

**Mismatch**: We have `ecdsa` but Integrity expects `bitwise` ❌

#### Cairo1 Program (`risk_example.cairo`)
```cairo
// No explicit builtin declaration
// Cairo1 handles builtins differently
```

**Cairo1**: Builtins are implicit/handled by the compiler

**Mismatch**: Cairo1's builtin handling may not match Integrity's expectations ❌

---

## Integrity's Small Layout Expected Builtins

From `integrity/src/air/layouts/small/constants.cairo`:

```cairo
fn get_builtins() -> Array<felt252> {
    array!['output', 'pedersen', 'range_check', 'ecdsa', 'bitwise']
}
```

**Small layout expects**: `output`, `pedersen`, `range_check`, `ecdsa` (4 builtins)

**Match**: Small layout matches our Cairo0 program exactly! ✅

---

## Why This Causes "Invalid builtin" Error

1. **Public Input Verification**: Integrity's `public_input.cairo` checks:
   ```cairo
   let builtins = get_builtins();
   assert(*program[1] == builtins.len().into(), 'Invalid program');
   ```
   This verifies the program declares the correct number of builtins.

2. **Builtin Validation**: The verifier expects the proof's builtin configuration to match the layout's expected builtins exactly.

3. **Our Mismatch**: 
   - Recursive layout expects: `[output, pedersen, range_check, bitwise]`
   - Our Cairo0 program has: `[output, pedersen, range_check, ecdsa]`
   - **Result**: Verifier rejects with "Invalid builtin"

---

## Solutions

### Option 1: Update Cairo0 Program to Use Bitwise (Not ECDSA)

**Change**:
```cairo
%builtins output pedersen range_check bitwise  // Remove ecdsa, add bitwise
```

**Pros**: Matches recursive layout exactly  
**Cons**: Need to remove ECDSA usage from program (if any)

**Check**: Does our program actually use ECDSA? Looking at `risk_example_cairo0.cairo`, we declare `ecdsa_ptr` in main but never use it. We can safely remove it.

### Option 2: Use Small Layout (Includes Both ECDSA and Bitwise)

**Keep**: Current Cairo0 program with `ecdsa`  
**Use**: Small layout (which expects both `ecdsa` and `bitwise`)

**Pros**: No code changes needed  
**Cons**: Small layout may not verify on Integrity (we saw `Invalid final_pc` before)

### Option 3: Remove Unused Builtins

**For Cairo0**: Remove `ecdsa` if not used, add `bitwise` if needed  
**For Cairo1**: Ensure builtins match layout expectations

**Pros**: Clean, matches layout exactly  
**Cons**: Need to verify program doesn't need removed builtins

---

## Recommended Fix

### For Recursive Layout (Canonical)

1. **Update Cairo0 program**:
   ```cairo
   %builtins output pedersen range_check bitwise  // Changed from ecdsa
   ```

2. **Remove ECDSA usage**:
   - Remove `ecdsa_ptr` from main function signature
   - Remove `ecdsa_ptr: felt*` from return type

3. **Verify program still works**: ECDSA wasn't used anyway, so this should be safe

### For Small Layout (Fallback)

1. **Keep current program**: Small layout includes both `ecdsa` and `bitwise`
2. **Test**: See if small layout works with Integrity (may still have `Invalid final_pc`)

---

## Verification

After fixing, the builtin configuration should match:

**Recursive Layout**:
- Expected: `[output, pedersen, range_check, bitwise]` (4 builtins)
- Our program: `[output, pedersen, range_check, bitwise]` (4 builtins) ✅

**Small Layout**:
- Expected: `[output, pedersen, range_check, ecdsa, bitwise]` (5 builtins)
- Our program: `[output, pedersen, range_check, ecdsa]` (4 builtins) ❌
  - Would need to add `bitwise` for small layout

---

## Next Steps

1. **Update Cairo0 program**: Change `ecdsa` to `bitwise` in builtin declaration
2. **Remove ECDSA from function signatures**: Clean up unused builtin
3. **Test with recursive layout**: Should resolve "Invalid builtin" error
4. **If still fails**: Check if there are other builtin-related issues

---

**Status**: Root cause identified! Builtin mismatch between our program (`ecdsa`) and Integrity's recursive layout expectation (`bitwise`).
