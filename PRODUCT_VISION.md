# Product Vision: Privacy Pool with Verifiable AI

## What We're Building

**Lightweight privacy pool where AI optimization is cryptographically proven**

Not a proof generator. Not a tech demo. A real product.

---

## User Flow

```
1. User deposits USDC → Gets shares in pool
2. Pool analyzes Jediswap + Ekubo yields
3. AI determines optimal allocation
4. Generates STARK proof of optimization
5. Executes rebalance on-chain
6. User sees: "Rebalanced to 60% Jedi / 40% Ekubo [Proof: 0xa580...]"
7. Performance tracked on-chain (APY, returns)
8. User withdraws shares + yield anytime
```

**Every rebalance has a cryptographic proof. Every decision is auditable.**

---

## Why This Matters

### Problem
- Yield aggregators are blackboxes
- Users can't verify AI decisions
- No transparency in optimization
- Privacy requires centralized mixers

### Solution
- Shared pool with transparent optimization
- Cryptographic proof of every decision
- On-chain performance tracking
- Privacy layer (MIST) coming in V1.4

---

## V1.3: Demonstrable Product (3-4 weeks)

**Goal**: Users can actually use it

### Week 1: Pool Contract
- SharedPool.cairo (deposit, withdraw, rebalance)
- Deploy to Sepolia
- Integration with StrategyRouter

### Week 2: Backend Orchestration
- Pool service (calculate optimal allocation)
- Performance tracking (APY from on-chain data)
- API endpoints (state, optimize, performance)

### Week 3: Frontend (Remove Demo Mode)
- Real deposits/withdrawals
- Proof visualization
- Performance charts (on-chain data only)
- Rebalance history with proofs

### Week 4: Polish + Testing
- End-to-end testing
- Error handling
- Documentation

**Deliverable**: Users deposit → Pool optimizes with proofs → Users see real performance

---

## V1.4: Privacy Layer (1-2 months)

**Add MIST integration**:
- Anonymous deposits (nullifier + commitment)
- Anonymous withdrawals (ZK proof)
- Transparent optimization (still provable)
- Individual balances hidden

**User Experience**:
- Deposit privately (like Tornado Cash)
- Pool optimizes publicly (with proofs)
- Withdraw privately
- Nobody knows who owns what

---

## What Makes This Different

### Traditional Yield Aggregators
- Centralized optimization
- Blackbox decisions
- No verification
- "Trust us"

### Obsqura
- Decentralized pool
- Cryptographic proofs
- On-chain verification
- "Verify everything"

---

## Current Status

### What Works
- Risk scoring algorithm ✓
- Proof generation (2-3s) ✓
- On-chain contracts ✓
- Backend API ✓
- Production deployment ✓

### What's Missing
- Shared pool contract
- Real deposits/withdrawals
- Performance tracking (on-chain)
- Frontend (real data only)
- Privacy layer (MIST)

**The Gap**: It's a demo, not a product

---

## Success Metrics

### V1.3 (Demonstrable)
- 10+ users deposit real USDC
- 7 days of automated rebalances
- All rebalances have proofs
- APY calculated from on-chain results
- 0 instances of demo/mock data

### V1.4 (Privacy)
- 50+ users
- $10k+ TVL
- Anonymous deposits/withdrawals
- Transparent optimization
- All proofs still visible

### V1.5 (Scale)
- 500+ users
- $100k+ TVL
- 5+ protocols (Nostra, zkLend, etc.)
- DAO governance
- Community constraints

---

## Technical Priorities

### Must Have (V1.3)
1. SharedPool contract
2. Real deposits/withdrawals
3. Performance tracking
4. Remove demo mode
5. Proof visibility in UX

### Should Have (V1.3)
1. Error handling
2. Loading states
3. Mobile responsive

### Nice to Have (V1.4)
1. Faster proofs (Rust binary)
2. MIST privacy
3. SHARP L1 verification

### Future (V1.5+)
1. Multi-protocol
2. Advanced strategies
3. Cairo ML (full on-chain)

---

## Next Steps

### This Week
1. Design SharedPool.cairo
2. Plan performance calculation
3. Audit frontend for demo code

### Next Week
1. Deploy SharedPool
2. Implement pool_service.py
3. Start frontend refactor

### Week 3-4
1. Remove ALL demo mode
2. Real data only
3. Proof visualization
4. End-to-end testing

---

## Long-Term Vision

**V1.3**: Demonstrable pool with proofs  
**V1.4**: Add privacy (MIST)  
**V1.5**: Multi-protocol, advanced strategies  
**V2.0**: Full zkML, DAO governance, cross-chain

**Ultimate Goal**: Privacy-preserving yield aggregator where every optimization decision is cryptographically proven and verifiable on L1.

---

## For Investors/Grants

**What We Have**:
- Production system (starknet.obsqra.fi)
- Working proof generation
- On-chain contracts
- Technical foundation

**What We're Building**:
- Real product (not demo)
- Privacy pool with verification
- Transparent AI optimization
- MIST privacy integration

**Why It Matters**:
- First verifiable AI in DeFi
- Privacy + transparency
- Cryptographic guarantees
- No blackbox decisions

**Timeline**:
- V1.3 (product): 3-4 weeks
- V1.4 (privacy): 2 months
- V1.5 (scale): 3-6 months

**Ask**: Time to build, feedback on direction

---

**Status**: V1.2 production (proof generator), pivoting to V1.3 (privacy pool product)

**Next**: Deploy SharedPool contract, remove demo mode, track real performance

**Goal**: Demonstrable privacy pool with verifiable AI in 3-4 weeks

