# Contract Migration to v2 - December 8, 2025

## Overview

Successfully deployed v2 contracts with full on-chain AI orchestration and deposit/withdraw functionality.

## New Contract Addresses

### RiskEngine v2
- **Address**: `0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31`
- **Class Hash**: `0x021f951bda14eebb6679430f7e1f691391bd392c54db0f9c9531fb1d5d962cc3`
- **Features**:
  - ✅ `propose_and_execute_allocation` - Full on-chain orchestration
  - ✅ `set_strategy_router` - Admin function
  - ✅ Complete audit trail events
  - ✅ Performance tracking
- **Explorer**: https://sepolia.starkscan.co/contract/0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31

### StrategyRouterV2
- **Address**: `0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6`
- **Class Hash**: `0x06f8a0d2d99aa3d98ae831a563cd2047b53a3fa33932c49839402e83724843cb`
- **Features**:
  - ✅ `deposit` / `withdraw` - Direct STRK deposits
  - ✅ `update_allocation` - Only callable by RiskEngine
  - ✅ `set_risk_engine` - Admin function
  - ✅ Performance tracking linked to decisions
- **Explorer**: https://sepolia.starkscan.co/contract/0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6

### DAOConstraintManager (unchanged)
- **Address**: `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856`

## Deprecated v1 Contracts

| Contract | Address | Status |
|----------|---------|--------|
| RiskEngine v1 | `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80` | Deprecated |
| StrategyRouter v1 | `0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a` | Deprecated |

## Updated Configuration Files

### Frontend
- ✅ `frontend/.env.local` - Updated with v2 addresses

### Backend
- ✅ `backend/app/config.py` - Updated with v2 addresses
- ✅ `backend/docker-compose.yml` - Updated with v2 addresses

### Documentation
- ✅ `README.md` - Updated contract table
- ✅ `docs/DEV_LOG.md` - Added v2 deployment entry
- ✅ `deployments/sepolia.json` - Updated with v2 addresses

## Frontend Fixes

### Fixed Infinite Loop Issue
- **Problem**: `useStrategyDeposit` hook was causing infinite re-renders
- **Root Cause**: 
  - `provider` was recreated on every render
  - `fetchBalance` depended on `contractVersion` which changed after `checkContractVersion`
  - This triggered useEffect in Dashboard repeatedly
- **Solution**:
  - Memoized `provider` with `useMemo`
  - Removed `contractVersion` from `fetchBalance` dependencies
  - Added separate `useEffect` for version checking
  - Reduced console logging spam

### Fixed "Pool Selection Loading" Placeholder
- Changed from "Pool selection UI loading..." to clear "coming soon" message
- Added note about using AI Risk Engine orchestration

## Testing Checklist

- [ ] Test AI orchestration flow from frontend
- [ ] Verify deposit/withdraw works with StrategyRouterV2
- [ ] Check audit trail events on Starkscan
- [ ] Verify performance tracking links decisions to outcomes
- [ ] Test backend API with new contract addresses

## Next Steps

1. **Test End-to-End Flow**:
   - Connect wallet
   - Click "AI Risk Engine: Orchestrate Allocation"
   - Verify transaction succeeds
   - Check events on Starkscan

2. **Verify Integration**:
   - Ensure RiskEngine can call StrategyRouterV2
   - Test deposit/withdraw functionality
   - Monitor performance tracking

3. **Documentation**:
   - Update API documentation
   - Create user guide for AI orchestration
   - Document event structure for audit trail

## Migration Notes

- Old v1 contracts remain on-chain but are deprecated
- All new deployments should use v2 addresses
- Frontend automatically detects contract version
- Backend must be restarted to use new addresses


