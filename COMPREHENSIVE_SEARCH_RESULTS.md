# Comprehensive Stone5 Commit Search - Final Results

**Date**: 2026-01-27  
**Status**: Comprehensive search completed (internal + external)

## Executive Summary

**Result**: ❌ **Exact Stone5 commit NOT found**

However, we've identified key information and narrowed down the possibilities.

## Search Results

### ✅ Internal Server Search

#### Stone Prover Repository
- **Current commit**: `1414a545e4fb38a85391289abe91dd4467d268e1` (Stone v3, Sept 16, 2024)
- **Stone v2 commit**: `7ac17c8ba63a789604350e501558ef0ab990fd88` (March 4, 2024)
- **Commits between v2-v3**: 15 commits (March-Sept 2024)
- **No tags**: Repository has no git tags
- **No "stone5" references**: No commits mention "stone5"

#### Integrity Repository
- **Canonical example added**: `5702c4f` (Nov 19, 2024)
- **No Stone commit info**: No references in deployment, CI, or docs
- **Stone5 is enum**: `StoneVersion::Stone5` in Cairo code (runtime setting)

### ✅ External Web Search

#### Stone Prover
- **Main repo**: https://github.com/starkware-libs/stone-prover
- **No stone5 tags**: No version tags for "stone5"
- **Version naming**: Uses "Stone v2", "Stone v3" (not "stone5")
- **Related commit**: `7b31959ba27eb0af384a95b3be49d1228714ace2` (not in our repo)

#### Integrity
- **No version docs**: No documentation specifying Stone commit
- **Runtime setting**: "stone5" is a verifier runtime configuration

## Critical Discovery: Version Naming Mismatch

### The Problem
- **Stone Prover**: Uses "Stone v2", "Stone v3" naming
- **Integrity**: Uses "stone5", "stone6" as runtime settings
- **Mapping unknown**: No documentation maps "Stone vX" to "stone5/stone6"

### Timeline Analysis
- **Stone v2**: March 4, 2024
- **Stone v3**: Sept 16, 2024 (our current)
- **Canonical examples**: Nov 19, 2024
- **Gap**: 2+ months between Stone v3 and examples

**Implication**: Examples likely generated with Stone v3 OR an intermediate commit

## Proof Version Field

**Canonical proof version**:
```json
{
  "commit_hash": "INVALID_COMMIT",
  "proof_hash": "INVALID_PROOF_HASH",
  "statement_name": "INVALID_NAME"
}
```

**Analysis**: Placeholder values - proof generated without version defines set during build. Not helpful for identifying commit.

## Most Likely Scenarios

### Scenario 1: Stone v3 = stone5 ✅ MOST LIKELY
- **Timeline fits**: Stone v3 (Sept) before examples (Nov)
- **Our commit**: Already using Stone v3
- **Problem**: OODS fails despite matching FRI params
- **Conclusion**: Either build/config difference OR verifier expects different Stone semantics

### Scenario 2: Stone v2 = stone5
- **Timeline fits**: Stone v2 (March) well before examples (Nov)
- **Test needed**: Build with Stone v2 and verify
- **Action**: Test Stone v2 commit

### Scenario 3: Intermediate commit = stone5
- **Between v2-v3**: 15 commits between March-Sept 2024
- **Test needed**: Try commits chronologically
- **Action**: Binary search through intermediate commits

## What We Know About stone5 vs stone6

From Integrity source code:
- **stone5 hashers**: `keccak_160_lsb`, `blake2s_160`
- **stone6 hashers**: `keccak_160_lsb`, `blake2s_248_lsb`
- **Runtime enum**: `StoneVersion::Stone5` = 0, `StoneVersion::Stone6` = 1
- **Verifier logic**: Different handling based on stone_version enum

**Key Insight**: The verifier has different code paths for stone5 vs stone6, but we don't know which Stone Prover commit generates "stone5" proofs.

## Recommended Next Actions

### Priority 1: Test Stone v2 ⭐ RECOMMENDED
**Why**: Stone v2 is the only other major version before examples were created

**Steps**:
1. Checkout Stone v2: `git checkout 7ac17c8ba63a789604350e501558ef0ab990fd88`
2. Rebuild Stone binary
3. Generate proof with Stone v2
4. Test on-chain verification
5. **If verifies** → Stone v2 is "stone5" ✅
6. **If fails** → Continue to Priority 2

### Priority 2: Check Integrity Source for stone5 Logic
- Look for code that shows what stone5 expects vs stone6
- May reveal version-specific proof structure differences
- Could indicate which Stone Prover version generates stone5 proofs

### Priority 3: Test Intermediate Commits
- If v2 doesn't work, test commits between v2 and v3
- Binary search: test midpoint commits
- Time-consuming but systematic

### Priority 4: Contact Integrity Team
- Direct question: "What Stone Prover commit generates stone5 proofs?"
- GitHub: https://github.com/HerodotusDev/integrity
- May be fastest path if team responds

## Files Created

1. **`STONE_COMMIT_SEARCH_RESULTS.md`** - Detailed search results
2. **`STONE_VERSION_MAPPING_ANALYSIS.md`** - Version mapping analysis
3. **`COMPREHENSIVE_SEARCH_RESULTS.md`** - This file (executive summary)
4. **`SEARCH_AGENT_PROMPT.md`** - Prompt for GPT search agent (if needed)

## Conclusion

**Status**: Exact commit not found, but **CRITICAL DISCOVERY** made

### ⚠️ CRITICAL FINDING: stone5 vs stone6 Hash Difference

**Found in**: `integrity/src/air/public_input.cairo`

**Key Difference**:
- **stone6**: Includes `n_verifier_friendly_commitment_layers` in public input hash
- **stone5**: Does NOT include it in public input hash

**Impact**: This affects channel seed → OODS point → OODS validation

**Most Likely Root Cause**: 
- Stone v3 might generate proofs with **stone6 semantics** (includes in hash)
- We're verifying as **stone5** (doesn't include in hash)
- **→ OODS mismatch** ✅ **This explains the failure!**

**Immediate Next Step**: **Test verifying as stone6 instead of stone5**

See `CRITICAL_DISCOVERY_STONE5_VS_STONE6.md` for details.
