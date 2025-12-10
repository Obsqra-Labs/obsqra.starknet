# Yield Implementation Plan

## Current Status

The `accrue_yields()` function exists in the contract but is a placeholder:

```cairo
fn accrue_yields(ref self: ContractState) -> u256 {
    // TODO: Query actual yields from protocols
    // For now, return 0
    let total_yield = 0_u256;
    
    self.emit(YieldsAccrued {
        total_yield,
        timestamp: get_block_timestamp(),
    });
    
    total_yield
}
```

## What We Need to Implement

### 1. Collect Fees from JediSwap Positions

**JediSwap NFT Position Manager** exposes:
- `collect()` - Collect fees from a position
- `positions()` - Get position details including `tokens_owed0` and `tokens_owed1`

**Implementation Steps:**
1. Track NFT position IDs (currently we only track counts)
2. For each position, call `collect()` to claim fees
3. Sum up collected fees in both tokens
4. Convert to STRK if needed (or keep as ETH)

**Code Structure:**
```cairo
// Store position IDs
#[storage]
struct Storage {
    jediswap_positions: Map<u256, u256>, // position_id -> deposit_amount
}

fn collect_jediswap_fees(ref self: ContractState) -> (u256, u256) {
    let nft_manager = self.jediswap_nft_manager.read();
    let mut total_fees_0 = 0_u256;
    let mut total_fees_1 = 0_u256;
    
    // Iterate through positions and collect fees
    // For each position_id:
    //   let (amount0, amount1) = nft_manager.collect(CollectParams { ... });
    //   total_fees_0 += amount0;
    //   total_fees_1 += amount1;
    
    (total_fees_0, total_fees_1)
}
```

### 2. Collect Fees from Ekubo Positions

**Ekubo Positions** contract exposes:
- `collect()` - Collect fees from a position
- Position details include accumulated fees

**Implementation Steps:**
1. Track Ekubo position IDs
2. For each position, call `collect()` to claim fees
3. Sum up collected fees

**Code Structure:**
```cairo
fn collect_ekubo_fees(ref self: ContractState) -> (u256, u256) {
    let ekubo_positions = self.ekubo_positions.read();
    let mut total_fees_0 = 0_u256;
    let mut total_fees_1 = 0_u256;
    
    // Iterate through positions and collect fees
    // Similar to JediSwap but using Ekubo's interface
    
    (total_fees_0, total_fees_1)
}
```

### 3. Update `accrue_yields()` Function

```cairo
fn accrue_yields(ref self: ContractState) -> u256 {
    // Collect fees from both protocols
    let (jedi_fees_0, jedi_fees_1) = self.collect_jediswap_fees();
    let (ekubo_fees_0, ekubo_fees_1) = self.collect_ekubo_fees();
    
    // Convert all fees to STRK (or keep as is and track separately)
    // For now, sum up STRK-equivalent value
    let total_yield = jedi_fees_0 + ekubo_fees_0; // Assuming token0 is STRK
    
    // Update user balances or create yield distribution mechanism
    // Option 1: Add to total TVL
    // Option 2: Distribute to users proportionally
    // Option 3: Store in yield pool for withdrawal
    
    self.emit(YieldsAccrued {
        total_yield,
        timestamp: get_block_timestamp(),
    });
    
    total_yield
}
```

### 4. Yield Distribution Strategy

**Option A: Proportional Distribution**
- Track each user's share of total deposits
- Distribute yields proportionally
- Users can claim their share

**Option B: Reinvestment**
- Automatically reinvest yields back into protocols
- Compound returns
- Users see growth in their position value

**Option C: Hybrid**
- Allow users to choose: claim or reinvest
- Default to reinvestment for compounding

### 5. Frontend Reporting

**What to Display:**
- Total yield accrued (historical)
- Yield per user
- Yield rate (APY calculation)
- Yield history (time series)

**Implementation:**
- Query `accrue_yields()` results
- Track yield events (`YieldsAccrued`)
- Calculate APY based on time and amount
- Display in dashboard

## Implementation Priority

1. **Phase 1: Position Tracking** (Required)
   - Store actual NFT position IDs
   - Map positions to deposits
   - This is needed for everything else

2. **Phase 2: Fee Collection** (Core)
   - Implement `collect_jediswap_fees()`
   - Implement `collect_ekubo_fees()`
   - Update `accrue_yields()` to call both

3. **Phase 3: Yield Distribution** (User-facing)
   - Decide on distribution strategy
   - Implement user yield tracking
   - Add withdrawal/claim mechanism

4. **Phase 4: Reporting** (Analytics)
   - Frontend yield display
   - APY calculations
   - Historical tracking

## Next Steps

1. **Update contract to track position IDs**
   - Modify `deploy_to_protocols()` to store NFT IDs
   - Add storage for position mappings

2. **Implement fee collection functions**
   - Start with JediSwap (simpler interface)
   - Then Ekubo
   - Test on Sepolia

3. **Update `accrue_yields()`**
   - Call collection functions
   - Sum up yields
   - Emit events

4. **Add frontend reporting**
   - Query yield data
   - Display in dashboard
   - Show APY metrics

## Questions to Answer

1. **Distribution Model**: Claim vs Reinvest vs Hybrid?
2. **Frequency**: How often to accrue yields? (Manual call vs automated)
3. **Gas Costs**: Fee collection has gas costs - who pays?
4. **Slippage**: When converting fees to STRK, handle slippage?

## Current Blockers

- Position IDs not stored (only counts)
- Fee collection interfaces need testing
- Distribution strategy not decided

