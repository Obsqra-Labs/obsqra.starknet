# Roadmap: What's Next

## Current Status ✅

**Completed:**
- ✅ Dual protocol integration (JediSwap + Ekubo)
- ✅ STRK deposits and withdrawals
- ✅ Automatic liquidity deployment
- ✅ Allocation management
- ✅ All interface fixes (I32 ticks, fee types, tick alignment)

**Working:**
- ✅ Full `deploy_to_protocols()` flow tested on Sepolia
- ✅ Both protocols receiving liquidity
- ✅ Position creation successful

## Immediate Next Steps (This Week)

### 1. Position Tracking Enhancement
**Priority: High**
- Currently only tracking position counts
- Need to store actual NFT position IDs
- Required for yield collection and position management

**Tasks:**
- Update storage to map position IDs to deposits
- Modify `deploy_to_protocols()` to return and store NFT IDs
- Add getter functions for position queries

### 2. Yield Implementation
**Priority: High**
- `accrue_yields()` function exists but returns 0
- Need to implement actual fee collection
- See `YIELD_IMPLEMENTATION_PLAN.md` for details

**Tasks:**
- Implement `collect_jediswap_fees()`
- Implement `collect_ekubo_fees()`
- Update `accrue_yields()` to call both
- Decide on distribution strategy (claim vs reinvest)

### 3. Frontend Yield Reporting
**Priority: Medium**
- Display yield metrics in dashboard
- Show APY calculations
- Historical yield tracking

**Tasks:**
- Query yield data from contract
- Calculate APY based on time and amount
- Add yield charts/graphs to dashboard
- Show per-user yield breakdown

## Short Term (Next 2-4 Weeks)

### 4. Rebalancing Logic
**Priority: Medium**
- `rebalance()` function exists but needs implementation
- Should adjust positions when allocation changes
- Handle partial withdrawals from positions

**Tasks:**
- Implement position withdrawal logic
- Calculate rebalancing amounts
- Execute rebalancing transactions
- Handle edge cases (insufficient liquidity, etc.)

### 5. Slippage Protection
**Priority: Medium**
- Currently set to 0 (no protection)
- Add configurable slippage tolerance
- Protect users from bad trades

**Tasks:**
- Add slippage parameters to swap functions
- Calculate minimum amounts out
- Validate against slippage limits
- Add frontend slippage settings

### 6. Position Management UI
**Priority: Low**
- View active positions
- See position performance
- Manual position management options

**Tasks:**
- Query position details from protocols
- Display position info (tokens, range, fees earned)
- Add position management actions

## Medium Term (1-3 Months)

### 7. Multi-Asset Support
**Priority: Medium**
- Currently STRK-only deposits
- Support ETH deposits
- Support other tokens

**Tasks:**
- Update deposit function to accept multiple tokens
- Handle token conversions/swaps
- Update allocation logic for multi-asset

### 8. Risk Engine Integration
**Priority: High**
- Risk engine contract exists but not fully integrated
- Should control allocations based on risk signals
- Dynamic rebalancing based on risk

**Tasks:**
- Integrate risk engine calls
- Implement risk-based allocation updates
- Add risk metrics to frontend

### 9. DAO Governance
**Priority: Medium**
- DAO manager contract exists
- Should control allocation decisions
- Voting on strategy changes

**Tasks:**
- Integrate DAO voting mechanism
- Allow DAO to update allocations
- Display governance proposals in frontend

### 10. Additional Protocol Support
**Priority: Low**
- Add support for more DEXs
- Add lending protocol support
- Diversify yield sources

**Tasks:**
- Research additional protocols
- Implement new protocol interfaces
- Update allocation system for multiple protocols

## Long Term (3-6 Months)

### 11. Automated Yield Accrual
**Priority: Medium**
- Currently manual `accrue_yields()` call
- Automate via keeper/relayer
- Regular fee collection and distribution

**Tasks:**
- Set up keeper infrastructure
- Schedule regular yield accrual
- Handle gas costs

### 12. Advanced Strategies
**Priority: Low**
- Concentrated liquidity strategies
- Dynamic range adjustment
- Yield optimization algorithms

**Tasks:**
- Research optimal liquidity ranges
- Implement range adjustment logic
- Test different strategies

### 13. Analytics & Reporting
**Priority: Medium**
- Comprehensive analytics dashboard
- Performance metrics
- Risk analysis

**Tasks:**
- Build analytics backend
- Create reporting UI
- Historical data tracking

## Technical Debt

### Code Quality
- [ ] Add comprehensive tests
- [ ] Improve error handling
- [ ] Add documentation comments
- [ ] Refactor duplicate code

### Security
- [ ] Security audit
- [ ] Formal verification (if needed)
- [ ] Bug bounty program

### Performance
- [ ] Gas optimization
- [ ] Batch operations where possible
- [ ] Caching strategies

## Questions to Resolve

1. **Yield Distribution**: Claim vs Reinvest vs Hybrid?
2. **Rebalancing Frequency**: How often should positions be rebalanced?
3. **Gas Costs**: Who pays for yield accrual and rebalancing?
4. **Multi-Asset Priority**: Which tokens to support first?
5. **Risk Engine**: What risk signals should trigger rebalancing?

## Success Metrics

**Short Term:**
- Position IDs tracked and queryable
- Yield collection working
- Frontend showing yield metrics

**Medium Term:**
- Rebalancing functional
- Risk engine integrated
- DAO governance active

**Long Term:**
- Automated yield accrual
- Multiple protocols supported
- Strong analytics and reporting

---

*This roadmap is a living document and will be updated as priorities shift and new requirements emerge.*

