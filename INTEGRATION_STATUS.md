# Protocol Integration Status - Exhaustive Documentation

**Last Updated**: December 10, 2025  
**Network**: Starknet Sepolia Testnet  
**Contract**: StrategyRouterV2 (`0x0146bb729339068bde94aa89c1668d898515a6df6cd7e2bd40543303abdee8f4`)

---

## Executive Summary

We are building a multi-protocol yield aggregator on Starknet that deploys user deposits across multiple DeFi protocols (JediSwap and Ekubo) to maximize yield. The system separates deposit/withdrawal operations from protocol deployment to reduce transaction complexity and improve reliability.

### Current Status: **PARTIALLY OPERATIONAL**

- ✅ **STRK Deposits/Withdrawals**: Fully functional
- ✅ **Ekubo Positions Integration**: Working (mint_and_deposit)
- ⚠️ **JediSwap NFT Position Manager**: Implemented but not fully tested
- ❌ **JediSwap V2 Router Swaps**: Failing with ENTRYPOINT_NOT_FOUND
- ⚠️ **Protocol Deployment**: Works but skips swap step (STRK-only liquidity)

---

## Architecture Overview

### Contract Structure

```
StrategyRouterV2
├── Deposit/Withdraw (User-facing)
│   ├── deposit(amount: u256) ✅
│   └── withdraw(amount: u256) ✅
│
├── Protocol Deployment (Owner-only)
│   └── deploy_to_protocols() ⚠️
│       ├── JediSwap Integration
│       │   ├── Swap STRK → ETH (❌ FAILING)
│       │   └── Add Liquidity via NFT Position Manager (⚠️ UNTESTED)
│       └── Ekubo Integration
│           ├── Swap STRK → ETH (❌ FAILING - same router issue)
│           └── Add Liquidity via Positions Contract (✅ WORKING)
│
└── Testing Functions (Owner-only)
    ├── test_jediswap_only(amount: u256) ⚠️
    └── test_ekubo_only(amount: u256) ✅
```

### Key Design Decisions

1. **Separated Deposit from Deployment**: Users deposit STRK, owner calls `deploy_to_protocols()` separately
2. **Token Handling**: Contract accepts STRK deposits, swaps half to ETH for liquidity pairs
3. **Protocol Selection**: Currently 50/50 split between JediSwap and Ekubo (configurable)

---

## Protocol Integrations - Detailed Status

### 1. JediSwap Integration

#### 1.1 JediSwap V2 Swap Router

**Status**: ❌ **NOT WORKING**

**Contract Address**: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`  
**Network**: Sepolia  
**Version**: V2 (V1 is only on Alpha Testnet)

**Function Attempted**: `exact_input_single(ExactInputSingleParams)`

**Error**: `ENTRYPOINT_NOT_FOUND`  
**Selector**: `0x3276861cf5e05d6daf8f352cabb47df623eb10c383ab742fcc7abea94d5c5cc`

**Interface Definition**:
```cairo
pub struct ExactInputSingleParams {
    pub token_in: ContractAddress,
    pub token_out: ContractAddress,
    pub fee: u128,              // 3000 = 0.3%
    pub recipient: ContractAddress,
    pub deadline: u64,
    pub amount_in: u256,
    pub amount_out_minimum: u256,
    pub sqrt_price_limit_x96: u256,
}
```

**Root Cause Analysis**:
- The selector matches `exact_input_single`, so the function exists
- Error suggests parameter serialization issue or struct field order mismatch
- Possible issues:
  1. Struct fields not in correct order for Cairo serialization
  2. Missing or incorrect fee tier (3000 might not exist for STRK/ETH pair)
  3. Router contract on Sepolia might have different interface than documented

**Workaround**: Currently skipping swap, adding liquidity with STRK only

**Next Steps**:
1. Verify actual ABI of deployed router contract on Starkscan
2. Check if fee tier 3000 exists for STRK/ETH pair
3. Test with different fee tiers (500, 10000)
4. Consider using JediSwap V1 router if available on Sepolia

**Documentation Reference**: 
- [JediSwap V2 Swap Router Docs](https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_swap_router)
- [JediSwap Contract Addresses](https://docs.jediswap.xyz/for-developers/jediswap-v2/contract-addresses)

---

#### 1.2 JediSwap V2 NFT Position Manager

**Status**: ⚠️ **IMPLEMENTED BUT UNTESTED**

**Contract Address**: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`  
**Network**: Sepolia

