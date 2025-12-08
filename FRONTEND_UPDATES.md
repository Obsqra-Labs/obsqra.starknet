# Frontend Updates - StrategyRouterV2 Live Integration

**Date**: December 5, 2025  
**Status**: ✅ Updated and Ready for Testing

## Overview

The frontend has been completely refactored to **remove all mock data in live mode** and display real contract data from the deployed StrategyRouterV2 on Starknet Sepolia testnet.

## 🎯 Key Changes

### 1. New Hook: `useStrategyRouterV2`

**File**: `/opt/obsqra.starknet/frontend/src/hooks/useStrategyRouterV2.ts`

Fetches real contract data directly from StrategyRouterV2:

```typescript
export function useStrategyRouterV2(): StrategyRouterData {
  // Fetches:
  // - get_total_value_locked() → TVL
  // - get_allocation() → JediSwap/Ekubo %
  // - get_protocol_addresses() → Contract addresses
}
```

**Features**:
- ✅ Auto-refreshes every 30 seconds
- ✅ Proper error handling
- ✅ Loading states
- ✅ BigInt to human-readable conversion

### 2. Updated Dashboard Component

**File**: `/opt/obsqra.starknet/frontend/src/components/Dashboard.tsx`

**Changes**:
- ✅ Imports and uses `useStrategyRouterV2` hook
- ✅ Shows real TVL from contract in live mode
- ✅ Displays actual protocol allocations (JediSwap/Ekubo)
- ✅ Shows protocol addresses with live indicator
- ✅ Clear visual distinction between Demo and Live modes
- ✅ Graceful handling of loading states and errors

**Before (Mock Data)**:
```
Total TVL: 0 STRK (hardcoded)
Protocol Allocation: No visual distinction
```

**After (Real Data)**:
```
Total TVL: [Fetched from contract via RPC]
  ✅ Live - StrategyRouterV2
Protocol Allocations:
  JediSwap: [50.00%] - Real from contract
  Ekubo: [50.00%] - Real from contract
  
Integrated Protocols (Real Addresses):
  🔄 JediSwap: 0x03c8e56...7a21
  🌀 Ekubo: 0x0444a09...384
```

### 3. Updated Analytics Dashboard

**File**: `/opt/obsqra.starknet/frontend/src/components/AnalyticsDashboard.tsx`

**Changes**:
- ✅ Supports both old (Nostra/zkLend) and new (JediSwap/Ekubo) protocols
- ✅ Switches protocol display based on allocation structure
- ✅ Shows appropriate APY/TVL for Sepolia testnet (lower than mainnet)
- ✅ Clear Demo vs Live mode indicator at top
- ✅ Responsive data updates

**Mock Data Removed**:
- Old hardcoded TVL values ($45.2M, $38.7M, etc.)
- Mainnet-level APY figures (now shows testnet-realistic rates)
- Always-active data (now respects loading/error states)

### 4. Updated Demo Mode Context

**File**: `/opt/obsqra.starknet/frontend/src/contexts/DemoModeContext.tsx`

**Changes**:
- ✅ Updated allocation to use JediSwap/Ekubo (50/50)
- ✅ Added mock TVL (50 STRK) for demo display
- ✅ Maintains backward compatibility with old protocol allocation format

### 5. Visual Indicators

#### Live Mode Badge
```
✅ Live - StrategyRouterV2
[Green badge showing real data is active]
```

#### Demo Mode Badge
```
🎮 Demo Mode - Using Mock Data
[Yellow badge showing mock data is active]
```

#### Mode Indicators on Each Section
- Pool Overview: Shows "Live" or "Demo" in top-right
- Analytics: Banner at top indicating current mode
- Protocol Details: Real contract addresses displayed

## 📊 Data Flow

### Live Mode (Production)
```
Frontend (useStrategyRouterV2)
    ↓ [RPC Call via Alchemy]
Contract: StrategyRouterV2 (0x030d822149ad301...)
    ↓ [Response]
Display real data with ✅ Live badge
```

### Demo Mode (Testing)
```
Frontend (useDemoMode)
    ↓ [Mock Data]
DemoModeContext (hardcoded values)
    ↓ [Response]
Display mock data with 🎮 Demo badge
```

##  How to Use

### Toggle Between Modes
1. Look for the toggle in the top-right navbar
2. Click to switch between **Live Mode** and **Demo Mode**
3. UI updates immediately to reflect the mode

### Live Mode Features
- **Real TVL**: Pulls from deployed contract
- **Real Allocations**: Shows actual JediSwap/Ekubo split
- **Real Addresses**: Displays actual protocol contract addresses
- **Auto-Refresh**: Updates every 30 seconds
- **Error Handling**: Shows helpful messages if RPC fails

