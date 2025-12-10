# Deposit Error Fix Applied

## Problem

**Error:** `u256_sub Overflow` when trying to deposit ETH

**Root Cause:**
- ERC20 `transfer_from` fails when:
  - User balance < deposit amount, OR
  - User allowance < deposit amount
- The subtraction `balance - amount` or `allowance - amount` overflows if the first value is smaller

## Fix Applied

### 1. Added Balance Check
Before attempting deposit, check if user has sufficient balance:
```typescript
if (balanceValue < amountWei) {
  throw new Error(`Insufficient balance...`);
}
```

### 2. Added Allowance Check
Check current allowance before approving:
```typescript
const currentAllowance = await ethContract.allowance(address, strategyRouterAddress);
if (allowanceValue < amountWei) {
  // Approve only if needed
}
```

### 3. Approve Max Amount
Instead of approving exact amount, approve max uint256 to avoid future approval issues:
```typescript
const maxApproval = uint256.bnToUint256(BigInt('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'));
```

### 4. Added `allowance` to ABI
Added the `allowance` function to ETH_TOKEN_ABI so we can check allowance.

## What Changed

**File:** `/opt/obsqra.starknet/frontend/src/hooks/useStrategyDeposit.ts`

**Changes:**
1. ✅ Check user balance before deposit
2. ✅ Check current allowance before approving
3. ✅ Only approve if allowance is insufficient
4. ✅ Approve max amount (not exact amount) for future convenience
5. ✅ Added `allowance` function to ETH_TOKEN_ABI
6. ✅ Better error messages

## Testing

**Before depositing, the frontend now:**
1. Checks if user has enough ETH
2. Checks current allowance
3. Only approves if needed
4. Approves max amount (so future deposits don't need approval)
5. Then deposits

**This should fix the `u256_sub Overflow` error!**

## Next Steps

1. **Test deposit again** - Should work now with proper checks
2. **If still fails**, check:
   - Is ETH token address correct?
   - Is contract address correct?
   - Is user on Sepolia testnet?
   - Does user have ETH in wallet?

## Debug Commands

If deposit still fails, check in browser console:

```javascript
// Check balance
const provider = new RpcProvider({ nodeUrl: 'https://starknet-sepolia-rpc.publicnode.com' });
const ethContract = new Contract(ETH_TOKEN_ABI, '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7', provider);
const balance = await ethContract.balanceOf('YOUR_ADDRESS');
console.log('Balance:', balance);

// Check allowance
const allowance = await ethContract.allowance('YOUR_ADDRESS', '0x053b69775c22246080a17c37a38dbda31d1841c8f6d7b4d928d54a99eda2748c');
console.log('Allowance:', allowance);
```


