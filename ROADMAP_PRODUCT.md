# Product Roadmap - Privacy Pool with Verifiable AI

## Vision

**Lightweight privacy pool where yield optimization is cryptographically proven**

Users deposit → Shared pool → AI optimizes across protocols → Prove every decision → Track real performance

**Not**: Standalone AI prover  
**Is**: Privacy-preserving yield aggregator with verifiable optimization

---

## Current State (V1.2)

**What Works**:
- Risk scoring (5-component model)
- Proof generation (2-3s)
- On-chain contracts (RiskEngine, StrategyRouter)
- Backend execution
- Demo frontend

**What's Missing**:
- Shared pool contract
- Real deposits/withdrawals
- Performance tracking (on-chain results)
- Proof visibility in UX
- Privacy layer (MIST integration)

**The Gap**: Users can't actually use it. It's a demo, not a product.

---

## V1.3: Demonstrable Product (3-4 weeks)

**Goal**: Lightweight privacy pool that works end-to-end

### Core Product Flow

```
1. User deposits USDC
   ↓
2. Joins shared pool
   ↓
3. AI analyzes protocols (Jedi, Ekubo)
   ↓
4. Generates STARK proof of optimization
   ↓
5. Executes rebalance (on-chain)
   ↓
6. Tracks performance (APY, gains)
   ↓
7. User withdraws + yield
```

**Every step cryptographically proven and visible in UI**

---

## V1.3 Architecture

### Smart Contracts (New)

```cairo
// 1. SharedPool.cairo - Lightweight privacy pool
contract SharedPool {
    // Deposits
    fn deposit(amount: u256) -> u256 { /* returns shares */ }
    
    // Withdrawals
    fn withdraw(shares: u256) -> u256 { /* returns amount */ }
    
    // Total value
    fn total_value() -> u256 { /* across all protocols */ }
    
    // Performance
    fn calculate_apy() -> u256 { /* based on on-chain data */ }
}

// 2. StrategyExecutor.cairo - Execute with proofs
contract StrategyExecutor {
    // Rebalance with proof
    fn rebalance_with_proof(
        allocations: Array<Allocation>,
        proof_hash: felt252
    ) {
        // Verify proof
        // Execute rebalance
        // Emit event
    }
}

// 3. PerformanceTracker.cairo - On-chain metrics
contract PerformanceTracker {
    fn record_rebalance(
        timestamp: u64,
        allocations: Array<Allocation>,
        proof_hash: felt252
    );
    
    fn get_performance() -> Performance {
        // Historical APY
        // Total returns
        // Sharpe ratio
    }
}
```

### Backend Changes

```python
# 1. Pool service
class PoolService:
    async def get_pool_state(self) -> PoolState:
        """Get current pool composition"""
        
    async def calculate_optimal_allocation(self) -> Allocation:
        """AI determines best allocation"""
        
    async def execute_rebalance_with_proof(self, allocation: Allocation) -> ProofJob:
        """Generate proof → Execute → Track"""

# 2. Performance service
class PerformanceService:
    async def get_apy(self) -> float:
        """Calculate APY from on-chain data"""
        
    async def get_historical_performance(self) -> List[PerformanceMetric]:
        """All rebalances with proofs"""
```

### Frontend Changes (Remove Demo Mode)

```typescript
// Remove ALL mock/demo data
// Show ONLY real on-chain state

// 1. PoolOverview.tsx - Real pool state
<PoolOverview>
  <TVL>{onChainTVL}</TVL>
  <CurrentAPY>{calculatedFromOnChainData}</CurrentAPY>
  <YourBalance>{userShares * sharePrice}</YourBalance>
  <Allocations>
    <Protocol name="Jediswap">{realAllocation}%</Protocol>
    <Protocol name="Ekubo">{realAllocation}%</Protocol>
  </Allocations>
</PoolOverview>

// 2. DepositWithdraw.tsx - Real transactions
<DepositFlow>
  <Input amount={userAmount} />
  <Button onClick={deposit}>Deposit USDC</Button>
  <TransactionStatus tx={depositTx} />
</DepositFlow>

// 3. ProofTimeline.tsx - Show every step
<ProofTimeline>
  <Step status="complete">
    AI Analysis: Jedi 60%, Ekubo 40%
  </Step>
  <Step status="complete">
    Proof Generated: 0xa580bd...
    <Badge>Verified Locally</Badge>
  </Step>
  <Step status="active">
    Executing Rebalance...
    <TxHash>0x123...</TxHash>
  </Step>
  <Step status="pending">
    SHARP Verification (est. 45min)
  </Step>
</ProofTimeline>

// 4. PerformanceChart.tsx - Real historical data
<PerformanceChart>
  <LineChart data={onChainPerformance}>
    {rebalances.map(r => (
      <Marker
        timestamp={r.timestamp}
        apy={r.apy}
        proof={r.proof_hash}
      />
    ))}
  </LineChart>
</PerformanceChart>

// 5. RebalanceHistory.tsx - All rebalances with proofs
<RebalanceHistory>
  <Table>
    {rebalances.map(r => (
      <Row>
        <Cell>{r.timestamp}</Cell>
        <Cell>Jedi {r.jedi}% / Ekubo {r.ekubo}%</Cell>
        <Cell>
          <ProofBadge hash={r.proof_hash} verified={r.verified} />
        </Cell>
        <Cell>{r.apy}% APY</Cell>
        <Cell>
          <Link href={voyager(r.tx)}>View TX</Link>
        </Cell>
      </Row>
    ))}
  </Table>
</RebalanceHistory>
```

