# Builtin Mismatch Fix Plan

**Date**: 2026-01-26  
**Status**: Fix identified and ready to implement

---

## Root Cause Summary

**Problem**: "Invalid builtin" error when verifying proofs with Integrity's recursive layout

**Root Cause**: Builtin mismatch
- **Recursive layout expects**: `[output, pedersen, range_check, bitwise]`
- **Our Cairo0 program has**: `[output, pedersen, range_check, ecdsa]`
- **Mismatch**: `ecdsa` vs `bitwise`

**Small layout matches**: `[output, pedersen, range_check, ecdsa]` ✅

---

## Fix Options

### Option 1: Update Cairo0 Program for Recursive Layout (Recommended for Canonical)

**Change**: Replace `ecdsa` with `bitwise` in builtin declaration

**File**: `verification/risk_example_cairo0.cairo`

**Changes**:
1. Line 1: Change `%builtins output pedersen range_check ecdsa` to `%builtins output pedersen range_check bitwise`
2. Line 76: Remove `ecdsa_ptr: felt*` from main function signature
3. Line 77: Remove `ecdsa_ptr: felt*` from return type

**Verification**: ECDSA is declared but never used in the program, so removing it is safe.

**Pros**:
- Matches recursive layout (canonical) exactly
- Should resolve "Invalid builtin" error
- Enables canonical AIR regeneration

**Cons**:
- Need to verify program doesn't need bitwise operations
- May need to add bitwise operations if program requires them

---

### Option 2: Use Small Layout (Matches Current Program)

**Keep**: Current Cairo0 program unchanged

**Change**: Use small layout instead of recursive

**Config**: `INTEGRITY_LAYOUT: str = "small"`

**Pros**:
- No code changes needed
- Matches our program's builtins exactly
- Fast proof generation

**Cons**:
- Not canonical (recursive is canonical)
- May still have `Invalid final_pc` issues (from previous tests)

---

## Recommended Approach

**For Canonical AIR (Recursive Layout)**:
1. Update Cairo0 program: `ecdsa` → `bitwise`
2. Remove unused ECDSA from function signatures
3. Test with recursive layout
4. Should resolve "Invalid builtin" error

**For Fallback (Small Layout)**:
1. Keep current program
2. Use small layout
3. Accept that it's not canonical

---

## Implementation Steps

### Step 1: Update Cairo0 Program

```cairo
// Before
%builtins output pedersen range_check ecdsa

func main{
    output_ptr: felt*,
    pedersen_ptr: felt*,
    range_check_ptr: felt,
    ecdsa_ptr: felt*,  // Remove this
}() {
    // ...
    return (
        output_ptr=&output_ptr[2],
        pedersen_ptr=pedersen_ptr,
        range_check_ptr=range_check_ptr,
        ecdsa_ptr=ecdsa_ptr,  // Remove this
    );
}

// After
%builtins output pedersen range_check bitwise

func main{
    output_ptr: felt*,
    pedersen_ptr: felt*,
    range_check_ptr: felt,
    bitwise_ptr: felt*,  // Add this (if needed)
}() {
    // ...
    return (
        output_ptr=&output_ptr[2],
        pedersen_ptr=pedersen_ptr,
        range_check_ptr=range_check_ptr,
        bitwise_ptr=bitwise_ptr,  // Add this (if needed)
    );
}
```

**Note**: If bitwise isn't used, we can omit `bitwise_ptr` from the function signature (just declare the builtin).

### Step 2: Test

1. Generate proof with updated program
2. Verify with Integrity recursive layout
3. Should pass "Invalid builtin" check
4. May still have other issues (e.g., `Invalid final_pc`)

---

## Expected Outcome

**After Fix**:
- ✅ Builtin configuration matches recursive layout
- ✅ "Invalid builtin" error should be resolved
- ⚠️ May still encounter other verification issues (e.g., `Invalid final_pc`)

**If Still Fails**:
- Check for other builtin-related issues
- Verify program structure matches Integrity's expectations
- Consider using small layout as fallback

---

**Status**: Ready to implement. Fix is straightforward: change `ecdsa` to `bitwise` in Cairo0 program.
