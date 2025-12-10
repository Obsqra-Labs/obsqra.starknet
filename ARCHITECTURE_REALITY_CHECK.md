# Architecture Reality Check: Current State & Gaps

## Quick Answers

### 1. Is this a Keeper?
**NO** - This is a **backend orchestration service**, not an autonomous keeper bot.

**What it is:**
- Backend API (`/api/v1/risk-engine/orchestrate-allocation`)
- Called manually via frontend or can be scheduled (cron job)
- Uses backend wallet to execute transactions
- Not decentralized - requires backend to be running

**What calls it:**
- Frontend user action → Backend API → Starknet contracts
- Could be called by cron/scheduler for automated rebalancing
- Currently manual trigger only

**Future:**
- Architecture mentions "Keeper network" as planned improvement
- Currently centralized backend orchestration

---

### 2. Are We Aggregating Yield?
**NO** - Yield aggregation is **NOT implemented yet**.

**Current State:**
```cairo
// From StrategyRouterV2.cairo line 243-254
fn accrue_yields(ref self: ContractState) -> u256 {
    // TODO: Query actual yields from protocols
    // For now, return 0
    let total_yield = 0_u256;
    // ...
}
```

**What's Missing:**
- ❌ No actual querying of protocol yields
- ❌ No yield calculation from positions
- ❌ No yield distribution to users
- ❌ Function returns 0 (placeholder)

**What We Have:**
- ✅ Function signature exists
- ✅ Event emission structure ready
- ✅ APY fetching from DefiLlama (external data)
- ❌ But no on-chain yield accrual

---

### 3. Is STRK Actually in a Vault for Strategies?
**PARTIALLY** - Funds are held in StrategyRouter contract, but **NOT deployed to protocols**.

**Current Flow:**
```
User deposits STRK
    ↓
StrategyRouter.deposit() receives tokens
    ↓
Tokens stored in StrategyRouter contract ✅
    ↓
TODO: Actually deposit to JediSwap/Ekubo ❌
```

**What the Contract Does:**
```cairo
// From StrategyRouterV2.cairo line 186-208
fn deposit(ref self: ContractState, amount: u256) {
    // Transfer tokens from user to this contract ✅
    let token = IERC20Dispatcher { contract_address: asset_token };
    let success = token.transfer_from(caller, contract_addr, amount);
    
    // Update total deposits ✅
    self.total_deposits.write(total + amount);
    
    // TODO: Actually deposit to protocols based on allocation ❌
    // This would call JediSwap.add_liquidity() and Ekubo.deposit_liquidity()
}
```

