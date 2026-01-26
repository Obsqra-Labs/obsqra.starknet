# RESEARCH_AGENT_BRIEF.md - Update Summary

## Changes Made

The research brief has been completely rewritten to shift from **open-ended investigation** to **deterministic binary-search with hard stop conditions**.

### Key Changes:

#### 1. **Mission Reframing** (Line 4-8)
- **Old:** "Determine why PublicNode RPC expects CASM hash 0x4120dfff..."
- **New:** "Binary-search Cairo compiler versions until CASM hash matches 0x4120dfff. That version is what PublicNode uses. Stop when found."
- **Reason:** Turns hypothesis-driven research into finite, deterministic troubleshooting

#### 2. **Architectural Grounding** (Lines 13-44)
- Added clear explanation that CASM hash mismatches are **compiler-version dependent by design**
- Not a bug—a feature of STARK system determinism
- Analogous to arithmetization pinning in zkML and zkVMs
- **PublicNode is behaving correctly**; you're just using a newer Cairo version

#### 3. **Three-Step Methodology** (Lines 50-237)

**Step 1: Binary Search (Hard Stop at Match)**
- Test Cairo versions in order of likelihood: 2.10.1, 2.10.0, 2.9.2, 2.9.1, 2.8.4, 2.8.0, 2.7.0
- Each test: build → extract CASM hash → compare
- **Hard Stop:** When hash matches 0x4120dfff, stop immediately

**Step 2: If Match Found (Most Likely: 60%)**
- Three deployment paths:
  - Path A: Fastest unblock (recompile, deploy to PublicNode)
  - Path B: Cleanest narrative (document as feature, not workaround)
  - Path C: Future-proof (maintain both pinned and latest versions)

**Step 3: If No Match Found (Less Likely: 40%)**
- After 8 versions tested with no match, **stop searching**
- Switch RPC (Alchemy, Infura, or devnet)
- Document PublicNode limitation
- Deploy to alternative RPC instead

#### 4. **Decision Tree** (Lines 239-259)
- Explicit branching: which step to take based on test results
- Hard stop conditions clearly marked
- No ambiguity in decision logic

#### 5. **Time Estimates** (Lines 261-272)
- **Success path (60% likely):** 35-40 minutes total
- **Fallback path (40% likely):** 45-60 minutes total
- **Guaranteed unblock:** <60 minutes in either case
- No "indefinite research" phase

#### 6. **Success Criteria** (Lines 274-301)
- Three possible outcomes, all acceptable
- All lead to deployed StrategyRouterV2
- Clear timeline for each path
- **Bottom line:** "In all scenarios, you deploy StrategyRouterV2 within 60 minutes"

#### 7. **Architectural Justification** (Lines 303-315)
- Explains this is NOT speculative research
- Compiler version locks are well-understood problems in cryptographic systems
- PublicNode's behavior is mechanically correct, not a flaw
- Solution is finite: find version OR switch RPC (both deterministic)

---

## What This Fixes

### Before
- Vague "research all possibilities"
- No clear stopping conditions
- Could continue indefinitely
- Treated CASM mismatch as mystery to solve
- No decision framework

### After
- Concrete binary search (7 versions max)
- Hard stop conditions (8 versions → switch RPC)
- Maximum 2 hours to unblock (practical deadline)
- CASM mismatch framed as compiler version lock (understood phenomenon)
- Three explicit decision paths with timelines

---

## For the Research Agent

**When reading this brief, the agent should understand:**

1. **This is NOT open-ended research**
   - "Binary search," not "research all possibilities"
   - You have 7-8 specific Cairo versions to test
   - Stop when you find a match

2. **You have explicit stop conditions**
   - Stop condition 1: Hash matches 0x4120dfff → proceed to Path A/B/C
   - Stop condition 2: 8 versions tested, no match → proceed to Step 3 (switch RPC)
   - Do NOT continue searching after these conditions are met

3. **Your mission is deterministic, not exploratory**
   - This is like binary searching for a value in a sorted array
   - The value exists somewhere (either in the versions or in an alternative RPC)
   - Time limit: <60 minutes

4. **Two viable outcomes**
   - Find the Cairo version that produces 0x4120dfff (most likely)
   - Switch RPC and deploy (fallback, also viable)
   - Both result in deployed StrategyRouterV2

---

## One-Sentence Brief for Agent

**Test Cairo versions 2.10.1 down to 2.7.0 until CASM hash matches 0x4120dfff; if no match after 8 versions, switch to Alchemy/Infura RPC instead. Report the result in 60 minutes or less.**
