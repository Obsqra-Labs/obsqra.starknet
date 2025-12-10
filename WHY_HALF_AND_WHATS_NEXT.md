# Why "Half" for Pools? And What's Next

## 🤔 Why Swap Half ETH to STRK?

### How Liquidity Pools Work

**Liquidity pools require BOTH tokens in a pair.**

When you add liquidity to a pool like **ETH/STRK**, you need to provide:
- Some amount of **ETH**
- Some amount of **STRK**

The pool maintains a ratio (e.g., 1 ETH = 100 STRK), and you must provide both tokens in that ratio.

### Our Strategy

**User deposits:** 1 ETH

**What happens:**
1. Contract receives 1 ETH
2. Contract swaps **0.5 ETH → STRK** (gets ~50 STRK, assuming 1 ETH = 100 STRK)
3. Contract now has:
   - 0.5 ETH
   - ~50 STRK
4. Contract adds liquidity to JediSwap with **both tokens**
5. Contract adds liquidity to Ekubo with **both tokens**

**Why half?**
- We need both tokens for the pool
- User only has ETH
- So we swap half to get STRK
- Then we have both tokens to add liquidity

### Alternative Approaches

**Option 1: Swap Half (Current Approach)**
- ✅ Simple
- ✅ Works with any amount
- ❌ Two transactions (swap + add liquidity)
- ❌ Slippage on swap

**Option 2: ZAP Contracts**
- ✅ Single transaction
- ✅ Better slippage protection
- ❌ Need ZAP contract to exist
- ❌ More complex

**Option 3: Accept Both Tokens**
- ✅ No swap needed
- ❌ User must have both ETH and STRK
- ❌ More complex UX

We chose **Option 1** (swap half) because it's simplest and works with what users have (ETH).

---

## 🌐 Is This How DeFi Works on Starknet?

**Yes!** This is standard for **AMM (Automated Market Maker)** liquidity pools.

### How It Works on Starknet (Same as Ethereum)

1. **Liquidity Pools** = Pairs of tokens (ETH/STRK, STRK/USDC, etc.)
2. **Liquidity Providers (LPs)** = People who add both tokens to the pool
3. **Traders** = People who swap tokens (paying fees to LPs)
4. **LPs Earn** = Trading fees from swaps

### JediSwap & Ekubo

Both are **AMM DEXs** (like Uniswap on Ethereum):

- **JediSwap**: Uniswap V2/V3 style (concentrated liquidity)
- **Ekubo**: Similar AMM with concentrated liquidity

**Both require:**
- Both tokens in the pair
- Providing liquidity in the correct ratio
- Earning fees from trades

---

## 📋 What's Next?

### Current Status

**✅ What's Done:**
- Contract accepts ETH deposits
- Contract structure ready for protocol integration
- Interfaces defined for JediSwap and Ekubo
- Frontend updated to use ETH

**❌ What's NOT Done:**
- Protocol integration is **commented out** (see `strategy_router_v2.cairo` line 228)
- No actual swaps happening
- No liquidity being added
- No yield being earned

### Next Steps (Priority Order)

#### 1. **Implement Protocol Integration** (Critical - Week 1)

**Current Code:**
```cairo
// TODO: Protocol integration - temporarily commented out
if jediswap_amount > 0 {
    // Increment position count (simplified tracking)
    let count = self.jediswap_position_count.read();
    self.jediswap_position_count.write(count + 1);
    // TODO: Implement actual swap and liquidity provision
}
```

**What Needs to Happen:**
1. **Swap half ETH → STRK**
   - Use JediSwap Swap Router
   - Swap `jediswap_amount / 2` ETH to STRK
   - Get STRK amount received

2. **Add Liquidity to JediSwap**
   - Approve NFT Position Manager for both ETH and STRK
   - Call `mint()` with both tokens
   - Store position NFT ID

3. **Add Liquidity to Ekubo**
   - Swap half ETH → STRK (same as JediSwap)
   - Approve Ekubo Core for both tokens
   - Call `deposit_liquidity()` with both tokens
   - Store position ID

**Files to Update:**
- `/opt/obsqra.starknet/contracts/src/strategy_router_v2.cairo` (lines 228-245)

---

#### 2. **Verify Protocol Interfaces** (Critical - Week 1)

**JediSwap:**
- ✅ Interface defined
- ⚠️ Need to verify `swap_exact_tokens_for_tokens()` signature
- ⚠️ Need to verify `mint()` parameters match actual contract

**Ekubo:**
- ⚠️ Interface might not match actual contract
- ⚠️ Need to verify `deposit_liquidity()` signature
- ⚠️ Might need PoolKey structure instead of direct params

**How to Verify:**
- Check contract ABIs on Starkscan
- Test with small amounts on Sepolia
- Check protocol documentation

---

#### 3. **Test on Sepolia** (Critical - Week 1-2)

**Test Plan:**
1. Deploy updated contract
2. Get testnet ETH
3. Deposit small amount (0.01 ETH)
4. Check if swap succeeds
5. Check if liquidity is added
6. Verify position IDs are stored
7. Check if funds are earning yield

