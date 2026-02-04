# Stone5 vs Stone6 Decision

**Date**: 2026-01-27  
**Decision**: **Stay with Stone5**

## Context from Integrity Documentation

### Stone6 Requirements
- Stone6 can work end-to-end, but **only if the verifier side is built+registered for stone6**
- Integrity supports stone6 as a runtime setting
- Hasher options for stone6: `keccak_160_lsb` or `blake2s_248_lsb`
- **Critical**: End-to-end only works if FactRegistry has stone6 verifiers registered for your layout/hasher

### Stone5 Status
- Public FactRegistry has stone5 verifiers registered ✅
- Canonical stone5 proof verifies successfully ✅
- Our current config uses stone5 ✅

## Decision Rationale

### ✅ Stay with Stone5

**Reasons**:
1. **Public registry ready**: Public FactRegistry (`0x4ce7851f...`) has stone5 verifiers registered
2. **Canonical proof verifies**: Integrity's canonical stone5 proof verifies on public registry
3. **Current config aligned**: We're already using stone5 in config
4. **No migration needed**: No need to register new verifiers or change infrastructure

**Action**: Fix our pipeline to match the stone5 verifier that's already registered

### ❌ Don't Switch to Stone6 (Yet)

**Blockers**:
1. **No stone6 verifiers registered**: Public FactRegistry likely only has stone5 verifiers
2. **Would require deployment**: Would need to deploy and register stone6 verifiers
3. **Unnecessary complexity**: Stone5 works, just need to match the registered verifier's Stone commit

**When to consider Stone6**:
- After stone5 pipeline is stable and verified
- If you deploy your own FactRegistry with stone6 verifiers
- If public registry adds stone6 verifiers for your layout/hasher

## Current Issue

**Problem**: Our Stone binary commit (`1414a545...` Stone v3) doesn't match the Stone commit used by the registered stone5 verifier

**Solution**: Find the exact Stone commit used by the registered stone5 verifier and rebuild our Stone binary to match

## Next Steps

1. **Continue with Stone5** ✅
2. **Find exact Stone5 commit** used by registered verifier (Priority 1)
3. **Rebuild Stone binary** with matching commit
4. **Test on-chain verification**

## References

- Integrity supports stone6: https://github.com/HerodotusDev/integrity
- Stone6 hasher options: `keccak_160_lsb` or `blake2s_248_lsb`
- FactRegistry routes proofs to correct verifier based on stone_version setting
