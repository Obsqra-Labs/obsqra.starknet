# Integration Tests Development Log

This log tracks notable findings, issues, and solutions discovered during integration testing.

---

## 2025-12-10 - Initial Setup & Critical Findings

### Finding: Deposit Transaction Succeeds But Gas Fee Extraction Fails

**Issue**: Deposit transactions were completing successfully on-chain, but the frontend was showing errors due to gas fee extraction from transaction receipts.

**Root Cause**: 
- `receipt.actual_fee` can be returned in multiple formats: string, number, or U256 object `{low: string, high: string}`
- The code was attempting `BigInt(receipt.actual_fee)` directly, which fails when `actual_fee` is an object

**Solution**: 
- Wrapped gas fee extraction in try-catch blocks to make it non-blocking
- Added proper type checking and handling for all possible `actual_fee` formats
- Gas fee extraction failures now log warnings but don't break the transaction flow

**Files Modified**:
- `frontend/src/hooks/useStrategyDeposit.ts` (deposit and withdraw functions)
- `frontend/src/components/IntegrationTests.tsx`

**Status**: ✅ Fixed

---

### Finding: Contract Address Mismatch in Deployment Script

**Issue**: The deployment script was saving the transaction hash as the contract address in the deployment JSON file.

**Root Cause**: 
- The script's regex extraction was capturing the wrong value
- Transaction hash and contract address have the same format (0x + 64 hex chars)

**Solution**: 
- Fixed the deployment script to correctly extract contract address vs transaction hash
- Updated `deployments/sepolia-v2-strk-test.json` with correct address
- Updated `frontend/.env.local` with correct contract address

**Contract Address**: `0x01e6d902d9bd0c83c55d5ca4fc77a8f2999b77ef9cc22975dd4081b491edd010`

**Status**: ✅ Fixed

---

### Finding: Integration Tests Require Contract Owner Wallet

**Issue**: Integration test functions (`deploy_to_protocols`, `test_jediswap_only`, `test_ekubo_only`) were failing with unclear error messages.

**Root Cause**: 
- These functions have `assert(caller == owner, 'Only owner can test')` checks in the contract
- Regular users cannot call these functions

**Solution**: 
- Added clear error message in `IntegrationTests.tsx` explaining owner-only requirement
- Error now shows: "❌ Owner-only function. This test requires the contract owner's wallet."

**Status**: ✅ Documented & Error Message Improved

---

### Finding: User Balance Not Displaying After Deposit

**Issue**: After successful deposits, the withdraw UI was not showing the deposited balance.

**Root Cause**: 
- `get_user_balance()` returns u256 which needs proper parsing
- RPC state might not be immediately updated after transaction
- Contract's `get_user_balance()` currently returns `total_deposits` (all users), not per-user balance (contract TODO)

**Solution**: 
- Fixed u256 parsing to handle string, number, `{low, high}`, and nested formats
- Added 1-second delay before fetching balance to allow RPC state sync
- Added logging to show fetched balance: `📊 Contract balance (deposited): X.XXXXXX STRK`

**Note**: Contract needs per-user deposit tracking implementation (currently returns total for all users)

**Status**: ✅ Fixed (with contract limitation noted)

---

### Finding: RPC Indexing Delays

**Issue**: Newly deployed contracts sometimes show "Contract not found" errors immediately after deployment.

**Root Cause**: 
- RPC providers (Alchemy, etc.) need time to index new contracts
- Typical delay: 2-5 minutes after deployment

**Solution**: 
- Added pre-flight contract verification in `IntegrationTests.tsx`
- Provides clear error message if contract not found
- Recommends waiting 2-5 minutes for RPC indexing

**Status**: ✅ Documented & Error Handling Improved

---

## Testing Checklist

- [x] Deposit functionality working
- [x] Withdraw functionality working
- [x] Gas fee tracking implemented
- [x] Balance display after deposit
- [x] Error messages for owner-only functions
- [ ] Per-user balance tracking (contract TODO)
- [ ] Integration tests with owner wallet
- [ ] Fee collection testing
- [ ] Yield accrual testing

---

## Known Limitations

1. **Per-User Balance Tracking**: Contract's `get_user_balance()` returns total deposits for all users, not per-user. This is a contract TODO.

2. **Owner-Only Test Functions**: Integration test functions require contract owner wallet. Regular users cannot test these functions.

3. **RPC Indexing Delays**: New deployments may take 2-5 minutes to be indexed by RPC providers.

---

## Next Steps

1. Implement per-user deposit tracking in contract
2. Test integration functions with owner wallet
3. Test fee collection mechanisms
4. Test yield accrual and reinvestment

