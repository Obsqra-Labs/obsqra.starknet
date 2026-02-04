# ECDSA Segment Issue - Empty but Still Rejected

**Date**: 2026-01-27  
**Status**: OODS fixed, but empty ecdsa segment causes Invalid builtin error

---

## Issue

**Proof has empty `ecdsa` segment:**
- `memory_segments.ecdsa: {begin_addr: 2840, stop_ptr: 2840}`
- `begin_addr == stop_ptr` means the segment is **empty** (no actual usage)
- But Integrity's recursive layout **does not support ecdsa at all**
- `HAS_ECDSA_BUILTIN: felt252 = 0` in recursive layout constants

**Result**: Integrity rejects the proof with "Invalid builtin" even though ecdsa is unused.

---

## Root Cause

**cairo-run with `--layout recursive` is adding an ecdsa segment** even though:
- The Cairo program doesn't declare ecdsa (`%builtins output pedersen range_check bitwise`)
- The compiled program doesn't have ecdsa (`["output", "pedersen", "range_check", "bitwise"]`)
- The ecdsa segment is empty (no actual usage)

**This suggests cairo-run is adding all layout-supported builtins to the trace**, even if they're not used.

---

## Solution

Need to prevent cairo-run from adding the ecdsa segment. Options:

1. **Check cairo-run flags** - See if there's a flag to exclude unused builtins
2. **Post-process the trace** - Remove ecdsa segment before proof generation
3. **Use different layout** - But we need recursive for Integrity
4. **Check if Stone prover can ignore empty segments** - Probably not, Integrity validates them

---

## Files to Check

- `backend/app/api/routes/risk_engine.py` - cairo-run command
- Stone prover configuration - Can it filter empty segments?
- Integrity validation code - Can it skip empty unsupported segments?

---

**Status**: 🎯 OODS fixed! But empty ecdsa segment causes Invalid builtin. Need to prevent cairo-run from adding it.
