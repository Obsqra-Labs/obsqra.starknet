# S-two Cairo AIR Research Summary

**Date**: 2026-01-26  
**Source**: [S-two Cairo AIR Documentation](https://docs.starknet.io/learn/S-two-book/cairo-air/index)  
**Purpose**: Understand Cairo AIR, builtins, and Integrity verification requirements

---

## Key Findings from Documentation

### Cairo AIR Architecture

From the [S-two Cairo AIR documentation](https://docs.starknet.io/learn/S-two-book/cairo-air/index):

1. **Cairo AIR follows standard CPU architecture**:
   - **Fetch phase**: Load instructions
   - **Decode phase**: Validate instructions
   - **Execute phase**: Execute operations

2. **Main Components**:
   - **Memory Component**: Maps addresses to IDs, then IDs to values (Small 72-bit vs Big 252-bit)
   - **VerifyInstruction Component**: Validates instruction correctness
   - **Opcode Component**: Handles execution semantics

3. **Component Interconnection**: Uses lookups (memory, instruction, register) to prove constraint satisfaction

---

## Builtin Configuration Requirements

### Integrity Layout Builtin Expectations

From Integrity's source code (`integrity/src/air/layouts/*/constants.cairo`):

#### Recursive Layout (Canonical)
```cairo
fn get_builtins() -> Array<felt252> {
    array!['output', 'pedersen', 'range_check', 'bitwise']
}
```
**Expected**: `[output, pedersen, range_check, bitwise]` (4 builtins)

#### Small Layout
```cairo
fn get_builtins() -> Array<felt252> {
    array!['output', 'pedersen', 'range_check', 'ecdsa']
}
```
**Expected**: `[output, pedersen, range_check, ecdsa]` (4 builtins)

#### Starknet Layout
```cairo
fn get_builtins() -> Array<felt252> {
    array!['output', 'pedersen', 'range_check', 'ecdsa', 'bitwise', 'ec_op', 'poseidon']
}
```
**Expected**: 7 builtins

#### Starknet with Keccak Layout
```cairo
fn get_builtins() -> Array<felt252> {
    array!['output', 'pedersen', 'range_check', 'ecdsa', 'bitwise', 'ec_op', 'keccak', 'poseidon']
}
```
**Expected**: 8 builtins

---

## Our Program's Builtins

### Cairo0 Program (`risk_example_cairo0.cairo`)
```cairo
%builtins output pedersen range_check ecdsa
```

**Has**: `[output, pedersen, range_check, ecdsa]` (4 builtins)

**Match Analysis**:
- ✅ **Small layout**: Perfect match!
- ❌ **Recursive layout**: Mismatch (`ecdsa` vs `bitwise`)
- ❌ **Starknet layouts**: Missing builtins

### Cairo1 Program (`risk_example.cairo`)
```cairo
// No explicit builtin declaration
// Cairo1 handles builtins implicitly
```

**Has**: Implicit builtins (handled by compiler)

**Match Analysis**: Unknown - depends on Cairo1 compiler's builtin selection

---

## Public Input Verification

From `integrity/src/air/layouts/*/public_input.cairo`:

The verifier checks:
```cairo
let builtins = get_builtins();
assert(*program[1] == builtins.len().into(), 'Invalid program');
```

This validates:
1. The program declares the correct number of builtins
2. The builtin configuration matches the layout's expectations

**Our Issue**: The program's builtin count/configuration doesn't match recursive layout's expectations.

---

## Why "Invalid builtin" Error Occurs

1. **Builtin Count Mismatch**: Program declares 4 builtins, but recursive layout expects specific 4 (different set)

2. **Builtin Type Mismatch**: 
   - Program has: `ecdsa`
   - Recursive expects: `bitwise`
   - Verifier rejects: "Invalid builtin"

3. **Public Input Validation**: The verifier checks builtin configuration in public input verification phase

---

## Solutions Based on Documentation

### Solution 1: Match Recursive Layout (Canonical)
- Change Cairo0 program: `ecdsa` → `bitwise`
- Matches Integrity's canonical recursive layout
- Should resolve "Invalid builtin" error

### Solution 2: Use Small Layout
- Keep current program (matches small layout)
- Not canonical, but may work
- Fast proof generation

### Solution 3: Use Appropriate Layout
- Match program's builtins to layout's expectations
- Each layout has specific builtin requirements
- Choose layout that matches program's needs

---

## Key Insights from S-two Documentation

1. **Cairo AIR is layout-specific**: Each layout (recursive, small, starknet, etc.) has specific builtin requirements

2. **Builtins are validated**: Integrity's verifier strictly validates builtin configuration

3. **Layout determines builtins**: The layout you choose determines which builtins are expected

4. **Canonical vs Practical**: 
   - Recursive is canonical but requires `bitwise`
   - Small is practical and matches our program

---

## Recommendations

1. **For Canonical AIR**: Update program to use `bitwise` instead of `ecdsa`
2. **For Practical Use**: Use small layout (matches current program)
3. **For Production**: Consider Atlantic integration (handles builtin configuration automatically)

---

**Status**: Research complete. Root cause identified: builtin mismatch between program and layout expectations.
