# Deposit Routing Visualization Plan

## Current State

**User Flow:**
1. User deposits STRK → StrategyRouter contract
2. Funds are allocated according to current allocation percentages
3. User sees deposit confirmation, but no visibility into routing

**Missing:**
- Visual connection between deposit and AI recommendation
- Proof that deposit followed risk engine's allocation
- Breakdown showing where funds went (JediSwap vs Ekubo)

## Proposed Solution: Deposit Flow Visualization

### Phase 1: Show Current Allocation When Depositing (Easy - 2-3 hours)

**What to Build:**
- Before deposit: Show "Your deposit will be allocated according to AI recommendation"
- Display current allocation percentages (from StrategyRouter)
- Show breakdown: "X% to JediSwap, Y% to Ekubo"
- After deposit: Show confirmation with allocation breakdown

**Implementation:**
1. Fetch current allocation from StrategyRouter before deposit
2. Display allocation preview in deposit modal/section
3. After deposit success, show allocation breakdown
4. Link to latest AI recommendation (if available)

### Phase 2: Link Deposit to AI Recommendation (Medium - 4-6 hours)

**What to Build:**
- Show which AI recommendation the deposit followed
- Display the decision ID and proof hash
- Show timestamp of recommendation vs deposit
- Verify allocation matches recommendation

**Implementation:**
1. Fetch latest AI decision from RiskEngine
2. Compare allocation percentages (deposit allocation vs AI recommendation)
3. Show match/mismatch status
4. Display proof hash if allocation matches

### Phase 3: Real-Time Allocation Tracking (Hard - 1-2 days)

**What to Build:**
- Track user's position across protocols
- Show "Your X STRK in JediSwap, Y STRK in Ekubo"
- Update in real-time as allocations change
- Show yield earned per protocol

**Implementation:**
1. Calculate user's share of total pool
2. Multiply by protocol allocations
3. Track over time
4. Display in dashboard

## Recommended Approach

**Start with Phase 1** - It's the easiest win and immediately shows the connection.

**Components Needed:**
1. `DepositAllocationPreview` - Shows allocation before deposit
2. `DepositConfirmation` - Shows allocation after deposit
3. `AllocationBreakdown` - Visual breakdown component

**Data Needed:**
- Current allocation from StrategyRouter (already available)
- Latest AI recommendation (already available)
- Deposit amount (user input)

## Technical Details

### Current Allocation Source
```typescript
// Already available in Dashboard
const allocation = {
  jediswap: routerV2.jediswapAllocation, // basis points
  ekubo: routerV2.ekuboAllocation,       // basis points
};
```

### Latest AI Recommendation
```typescript
// From RiskEngine contract
const latestDecision = await riskEngine.get_decision(decision_count);
// Contains: jediswap_pct, ekubo_pct, proof_hash, etc.
```

### Deposit Flow Enhancement
```typescript
// In handleDeposit:
1. Fetch current allocation
2. Show preview: "Your 100 STRK will be allocated: 51% JediSwap, 49% Ekubo"
3. Execute deposit
4. Show confirmation with breakdown
5. Optionally: Verify it matches latest AI recommendation
```

## UI Mockup Concept

```
┌─────────────────────────────────────┐
│  Deposit STRK                       │
├─────────────────────────────────────┤
│  Amount: [100 STRK]                 │
│                                     │
│  📊 Allocation Preview              │
│  Your deposit will be allocated     │
│  according to AI recommendation:   │
│                                     │
│  ┌─────────────┬─────────────┐     │
│  │ JediSwap    │ Ekubo       │     │
│  │ 51.06%      │ 48.94%      │     │
│  │ 51.06 STRK  │ 48.94 STRK  │     │
│  └─────────────┴─────────────┘     │
│                                     │
│  ✅ Based on AI Decision #14        │
│  🔐 Proof: 0x19e7cce9...           │
│                                     │
│  [Deposit]                         │
└─────────────────────────────────────┘
```

## Benefits

1. **Transparency**: Users see exactly where funds go
2. **Trust**: Shows connection to AI recommendation
3. **Verifiability**: Links to on-chain proof
4. **UX**: Makes the flow more comprehensive

## Difficulty Assessment

- **Phase 1**: ⭐ Easy (2-3 hours)
  - Just UI components + data display
  - All data already available
  
- **Phase 2**: ⭐⭐ Medium (4-6 hours)
  - Need to fetch and compare recommendations
  - Add verification logic
  
- **Phase 3**: ⭐⭐⭐ Hard (1-2 days)
  - Need position tracking
  - Real-time updates
  - Yield calculations

## Recommendation

**Start with Phase 1** - Quick win that immediately improves UX and shows the AI connection.

