# Protocol Integration - Updated with Official Docs

## Key Discovery: JediSwap Uses NFT Position Manager for Liquidity

Based on [JediSwap V2 documentation](https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_nft_position_manager), **we need the NFT Position Manager, not the Swap Router** for adding/removing liquidity.

**JediSwap V2 Contract Addresses (Sepolia):**
- ✅ Factory: `0x050d3df81b920d3e608c4f7aeb67945a830413f618a1cf486bdcce66a395109c`
- ✅ Swap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21` (for swaps only)
- ⚠️ **NFT Position Manager**: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399` (for liquidity!)

**Current Issue:**
- We're storing Swap Router address, but need NFT Position Manager for liquidity operations
- Need to update StrategyRouter to store NFT Position Manager address instead

---

## Updated Implementation Plan

### Step 1: Update Protocol Addresses

**Current Storage:**
```cairo
jediswap_router: ContractAddress,  // Currently Swap Router
ekubo_core: ContractAddress,
```

**Should Be:**
```cairo
jediswap_nft_manager: ContractAddress,  // NFT Position Manager for liquidity
jediswap_swap_router: ContractAddress,   // Swap Router (for swaps if needed)
ekubo_core: ContractAddress,
```

**Addresses to Use:**
- JediSwap NFT Position Manager: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`
- Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`

---

### Step 2: Define JediSwap NFT Position Manager Interface

**File**: `contracts/src/interfaces/jediswap_nft_position_manager.cairo`

Based on [JediSwap V2 NFT Position Manager docs](https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_nft_position_manager):

```cairo
#[starknet::interface]
pub trait IJediSwapV2NFTPositionManager<TContractState> {
    // Add liquidity to a pool
    fn mint(
        ref self: TContractState,
        params: MintParams
    ) -> (u256, u256, u256, u256);  // Returns (token_id, liquidity, amount0, amount1)
    
    // Remove liquidity from a position
    fn decrease_liquidity(
        ref self: TContractState,
        params: DecreaseLiquidityParams
    ) -> (u256, u256);  // Returns (amount0, amount1)
    
    // Collect fees from a position
    fn collect(
        ref self: TContractState,
        params: CollectParams
    ) -> (u256, u256);  // Returns (amount0, amount1)
    
    // Burn a position NFT
    fn burn(
        ref self: TContractState,
        token_id: u256
    );
    
    // Get position details
    fn positions(
        self: @TContractState,
        token_id: u256
    ) -> Position;  // Returns position struct
}

// Parameter structs
#[derive(Drop, Serde)]
struct MintParams {
    token0: ContractAddress,
    token1: ContractAddress,
    fee: u32,
    tick_lower: i128,
    tick_upper: i128,
    amount0_desired: u256,
    amount1_desired: u256,
    amount0_min: u256,
    amount1_min: u256,
    recipient: ContractAddress,
    deadline: u64,
}

#[derive(Drop, Serde)]
struct DecreaseLiquidityParams {
    token_id: u256,
    liquidity: u128,
    amount0_min: u256,
    amount1_min: u256,
    deadline: u64,
}

#[derive(Drop, Serde)]
struct CollectParams {
    token_id: u256,
    recipient: ContractAddress,
    amount0_max: u256,
    amount1_max: u256,
}

#[derive(Drop, Serde)]
struct Position {
    nonce: u128,
    operator: ContractAddress,
    token0: ContractAddress,
    token1: ContractAddress,
    fee: u32,
    tick_lower: i128,
    tick_upper: i128,
    liquidity: u128,
    fee_growth_inside0_last_x128: u256,
    fee_growth_inside1_last_x128: u256,
    tokens_owed0: u256,
    tokens_owed1: u256,
}
```

**Note:** Exact struct definitions need to be verified from JediSwap's actual interface. This is based on Uniswap V3 pattern which JediSwap V2 follows.

---

### Step 3: Define Ekubo Core Interface