---

## V1.3 Implementation Plan

### Week 1: Pool Contract + Backend

**Tasks**:
1. Deploy SharedPool contract
2. Integrate with StrategyRouter
3. Add deposit/withdraw flows
4. Update backend pool service
5. Performance tracking service

**Deliverable**: Users can deposit, pool rebalances with proofs

### Week 2: Performance + Proofs

**Tasks**:
1. On-chain performance calculation
2. Real proof generation integration
3. Backend orchestration (deposit → rebalance → prove)
4. Historical data indexing

**Deliverable**: Real APY, all rebalances tracked

### Week 3: Frontend - Real Data

**Tasks**:
1. Remove ALL demo mode
2. Pool overview (real TVL, APY)
3. Deposit/withdraw UI
4. Proof timeline component
5. Performance chart

**Deliverable**: Working UI with real on-chain data

### Week 4: Polish + Testing

**Tasks**:
1. End-to-end testing
2. Performance optimization
3. Error handling
4. Documentation

**Deliverable**: Demonstrable product

---

## V1.3 User Experience

### Deposit Flow

```
1. Connect wallet
2. Enter USDC amount
3. Approve USDC
4. Deposit → Get shares
5. See: "You own 2.5% of pool"
```

**Time**: ~30 seconds

### Rebalance Flow (Automated)

```
1. Backend analyzes protocols
2. Determines optimal allocation
3. Generates STARK proof (2-3s)
4. Executes rebalance on-chain
5. Updates performance metrics
6. User sees: "Rebalanced to Jedi 60% / Ekubo 40%"
   With proof: 0xa580bd... [Verified]
```

**Frequency**: Every 24 hours or when opportunity > 1%

**User sees**:
- Notification: "Pool rebalanced"
- New allocation percentages
- Proof hash with verification status
- Updated APY

### Performance View

```
Pool Performance
├── Current APY: 8.5%
├── 7-day return: +2.3%
├── Total rebalances: 12
└── All proofs verified: ✓

Recent Rebalances:
1. Dec 8, 14:00 - Jedi 60%, Ekubo 40% [Proof: 0xa580bd...]
2. Dec 7, 14:00 - Jedi 55%, Ekubo 45% [Proof: 0x8f91ca...]
3. Dec 6, 14:00 - Jedi 65%, Ekubo 35% [Proof: 0x2b45ef...]
```

**Every rebalance shows**:
- Timestamp
- Allocation change
- Proof hash
- Verification status
- Transaction link

---

## V1.4: Privacy Layer (MIST Integration)

**After V1.3 works, add privacy**

### MIST Integration

```cairo
contract PrivatePool {
    // Deposit privately (nullifier + commitment)
    fn private_deposit(
        commitment: felt252,
        amount: u256
    );
    
    // Withdraw privately (nullifier proof)
    fn private_withdraw(
        nullifier: felt252,
        proof: Array<felt252>,
        amount: u256
    );
    
    // Pool still optimizes transparently
    // But individual balances hidden
}
```

**User Experience**:
1. Deposit anonymously (like Tornado Cash)
2. Pool optimizes visibly (with proofs)
3. Withdraw anonymously
4. Nobody knows who owns what, but everyone can verify optimization

**Timeline**: 1-2 months after V1.3

---

## V1.5: Enhanced Features

### Multi-Protocol

- Add Nostra, zkLend, etc.
- More optimization opportunities
- More complex proof generation

### Advanced Strategies

- Delta-neutral positions
- Leverage (borrow + lend)
- Cross-protocol arbitrage
- All with cryptographic proofs