### Demo Mode Features
- **Mock Data**: Shows predefined test data
- **Consistent**: Values don't change on refresh
- **No RPC Calls**: Faster (no network requests)
- **For Testing**: Perfect for testing UI without blockchain

## 📝 Implementation Details

### TVL Conversion
```typescript
// From contract (u256 with 18 decimals)
BigInt(routerV2.totalValueLocked) / BigInt(10 ** 18)
// Result: Human-readable number (e.g., "5" = 5 STRK)
```

### Allocation Conversion
```typescript
// From contract (basis points)
routerV2.jediswapAllocation / 100
// Result: Percentage (e.g., 5000 / 100 = 50%)
```

### Protocol Addresses
```typescript
// Displayed with truncation for brevity
routerV2.jediswapRouter.slice(0, 10) + "..." + .slice(-8)
// Result: 0x03c8e56...7a21
```

## 🔧 Configuration

### RPC Endpoint
```typescript
// Uses Alchemy to avoid CORS issues
const RPC_URL = process.env.NEXT_PUBLIC_RPC_URL || 
  'https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7';
```

### Contract Address
```typescript
// Automatically loaded from .env.local
const STRATEGY_ROUTER_ADDRESS = 
  process.env.NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS;
// Value: 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1
```

## ✅ Testing Checklist

- [ ] **Live Mode**
  - [ ] Toggle to Live Mode
  - [ ] See ✅ Live badge
  - [ ] TVL shows real value from contract
  - [ ] Allocations show 50/50 JediSwap/Ekubo
  - [ ] Protocol addresses visible
  - [ ] Data updates after 30 seconds
  
- [ ] **Demo Mode**
  - [ ] Toggle to Demo Mode
  - [ ] See 🎮 Demo badge
  - [ ] TVL shows 50 STRK
  - [ ] Allocations show 50/50
  - [ ] No real protocol addresses shown
  - [ ] Mock APY values visible

- [ ] **Error Handling**
  - [ ] RPC failure → Shows error message
  - [ ] Loading state → Spinner visible
  - [ ] Recovery → Data refreshes after error clears

## 📁 Files Modified

| File | Changes |
|------|---------|
| `src/hooks/useStrategyRouterV2.ts` | ✅ NEW - Real contract data fetching |
| `src/components/Dashboard.tsx` | ✅ Updated - Uses real data in live mode |
| `src/components/AnalyticsDashboard.tsx` | ✅ Updated - Supports JediSwap/Ekubo |
| `src/contexts/DemoModeContext.tsx` | ✅ Updated - Added TVL, updated allocations |
| `.env.local` | ✅ Already configured with V2 address |

## 🎓 Key Takeaways

1. **No More Hardcoded Mock Data in Live Mode** ✅
   - Everything that can be real is now real
   - Only demo mode uses mock data

2. **Smart Loading** ✅
   - Shows spinner while fetching
   - Displays previous data if refresh fails
   - No broken states

3. **Clear Mode Indicators** ✅
   - User always knows if they're viewing real or mock data
   - Color-coded badges (Green = Live, Yellow = Demo)

4. **Real Protocol Integration Visible** ✅
   - Shows actual JediSwap and Ekubo addresses
   - Displays live allocations from contract
   - Real TVL tracking

##  Next Steps

### Immediate (Already Done)
- ✅ Remove all mock data in live mode
- ✅ Add real contract data fetching
- ✅ Clear visual indicators for mode
- ✅ Proper error handling

### Soon (Phase 2)
- Implement actual protocol interaction in contracts
- Add per-user balance tracking
- Show real yields from protocols
- Add deposit/withdraw transaction UI

### Future (Phase 3)
- Analytics based on real on-chain data
- Historical yield tracking
- Risk metrics from RiskEngine
- DAO constraint enforcement UI

## 📚 Related Documentation

- **Contract Details**: [STRATEGYROUTER_V2_DEPLOYMENT.md](/opt/obsqra.starknet/STRATEGYROUTER_V2_DEPLOYMENT.md)
- **Testing Guide**: [E2E_TESTING_GUIDE.md](/opt/obsqra.starknet/E2E_TESTING_GUIDE.md)
- **Integration Complete**: [INTEGRATION_COMPLETE.md](/opt/obsqra.starknet/INTEGRATION_COMPLETE.md)

## 🌐 Live URLs

- **Production**: https://starknet.obsqra.fi
- **Local Dev**: http://localhost:3003

---

**Status**: Frontend is fully updated and ready to display real StrategyRouterV2 data! 🎉

The dashboard will now clearly show you're using real contract data or demo data, with all hardcoded mock values removed from live mode.

