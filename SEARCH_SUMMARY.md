# Stone5 Commit Search - Summary

**Date**: 2026-01-27  
**Status**: Search tools and prompts ready

## What We've Done

### ✅ Local Server Search
- Checked Integrity repository files
- Reviewed deployment scripts
- Examined CI/CD workflows
- Searched commit history
- **Result**: No Stone commit hash found in Integrity repo

### ✅ Web Search Attempted
- Searched for "Integrity stone5 verifier commit"
- Searched for "HerodotusDev integrity FactRegistry deployment"
- **Result**: General info about Integrity but no specific Stone commit

### ✅ Search Agent Prompt Created
- **File**: `SEARCH_AGENT_PROMPT.md`
- **Contains**: Full context, search strategy, key terms, expected output format
- **Ready for**: Your GPT search agent

## Key Insight

**Important**: Integrity is the **verifier** (Cairo-based), not the prover. It doesn't depend on stone-prover directly. The Stone commit we need is the one used to:
1. Generate the canonical example proofs (Nov 2024)
2. Build the stone5 verifier that's registered in FactRegistry

## Next Steps

### Option 1: Use Search Agent Prompt
- **File**: `SEARCH_AGENT_PROMPT.md`
- **Action**: Give this file to your GPT search agent
- **Contains**: All context, search strategy, and expected output format

### Option 2: Manual Research
Focus on these areas:
1. **Stone Prover Repository** (https://github.com/starkware-libs/stone-prover)
   - Look for "stone5" tags/releases around Nov 2024
   - Check commit history for stone5-related commits
   - Review release notes/changelog

2. **Integrity GitHub Issues/Discussions**
   - Search for Stone version compatibility discussions
   - Look for questions about which Stone version to use
   - Check deployment-related discussions

3. **Contact Integrity Team**
   - GitHub: https://github.com/HerodotusDev/integrity
   - Ask: "What exact Stone Prover commit was used to generate the canonical stone5 example proofs?"

## Files Created

1. **`SEARCH_AGENT_PROMPT.md`** - Comprehensive prompt for your GPT search agent
2. **`SEARCH_SUMMARY.md`** - This file (summary of search efforts)
3. **`STONE5_VS_STONE6_DECISION.md`** - Decision to stay with Stone5
4. **`NEXT_STEPS_SUMMARY.md`** - Prioritized action plan

## What the Search Agent Should Find

**Target**: The exact Stone Prover commit hash that:
- Was used to generate `cairo0_stone5_keccak_160_lsb_example_proof.json` (Nov 2024)
- Matches the stone5 verifier registered in public FactRegistry
- Will produce proofs compatible with the registered verifier

**Success Criteria**:
- Exact commit hash found
- OR documentation stating which Stone version/commit to use
- OR build script/dependency that specifies the commit
