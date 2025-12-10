# Deposit Error Debug: u256_sub Overflow

## Error Analysis

**Error Message:**
```
u256_sub Overflow
argent/multicall-failed
ENTRYPOINT_FAILED
```

**What This Means:**
- `u256_sub Overflow` = Trying to subtract a larger number from a smaller number
- This happens in ERC20 `transfer_from` when:
  - User balance < amount, OR
  - User allowance < amount

## Likely Causes

### 1. **Insufficient Allowance** (Most Likely)
The approval might not have completed or the amount approved is less than the deposit amount.

**Check:**
- Did the approval transaction succeed?
- Is the approval amount >= deposit amount?
- Did you wait for approval confirmation?

### 2. **Insufficient Balance**
User doesn't have enough ETH in their wallet.

**Check:**
- Does user have enough ETH?
- Is the amount in the correct format (wei vs ETH)?

### 3. **Wrong Token Address**
The ETH token address might be incorrect.

**Current Address:**
- Frontend: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`
- Contract expects: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`

### 4. **Amount Format Issue**
The amount might be in wrong format (needs to be in wei, not ETH).

**Current Code:**
```typescript
const amountWei = BigInt(Math.floor(amount * 1e18));
const amountU256 = uint256.bnToUint256(amountWei);
```

This should be correct, but let's verify.

## Debugging Steps

### Step 1: Check User Balance
```typescript
// In browser console
const provider = new RpcProvider({ nodeUrl: 'https://starknet-sepolia-rpc.publicnode.com' });
const ethContract = new Contract(ETH_TOKEN_ABI, ETH_TOKEN_ADDRESS, provider);
const balance = await ethContract.balanceOf(userAddress);
console.log('ETH Balance:', balance);
```

### Step 2: Check Allowance
```typescript
const allowance = await ethContract.allowance(userAddress, strategyRouterAddress);
console.log('Allowance:', allowance);
console.log('Deposit Amount:', amountU256);
console.log('Allowance >= Amount?', allowance >= amountU256);
```

### Step 3: Check Contract Address
```typescript
// Verify contract is deployed and has correct asset_token
const routerContract = new Contract(STRATEGY_ROUTER_V2_ABI, strategyRouterAddress, provider);
// Call get_asset_token() to verify
```

## Quick Fixes

### Fix 1: Increase Approval Amount
Approve a larger amount (e.g., max uint256) to avoid approval issues:

```typescript
// Approve max amount instead of exact amount
const maxApproval = uint256.bnToUint256(BigInt('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'));
const approveCall = ethContract.populate('approve', [
  strategyRouterAddress,
  maxApproval,  // Max approval
]);
```

### Fix 2: Check Balance Before Deposit
Add balance check in frontend:

```typescript
if (userBalance < amount) {
  throw new Error(`Insufficient balance. You have ${userBalance} ETH but trying to deposit ${amount} ETH`);
}
```

### Fix 3: Verify Approval Before Deposit
Add allowance check:

```typescript
const allowance = await ethContract.allowance(address, strategyRouterAddress);
if (allowance < amountU256) {
  throw new Error('Insufficient allowance. Please approve first.');
}
```

## Most Likely Issue

**The approval transaction might not have completed before the deposit transaction was sent.**

**Solution:**
1. Make sure approval transaction is confirmed
2. Check allowance before depositing
3. Or use max approval to avoid this issue

## Next Steps

1. Check browser console for approval transaction hash
2. Verify approval transaction on Starkscan
3. Check allowance before attempting deposit
4. If allowance is 0, approve again
5. If balance is insufficient, deposit less


