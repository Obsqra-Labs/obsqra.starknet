# The Journey: Integrating Dual Protocol Liquidity on Starknet

*How we built a unified strategy router that seamlessly deploys capital across JediSwap and Ekubo*

---

## The Vision

Imagine you're a DeFi user on Starknet. You've got some STRK tokens sitting in your wallet, and you want to earn yield. But here's the thing—you don't want to manually manage positions across multiple protocols. You don't want to constantly rebalance. You just want to deposit and let the protocol handle the complexity.

That's what we built. A single contract that accepts your STRK, intelligently splits it between JediSwap and Ekubo, and manages the entire liquidity provision process for you.

## The Challenge

Starknet's DeFi ecosystem is growing, but it's fragmented. Each protocol has its own interface, its own quirks, its own way of doing things. JediSwap uses NFT-based positions. Ekubo uses a lock/callback pattern. They're both great, but they're different.

We wanted to abstract away that complexity. One deposit. Multiple protocols. Automatic allocation.

## The Architecture

Our Strategy Router is simple in concept but sophisticated in execution:

1. **Deposit**: Users send STRK to the contract
2. **Allocation**: The contract splits funds based on configured percentages (default: 50/50)
3. **Deployment**: Funds are automatically deployed to both protocols
4. **Management**: Positions are tracked, yields accrue, and users can withdraw anytime

But here's where it gets interesting...

## The Technical Journey

### Step 1: Understanding the Protocols

**JediSwap V2** uses a familiar Uniswap V3-style approach:
- NFT Position Manager for concentrated liquidity
- Router for swaps
- Full-range or custom tick ranges

**Ekubo** is different:
- Lock/callback pattern (no direct function calls)
- Positions contract handles the complexity
- Requires understanding of their unique architecture

We had to learn both. Deeply.

### Step 2: The Swap Problem

Both protocols need STRK/ETH pairs for liquidity. But users deposit STRK. So we need to:
1. Swap half the STRK to ETH
2. Deploy both tokens to each protocol

The JediSwap V2 router uses `exact_input_single()` with a specific parameter structure. The fee parameter? It's `u32`, not `u128`. That took us a while to figure out.

### Step 3: The Tick Problem

JediSwap's NFT Position Manager uses a custom `i32` struct for ticks:
```cairo
struct I32 {
    mag: u32,
    sign: bool,  // true for negative
}
```

Not a plain integer. A struct. That was the "Failed to deserialize param #1" error that haunted us for hours.

### Step 4: The Alignment Problem

Even after we got the struct right, ticks must be aligned to the tick spacing. For a 1% fee tier, that's multiples of 200. Our initial ticks (887272) weren't aligned. We needed 887200.

### Step 5: The Integration

Once we solved all the interface issues, the integration became straightforward:
- Swap STRK → ETH via JediSwap router
- Add liquidity to JediSwap via NFT Position Manager
- Add liquidity to Ekubo via Positions contract

All in a single transaction.

## What This Means

### For Users

**Simplicity**: One deposit, multiple protocols. No need to understand the intricacies of each.

**Diversification**: Capital is automatically split across protocols, reducing risk.

**Yield Optimization**: The contract can rebalance based on performance, risk signals, or DAO decisions.

### For the Ecosystem

**Liquidity**: More capital flowing into both protocols means deeper liquidity for everyone.

**Composability**: Other protocols can build on top of our router, creating new financial primitives.

**Innovation**: We're proving that complex multi-protocol strategies can be trustless and on-chain.

## The Future

This is just the beginning. We're working on:

- **Yield Accrual**: Automatically collecting and compounding fees from positions
- **Rebalancing**: Dynamic allocation based on performance metrics
- **More Protocols**: Adding support for additional DEXs and yield sources
- **Risk Management**: Integration with our risk engine for automated position adjustments

## The Takeaway

Building on Starknet is different. The protocols are different. The patterns are different. But that's what makes it exciting. We're not just copying EVM patterns—we're building something new.

The dual protocol integration wasn't just a technical achievement. It was a proof of concept that complex DeFi strategies can be built trustlessly on Starknet, abstracting away complexity while maintaining transparency and control.

---

*This is the story of how we made it work. The errors, the fixes, the "aha" moments. And it's just the beginning.*

