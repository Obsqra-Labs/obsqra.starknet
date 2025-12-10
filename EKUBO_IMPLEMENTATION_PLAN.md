# Ekubo Implementation Plan

## 🔍 Discovery

From [Ekubo documentation](https://docs.ekubo.org/integration-guides/till-pattern), Ekubo uses a **lock/callback pattern**, not direct function calls.

### How Ekubo Works

1. **Call `lock()`** on Ekubo Core with your contract address
2. **Ekubo calls back** to your contract's `locked()` function
3. **Within `locked()`**, you:
   - Call `pay()` to send tokens to Ekubo
   - Call `update_position()` to add/remove liquidity
   - Call `withdraw()` to receive tokens from Ekubo

### Why Our Direct Call Failed

Our original approach:
```cairo
ekubo.deposit_liquidity(token0, token1, amount0, amount1, fee)
```

**This function doesn't exist!** That's why we got `ENTRYPOINT_NOT_FOUND`.

## ✅ Updated Interface

The interface has been updated to reflect Ekubo's actual architecture:

```cairo
pub trait IEkuboCore<TContractState> {
    fn lock(ref self: TContractState, locker: ContractAddress, data: Span<felt252>);
    fn pay(ref self: TContractState, token: ContractAddress, amount: u256);
    fn withdraw(ref self: TContractState, token: ContractAddress, amount: u256, recipient: ContractAddress);
    fn update_position(...) -> (u256, u256);
}
```

## 📋 Implementation Steps

### Step 1: Implement ILocker Interface

Add to `strategy_router_v2.cairo`:

```cairo
use super::super::interfaces::ekubo::ILocker;

#[external(v0)]
fn locked(
    ref self: ContractState,
    core: ContractAddress,
    data: Span<felt252>
) {
    // This is called by Ekubo Core after we call lock()
    // Here we execute the actual liquidity operations
    
    let ekubo = IEkuboCoreDispatcher { contract_address: core };
    let asset_token = self.asset_token.read();
    let strk_token = ...;
    
    // Pay tokens to Ekubo
    ekubo.pay(asset_token, amount_eth);
    ekubo.pay(strk_token, amount_strk);
    
    // Update position (add liquidity)
    let fee: u128 = 3000;
    let tick_lower: i128 = -887272; // Full range
    let tick_upper: i128 = 887272;  // Full range
    let liquidity_delta: i256 = ...; // Calculate based on amounts
    let (amount0, amount1) = ekubo.update_position(
        asset_token,
        strk_token,
        fee,
        tick_lower,
        tick_upper,
        liquidity_delta
    );
}
```

### Step 2: Update deploy_to_protocols()

Replace the direct `deposit_liquidity()` call with:

```cairo
let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
let contract_addr = get_contract_address();
ekubo.lock(contract_addr, array![]); // This triggers locked() callback
```

### Step 3: Handle Token Approvals

Before calling `lock()`, approve Ekubo Core to spend tokens:
```cairo
eth_token_erc20.approve(ekubo_core, amount_eth);
strk_token_erc20.approve(ekubo_core, amount_strk);
```

## 🚧 Current Status

- ✅ Interface updated to reflect Ekubo's architecture
- ✅ Contract compiles (Ekubo calls commented out)
- ⏳ Need to implement `locked()` callback
- ⏳ Need to calculate `liquidity_delta` correctly
- ⏳ Need to handle tick ranges properly

## 📚 Resources

- [Ekubo Till Pattern](https://docs.ekubo.org/integration-guides/till-pattern)
- [Ekubo Swapping Guide](https://docs.ekubo.org/integration-guides/swapping)
- [Ekubo Core Interfaces](https://docs.ekubo.org/integration-guides/reference/core-interfaces)
- [Ekubo Contract Addresses](https://docs.ekubo.org/integration-guides/reference/contract-addresses)

## 💡 Alternative: Use Ekubo Router

If the callback pattern is too complex, consider using Ekubo Router contracts which might have simpler interfaces:
- Router V3.0.13 (Sepolia): `0x0045f933adf0607292468ad1c1dedaa74d5ad166392590e72676a34d01d7b763`