**Expected Issues:**
- Interface mismatches
- Slippage errors
- Approval failures
- Gas estimation issues

---

#### 4. **Implement Yield Tracking** (Important - Week 2)

**Current Code:**
```cairo
fn accrue_yields(ref self: ContractState) -> u256 {
    // TODO: Query actual yields from protocols
    let total_yield = 0_u256;  // Always returns 0!
    // ...
}
```

**What Needs to Happen:**
1. Query position values from JediSwap
   - Call `positions(token_id)` to get current liquidity
   - Calculate current value in ETH
   - Compare to deposited value

2. Query position values from Ekubo
   - Call position query function
   - Get current value
   - Compare to deposited value

3. Calculate yield
   - Yield = current_value - deposited_value
   - Return total yield

**Files to Update:**
- `/opt/obsqra.starknet/contracts/src/strategy_router_v2.cairo` (line 291)

---

#### 5. **Implement Withdrawal** (Important - Week 2)

**Current Code:**
```cairo
fn withdraw(ref self: ContractState, amount: u256) -> u256 {
    // TODO: Withdraw from protocols proportionally
    // For now, simple withdrawal without yields
    // ...
}
```

**What Needs to Happen:**
1. Calculate which positions to withdraw from
2. For JediSwap:
   - Call `decrease_liquidity()` to remove liquidity
   - Call `collect()` to collect fees
   - Get ETH and STRK back
   - Swap STRK → ETH (if needed)
3. For Ekubo:
   - Call `withdraw_liquidity()` or similar
   - Get tokens back
   - Swap STRK → ETH (if needed)
4. Return ETH to user

**Files to Update:**
- `/opt/obsqra.starknet/contracts/src/strategy_router_v2.cairo` (line 258)

---

#### 6. **Implement Rebalancing** (Nice-to-Have - Week 3)

**Current Code:**
```cairo
fn rebalance(ref self: ContractState) {
    // TODO: Implement rebalancing logic
    // 1. Calculate current positions in each protocol
    // 2. Calculate target positions based on allocation
    // 3. Move funds as needed
}
```

**What Needs to Happen:**
1. Query current positions
2. Calculate target allocation
3. Calculate deltas (how much to move)
4. Withdraw from over-allocated protocol
5. Deposit to under-allocated protocol

---

## 🎯 Immediate Action Items

### This Week

1. **Uncomment and Fix Protocol Integration**
   - Uncomment lines 228-245 in `strategy_router_v2.cairo`
   - Implement swap logic
   - Implement liquidity provision
   - Fix any compilation errors

2. **Test Swap Function**
   - Test ETH → STRK swap on Sepolia
   - Verify amounts received
   - Check slippage

3. **Test Liquidity Provision**
   - Test adding liquidity to JediSwap
   - Test adding liquidity to Ekubo
   - Verify position IDs

### Next Week

4. **Implement Yield Tracking**
   - Query position values
   - Calculate yield
   - Update `accrue_yields()`

5. **Implement Withdrawal**
   - Withdraw from protocols
   - Return funds to users

---

## 📊 Current Architecture

```
User deposits 1 ETH
    ↓
StrategyRouter receives 1 ETH
    ↓
Allocation: 50% JediSwap, 50% Ekubo
    ↓
JediSwap (0.5 ETH):
  - Swap 0.25 ETH → STRK ✅ (needs implementation)
  - Add liquidity: 0.25 ETH + STRK ✅ (needs implementation)
  - Store position NFT ID ✅ (needs implementation)
    ↓
Ekubo (0.5 ETH):
  - Swap 0.25 ETH → STRK ✅ (needs implementation)
  - Deposit: 0.25 ETH + STRK ✅ (needs implementation)
  - Store position ID ✅ (needs implementation)
    ↓
Funds earning yield ✅ (once above is done)
```

---

## 🚨 Known Issues

1. **Protocol Integration Commented Out**
   - Code is ready but not active
   - Need to uncomment and test

2. **Interface Verification Needed**
   - JediSwap interfaces might not match exactly
   - Ekubo interfaces definitely need verification

3. **No Yield Tracking**
   - `accrue_yields()` always returns 0
   - Need to query position values

4. **No Withdrawal from Protocols**
   - `withdraw()` just transfers from contract balance
   - Doesn't actually withdraw from pools

---

## 💡 Summary

**Why Half?**
- Liquidity pools need both tokens (ETH + STRK)
- User only has ETH
- So we swap half ETH → STRK to get both tokens
- Then add liquidity with both

**Is This Standard?**
- Yes! This is how AMM liquidity pools work everywhere (Ethereum, Starknet, etc.)
- You always need both tokens in a pair

**What's Next?**
1. **Implement protocol integration** (uncomment and fix the code)
2. **Test on Sepolia** (verify it works)
3. **Implement yield tracking** (so we can see actual returns)
4. **Implement withdrawal** (so users can get their funds back)

**Current State:**
- ✅ Contract structure ready
- ✅ Interfaces defined
- ✅ Frontend updated
- ❌ Protocol integration commented out
- ❌ No actual yield being earned yet

**Next Milestone:**
Get funds actually deployed to protocols and earning yield! 🚀