**Function Used**: `mint(MintParams)`

**Interface Definition**:
```cairo
pub struct MintParams {
    pub token0: ContractAddress,
    pub token1: ContractAddress,
    pub fee: u32,                    // 3000 = 0.3%
    pub tick_lower: i128,            // -887272 (full range)
    pub tick_upper: i128,            // 887272 (full range)
    pub amount0_desired: u256,
    pub amount1_desired: u256,
    pub amount0_min: u256,
    pub amount1_min: u256,
    pub recipient: ContractAddress,
    pub deadline: u64,
}
```

**Current Implementation**:
- Adds liquidity with STRK only (amount1 = 0)
- Position manager should handle swap internally if needed
- Full range liquidity (-887272 to 887272 ticks)

**Testing Status**: Not yet tested end-to-end

**Known Issues**:
- May fail if position manager requires both tokens
- No slippage protection (amount0_min = 0, amount1_min = 0)

**Next Steps**:
1. Test `mint()` with STRK-only to verify behavior
2. If fails, implement proper swap before mint
3. Add slippage protection based on current pool price

**Documentation Reference**:
- [JediSwap V2 NFT Position Manager](https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_nft_position_manager)

---

### 2. Ekubo Integration

#### 2.1 Ekubo Positions Contract

**Status**: ✅ **WORKING**

**Contract Address**: `0x06a2aee84bb0ed5dded4384ddd0e40e9c1372b818668375ab8e3ec08807417e5`  
**Network**: Sepolia

**Function Used**: `mint_and_deposit(PoolKey, Bounds, min_liquidity)`

**Why This Works**:
- Ekubo Positions contract handles Core's lock/callback pattern internally
- No need to implement `locked()` callback in our contract
- Simpler integration than direct Core interaction

**Interface Definition**:
```cairo
pub struct PoolKey {
    pub token0: ContractAddress,
    pub token1: ContractAddress,
    pub fee: u128,              // 3000 = 0.3%
    pub tick_spacing: u128,     // 60
    pub extension: ContractAddress,
}

pub struct Bounds {
    pub lower: i129,            // -887280 (full range)
    pub upper: i129,            // 887280 (full range)
}
```

**Current Implementation**:
- Adds liquidity with STRK only (ETH = 0)
- Full range bounds
- Positions contract handles Core interaction

**Testing Status**: ✅ Successfully tested via `test_ekubo_only()`

**Known Limitations**:
- Currently adding STRK-only liquidity (may not work if pair requires both tokens)
- No swap before liquidity provision

**Next Steps**:
1. Test with actual STRK/ETH pair to verify behavior
2. If fails, implement swap before `mint_and_deposit`
3. Add proper token amount calculation based on pool price