**File**: `contracts/src/interfaces/ekubo_core.cairo`

Based on [Ekubo Core Interfaces documentation](https://docs.ekubo.org/integration-guides/reference/core-interfaces):

```cairo
#[starknet::interface]
pub trait IEkuboCore<TContractState> {
    // Deposit liquidity to a pool
    fn deposit(
        ref self: TContractState,
        pool_key: PoolKey,
        liquidity: u256,
        recipient: ContractAddress,
        sqrt_price_x96: Option<u256>
    ) -> u256;  // Returns position ID
    
    // Withdraw liquidity from a position
    fn withdraw(
        ref self: TContractState,
        position_id: u256,
        liquidity: u256,
        recipient: ContractAddress
    ) -> (u256, u256);  // Returns (amount0, amount1)
    
    // Get position details
    fn get_position(
        self: @TContractState,
        position_id: u256
    ) -> Position;
    
    // Get pool state
    fn get_pool(
        self: @TContractState,
        pool_key: PoolKey
    ) -> PoolState;
}

// Ekubo uses PoolKey to identify pools
#[derive(Drop, Serde)]
struct PoolKey {
    token0: ContractAddress,
    token1: ContractAddress,
    fee: u32,
    tick_spacing: u32,
    extension: felt252,  // Protocol-specific extension
}

#[derive(Drop, Serde)]
struct Position {
    pool_key: PoolKey,
    liquidity: u256,
    fee_growth_inside0_last_x128: u256,
    fee_growth_inside1_last_x128: u256,
    tokens_owed0: u256,
    tokens_owed1: u256,
}

#[derive(Drop, Serde)]
struct PoolState {
    sqrt_price_x96: u256,
    tick: i128,
    fee_growth_global0_x128: u256,
    fee_growth_global1_x128: u256,
    liquidity: u256,
}
```

**Note:** Exact interface needs verification from [Ekubo Core Interfaces docs](https://docs.ekubo.org/integration-guides/reference/core-interfaces).

---

### Step 4: Update StrategyRouter deposit() Function

**Key Changes:**
1. Use NFT Position Manager instead of Swap Router
2. Handle concentrated liquidity (tick ranges for JediSwap)
3. Handle Ekubo pool keys

```cairo
use super::interfaces::jediswap_nft_position_manager::IJediSwapV2NFTPositionManagerDispatcher;
use super::interfaces::ekubo_core::IEkuboCoreDispatcher;

fn deposit(ref self: ContractState, amount: u256) {
    let caller = get_caller_address();
    let contract_addr = get_contract_address();
    let asset_token = self.asset_token.read();
    let eth_token = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7;
    
    // 1. Transfer tokens from user
    let token = IERC20Dispatcher { contract_address: asset_token };
    let success = token.transfer_from(caller, contract_addr, amount);
    assert(success, 'Transfer failed');
    
    // 2. Get allocation
    let jediswap_pct = self.jediswap_allocation.read();
    let ekubo_pct = self.ekubo_allocation.read();
    
    let jediswap_amount = (amount * jediswap_pct) / 10000;
    let ekubo_amount = (amount * ekubo_pct) / 10000;
    
    // 3. Deploy to JediSwap via NFT Position Manager
    if jediswap_amount > 0 {
        let nft_manager = self.jediswap_nft_manager.read();
        let manager = IJediSwapV2NFTPositionManagerDispatcher { 
            contract_address: nft_manager 
        };
        
        // Approve NFT manager
        let approve_success = token.approve(nft_manager, jediswap_amount);
        assert(approve_success, 'JediSwap approval failed');
        
        // For full-range liquidity (simplified - would need proper tick calculation)
        let tick_lower = -887272;  // Min tick
        let tick_upper = 887272;   // Max tick
        let fee = 3000;  // 0.3% fee tier
        
        let mint_params = MintParams {
            token0: asset_token,  // STRK
            token1: eth_token,    // ETH
            fee,
            tick_lower,
            tick_upper,
            amount0_desired: jediswap_amount,
            amount1_desired: 0,  // Would need to calculate based on pool ratio
            amount0_min: jediswap_amount * 95 / 100,  // 5% slippage
            amount1_min: 0,
            recipient: contract_addr,
            deadline: get_block_timestamp() + 3600,
        };
        
        let (token_id, liquidity, amount0, amount1) = manager.mint(mint_params);
        
        // Store position NFT token ID
        let mut positions = self.jediswap_positions.read(caller);
        positions.append(token_id);
        self.jediswap_positions.write(caller, positions);
    }
    
    // 4. Deploy to Ekubo
    if ekubo_amount > 0 {
        let ekubo_core = self.ekubo_core.read();
        let core = IEkuboCoreDispatcher { contract_address: ekubo_core };
        
        // Approve Ekubo
        let approve_success = token.approve(ekubo_core, ekubo_amount);
        assert(approve_success, 'Ekubo approval failed');
        
        // Create pool key for STRK/ETH pool
        let pool_key = PoolKey {
            token0: asset_token,  // STRK
            token1: eth_token,    // ETH
            fee: 3000,  // 0.3% fee
            tick_spacing: 60,
            extension: 0,  // Would need to check Ekubo docs for extension
        };
        
        // Deposit liquidity
        let position_id = core.deposit(
            pool_key,
            ekubo_amount,
            contract_addr,
            Option::None  // Let Ekubo determine price
        );
        
        // Store position ID
        let mut positions = self.ekubo_positions.read(caller);
        positions.append(position_id);
        self.ekubo_positions.write(caller, positions);
    }
    
    // 5. Update total deposits
    let total = self.total_deposits.read();
    self.total_deposits.write(total + amount);
    
    self.emit(Deposit {
        user: caller,
        amount,
        timestamp: get_block_timestamp(),
    });
}
```

---

## Critical Research Items

1. **JediSwap NFT Position Manager:**
   - ✅ Address: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`
   - ❓ Exact `mint()` function signature
   - ❓ How to calculate tick ranges for full-range liquidity
   - ❓ How to handle single-sided vs dual-sided deposits

2. **Ekubo Core:**
   - ✅ Address: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
   - ❓ Exact `deposit()` function signature
   - ❓ How to construct PoolKey correctly
   - ❓ What is the `extension` field in PoolKey?

3. **Token Pairs:**
   - ✅ STRK: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`
   - ✅ ETH: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`
   - ❓ Do STRK/ETH pools exist on both protocols?
   - ❓ What fee tiers are available?

---

## Next Steps

1. **Verify Interfaces:**
   - Check [JediSwap NFT Position Manager docs](https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_nft_position_manager) for exact function signatures
   - Check [Ekubo Core Interfaces](https://docs.ekubo.org/integration-guides/reference/core-interfaces) for exact function signatures

2. **Update Contract Storage:**
   - Change `jediswap_router` to `jediswap_nft_manager`
   - Add position tracking storage

3. **Implement deposit():**
   - Add JediSwap NFT Position Manager integration
   - Add Ekubo Core integration
   - Handle position tracking

4. **Test on Sepolia:**
   - Deploy updated contract
   - Test with small amounts
   - Verify positions are created

---

## References

- [JediSwap V2 Factory](https://docs.jediswap.xyz/for-developers/jediswap-v2/core/jediswap_v2_factory)
- [JediSwap V2 Swap Router](https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_swap_router)
- [JediSwap V2 Contract Addresses](https://docs.jediswap.xyz/for-developers/jediswap-v2/contract-addresses)
- [Ekubo Core Interfaces](https://docs.ekubo.org/integration-guides/reference/core-interfaces)
- [Ekubo Contract Addresses](https://docs.ekubo.org/integration-guides/reference/contract-addresses)
- [Starknet Sepolia Chain Info](https://docs.starknet.io/learn/cheatsheets/chain-info#sepolia)


