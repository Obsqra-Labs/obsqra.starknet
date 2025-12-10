# Deep Dive: JediSwap and Ekubo Integration Architecture

*A technical deep dive into how we integrated two fundamentally different DEX protocols on Starknet*

---

## Introduction

When we set out to build a unified liquidity strategy router, we knew we'd need to integrate with multiple protocols. What we didn't realize was how fundamentally different each protocol's architecture would be.

JediSwap and Ekubo are both excellent DEXs on Starknet, but they approach liquidity provision in completely different ways. This post dives deep into those differences and how we bridged them.

---

## Part 1: JediSwap V2 Integration

### Architecture Overview

JediSwap V2 follows the Uniswap V3 model:
- **Concentrated Liquidity**: Liquidity providers choose price ranges (ticks)
- **NFT Positions**: Each position is an NFT, allowing for granular management
- **Router Pattern**: Separate router contract for swaps, NFT manager for liquidity

### The Components

**1. Swap Router (`0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`)**

The V2 Swap Router uses `exact_input_single()` for single-hop swaps:

```cairo
fn exact_input_single(
    params: ExactInputSingleParams
) -> u256; // Returns amount_out
```

**Key Parameters:**
- `fee: u32` - **Critical**: Not `u128`! This caused us hours of debugging
- `amount_in: u256` - Input amount (split into low/high)
- `amount_out_minimum: u256` - Slippage protection

**2. NFT Position Manager (`0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`)**

This is where liquidity is added. The `mint()` function takes a `MintParams` struct:

```cairo
struct MintParams {
    token0: ContractAddress,
    token1: ContractAddress,
    fee: u32,
    tick_lower: I32,  // Custom struct!
    tick_upper: I32,  // Custom struct!
    amount0_desired: u256,
    amount1_desired: u256,
    amount0_min: u256,
    amount1_min: u256,
    recipient: ContractAddress,
    deadline: u64,
}
```

### The I32 Struct Problem

This was our biggest challenge. JediSwap doesn't use plain integers for ticks. They use a custom struct:

```cairo
struct I32 {
    mag: u32,   // Magnitude (absolute value)
    sign: bool, // true for negative numbers
}
```

**Why?** Cairo's type system. Negative numbers need special handling. The struct allows explicit sign representation.

**The Error**: `Failed to deserialize param #1`

This happened because we were passing `i128` values directly. The ABI expected the struct format.

**The Fix**:
```cairo
let tick_lower_mag: u32 = 887200; // Aligned to tick spacing
let tick_lower_sign: bool = true; // Negative
let tick_lower_i32 = I32 { mag: tick_lower_mag, sign: tick_lower_sign };
```

### Tick Alignment

Ticks must be multiples of the tick spacing:
- **0.05% fee tier**: Tick spacing = 10
- **0.3% fee tier**: Tick spacing = 60
- **1% fee tier**: Tick spacing = 200

We use full-range liquidity (-887200 to 887200), which is aligned to the 200 tick spacing for 1% pools.

### Our Integration Flow

1. **Swap**: Half STRK → ETH via router
2. **Approve**: Both tokens to NFT Position Manager
3. **Mint**: Create position with both tokens
4. **Track**: Store NFT ID for future management

---

## Part 2: Ekubo Integration

### Architecture Overview

Ekubo is fundamentally different. It uses a **lock/callback pattern**:
- No direct function calls for liquidity provision
- You "lock" the core contract
- Core calls back to your contract's `locked()` function
- Within the callback, you can `pay()`, `withdraw()`, and `update_position()`

### The Components

**1. Ekubo Core (`0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`)**

The core contract exposes:
```cairo
fn lock(ref self: TContractState, data: Span<felt252>) -> Span<felt252>;
```

This triggers a callback to your contract.

**2. Ekubo Positions (`0x06a2aee84bb0ed5dded4384ddd0e40e9c1372b818668375ab8e3ec08807417e5`)**

**This is what we actually use!** The Positions contract abstracts away the lock/callback complexity:

