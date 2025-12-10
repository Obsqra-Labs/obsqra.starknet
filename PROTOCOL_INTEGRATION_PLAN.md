# Protocol Integration Implementation Plan

## Current State ✅

**Protocol Addresses (Already Integrated):**
- ✅ JediSwap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- ✅ Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
- ✅ STRK Token: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`
- ✅ ETH Token: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`

**What's Stored:**
- Addresses are in StrategyRouter contract storage
- Can be read via `self.jediswap_router.read()` and `self.ekubo_core.read()`
- Contract has `get_protocol_addresses()` function that returns them

**What's Missing:**
- ❌ Actual calls to protocol contracts
- ❌ Interface dispatchers (IJediSwapRouterDispatcher, IEkuboCoreDispatcher)
- ❌ Liquidity provision logic
- ❌ Position tracking

---

## Implementation Steps

### Step 1: Define Protocol Interfaces

**File**: `contracts/src/interfaces/jediswap_router.cairo`

```cairo
#[starknet::interface]
pub trait IJediSwapRouter<TContractState> {
    fn add_liquidity(
        ref self: TContractState,
        token_a: ContractAddress,
        token_b: ContractAddress,
        amount_a: u256,
        amount_b: u256,
        min_amount_a: u256,
        min_amount_b: u256,
        to: ContractAddress,
        deadline: u64
    ) -> (u256, u256);
    
    fn remove_liquidity(
        ref self: TContractState,
        token_a: ContractAddress,
        token_b: ContractAddress,
        liquidity: u256,
        min_amount_a: u256,
        min_amount_b: u256,
        to: ContractAddress,
        deadline: u64
    ) -> (u256, u256);
    
    fn get_pair_address(
        self: @TContractState,
        token_a: ContractAddress,
        token_b: ContractAddress
    ) -> ContractAddress;
}
```

**File**: `contracts/src/interfaces/ekubo_core.cairo`

```cairo
#[starknet::interface]
pub trait IEkuboCore<TContractState> {
    fn deposit_liquidity(
        ref self: TContractState,
        pool_key: felt252,  // Pool identifier
        liquidity: u256,
        recipient: ContractAddress
    ) -> u256;  // Returns position ID
    
    fn withdraw_liquidity(
        ref self: TContractState,
        position_id: u256,
        liquidity: u256,
        recipient: ContractAddress
    ) -> u256;
    
    fn get_position_value(
        self: @TContractState,
        position_id: u256
    ) -> u256;
}
```

---

### Step 2: Update StrategyRouter deposit() Function

**File**: `contracts/src/strategy_router_v2.cairo`

