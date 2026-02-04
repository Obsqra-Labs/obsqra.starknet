# Stone Version Mapping Analysis

**Date**: 2026-01-27  
**Status**: Resolved — Stone v3 maps to stone6 semantics

## Resolution (Jan 27, 2026) ✅ RESOLVED

**Finding**: Stone v3 (`1414a545e4fb38a85391289abe91dd4467d268e1`) produces **stone6** semantics.

**Root Cause**: 
- Stone v3 includes `n_verifier_friendly_commitment_layers` in public input hash calculation
- Integrity's `stone6` verifier expects this in the hash
- Integrity's `stone5` verifier does NOT expect this in the hash
- Mismatch causes OODS failures

**Resolution**:
- ✅ **Stone v3 → stone6 is canonical production path**
- ✅ Updated `INTEGRITY_STONE_VERSION = "stone6"` in production config
- ✅ OODS passes when verifying Stone v3 proofs as `stone6`
- ✅ Dropped Stone v2 path (no longer needed)
- ✅ Cleaned up temporary Stone v2 worktree

**Impact**:
- Verifying Stone v3 proofs as **stone5** fails OODS (public input hash mismatch).
- Verifying as **stone6** passes OODS ✅
- Public FactRegistry has **both** stone5 and stone6 verifiers registered.

**Production Action**:
- ✅ Production config uses `INTEGRITY_STONE_VERSION = "stone6"` (confirmed)
- ✅ All Obsqra proofs must use `stone6` verifier
- ✅ Canonical Integrity examples remain `stone5` (historical, for replaying examples only)

## Key Discovery: Version Naming Mismatch

### Stone Prover Naming
- **Stone v2**: `7ac17c8ba63a789604350e501558ef0ab990fd88` (March 4, 2024)
- **Stone v3**: `1414a545e4fb38a85391289abe91dd4467d268e1` (Sept 16, 2024) - **Our current**

### Integrity Naming
- **stone5**: Runtime setting for verifier
- **stone6**: Runtime setting for verifier

### The Question
**Is "Stone v3" the same as "stone5"?**

## Timeline Analysis

### Stone Prover Timeline
- **March 2024**: Stone v2 released
- **Sept 2024**: Stone v3 released (our current)
- **Nov 2024**: Canonical examples added to Integrity

### Gap Analysis
- **2 months** between Stone v3 (Sept) and canonical examples (Nov)
- No commits in stone-prover repo during Nov 2024
- Canonical examples likely generated with Stone v3 OR Stone v2

## Hypothesis Testing

### Hypothesis 1: Stone v3 = stone5
- **Timeline fits**: Stone v3 (Sept) before examples (Nov)
- **Our commit**: Already using Stone v3
- **Problem**: OODS still fails
- **Conclusion**: Either Stone v3 ≠ stone5, OR there's a build/config difference

### Hypothesis 2: Stone v2 = stone5
- **Timeline fits**: Stone v2 (March) well before examples (Nov)
- **Test needed**: Build with Stone v2 and test
- **Action**: Checkout Stone v2, rebuild, generate proof, test on-chain

### Hypothesis 3: Intermediate commit = stone5
- **Between v2 and v3**: Check commits between March-Sept 2024
- **Test needed**: Try commits between v2 and v3
- **Action**: Test commits chronologically between v2 and v3

## Proof Version Field

**Canonical proof version field**:
```json
{
  "commit_hash": "INVALID_COMMIT",
  "proof_hash": "INVALID_PROOF_HASH",
  "statement_name": "INVALID_NAME"
}
```

**Analysis**: These are placeholder values - proof was generated without proper version info set during build. This is common when Stone is built without version defines.

## Next Steps

### Priority 1: Test Stone v2
1. Checkout Stone v2: `git checkout 7ac17c8ba63a789604350e501558ef0ab990fd88`
2. Rebuild Stone binary
3. Generate proof with Stone v2
4. Test on-chain verification
5. If verifies → Stone v2 is "stone5"

### Priority 2: Check Integrity Source
- Look for code that maps "stone5" to specific Stone behavior
- Check if there are version-specific checks in verifier
- May reveal which Stone version corresponds to "stone5"

### Priority 3: Test Intermediate Commits
- If v2 doesn't work, test commits between v2 and v3
- Binary search approach: test midpoint commits

## Current Status ✅ RESOLVED

**Resolution Confirmed**:
- ✅ Stone v3 (`1414a545...`) → **stone6** semantics (confirmed)
- ✅ OODS passes with stone6 verifier (tested and validated)
- ✅ Production config updated to use `stone6`
- ✅ Stone v2 path dropped (no longer needed)

**Production Configuration**:
```python
INTEGRITY_STONE_VERSION = "stone6"  # CONFIRMED: Stone v3 generates stone6 proofs
```

**Canonical Examples**:
- Integrity's canonical examples use `stone5`
- Use `stone5` **only** when replaying Integrity's canonical example proofs
- **All Obsqra production proofs must use `stone6`**

**Files Updated**:
- `backend/app/config.py` - Set `INTEGRITY_STONE_VERSION = "stone6"`
- `STONE_VERSION_MAPPING_ANALYSIS.md` - This document (resolution documented)
- `docs/proving_flows.md` - Clarified canonical vs production paths
- `integration_tests/dev_log.md` - Logged resolution

**Status**: ✅ **RESOLVED** - Stone v3 → stone6 is canonical production path
