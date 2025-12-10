# ETH Deposit Update Summary

**Date**: January 27, 2025  
**Status**: ✅ Complete

## Overview

Updated all documentation and frontend code to reflect that the StrategyRouterV2 contract now accepts **ETH** deposits instead of STRK. Users deposit ETH, and the contract automatically swaps half to STRK for liquidity pools.

---

## Contract Changes

### New Deployment
- **Contract Address**: `0x053b69775c22246080a17c37a38dbda31d1841c8f6d7b4d928d54a99eda2748c`
- **Asset Token**: ETH (`0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`)
- **Previous**: STRK token
- **New**: ETH token

### How It Works
1. User deposits **ETH**
2. Contract receives ETH
3. Contract swaps **half ETH → STRK** internally
4. Adds liquidity to JediSwap + Ekubo with **ETH + STRK**
5. Funds start earning yield

---

## Documentation Updated

### ✅ Files Updated

1. **STRATEGYROUTER_V2_DEPLOYMENT.md**
   - Updated contract address
   - Changed asset_token from STRK to ETH
   - Updated constructor parameters
   - Added note about ETH deposits

2. **USER_GUIDE.md**
   - Changed "Total STRK" to "Total ETH"
   - Updated deposit flow descriptions

3. **DEPLOY_V2_ETH_GUIDE.md**
   - Created deployment guide for ETH version

4. **FIXED_DEPOSIT_TOKEN.md**
   - Documented the fix from STRK to ETH

---

## Frontend Code Updated

### ✅ Files Updated

1. **useStrategyDeposit.ts**
   - Changed `STRK_TOKEN_ABI` → `ETH_TOKEN_ABI`
   - Changed `STRK_TOKEN_ADDRESS` → `ETH_TOKEN_ADDRESS`
   - Updated to ETH token address: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`
   - Updated comments: "User's ETH balance" (not STRK)
   - Updated deposit function: "Deposit ETH" (contract swaps internally)
   - Updated withdraw function: "Withdraw ETH"

2. **Dashboard.tsx**
   - Changed all "STRK" labels to "ETH"
   - Updated deposit UI: "Deposit ETH"
   - Updated withdraw UI: "Withdraw ETH"
   - Updated balance displays: "ETH" instead of "STRK"
   - Added note: "Contract swaps half ETH to STRK for pools"
   - Updated TVL display: "ETH" instead of "STRK"

3. **DepositAllocationPreview.tsx**
   - Changed allocation preview amounts: "ETH" instead of "STRK"

4. **TransactionHistory.tsx**
   - Updated transaction types: "Deposit ETH", "Withdraw ETH"

5. **AnalyticsDashboard.tsx**
   - Updated all portfolio value displays: "ETH" instead of "STRK"
   - Updated yield calculations: "ETH" instead of "STRK"
   - Updated TVL displays: "ETH" instead of "STRK"

---

## User Experience Changes

### Before
- Users needed to deposit **STRK**
- UI showed "Deposit STRK"
- Balance showed "STRK"

### After
- Users deposit **ETH** ✅
- UI shows "Deposit ETH"
- Balance shows "ETH"
- Note: "Contract swaps half ETH to STRK for pools"

---

## Testing Checklist

- [ ] Frontend displays "ETH" instead of "STRK"
- [ ] Deposit flow uses ETH token address
- [ ] Balance fetching uses ETH token
- [ ] Approval uses ETH token
- [ ] Deposit transaction uses ETH
- [ ] UI messages reference ETH
- [ ] Documentation is consistent

---

## Environment Variables

Update `.env.local`:

```bash
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x053b69775c22246080a17c37a38dbda31d1841c8f6d7b4d928d54a99eda2748c
```

---

## Next Steps

1. ✅ Documentation updated
2. ✅ Frontend code updated
3. ⏳ Test deposit flow with ETH
4. ⏳ Verify contract swaps ETH to STRK correctly
5. ⏳ Test withdrawal returns ETH

---

**All updates complete!** The system now consistently uses ETH as the deposit token throughout documentation and frontend code.


