# What Went Wrong with the ETH-Based Strategy Router Contracts

## Summary

The ETH-based contracts (`0x01c2e698bc0f263ea62dc3c557d32afe25c13cbc91900d726b84c58a0baa09f0` and `0x01888e3f3d6cd137e63ff1a090a1e2c9ed5754162a8d5739364aba657fab20e4`) failed because they tried to integrate DeFi protocol calls **directly into the deposit function**, making it too complex and causing multiple failure points.

## The Working Contract (STRK - Current)

**Contract**: `0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a`

**What it does:**
- ✅ Simple deposit: Accepts STRK, stores it
- ✅ Simple withdraw: Returns STRK
- ✅ No protocol integration in deposit function
- ✅ Just tracks balances

**Why it works:**
- Single, simple operation
- No external protocol calls
- No complex state changes
- Minimal gas usage

## The Broken Contracts (ETH with Protocol Integration)

**Contracts:**
1. `0x01c2e698bc0f263ea62dc3c557d32afe25c13cbc91900d726b84c58a0baa09f0` - **"Functions not exposed in ABI (ENTRYPOINT_NOT_FOUND)"**
2. `0x01888e3f3d6cd137e63ff1a090a1e2c9ed5754162a8d5739364aba657fab20e4` - Latest attempt, also failed

**What they tried to do in ONE deposit transaction:**

```cairo
fn deposit(ref self: ContractState, amount: u256) {
    // 1. Transfer ETH from user
    token.transfer_from(caller, contract_addr, amount);
    
    // 2. For JediSwap allocation:
    //    - Swap ETH → STRK via JediSwap Router
    //    - Approve NFT Position Manager
    //    - Add liquidity via NFT Position Manager
    //    - Mint position NFT
    
    // 3. For Ekubo allocation:
    //    - Swap ETH → STRK via JediSwap Router
    //    - Approve Ekubo Core
    //    - Deposit liquidity to Ekubo Core
    
    // 4. Track positions
    // 5. Update totals
}
```

**Why this failed:**

### 1. **ENTRYPOINT_NOT_FOUND Error**
- The contract's `deposit` function signature might not match what was expected
- Or the function wasn't properly exposed in the ABI
- This suggests a compilation/deployment issue

### 2. **Too Many Operations in One Transaction**
The deposit function tried to do:
- ✅ Transfer tokens (1 operation)
- ❌ Swap ETH → STRK (2 swaps - one for each protocol)
- ❌ Approve NFT Manager (2 approvals)
- ❌ Add liquidity to JediSwap (1 complex operation)
- ❌ Approve Ekubo Core (2 approvals)
- ❌ Deposit to Ekubo (1 complex operation)
- ❌ Track positions (2 storage writes)

**Total: ~10+ operations in a single transaction**

### 3. **Gas Limit Issues**
- Each operation costs gas
- Multiple approvals, swaps, and liquidity operations
- Could easily exceed transaction gas limits
- Wallet might reject before even trying

### 4. **Interface Mismatches**
- JediSwap Router interface might not match exactly
- JediSwap NFT Manager `mint()` parameters might be wrong
- Ekubo Core `deposit_liquidity()` signature might be incorrect
- Any mismatch = ENTRYPOINT_NOT_FOUND

### 5. **Protocol Call Failures**
- If swap fails → entire deposit fails
- If liquidity provision fails → entire deposit fails
- No error recovery or partial success handling
- All-or-nothing approach is risky

### 6. **Complex State Management**
- Multiple approvals needed
- Multiple protocol interactions
- Position tracking
- Error handling across multiple systems

## The Root Problem

**You tried to do too much in one function call.**

Instead of:
```
User → Deposit → Contract stores funds → Done ✅
```

You tried:
```
User → Deposit → Contract → Swap → Approve → Add Liquidity → Approve → Deposit → Track → Done ❌
```

**This is like trying to:**
- Buy groceries
- Cook dinner
- Set the table
- Serve the meal
- Clean the dishes
- All in one action

## What Should Have Been Done

### Option 1: Separate Functions (Recommended)
```cairo
fn deposit(ref self: ContractState, amount: u256) {
    // Just accept and store funds
    token.transfer_from(caller, contract_addr, amount);
    // Store user balance
}

fn deploy_to_protocols(ref self: ContractState) {
    // Separate function to deploy funds
    // Can be called by owner or automated
    // Can retry if it fails
}
```

### Option 2: Two-Step Process
1. User deposits → Contract stores funds
2. Backend/owner calls `deploy_to_protocols()` separately
3. Funds get deployed when ready

### Option 3: Keep It Simple (Current Working Approach)
- Just accept deposits
- Store funds
- Deploy to protocols later via separate mechanism
- Or don't deploy at all (just track allocations)

## Why the STRK Contract Works

The STRK contract (`0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a`) works because:

1. **Simple deposit function:**
   ```cairo
   fn deposit(ref self: ContractState, amount: u256) {
       token.transfer_from(caller, contract_addr, amount);
       // That's it!
   }
   ```

2. **No protocol integration** - Just accepts and stores funds

3. **No complex operations** - Single transfer, minimal gas

4. **No interface dependencies** - Doesn't call external protocols

5. **Reliable** - Can't fail due to protocol issues

## Lessons Learned

1. **Keep deposit functions simple** - Just accept funds, don't do complex operations
2. **Separate concerns** - Deposit vs. Protocol deployment should be separate
3. **Test incrementally** - Add protocol integration after basic deposit works
4. **Handle failures gracefully** - Don't make deposit fail if protocol calls fail
5. **Verify interfaces** - Make sure protocol interfaces match before deploying

## Current Status

✅ **Working**: STRK contract with simple deposit/withdraw
❌ **Broken**: ETH contracts with protocol integration in deposit function
✅ **Solution**: Reverted to STRK contract, removed all ETH references

## Next Steps (If You Want Protocol Integration)

1. **Keep deposit simple** - Just accept funds
2. **Add separate function** - `deploy_to_protocols()` that can be called separately
3. **Test protocol calls separately** - Don't bundle with deposits
4. **Add error handling** - If protocol call fails, don't fail the deposit
5. **Consider backend orchestration** - Let backend handle protocol deployment

## Files Changed

When we reverted to STRK:
- ✅ `/opt/obsqra.starknet/frontend/.env.local` - Updated contract address
- ✅ `/opt/obsqra.starknet/frontend/src/hooks/useStrategyDeposit.ts` - Changed ETH → STRK
- ✅ `/opt/obsqra.starknet/frontend/src/components/Dashboard.tsx` - Changed all ETH labels to STRK
- ✅ `/opt/obsqra.starknet/frontend/src/components/TransactionHistory.tsx` - Changed ETH labels to STRK

## Conclusion

The ETH contracts failed because they tried to integrate DeFi protocols directly into the deposit function, making it too complex and error-prone. The STRK contract works because it keeps things simple - just accept funds and store them. Protocol integration should be a separate concern, handled either by a separate function or by backend orchestration.

