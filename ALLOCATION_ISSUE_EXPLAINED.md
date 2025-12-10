# Allocation Display Issue - Explained

## The Problem

**What you're seeing:**
- Top of dashboard shows: **50/50** (from contract)
- Allocation process shows: **Different values** (from AI decisions)

**Why this happens:**

1. **Contract is stuck at 50/50** because:
   - `update_allocation()` requires **owner** or **risk_engine** to call it
   - Regular users can't update allocations
   - The contract was initialized with 50/50 and never changed

2. **Frontend shows different values** because:
   - AI orchestration process calculates and displays proposed allocations
   - These are shown in the UI but **not persisted to the contract**
   - The contract still has the default 50/50

## The Code

**Contract requirement (line 179):**
```cairo
assert(caller == owner || caller == risk_engine, 'Unauthorized');
```

**What this means:**
- Only the contract owner or the RiskEngine contract can update allocations
- User wallet calls will fail with "Unauthorized"
- AI orchestration should call via RiskEngine, but might not be doing so

## Solutions

### Option 1: Fix AI Orchestration to Use RiskEngine
- AI orchestration should call `update_allocation` via the RiskEngine contract
- RiskEngine has permission to update allocations
- This is the intended flow

### Option 2: Allow Users to Update (Not Recommended)
- Remove the authorization check
- Let anyone update allocations
- **Security risk** - not recommended

### Option 3: Show Both Values Clearly
- Display "Contract Allocation: 50/50" (what's actually stored)
- Display "Proposed Allocation: X/Y" (what AI suggests)
- Make it clear they're different

## Current State

- ✅ Contract initialized with 50/50
- ✅ AI can calculate optimal allocations
- ❌ AI allocations not being persisted to contract
- ❌ Contract stuck at 50/50
- ❌ UI shows confusing mix of values

## Next Steps

1. **Check if RiskEngine is calling `update_allocation`**
   - Look at AI orchestration code
   - Verify it's using RiskEngine address
   - Check transaction logs

2. **Fix the flow:**
   - AI → RiskEngine → StrategyRouter.update_allocation()
   - Or: AI → User wallet → StrategyRouter.update_allocation() (if we allow users)

3. **Update UI to show both:**
   - Contract allocation (what's stored)
   - Proposed allocation (what AI suggests)
   - Make it clear when they differ


