# APY Tracking Explained

## Understanding APY in DeFi

### Key Concepts

1. **Projected APY** (What the protocol offers):
   - This is the APY rate that the protocol is currently offering
   - Comes from existing trading activity in the pools (other users trading)
   - We DON'T need to generate trading - the APY is what the protocol offers based on current pool activity
   - Source: DefiLlama API or protocol contracts

2. **Actual APY** (What we're earning):
   - This is calculated from fees we've actually collected
   - Formula: `APY = (fees_collected / tvl) * (365 / days_elapsed) * 100`
   - Requires tracking yield accrual over time
   - More accurate but takes time to calculate (needs historical data)

### How Fees Work

**JediSwap (Concentrated Liquidity)**:
- Fees accumulate as `tokens_owed0` and `tokens_owed1` in the position
- Fees come from trading activity (other users swapping)
- We can query `positions(token_id)` to see pending fees without collecting
- Fees are collected when we call `collect()` or `accrue_yields()`

**Ekubo (Concentrated Liquidity)**:
- Fees are collected via `collect_fees()` in the `locked()` callback
- Fees accumulate in the pool and are collected on-demand
- We track collected fees in `ekubo_collected_fees_0`

### Why Yield Might Be 0

1. **Positions are new**: Fees accumulate over time as traders use the pools
2. **No trading activity**: If no one is trading in the pools, no fees are generated
3. **Fees not collected yet**: Fees exist but haven't been collected via `accrue_yields()`

### How to Track Actual Earnings

1. **Query pending fees** (without collecting):
   - Call `get_pending_fees()` to see fees available
   - This queries `positions()` for JediSwap and estimates Ekubo fees

2. **Track yield accrual**:
   - Store `first_yield_timestamp` when first yield is accrued
   - Store `last_yield_timestamp` on each accrual
   - Calculate actual APY: `(total_yield / tvl) * (365 / days_since_first_yield) * 100`

3. **Display both metrics**:
   - **Projected APY**: What the protocol offers (from DefiLlama)
   - **Actual APY**: What we're earning (from on-chain data)

### Starknet-Specific Advantages

- **Direct on-chain queries**: We can query protocol contracts directly for fee data
- **Position tracking**: We can track position values and fees over time
- **Event-based tracking**: We can use events to track yield accrual
- **No need for external APIs**: Everything is on-chain

## Implementation Plan

1. ✅ Add `get_pending_fees()` to query fees without collecting
2. ✅ Add `get_yield_timestamps()` to track yield accrual timeline
3. ✅ Update `accrue_yields()` to track timestamps
4. ✅ Frontend: Show both projected and actual APY
5. ✅ Calculate actual APY from on-chain data

## Testing

- **Projected APY**: Should show current protocol rates (from DefiLlama)
- **Actual APY**: Will be 0 initially, increases as fees are collected
- **Pending Fees**: Query to see fees available before collecting

