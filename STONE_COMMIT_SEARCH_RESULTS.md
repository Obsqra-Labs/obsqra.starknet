# Stone Commit Search Results

**Date**: 2026-01-27  
**Status**: Comprehensive search completed

## Search Summary

### ✅ Internal Server Search (Complete)

#### Stone Prover Repository
- **Our current commit**: `1414a545e4fb38a85391289abe91dd4467d268e1` (Stone v3, Sept 16, 2024)
- **Stone v2 commit**: `7ac17c8ba63a789604350e501558ef0ab990fd88` (March 4, 2024)
- **No tags found**: Repository has no git tags
- **No stone5-specific commits**: No commits specifically mentioning "stone5"
- **No commits in Nov 2024**: No activity in stone-prover repo during Nov 2024 (when canonical examples were added)

#### Integrity Repository
- **Canonical example added**: Commit `5702c4f` (Nov 19, 2024) - "example proofs"
- **No Stone commit info**: No references to specific Stone commits in:
  - Deployment scripts
  - CI workflows
  - README
  - Example generation scripts
  - Cargo.toml (no stone-prover dependency)

### ✅ External Web Search (Complete)

#### Stone Prover Repository
- **Main repo**: https://github.com/starkware-libs/stone-prover
- **No stone5 tags/releases found**: No specific "stone5" version tags
- **Version structure**: Uses "Stone v2", "Stone v3" naming (not "stone5")
- **Related commit found**: `7b31959ba27eb0af384a95b3be49d1228714ace2` (used in stone-prover-cairo0-verifier project)

#### Integrity Repository
- **Main repo**: https://github.com/HerodotusDev/integrity
- **No version requirements found**: No documentation specifying exact Stone commit
- **Stone5 is runtime setting**: "stone5" is a runtime configuration, not a specific commit

## Key Findings

### 1. Version Naming Confusion

**Important Discovery**: 
- Stone Prover uses "Stone v2", "Stone v3" naming in commits
- Integrity uses "stone5", "stone6" as runtime settings
- **These are different naming schemes!**

**Our commit**: `1414a545...` is labeled "Stone v3" (Sept 2024)
**Integrity expects**: "stone5" (runtime setting)

**Question**: Is "Stone v3" the same as "stone5"? Or is there a different commit?

### 2. No Stone Commit in Proof JSON

- Canonical proof JSON has a `version` field
- Need to check if it contains commit hash info

### 3. Timeline Mismatch

- **Stone v3 created**: Sept 16, 2024
- **Canonical examples added**: Nov 19, 2024
- **Gap**: 2+ months between Stone v3 and canonical examples

**Implication**: Canonical examples might have been generated with Stone v3, OR with a different commit between Sept-Nov 2024

## Next Steps

### Option 1: Check Proof Version Field
- Extract version info from canonical proof JSON
- May contain commit hash or version identifier

### Option 2: Test Stone v2
- Try building with Stone v2 commit (`7ac17c8b...`)
- Generate proof and test on-chain
- If verifies → Stone v2 is "stone5"

### Option 3: Contact Integrity Team
- Ask directly: "What Stone Prover commit was used to generate the canonical stone5 examples?"
- GitHub: https://github.com/HerodotusDev/integrity
- Discord/Community: Check Integrity's community channels

### Option 4: Reverse Engineer from Proof
- Compare proof structure between our proof and canonical
- Look for differences that might indicate different Stone versions
- Check if there are version-specific proof features

## References Found

1. **stone-prover-cairo0-verifier**: Uses commit `7b31959ba27eb0af384a95b3be49d1228714ace2`
   - This might be a different/older version
   - Worth checking if this commit exists in our repo

2. **Stone v2**: `7ac17c8ba63a789604350e501558ef0ab990fd88` (March 2024)
3. **Stone v3**: `1414a545e4fb38a85391289abe91dd4467d268e1` (Sept 2024) - **Our current**

## Conclusion

**Status**: Exact Stone5 commit not found through search

**Most Likely Scenarios**:
1. "Stone v3" (our commit) IS "stone5" - but verifier was built differently
2. "Stone v2" is actually "stone5" - need to test
3. There's an intermediate commit between v2 and v3 that's "stone5"
4. Version field in proof JSON contains the answer

**Recommended Next Action**: Check the `version` field in canonical proof JSON for commit hash
