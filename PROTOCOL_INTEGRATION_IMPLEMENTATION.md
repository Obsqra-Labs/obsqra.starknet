# Protocol Integration Implementation Plan

## Goal
Uncomment and implement the protocol integration code so that deposits actually deploy funds to JediSwap and Ekubo, generating yield.

## Current State
- ✅ Interfaces defined (`jediswap.cairo`, `ekubo.cairo`)
- ✅ Protocol addresses configured
- ✅ Contract structure ready
- ❌ Protocol integration code commented out (lines 228-245)
- ❌ Funds just sit in contract, not earning yield

## Implementation Steps

### Step 1: Uncomment Interface Imports
**File**: `contracts/src/strategy_router_v2.cairo` (lines 34-45)

**Current:**
```cairo
// use super::super::interfaces::jediswap::{
//     IJediSwapV2NFTPositionManagerDispatcher, 
//     IJediSwapV2NFTPositionManagerDispatcherTrait,
//     IJediSwapRouterDispatcher,
//     IJediSwapRouterDispatcherTrait,
//     MintParams
// };
// use super::super::interfaces::ekubo::{
//     IEkuboCoreDispatcher,
//     IEkuboCoreDispatcherTrait
// };
```

**Action**: Uncomment these imports

---

### Step 2: Implement JediSwap Integration

**Location**: Inside `deposit()` function, `if jediswap_amount > 0` block

**Strategy:**
1. Swap half of `jediswap_amount` ETH → STRK
2. Approve NFT Position Manager for both ETH and STRK
3. Call `mint()` to add liquidity
4. Store position NFT token ID

**Code to add:**
```cairo
if jediswap_amount > 0 {
    let contract_addr = get_contract_address();
    let eth_token = self.asset_token.read(); // ETH
    let strk_token = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d; // STRK
    let jediswap_router = self.jediswap_router.read();
    let nft_manager = self.jediswap_nft_manager.read();
    
    // Step 1: Swap half ETH to STRK
    let swap_amount = jediswap_amount / 2; // Half for swap
    let remaining_eth = jediswap_amount - swap_amount; // Half for liquidity
    
    // Approve router for swap
    let eth_erc20 = IERC20Dispatcher { contract_address: eth_token };
    eth_erc20.approve(jediswap_router, swap_amount);
    
    // Perform swap: ETH → STRK
    let router = IJediSwapRouterDispatcher { contract_address: jediswap_router };
    let path = array![eth_token, strk_token];
    let deadline = get_block_timestamp() + 1800; // 30 min from now
    let amounts = router.swap_exact_tokens_for_tokens(
        swap_amount,
        0, // min_amount_out (slippage protection - set to 0 for now)
        path,
        contract_addr,
        deadline
    );
    let strk_received = amounts[1]; // Amount of STRK received
    
    // Step 2: Approve NFT Position Manager for both tokens
    eth_erc20.approve(nft_manager, remaining_eth);
    let strk_erc20 = IERC20Dispatcher { contract_address: strk_token };
    strk_erc20.approve(nft_manager, strk_received);
    
    // Step 3: Add liquidity via NFT Position Manager
    let nft = IJediSwapV2NFTPositionManagerDispatcher { contract_address: nft_manager };
    let mint_params = MintParams {
        token0: eth_token,
        token1: strk_token,
        fee: 3000, // 0.3% fee tier (standard for ETH/STRK)
        tick_lower: -887272, // Full range (min tick)
        tick_upper: 887272,  // Full range (max tick)
        amount0_desired: remaining_eth,
        amount1_desired: strk_received,
        amount0_min: 0, // Slippage protection
        amount1_min: 0,
        recipient: contract_addr,
        deadline: deadline,
    };
    let (token_id, liquidity, amount0, amount1) = nft.mint(mint_params);
    
    // Step 4: Store position NFT ID
    // TODO: Store in user-specific mapping when per-user tracking is implemented
    let count = self.jediswap_position_count.read();
    self.jediswap_position_count.write(count + 1);
}
```

---

### Step 3: Implement Ekubo Integration

**Location**: Inside `deposit()` function, `if ekubo_amount > 0` block

**Strategy:**
1. Swap half of `ekubo_amount` ETH → STRK
2. Approve Ekubo Core for both ETH and STRK
3. Call `deposit_liquidity()` to add liquidity
4. Store position ID (if returned)

