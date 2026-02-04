# Builtin Issue: Proof Has ECDSA Segment

**Date**: 2026-01-27  
**Status**: OODS fixed, but builtin issue re-emerged with ecdsa segment

---

## Progress! ✅

**The `n_verifier_friendly_commitment_layers` fix worked!**

- ✅ Error changed from **"Invalid OODS"** to **"Invalid builtin"**
- ✅ This means we **passed the OODS check!**

---

## New Issue: Proof Has ECDSA Segment ❌

**Error**: `Invalid builtin - The proof's builtins do not match the verifier's expectations`

**Root Cause Found**:
- Proof has `memory_segments.ecdsa: {begin_addr: 2840, stop_ptr: 2840}`
- But Integrity's recursive layout expects: `output, pedersen, range_check, bitwise`
- **NO ecdsa!**

**The Cairo program is correct:**
- `risk_example_cairo0.cairo` has: `%builtins output pedersen range_check bitwise`
- But the proof was generated with an `ecdsa` segment

---

## Possible Causes

1. **Compiled program cache** - Old compiled program still has ecdsa builtins
2. **cairo-run behavior** - Adding ecdsa based on old compiled program
3. **Trace generation** - Trace was generated before the bitwise fix

---

## Solution

Need to ensure:
1. Compiled program uses `bitwise`, not `ecdsa`
2. No cached compiled programs with old builtins
3. Fresh compilation before proof generation

---

## Files to Check

- `verification/risk_example_cairo0.cairo` - ✅ Has correct builtins
- Compiled program JSON - ❓ May have old ecdsa builtins
- Proof generation process - ❓ May be using cached compiled program

---

**Status**: 🎯 OODS fixed! But proof has ecdsa segment instead of bitwise. Need to fix compiled program.