**Documentation Reference**:
- [Ekubo Protocol GitHub](https://github.com/EkuboProtocol/starknet-contracts)
- [Ekubo Positions Contract](https://docs.ekubo.org/)

---

#### 2.2 Ekubo Core (Not Used)

**Status**: ❌ **NOT USED** (by design)

**Contract Address**: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`  
**Network**: Sepolia

**Why Not Used**:
- Ekubo Core uses lock/callback pattern requiring `locked()` implementation
- Direct Core interaction is complex and error-prone
- Ekubo Positions contract provides simpler interface

**Previous Attempts**:
- Tried implementing `locked()` callback in StrategyRouterV2
- Failed with selector mismatch issues
- Switched to Positions contract for simpler integration

**Documentation Reference**:
- [Ekubo Core Interface](https://github.com/EkuboProtocol/starknet-contracts/blob/main/src/interfaces/core.cairo)

---

## Token Support

### STRK Token

**Status**: ✅ **FULLY SUPPORTED**

**Contract Address**: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d`  
**Network**: Sepolia

**Functions**:
- ✅ `deposit(amount: u256)` - Accepts STRK deposits
- ✅ `withdraw(amount: u256)` - Returns STRK to users
- ✅ Balance tracking per user
- ✅ ERC20 approval/transfer handling

**Current Usage**: Primary deposit token

---

### ETH Token

**Status**: ⚠️ **CONFIGURED BUT NOT FULLY INTEGRATED**

**Contract Address**: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`  
**Network**: Sepolia

**Purpose**: Used for liquidity pairs (STRK/ETH)

**Current Status**:
- Address stored in contract storage
- Used in swap attempts (currently failing)
- Not directly accepted as deposit token

**Future Plans**:
- Enable ETH deposits (users deposit ETH, contract swaps half to STRK)
- Currently blocked by swap router issues

---

## Contract Functions - Complete Reference

### User-Facing Functions

#### `deposit(amount: u256)`
- **Status**: ✅ Working
- **Purpose**: Accept STRK deposits from users
- **Behavior**: 
  - Transfers STRK from user to contract
  - Updates `pending_deposits` storage
  - Does NOT deploy to protocols automatically
- **Authorization**: Public (anyone can deposit)

#### `withdraw(amount: u256) -> u256`
- **Status**: ✅ Working
- **Purpose**: Return STRK to users
- **Behavior**: 
  - Transfers STRK from contract to user
  - Updates user balance
  - Does NOT withdraw from protocols (funds must be in contract)
- **Authorization**: Public (users can withdraw their own funds)

#### `get_user_balance(user: ContractAddress) -> u256`
- **Status**: ✅ Working
- **Purpose**: Query user's deposited balance
- **Authorization**: Public (view function)

---

### Owner-Only Functions

#### `deploy_to_protocols()`
- **Status**: ⚠️ Partially Working
- **Purpose**: Deploy pending deposits to JediSwap and Ekubo
- **Behavior**:
  1. Calculates amounts for each protocol (based on allocation %)
  2. Attempts to swap half STRK to ETH (❌ FAILING)
  3. Adds liquidity to JediSwap via NFT Position Manager (⚠️ UNTESTED)
  4. Adds liquidity to Ekubo via Positions Contract (✅ WORKING)
  5. Clears `pending_deposits`
- **Authorization**: Owner only
- **Current Workaround**: Skips swap, adds STRK-only liquidity

#### `update_allocation(jediswap_pct: felt252, ekubo_pct: felt252)`
- **Status**: ✅ Working
- **Purpose**: Update allocation percentages (basis points, e.g., 5000 = 50%)
- **Authorization**: Owner or Risk Engine

#### `test_jediswap_only(amount: u256)`
- **Status**: ⚠️ Implemented but not tested
- **Purpose**: Test JediSwap integration in isolation
- **Behavior**: Similar to `deploy_to_protocols()` but only for JediSwap
- **Authorization**: Owner only

#### `test_ekubo_only(amount: u256)`
- **Status**: ✅ Working
- **Purpose**: Test Ekubo integration in isolation
- **Behavior**: Adds liquidity to Ekubo only
- **Authorization**: Owner only
- **Test Result**: Successfully tested

---

## Deployment Information

### Current Deployment

**Contract Address**: `0x0146bb729339068bde94aa89c1668d898515a6df6cd7e2bd40543303abdee8f4`  
**Class Hash**: `0x7af696ae8321e39a73ec85eed8fb6d3d0208cbf1b0776e0f7464df7b55b9d42`  
**Network**: Sepolia  
**Deployed**: December 10, 2025

**Constructor Parameters**:
- Owner: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`
- JediSwap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- JediSwap NFT Manager: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`
- Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
- Ekubo Positions: `0x06a2aee84bb0ed5dded4384ddd0e40e9c1372b818668375ab8e3ec08807417e5`
- Risk Engine: `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80`
- DAO Manager: `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856`
- Asset Token (STRK): `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d`
- JediSwap Allocation: 5000 (50%)
- Ekubo Allocation: 5000 (50%)

**Explorer Links**:
- [Contract on Starkscan](https://sepolia.starkscan.co/contract/0x0146bb729339068bde94aa89c1668d898515a6df6cd7e2bd40543303abdee8f4)
- [Class on Starkscan](https://sepolia.starkscan.co/class/0x7af696ae8321e39a73ec85eed8fb6d3d0208cbf1b0776e0f7464df7b55b9d42)

---

## Known Issues & Limitations

### Critical Issues

1. **JediSwap V2 Router Swap Failing**
   - **Impact**: Cannot swap STRK to ETH before adding liquidity
   - **Workaround**: Adding STRK-only liquidity (may not work)
   - **Priority**: HIGH
   - **Next Steps**: Verify router ABI, test different fee tiers

2. **JediSwap NFT Position Manager Untested**
   - **Impact**: Unknown if STRK-only liquidity works
   - **Priority**: HIGH
   - **Next Steps**: Test `mint()` with STRK-only

### Medium Priority Issues

3. **No Slippage Protection**
   - **Impact**: Vulnerable to front-running and price manipulation
   - **Priority**: MEDIUM
   - **Next Steps**: Add price oracle or off-chain price feed

4. **Ekubo STRK-Only Liquidity**
   - **Impact**: May fail if pair requires both tokens
   - **Priority**: MEDIUM
   - **Next Steps**: Test with actual pool, implement swap if needed

### Low Priority Issues

5. **No Position Tracking**
   - **Impact**: Cannot withdraw from specific positions
   - **Priority**: LOW
   - **Next Steps**: Store NFT token IDs and position details

6. **No Yield Accrual**
   - **Impact**: Deposits don't earn yield yet
   - **Priority**: LOW
   - **Next Steps**: Implement `accrue_yields()` and `rebalance()`

---

## Testing Status

### Completed Tests

- ✅ STRK deposit
- ✅ STRK withdrawal
- ✅ Ekubo `test_ekubo_only()` (approval + mint_and_deposit)

### Pending Tests

- ⏳ JediSwap `test_jediswap_only()` (approval + mint)
- ⏳ Full `deploy_to_protocols()` with both protocols
- ⏳ JediSwap V2 Router swap (any swap function)
- ⏳ Position withdrawal
- ⏳ Rebalancing

---

## Roadmap

### Phase 1: Fix Critical Issues (Current)
- [ ] Fix JediSwap V2 Router swap integration
- [ ] Test JediSwap NFT Position Manager
- [ ] Verify end-to-end liquidity provision

### Phase 2: Complete Core Functionality
- [ ] Implement position tracking (NFT IDs)
- [ ] Add slippage protection
- [ ] Implement yield accrual
- [ ] Add rebalancing logic

### Phase 3: Enhancements
- [ ] Support ETH deposits
- [ ] Add more protocols (10KSwap, etc.)
- [ ] Implement dynamic allocation based on APY
- [ ] Add frontend UI for protocol testing

---

## Resources & Documentation

### Protocol Documentation
- [JediSwap V2 Docs](https://docs.jediswap.xyz/for-developers/jediswap-v2)
- [Ekubo Protocol GitHub](https://github.com/EkuboProtocol/starknet-contracts)
- [Starknet Book](https://book.starknet.io/)

### Contract Addresses
- [JediSwap Sepolia Addresses](https://docs.jediswap.xyz/for-developers/jediswap-v2/contract-addresses)
- [Ekubo Sepolia Addresses](https://docs.ekubo.org/)

### Tools
- [Starkscan Explorer](https://sepolia.starkscan.co/)
- [Starkli CLI](https://book.starknet.io/toolchain/starkli)
- [Scarb (Cairo Package Manager)](https://docs.swmansion.com/scarb/)

---

## Contact & Support

For issues or questions:
- Check contract on Starkscan for latest state
- Review error messages in transaction receipts
- Test individual protocol functions before full integration

---

**Document Maintained By**: Development Team  
**Last Review**: December 10, 2025
