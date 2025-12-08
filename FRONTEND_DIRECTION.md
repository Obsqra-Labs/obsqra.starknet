# Frontend Direction & Performance Analytics Fix

## Current State

### Analytics Dashboard Issues
- ❌ Hardcoded portfolio value (100 STRK)
- ❌ Hardcoded APY values (5.2%, 8.5%)
- ❌ No real performance tracking
- ❌ No on-chain data integration

### What We Have
- ✅ StrategyRouter contract with `get_total_value_locked()`
- ✅ User deposit balances via `get_user_balance()`
- ✅ Allocation percentages from contract
- ✅ Rebalance history with proof data
- ✅ Backend analytics endpoints

---

## Frontend Direction

### Core Philosophy
**"Verifiable AI Execution Layer"**
- Show users their deposits follow AI recommendations
- Display real on-chain performance
- Prove every action with cryptographic proofs
- Transparent, auditable, trustless

### Key Features

1. **Deposit Flow** (✅ Done)
   - Allocation preview
   - AI recommendation matching
   - Proof verification

2. **Analytics Dashboard** (🟡 In Progress)
   - Real portfolio value from contract
   - Actual APY from protocol data
   - Performance tracking over time
   - Proof verification status

3. **History & Audit Trail** (✅ Done)
   - Transaction history
   - Proof hashes
   - On-chain verification links

4. **Performance Metrics** (❌ Missing)
   - Real yield earned
   - Actual returns
   - Historical performance
   - Comparison to benchmarks

---

## Performance Analytics Fix

### What We Need

1. **Portfolio Value**
   - From: `StrategyRouter.get_total_value_locked()`
   - User's share: `StrategyRouter.get_user_balance(user)`
   - Real-time updates

2. **APY Data**
   - From: Protocol contracts (JediSwap, Ekubo)
   - Or: Backend API that fetches from protocols
   - Real-time rates

3. **Performance Tracking**
   - Track deposits over time
   - Calculate actual returns
   - Compare to expected returns
   - Show yield earned

4. **Historical Data**
   - Past allocations
   - Past performance
   - Trends over time

---

## Implementation Plan

### Phase 1: Real Portfolio Data (Now)
- Fetch TVL from contract
- Fetch user balance from contract
- Display real values in analytics

### Phase 2: Real APY Data (Next)
- Fetch APY from protocol contracts
- Or: Use backend API to fetch rates
- Display real APY in analytics

### Phase 3: Performance Tracking (Future)
- Track deposits/withdrawals
- Calculate actual returns
- Show yield earned
- Historical charts

---

## SHARP Fact Hash Verification

### What It Is
- Public, trustless verification on Ethereum L1
- Permanent record of proof validity
- Anyone can verify independently

### Current State
- ✅ Local verification (fast, but requires trust)
- ✅ SHARP submission (background process)
- ✅ Fact hash storage (database)
- ❌ On-chain fact hash verification (missing)

### What We Need
- Cairo verifier contract
- Public verification endpoint
- UI display of verification status

### Difference from ETH Version
- **ETH (obsqura.fi):** Direct L1 verification
- **Starknet (starknet.obsqura.fi):** L2 execution + L1 settlement via SHARP

See `SHARP_FACT_HASH_EXPLAINED.md` for full details.

---

## Next Steps

1. **Fix Analytics Dashboard** (Priority 1)
   - Replace hardcoded values with real data
   - Fetch from contracts/backend
   - Display real performance

2. **Add Performance Tracking** (Priority 2)
   - Track actual returns
   - Calculate yield earned
   - Historical charts

3. **SHARP Fact Hash Verification** (Priority 3)
   - On-chain verifier contract
   - Public verification
   - UI integration

