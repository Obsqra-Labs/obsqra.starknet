# Strategy Router V3 Changes

## Overview
V3 includes the yield accrual fix from v2 plus slippage protection for swaps and liquidity provision.

## Changes from V2

### 1. Fixed Yield Accrual Bug ✅
- **Issue**: Missing `ekubo_collect_salt` assignment in `accrue_yields()` causing "Input too long for arguments" error
- **Fix**: Added salt read and write operations before calling `ekubo.lock()`
- **Location**: `accrue_yields()` and `accrue_ekubo_yields()` functions

### 2. Added Individual Yield Accrual Functions ✅
- `accrue_jediswap_yields()` - Collect fees from JediSwap positions only
- `accrue_ekubo_yields()` - Collect fees from Ekubo positions only
- Both are owner-only functions

### 3. Slippage Protection Implementation ✅

#### Storage Variables
- `swap_slippage_bps: u256` - Slippage tolerance for swaps (basis points, default: 100 = 1%)
- `liquidity_slippage_bps: u256` - Slippage tolerance for liquidity provision (basis points, default: 50 = 0.5%)

#### New Functions
- `update_slippage_tolerance(swap_slippage_bps, liquidity_slippage_bps)` - Owner-only function to update slippage tolerance
- `get_slippage_tolerance()` - View function to get current slippage settings

#### Implementation Details
- **Swaps**: `amount_out_minimum` is calculated based on `swap_slippage_bps`
  - Currently uses a conservative 95% estimate of input value
  - **Note**: In production, should get a quote from router first, then apply slippage
- **Liquidity Provision**: `amount0_min` and `amount1_min` are calculated based on `liquidity_slippage_bps`
  - Applied to both `deploy_to_protocols()` and `test_jediswap_only()`

#### Slippage Calculation
```cairo
// For swaps:
estimated_output = swap_amount * 95 / 100  // Conservative estimate
slippage_amount = estimated_output * swap_slippage_bps / 10000
amount_out_minimum = estimated_output - slippage_amount

// For liquidity:
slippage_amount0 = amount0 * liquidity_slippage_bps / 10000
amount0_min = amount0 - slippage_amount0
```

### 4. Contract Naming
- Interface: `IStrategyRouterV3`
- Contract: `StrategyRouterV3`

## Migration Notes

### Constructor Changes
V3 constructor initializes slippage tolerance:
```cairo
self.swap_slippage_bps.write(100);  // 1% default
self.liquidity_slippage_bps.write(50);  // 0.5% default
```

### Breaking Changes
- Interface name changed from `IStrategyRouterV2` to `IStrategyRouterV3`
- Contract module name changed from `StrategyRouterV2` to `StrategyRouterV3`
- New storage variables: `swap_slippage_bps`, `liquidity_slippage_bps`

### Backward Compatibility
- V2 contract remains available as `strategy_router_v2.cairo` and `strategy_router_v2_backup.cairo`
- V3 is a new contract that needs to be deployed separately

## Testing Recommendations

1. **Yield Accrual**: Test `accrue_yields()`, `accrue_jediswap_yields()`, and `accrue_ekubo_yields()`
2. **Slippage Protection**: 
   - Test with different slippage settings
   - Verify swaps fail if output is below minimum
   - Verify liquidity provision fails if amounts are below minimum
3. **Slippage Updates**: Test `update_slippage_tolerance()` with owner and non-owner accounts

## Future Improvements

1. **Swap Quote Integration**: Get actual quote from router before calculating slippage
2. **Oracle Integration**: Use price oracles for more accurate swap output estimates
3. **Dynamic Slippage**: Adjust slippage based on market conditions or pool liquidity
4. **Per-Protocol Slippage**: Different slippage settings for JediSwap vs Ekubo