**Reality:**
- ✅ STRK tokens ARE in the StrategyRouter contract (it's a vault)
- ❌ But they're NOT deployed to JediSwap/Ekubo yet
- ❌ Funds are sitting idle in the contract
- ❌ No yield is being generated

---

### 4. How Does the Mechanism Work?

**Current Architecture:**

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ 1. Deposits STRK
       ↓
┌──────────────────────┐
│ StrategyRouterV2     │
│ (Contract)           │
│                      │
│ ✅ Receives STRK     │
│ ✅ Stores balance    │
│ ❌ TODO: Deploy to   │
│    protocols         │
└──────────────────────┘
       │
       │ 2. Allocation Decision
       ↓
┌──────────────────────┐
│ RiskEngine           │
│ (Contract)           │
│                      │
│ ✅ Calculates risk   │
│ ✅ Proposes alloc    │
│ ✅ Updates Strategy  │
│    Router allocation │
└──────────────────────┘
       │
       │ 3. Backend Orchestration
       ↓
┌──────────────────────┐
│ Backend API          │
│                      │
│ ✅ Generates proof   │
│ ✅ Calls RiskEngine  │
│ ✅ Updates allocation│
│ ❌ Does NOT deploy   │
│    funds to protocols│
└──────────────────────┘
```

**What's Missing:**
- ❌ No actual interaction with JediSwap router
- ❌ No actual interaction with Ekubo core
- ❌ No liquidity provision
- ❌ No position tracking
- ❌ No yield accrual

---

### 5. Can Our Strategies Generate Yield and Have APYs?

**SHORT ANSWER: NO** - Not yet, because funds aren't deployed.

**Why:**
1. **Deposit function doesn't deploy funds:**
   - Just transfers STRK to contract
   - Doesn't call `JediSwap.add_liquidity()`
   - Doesn't call `Ekubo.deposit_liquidity()`

2. **No protocol integration:**
   - Contract has protocol addresses stored
   - But never actually calls them
   - No position tracking

3. **APY data is external:**
   - We fetch APY from DefiLlama API ✅
   - But our funds aren't earning that APY ❌
   - We're just displaying what protocols offer
   - Not what we're actually earning

**What Would Need to Happen:**

```
1. User deposits 100 STRK
   ↓
2. StrategyRouter receives 100 STRK
   ↓
3. Current allocation: 50% JediSwap, 50% Ekubo
   ↓
4. StrategyRouter should:
   - Call JediSwap.add_liquidity(50 STRK) ❌ NOT DONE
   - Call Ekubo.deposit_liquidity(50 STRK) ❌ NOT DONE
   - Track positions (LP tokens, etc.) ❌ NOT DONE
   ↓
5. Protocols generate yield on deployed funds
   ↓
6. StrategyRouter.accrue_yields() should:
   - Query JediSwap position value ❌ NOT DONE
   - Query Ekubo position value ❌ NOT DONE
   - Calculate total yield ❌ NOT DONE
   - Distribute to users ❌ NOT DONE
```

---

## Implementation Gaps

### Critical Missing Pieces:

1. **Protocol Integration (HIGH PRIORITY)**
   ```cairo
   // Need to implement in deposit():
   // Addresses are already stored in contract storage:
   // - self.jediswap_router.read() → 0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21
   // - self.ekubo_core.read() → 0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384
   
   // Need to:
   - Create IJediSwapRouterDispatcher from jediswap_router address
   - Call JediSwap.add_liquidity(amount * jediswap_pct / 10000)
   - Create IEkuboCoreDispatcher from ekubo_core address
   - Call Ekubo.deposit_liquidity(amount * ekubo_pct / 10000)
   - Store LP token addresses/positions
   ```

2. **Position Tracking (HIGH PRIORITY)**
   ```cairo
   // Need to track:
   - JediSwap LP token balance
   - Ekubo position IDs
   - Current position values
   - Yield accrued per position
   ```

3. **Yield Accrual (HIGH PRIORITY)**
   ```cairo
   // Need to implement in accrue_yields():
   - Query JediSwap position value
   - Query Ekubo position value
   - Calculate: current_value - deposited_value = yield
   - Update user balances with yield
   ```

4. **Rebalancing (MEDIUM PRIORITY)**
   ```cairo
   // Need to implement in rebalance():
   - Calculate current positions vs target allocation
   - Withdraw excess from over-allocated protocol
   - Deposit to under-allocated protocol
   - Update position tracking
   ```

5. **Withdrawal (MEDIUM PRIORITY)**
   ```cairo
   // Need to implement in withdraw():
   - Calculate proportional withdrawal from each protocol
   - Call JediSwap.remove_liquidity(proportional_amount)
   - Call Ekubo.withdraw_liquidity(proportional_amount)
   - Transfer STRK + yield to user
   ```

---

## Current Testnet Status

**What Works:**
- ✅ User can deposit STRK to StrategyRouter
- ✅ Tokens are held in contract
- ✅ RiskEngine calculates allocations
- ✅ Allocation percentages are updated
- ✅ Proof generation works
- ✅ APY data fetched from DefiLlama
- ✅ **Protocol addresses are stored in contract:**
  - JediSwap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
  - Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
  - STRK Token: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`

**What Doesn't Work:**
- ❌ Funds are NOT earning yield
- ❌ Funds are NOT deployed to protocols
- ❌ No actual protocol interaction (addresses stored but not called)
- ❌ No yield accrual
- ❌ No position tracking

**Bottom Line:**
The contracts are a **skeleton** - they hold funds and make allocation decisions, but don't actually interact with JediSwap/Ekubo to deploy capital and generate yield.

---

## Next Steps to Make It Real

1. **Implement Protocol Integration** (Week 1)
   - Add JediSwap.add_liquidity() calls in deposit()
   - Add Ekubo.deposit_liquidity() calls in deposit()
   - Store LP token positions

2. **Implement Yield Tracking** (Week 2)
   - Query position values from protocols
   - Calculate yield = current_value - deposited_value
   - Update accrue_yields() to return real yield

3. **Implement Withdrawal** (Week 2)
   - Withdraw from protocols proportionally
   - Return STRK + yield to users

4. **Implement Rebalancing** (Week 3)
   - Calculate position deltas
   - Move funds between protocols
   - Update allocations

5. **Testing** (Week 4)
   - Test on Sepolia testnet
   - Verify yield accrual
   - Verify withdrawals work
   - Verify rebalancing works

---

## Summary

**Current State:**
- Funds are in a vault (StrategyRouter contract) ✅
- But not deployed to earn yield ❌
- APY data is fetched but not earned ❌
- Allocation decisions are made but not executed ❌

**To Generate Real Yield:**
- Need to implement protocol integration
- Need to deploy funds to JediSwap/Ekubo
- Need to track positions and calculate yield
- Need to distribute yield to users

**Timeline to Production:**
- ~4 weeks to implement protocol integration
- ~2 weeks for testing and refinement
- **Total: ~6 weeks to actually generate yield**