```cairo
use super::interfaces::jediswap_router::IJediSwapRouterDispatcher;
use super::interfaces::ekubo_core::IEkuboCoreDispatcher;

// Add to Storage struct:
#[storage]
struct Storage {
    // ... existing storage ...
    
    // Position tracking
    jediswap_lp_tokens: Map<ContractAddress, u256>,  // user -> LP token balance
    ekubo_positions: Map<ContractAddress, Span<u256>>,  // user -> position IDs
}

fn deposit(ref self: ContractState, amount: u256) {
    let caller = get_caller_address();
    let contract_addr = get_contract_address();
    let asset_token = self.asset_token.read();
    
    // 1. Transfer tokens from user to this contract
    let token = IERC20Dispatcher { contract_address: asset_token };
    let success = token.transfer_from(caller, contract_addr, amount);
    assert(success, 'Transfer failed');
    
    // 2. Get current allocation
    let jediswap_pct = self.jediswap_allocation.read();
    let ekubo_pct = self.ekubo_allocation.read();
    
    // 3. Calculate amounts for each protocol
    let jediswap_amount = (amount * jediswap_pct) / 10000;
    let ekubo_amount = (amount * ekubo_pct) / 10000;
    
    // 4. Deploy to JediSwap
    if jediswap_amount > 0 {
        let jediswap_router = self.jediswap_router.read();
        let router = IJediSwapRouterDispatcher { contract_address: jediswap_router };
        
        // Approve router to spend STRK
        let approve_success = token.approve(jediswap_router, jediswap_amount);
        assert(approve_success, 'JediSwap approval failed');
        
        // Get ETH token address (for STRK/ETH pair)
        let eth_token = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7;
        
        // Add liquidity (STRK/ETH pair)
        // Note: This is simplified - real implementation needs to handle pair ratios
        let (amount_a, amount_b) = router.add_liquidity(
            asset_token,  // token_a (STRK)
            eth_token,    // token_b (ETH)
            jediswap_amount,  // amount_a
            0,  // amount_b (would need to calculate based on pool ratio)
            jediswap_amount * 95 / 100,  // min_amount_a (5% slippage)
            0,  // min_amount_b
            contract_addr,  // to (this contract)
            get_block_timestamp() + 3600  // deadline (1 hour)
        );
        
        // Store LP token balance (simplified - would need to track LP tokens)
        let current_lp = self.jediswap_lp_tokens.read(caller);
        self.jediswap_lp_tokens.write(caller, current_lp + amount_a);
    }
    
    // 5. Deploy to Ekubo
    if ekubo_amount > 0 {
        let ekubo_core = self.ekubo_core.read();
        let core = IEkuboCoreDispatcher { contract_address: ekubo_core };
        
        // Approve core to spend STRK
        let approve_success = token.approve(ekubo_core, ekubo_amount);
        assert(approve_success, 'Ekubo approval failed');
        
        // Get pool key (would need to determine from token pair)
        // For STRK/ETH pool, this would be calculated from token addresses
        let pool_key = calculate_pool_key(asset_token, eth_token);
        
        // Deposit liquidity
        let position_id = core.deposit_liquidity(
            pool_key,
            ekubo_amount,
            contract_addr  // recipient (this contract)
        );
        
        // Store position ID
        let mut positions = self.ekubo_positions.read(caller);
        positions.append(position_id);
        self.ekubo_positions.write(caller, positions);
    }
    
    // 6. Update total deposits
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

### Step 3: Implement Position Value Queries

**For Yield Accrual:**

```cairo
fn accrue_yields(ref self: ContractState) -> u256 {
    let total_yield = 0_u256;
    
    // Query JediSwap positions
    // (Would need to iterate user positions and query LP token values)
    
    // Query Ekubo positions
    // (Would need to iterate user positions and query position values)
    
    // Calculate: current_value - deposited_value = yield
    
    self.emit(YieldsAccrued {
        total_yield,
        timestamp: get_block_timestamp(),
    });
    
    total_yield
}
```

---

### Step 4: Implement Withdrawal

```cairo
fn withdraw(ref self: ContractState, amount: u256) -> u256 {
    let caller = get_caller_address();
    let total = self.total_deposits.read();
    
    assert(total >= amount, 'Insufficient balance');
    
    // Calculate proportional withdrawal
    let jediswap_pct = self.jediswap_allocation.read();
    let ekubo_pct = self.ekubo_allocation.read();
    
    let jediswap_withdraw = (amount * jediswap_pct) / 10000;
    let ekubo_withdraw = (amount * ekubo_pct) / 10000;
    
    // Withdraw from JediSwap
    if jediswap_withdraw > 0 {
        let jediswap_router = self.jediswap_router.read();
        let router = IJediSwapRouterDispatcher { contract_address: jediswap_router };
        
        // Remove liquidity
        // (Would need to calculate LP tokens to remove)
        // router.remove_liquidity(...);
    }
    
    // Withdraw from Ekubo
    if ekubo_withdraw > 0 {
        let ekubo_core = self.ekubo_core.read();
        let core = IEkuboCoreDispatcher { contract_address: ekubo_core };
        
        // Withdraw liquidity
        // (Would need to determine which position to withdraw from)
        // core.withdraw_liquidity(...);
    }
    
    // Transfer STRK to user
    let asset_token = self.asset_token.read();
    let token = IERC20Dispatcher { contract_address: asset_token };
    let success = token.transfer(caller, amount);
    assert(success, 'Transfer failed');
    
    // Update total deposits
    self.total_deposits.write(total - amount);
    
    self.emit(Withdrawal {
        user: caller,
        amount,
        yield_amount: 0,  // Would calculate actual yield
        timestamp: get_block_timestamp(),
    });
    
    amount
}
```

---

## Research Needed

1. **JediSwap Router Interface:**
   - Exact function signatures
   - How to handle pair ratios
   - LP token tracking

2. **Ekubo Core Interface:**
   - Pool key calculation
   - Position ID management
   - Liquidity withdrawal mechanics

3. **Token Pair Handling:**
   - STRK/ETH pair addresses
   - How to handle single-sided vs dual-sided liquidity
   - Slippage calculations

4. **Position Tracking:**
   - How to track LP tokens per user
   - How to track Ekubo positions per user
   - How to calculate position values

---

## Testing Strategy

1. **Unit Tests:**
   - Test deposit with 50/50 allocation
   - Test deposit with 100/0 allocation
   - Test withdrawal calculations

2. **Integration Tests:**
   - Deploy to Sepolia testnet
   - Test with small amounts (0.1 STRK)
   - Verify funds actually go to protocols
   - Verify position tracking works

3. **Yield Tests:**
   - Wait for some time
   - Query position values
   - Verify yield calculation

---

## Timeline

- **Week 1:** Research protocol interfaces, implement deposit()
- **Week 2:** Implement withdrawal, position tracking
- **Week 3:** Implement yield accrual, testing
- **Week 4:** Bug fixes, optimization, documentation

**Total: 4 weeks to fully functional protocol integration**