### DAO Governance

- Community sets constraints
- Vote on new protocols
- Risk parameter adjustments

---

## Technical Priorities (Revised)

### Must Have (V1.3)

1. **SharedPool contract** - Core product
2. **Real deposits/withdrawals** - Users need this
3. **Performance tracking** - Prove it works
4. **Proof visibility in UX** - Show verification
5. **Remove demo mode** - Only real data

### Should Have (V1.3)

1. **Faster proofs** (Rust binary) - UX improvement
2. **Better error handling** - Production quality
3. **Mobile responsive** - Accessibility

### Nice to Have (V1.4)

1. **MIST privacy** - Privacy layer
2. **SHARP L1 verification** - Extra security
3. **Cairo ML** - Full on-chain inference

### Future (V1.5+)

1. **Multi-protocol** - More strategies
2. **Advanced features** - Leverage, arb
3. **DAO governance** - Community control

---

## Key Differences from Previous Roadmap

### Before (Wrong)

Focus: Prove STARK generation works
Product: AI prover demo
Users: Can generate proofs
Value: "Look, we can make proofs!"

### After (Right)

Focus: Privacy pool that works
Product: Verifiable yield aggregator
Users: Deposit, earn, withdraw
Value: "Privacy + verifiable optimization"

### Changes

| Feature | Old Priority | New Priority |
|---------|-------------|--------------|
| Rust prover | Week 1 | Nice to have |
| SHARP integration | Week 2 | V1.4 |
| Cairo ML | V1.4 | V2.0 |
| Pool contract | Not mentioned | Week 1 |
| Real deposits | Not mentioned | Week 1 |
| Performance tracking | Not mentioned | Week 2 |
| Remove demo mode | Not mentioned | Week 3 |
| MIST privacy | Not mentioned | V1.4 |

---

## Success Metrics

### V1.3 (Demonstrable)

- [ ] Users can deposit real USDC
- [ ] Pool rebalances automatically
- [ ] Every rebalance has proof
- [ ] Performance tracked on-chain
- [ ] UI shows real data only
- [ ] End-to-end flow works

**Measure**: 10 users deposit, 1 week of rebalances, all proofs verified

### V1.4 (Privacy)

- [ ] MIST integrated
- [ ] Anonymous deposits/withdrawals
- [ ] Transparent optimization
- [ ] All proofs still visible

**Measure**: 50 users, $10k TVL, privacy preserved

### V1.5 (Scale)

- [ ] 5+ protocols
- [ ] Advanced strategies
- [ ] DAO governance

**Measure**: 500 users, $100k TVL, community driven

---

## Immediate Next Steps

### This Week

1. **Design SharedPool contract**
   - Simple deposit/withdraw
   - Share calculation
   - Integration with StrategyRouter

2. **Plan performance tracking**
   - What metrics?
   - How to calculate APY?
   - Storage structure

3. **Frontend audit**
   - Identify ALL demo mode code
   - Plan removal strategy
   - Design real-data components

### Next Week

1. **Deploy SharedPool**
2. **Implement deposits**
3. **Connect to proof generation**
4. **Start frontend refactor**

---

## Questions to Resolve

1. **Pool token?**
   - ERC20 shares or internal accounting?
   - Answer: ERC20 for composability

2. **Rebalance frequency?**
   - Daily? On-demand? Threshold-based?
   - Answer: Start daily, optimize later

3. **Performance calculation?**
   - On-chain or backend?
   - Answer: Both (backend for UX, on-chain for verification)

4. **MIST timeline?**
   - After V1.3 stable? Parallel?
   - Answer: After V1.3 works

5. **Testnet only?**
   - Or mainnet ready?
   - Answer: Testnet for V1.3, mainnet for V1.4

---

## Summary

**Old Plan**: Build cool tech (proofs, SHARP, Cairo ML)  
**New Plan**: Build usable product (pool, deposits, performance)

**Old Timeline**: Rust (week 1), SHARP (week 2), UI (week 3)  
**New Timeline**: Pool (week 1), Performance (week 2), Real UI (week 3)

**Old Value**: "We can generate proofs"  
**New Value**: "Privacy pool with verifiable optimization"

**Old Demo**: Mock data, proof generation  
**New Demo**: Real deposits, real rebalances, real proofs, real performance

---

**Next**: Deploy SharedPool contract, remove demo mode, track real performance

**Goal**: Demonstrable product in 3-4 weeks, privacy layer in 2 months

**Vision**: Privacy-preserving yield aggregator where every optimization is cryptographically proven

