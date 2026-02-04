# Finding the Actual Failing Proof

**Date**: 2026-01-26  
**Status**: Resolving logical conflict - finding actual failing proof

---

## The Conflict

### What We Found
- **Public input**: `layout: "small"`, `ecdsa` segment
- **Proof file**: Same - `small + ecdsa`
- **Error**: Passed builtin validation → Failed at OODS

### User's Logic ✅
If proof had `small + ecdsa`, Integrity recursive would:
- Fail at builtin gate (not OODS)
- Never reach OODS validation

Since we reached OODS, verifier must have seen:
- `recursive + bitwise` (compatible)

---

## Conclusion

**This is NOT the actual failing proof.**

The proof we're looking at (`/tmp/risk_stone_dgpxtm73`) has `small + ecdsa`, but:
- We passed builtin validation
- We reached OODS
- This means the actual failing proof has `recursive + bitwise`

---

## Possible Explanations

### 1. Different Code Path
- Current run used Cairo0 path (`INTEGRITY_MEMORY_VERIFICATION = "strict"`)
- Actual failing proof used Cairo1 path (`INTEGRITY_MEMORY_VERIFICATION = "cairo1"`)
- Cairo1 path generates `recursive + bitwise`

### 2. Different Run
- This proof is from a different/test run
- Actual failing proof is from a different directory
- Need to find the actual failing proof directory

### 3. Stale Artifact
- This is an old proof
- Actual failing proof is newer
- Need to check timestamps

---

## User's Confirmation

User confirmed locally that a recent proof had:
- `layout: recursive`
- `memory_segments: bitwise, pedersen, range_check, output, program, execution`

**This matches what the verifier must have seen to pass builtin validation.**

---

## Next Steps

1. **Find actual failing proof** → Check all recent directories
2. **Check code path** → Verify if Cairo1 path was used
3. **Check timestamps** → Ensure we're looking at the right run
4. **If recursive + bitwise found** → Then the issue is deeper AIR/public_input mismatch

---

**Status**: This is NOT the failing proof. Need to find the actual failing proof with `recursive + bitwise`.