**Code to add:**
```cairo
if ekubo_amount > 0 {
    let contract_addr = get_contract_address();
    let eth_token = self.asset_token.read(); // ETH
    let strk_token = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d; // STRK
    let ekubo_core = self.ekubo_core.read();
    
    // Step 1: Swap half ETH to STRK (similar to JediSwap)
    let swap_amount = ekubo_amount / 2;
    let remaining_eth = ekubo_amount - swap_amount;
    
    // Approve router for swap (using JediSwap router for now)
    let jediswap_router = self.jediswap_router.read();
    let eth_erc20 = IERC20Dispatcher { contract_address: eth_token };
    eth_erc20.approve(jediswap_router, swap_amount);
    
    // Perform swap: ETH → STRK
    let router = IJediSwapRouterDispatcher { contract_address: jediswap_router };
    let path = array![eth_token, strk_token];
    let deadline = get_block_timestamp() + 1800;
    let amounts = router.swap_exact_tokens_for_tokens(
        swap_amount,
        0,
        path,
        contract_addr,
        deadline
    );
    let strk_received = amounts[1];
    
    // Step 2: Approve Ekubo Core for both tokens
    eth_erc20.approve(ekubo_core, remaining_eth);
    let strk_erc20 = IERC20Dispatcher { contract_address: strk_token };
    strk_erc20.approve(ekubo_core, strk_received);
    
    // Step 3: Deposit liquidity to Ekubo
    let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
    let fee = 3000; // 0.3% fee tier
    let liquidity_tokens = ekubo.deposit_liquidity(
        eth_token,
        strk_token,
        remaining_eth,
        strk_received,
        fee
    );
    
    // Step 4: Store position (Ekubo returns liquidity tokens, not position ID)
    let count = self.ekubo_position_count.read();
    self.ekubo_position_count.write(count + 1);
}
```

---

### Step 4: Handle Errors and Edge Cases

**Issues to address:**

1. **Slippage Protection**: Currently set to 0, should calculate minimum amounts
2. **Deadline**: Currently 30 minutes, should be configurable
3. **Fee Tiers**: Hardcoded to 3000 (0.3%), should verify this is correct
4. **Tick Range**: Using full range (-887272 to 887272), might want to optimize
5. **Error Handling**: Need to handle swap failures, approval failures, etc.

---

### Step 5: Testing Plan

1. **Test Swap**: Verify ETH → STRK swap works
2. **Test JediSwap Liquidity**: Verify liquidity is added and NFT is minted
3. **Test Ekubo Liquidity**: Verify liquidity is deposited
4. **Test Position Tracking**: Verify position IDs are stored
5. **Test Small Amounts**: Start with 0.001 ETH to minimize risk

---

## Known Issues / Questions

1. **JediSwap Router Interface**: Using V1 router interface, but we have V2 addresses. Need to verify compatibility.

2. **Ekubo Interface**: The `deposit_liquidity` interface might not match actual Ekubo contract. Need to verify:
   - Actual function signature
   - Parameter types
   - Return values

3. **Tick Range**: Full range liquidity might not be optimal. Consider:
   - Calculating optimal tick range based on current price
   - Using a narrower range for better capital efficiency

4. **Slippage**: Need to implement proper slippage protection:
   - Calculate expected output from swap
   - Set minimum amounts based on slippage tolerance

5. **Gas Costs**: Multiple approvals and swaps will be expensive. Consider:
   - Batch operations if possible
   - Optimizing approval amounts

---

## Next Steps

1. ✅ Uncomment interface imports
2. ⏳ Implement JediSwap integration (with error handling)
3. ⏳ Implement Ekubo integration (with error handling)
4. ⏳ Add slippage protection
5. ⏳ Test on Sepolia with small amounts
6. ⏳ Fix any interface mismatches
7. ⏳ Optimize gas usage

---

## Files to Modify

- `/opt/obsqra.starknet/contracts/src/strategy_router_v2.cairo`
  - Uncomment imports (lines 34-45)
  - Implement JediSwap integration (lines 231-236)
  - Implement Ekubo integration (lines 240-245)

---

## Verification Checklist

- [ ] Code compiles without errors
- [ ] Interfaces match actual protocol contracts
- [ ] Swap functionality works
- [ ] Liquidity provision works
- [ ] Position tracking works
- [ ] Error handling works
- [ ] Gas costs are reasonable
- [ ] Tested on Sepolia


