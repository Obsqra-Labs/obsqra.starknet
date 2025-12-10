# Deposit Issue Explained

## The Problem: Contract Expects STRK, Not ETH

### What Happened

**The `deposit()` function expects STRK, not ETH!**

Looking at the code:
```cairo
fn deposit(ref self: ContractState, amount: u256) {
    let asset_token = self.asset_token.read();  // This is STRK address!
    let token = IERC20Dispatcher { contract_address: asset_token };
    let success = token.transfer_from(caller, contract_addr, amount);
    // ...
}
```

**The contract:**
- Expects you to deposit **STRK** (the `asset_token`)
- Then it swaps half STRK → ETH internally
- Then adds liquidity with both tokens

**If you deposited ETH directly:**
- The contract tried to transfer STRK from your wallet
- You probably don't have STRK approved/available
- Transaction might have failed or done nothing

---

## Are We Earning Yield?

### Short Answer: **NO, not yet!**

**Current State:**

1. **Deposit Function**: ✅ Tries to deploy funds (if it worked)
   - Swaps STRK → ETH
   - Adds liquidity to JediSwap
   - Adds liquidity to Ekubo
   - Stores position IDs

2. **Yield Accrual**: ❌ **NOT implemented**
   ```cairo
   fn accrue_yields(ref self: ContractState) -> u256 {
       // TODO: Query actual yields from protocols
       // For now, return 0
       let total_yield = 0_u256;
       // ...
   }
   ```

3. **Position Value Tracking**: ❌ **NOT implemented**
   - We store position IDs
   - But don't query their current values
   - Don't calculate yield = current_value - deposited_value

**So:**
- ✅ Funds might be deployed to protocols (earning yield in the background)
- ❌ But we're not tracking/calculating it yet
- ❌ `accrue_yields()` returns 0
- ❌ No yield distribution to users

---

## What Are "The Decimals"?

If you're seeing small balance changes:

**Possible Explanations:**

1. **Gas Fees**: 
   - Every transaction costs STRK for gas
   - Your balance decreases slightly with each transaction
   - This is normal!

2. **Rounding/Display Issues**:
   - Token decimals (18 decimals for ETH/STRK)
   - UI might show rounded values
   - Small differences are normal

3. **Actual Yield** (if funds are deployed):
   - If deposit() worked, funds are in protocols
   - They might be earning yield
   - But we can't see it because `accrue_yields()` isn't implemented

4. **Transaction Fees**:
   - Swap fees
   - Liquidity provision fees
   - Protocol fees

---

## How to Check What Actually Happened

### Check Transaction on StarkScan:

1. **Go to**: https://sepolia.starkscan.co/
2. **Paste your transaction hash**
3. **Look for**:
   - Did `transfer_from` succeed? (STRK transfer)
   - Did swap execute? (STRK → ETH)
   - Did `mint()` execute? (JediSwap liquidity)
   - Did `deposit_liquidity()` execute? (Ekubo)
   - Any errors/reverts?

### Check Your Wallet:

- **STRK balance**: Did it decrease? (means transfer worked)
- **ETH balance**: Did it change? (means swap might have worked)
- **Position NFTs**: Check if you received any NFT (JediSwap position)

### Check Contract State:

```bash
# Query total deposits
starkli call <STRATEGY_ROUTER> get_total_value_locked

# Query your positions
starkli call <STRATEGY_ROUTER> get_user_balance <your_address>
```

---

## The Real Issue

**You need to deposit STRK, not ETH!**

**Correct Flow:**
1. You have ETH ✅
2. **Swap ETH → STRK** on JediSwap first
3. **Then deposit STRK** to StrategyRouter
4. Contract swaps half STRK → ETH internally
5. Adds liquidity

**Or:**
- Update contract to accept ETH directly
- But current implementation expects STRK

---

## Quick Fix Options

### Option 1: Swap ETH → STRK First
1. Go to JediSwap
2. Swap your ETH → STRK
3. Then deposit STRK to StrategyRouter

### Option 2: Update Contract to Accept ETH
- Modify `deposit()` to check if user is sending ETH
- Handle ETH deposits differently
- More complex but more flexible

### Option 3: Check If Deposit Actually Worked
- Maybe it did work if you had STRK?
- Check transaction on StarkScan
- Verify positions were created

---

## About Yield

**Are funds earning yield?**
- **Maybe** - if deposit() succeeded and funds are in protocols
- **But we can't see it** - because `accrue_yields()` returns 0
- **We need to implement**:
  - Query position values from JediSwap
  - Query position values from Ekubo
  - Calculate: yield = current_value - deposited_value
  - Update `accrue_yields()` to return real yield

**The decimals you're seeing:**
- Most likely **gas fees** (STRK spent on transactions)
- Or **rounding** in UI display
- **Not yield** (because we're not tracking it yet)

---

## Next Steps

1. **Check transaction** on StarkScan to see what actually happened
2. **If it failed**: Swap ETH → STRK, then deposit STRK
3. **If it worked**: Funds might be earning yield, but we can't see it yet
4. **Implement yield tracking**: Update `accrue_yields()` to query real values

Want me to help check the transaction or implement yield tracking?