```cairo
fn mint_and_deposit(
    pool_key: PoolKey,
    bounds: Bounds,
    min_liquidity: u128
) -> (u64, u128); // Returns (token_id, liquidity)
```

Much simpler. The Positions contract handles the lock pattern internally.

### The PoolKey Structure

```cairo
struct PoolKey {
    token0: ContractAddress,
    token1: ContractAddress,
    fee: u128,
    tick_spacing: u128,
    extension: ContractAddress,
}
```

**Note**: Tokens must be sorted (token0 < token1 by address).

### The Bounds Structure

```cairo
struct Bounds {
    lower: i129, // Custom signed integer
    upper: i129,
}
```

Ekubo uses `i129` (which we alias to `i128`). Similar to JediSwap's I32, but different format.

### Our Integration Flow

1. **Swap**: Half STRK → ETH (via JediSwap router)
2. **Approve**: Both tokens to Ekubo Positions
3. **Mint & Deposit**: Single call to `mint_and_deposit()`
4. **Track**: Store position ID

---

## Part 3: The Unified Strategy Router

### How We Bridge the Differences

Our `deploy_to_protocols()` function handles both:

```cairo
fn deploy_to_protocols(ref self: ContractState) {
    // 1. Calculate allocations
    let jediswap_amount = (pending * jediswap_pct) / 10000;
    let ekubo_amount = (pending * ekubo_pct) / 10000;
    
    // 2. Deploy to JediSwap
    // - Swap half STRK → ETH
    // - Add liquidity via NFT Manager
    // - Store position NFT ID
    
    // 3. Deploy to Ekubo
    // - Swap half STRK → ETH
    // - Add liquidity via Positions
    // - Store position ID
}
```

### Key Design Decisions

**1. Separate Swap Steps**

We swap separately for each protocol. This gives us:
- Better control over slippage
- Ability to use different swap routes if needed
- Clearer error handling

**2. Position Tracking**

We store position IDs (simplified as counts for now):
- `jediswap_position_count`: Number of JediSwap positions
- `ekubo_position_count`: Number of Ekubo positions

Future: Store actual NFT IDs for granular management.

**3. Allocation Flexibility**

Allocations are configurable via `update_allocation()`:
- Can be 50/50, 70/30, 100/0, etc.
- Enforced by risk engine and DAO
- Emits events for transparency

---

## Part 4: What This Means for Starknet

### Composability

Our router is itself composable. Other protocols can:
- Deposit to our router
- Build on top of our allocation logic
- Create new financial primitives

### Liquidity Depth

By routing capital to both protocols, we:
- Increase liquidity depth across the ecosystem
- Reduce slippage for all users
- Create more efficient markets

### Innovation

We're proving that:
- Complex multi-protocol strategies can be trustless
- Different protocol architectures can be unified
- On-chain DeFi can be as sophisticated as off-chain

### The Future

**Yield Accrual**: We're working on automatically collecting fees from positions and distributing them to users.

**Rebalancing**: Dynamic allocation based on:
- Performance metrics
- Risk signals
- DAO governance decisions

**More Protocols**: Adding support for:
- Additional DEXs
- Lending protocols
- Yield aggregators

---

## Technical Takeaways

1. **Read the Docs**: Each protocol has unique patterns. JediSwap's I32 struct, Ekubo's lock/callback—these aren't obvious.

2. **Test Incrementally**: We tested each protocol separately before combining them.

3. **Handle Errors Gracefully**: "Failed to deserialize param #1" led us to the I32 struct. "Tick misaligned" led us to alignment requirements.

4. **Abstract Complexity**: The Positions contract abstracts Ekubo's complexity. We abstract both protocols' complexity for users.

5. **Plan for Growth**: Our architecture supports adding more protocols without major refactoring.

---

## Conclusion

Integrating JediSwap and Ekubo wasn't just about calling functions. It was about understanding fundamentally different architectures and creating a unified interface.

The result? A single contract that lets users deposit STRK and automatically deploy it across multiple protocols. No manual management. No complexity. Just yield.

And we're just getting started.

---

*For technical details, see our contract source code and integration tests.*

