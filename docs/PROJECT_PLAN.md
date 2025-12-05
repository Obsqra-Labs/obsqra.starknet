# Obsqra.fi Starknet MVP/POC — Project Plan

**Version:** 1.0  
**Date:** December 2025  
**Status:** Planning Phase  
**Target:** Production-ready POC for Grant Application

---

## Executive Summary

Build a Starknet MVP/POC demonstrating verifiable AI infrastructure for private DeFi capital routing. The POC will show on-chain AI computation (Cairo) with automatic proving (SHARP), integrated with MIST.cash privacy infrastructure.

**Key Deliverables:**
- Cairo risk engine (on-chain computation)
- MIST.cash privacy integration
- Strategy router with multi-protocol support
- Simplified frontend dashboard
- Full end-to-end flow: deposit → AI rebalance → withdraw

**Timeline:** 12 weeks  
**Budget:** $25,000 (grant ask)

---

## 1. Project Goals & Success Criteria

### 1.1 Primary Goals

1. Demonstrate on-chain AI computation (Cairo vs off-chain Python)
2. Show SHARP automatic proving (no validator network needed)
3. Integrate MIST.cash for privacy (amount correlation solved)
4. Prove the concept works end-to-end (deposit → AI → withdraw)
5. Create reusable infrastructure for other builders

### 1.2 Success Criteria

**Technical:**
- ✅ Cairo contracts deployed and verified on testnet
- ✅ MIST.cash integration working (deposit/withdraw)
- ✅ SHARP proving costs < $0.01 per computation
- ✅ Full flow: deposit → AI rebalance → withdraw
- ✅ All unit tests passing
- ✅ Integration tests passing

**Functional:**
- ✅ Users can deposit via MIST.cash (private)
- ✅ AI computes allocation on-chain (Cairo)
- ✅ Allocation respects DAO constraints
- ✅ Users can withdraw to fresh addresses (unlinkable)
- ✅ Frontend shows pool state and AI decisions

**Ecosystem:**
- ✅ 3+ DAOs testing the protocol
- ✅ $100K+ TVL on testnet
- ✅ 10+ builders using the code as reference
- ✅ 2+ integrations with other Starknet protocols

**Documentation:**
- ✅ Technical documentation complete
- ✅ User guides published
- ✅ Code examples for builders
- ✅ Architecture diagrams

---

## 2. Technical Architecture

### 2.1 System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  • Simplified dashboard                                  │
│  • MIST.cash integration                                 │
│  • Contract interactions                                 │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              MIST.cash Privacy Layer                    │
│  • Deposit/Withdraw with ZK proofs                      │
│  • Amount correlation mitigation                        │
│  • Privacy pool contracts                               │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          Cairo Contracts (On-Chain AI)                  │
│  • RiskEngine.cairo (risk scoring)                      │
│  • StrategyRouter.cairo (allocation routing)            │
│  • DAOConstraintManager.cairo (governance)              │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              SHARP (Automatic Proving)                   │
│  • Proves all Cairo computations                        │
│  • Batches transactions                                 │
│  • Cost amortized                                       │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Off-Chain Service (Python)                      │
│  • Monitors protocols                                    │
│  • Fetches data                                         │
│  • Triggers rebalances                                  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Contract Architecture

**Core Contracts:**
1. **RiskEngine.cairo** — On-chain risk scoring and allocation calculation
2. **StrategyRouter.cairo** — Multi-protocol routing and rebalancing
3. **DAOConstraintManager.cairo** — Governance constraints and validation

**Integration Points:**
- MIST.cash SDK for privacy layer
- Starknet DeFi protocols (Ekubo, zkLend, Nostra)
- SHARP for automatic proving

### 2.3 Data Flow

```
1. User deposits via MIST.cash (private)
   ↓
2. Off-chain service monitors protocols
   ↓
3. Service calls Cairo contract with data
   ↓
4. Cairo contract computes:
   - Risk scores (on-chain)
   - Allocation (on-chain)
   - Constraint verification (on-chain)
   ↓
5. SHARP automatically proves computations
   ↓
6. If constraints met: Execute allocation
   If constraints violated: Revert
   ↓
7. User withdraws via MIST.cash (unlinkable)
```

---

## 3. Implementation Phases

### Phase 1: Foundation (Weeks 1-3)

**Goal:** Set up development environment and port core AI logic to Cairo

**Tasks:**
- [ ] Set up development environment (Rust, Cairo, Scarb)
- [ ] Initialize project structure
- [ ] Port risk scoring algorithm to Cairo
- [ ] Port allocation algorithm to Cairo
- [ ] Port constraint verification to Cairo
- [ ] Write unit tests for all Cairo functions
- [ ] Set up CI/CD pipeline

**Deliverables:**
- ✅ RiskEngine.cairo contract
- ✅ Unit tests passing
- ✅ Development environment documented

**Success Criteria:**
- All Cairo functions compile
- Unit tests pass
- Risk scoring matches Python implementation

---

### Phase 2: Privacy Integration (Weeks 4-5)

**Goal:** Integrate MIST.cash for privacy layer

**Tasks:**
- [ ] Install and configure MIST.cash SDK
- [ ] Implement deposit flow
- [ ] Implement withdraw flow
- [ ] Test amount correlation mitigation
- [ ] End-to-end privacy testing
- [ ] Frontend integration

**Deliverables:**
- ✅ MIST.cash integration working
- ✅ Deposit/withdraw flows tested
- ✅ Privacy guarantees verified

**Success Criteria:**
- Users can deposit privately
- Users can withdraw to fresh addresses
- Deposit-withdrawal unlinkable
- Amount correlation mitigated

---

### Phase 3: Strategy Router (Weeks 6-7)

**Goal:** Build multi-protocol routing and rebalancing

**Tasks:**
- [ ] Build StrategyRouter.cairo contract
- [ ] Integrate with Starknet DeFi protocols
- [ ] Implement rebalancing logic
- [ ] Implement yield tracking
- [ ] Test protocol integrations
- [ ] Integration tests

**Deliverables:**
- ✅ StrategyRouter.cairo contract
- ✅ Protocol integrations working
- ✅ Rebalancing logic tested

**Success Criteria:**
- Router can update allocations
- Protocol integrations working
- Rebalancing executes correctly
- Yields tracked accurately

---

### Phase 4: Frontend & Testing (Weeks 8-10)

**Goal:** Build frontend and comprehensive testing

**Tasks:**
- [ ] Build simplified dashboard
- [ ] Connect to Starknet contracts
- [ ] Integrate MIST.cash in frontend
- [ ] Test full flow: deposit → AI → withdraw
- [ ] Performance testing with SHARP
- [ ] User acceptance testing
- [ ] Bug fixes and polish

**Deliverables:**
- ✅ Frontend deployed
- ✅ Full flow tested
- ✅ Performance benchmarks
- ✅ User documentation

**Success Criteria:**
- Frontend connects to contracts
- Full flow works end-to-end
- Performance acceptable (< 5s per operation)
- Users can complete all actions

---

### Phase 5: Documentation & Launch (Weeks 11-12)

**Goal:** Complete documentation and launch POC

**Tasks:**
- [ ] Write technical documentation
- [ ] Write user guides
- [ ] Create code examples for builders
- [ ] Deploy to public testnet
- [ ] Community announcement
- [ ] Grant report preparation

**Deliverables:**
- ✅ Complete documentation
- ✅ Public testnet deployment
- ✅ Community announcement
- ✅ Grant report

**Success Criteria:**
- Documentation complete
- POC deployed to testnet
- Community engaged
- Grant report submitted

---

## 4. Detailed Task Breakdown

### 4.1 Week 1: Environment Setup

**Day 1-2: Development Environment**
- Install Rust, Cairo, Scarb
- Set up project structure
- Initialize Git repository
- Configure IDE (VS Code with Cairo extension)

**Day 3-4: Cairo Basics**
- Learn Cairo syntax
- Write simple Cairo programs
- Understand felt252 arithmetic
- Test compilation and execution

**Day 5: Project Initialization**
- Initialize Scarb project
- Set up contract structure
- Create test framework
- Write first test

**Deliverables:**
- ✅ Development environment set up
- ✅ Project structure created
- ✅ First Cairo contract compiles

---

### 4.2 Week 2: Risk Engine Port

**Day 1-2: Risk Scoring Algorithm**
- Port `calculate_risk_score()` to Cairo
- Handle felt252 arithmetic
- Test with various inputs
- Verify against Python implementation

**Day 3-4: Allocation Algorithm**
- Port `calculate_allocation()` to Cairo
- Handle percentage calculations
- Test edge cases
- Verify outputs sum to 100%

**Day 5: Constraint Verification**
- Port `verify_constraints()` to Cairo
- Test constraint logic
- Test edge cases
- Integration with risk engine

**Deliverables:**
- ✅ Risk engine contract complete
- ✅ All functions tested
- ✅ Matches Python implementation

---

### 4.3 Week 3: Testing & Refinement

**Day 1-2: Unit Tests**
- Write comprehensive unit tests
- Test all edge cases
- Test error conditions
- Achieve 100% code coverage

**Day 3-4: Integration Tests**
- Test contract interactions
- Test with mock data
- Test rebalancing flow
- Performance testing

**Day 5: Documentation**
- Document contract interfaces
- Document function parameters
- Create code examples
- Update README

**Deliverables:**
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Code ready for integration

---

### 4.4 Week 4: MIST.cash Integration (Part 1)

**Day 1-2: SDK Setup**
- Install MIST.cash SDK
- Understand SDK API
- Set up test environment
- Create test account

**Day 3-4: Deposit Flow**
- Implement deposit function
- Test with small amounts
- Verify commitments created
- Test error handling

**Day 5: Withdraw Flow**
- Implement withdraw function
- Test proof generation
- Verify withdrawals work
- Test to fresh addresses

**Deliverables:**
- ✅ MIST.cash SDK integrated
- ✅ Deposit flow working
- ✅ Withdraw flow working

---

### 4.5 Week 5: MIST.cash Integration (Part 2)

**Day 1-2: Privacy Testing**
- Test deposit-withdrawal unlinking
- Verify amount correlation mitigation
- Test with multiple users
- Privacy audit

**Day 3-4: Frontend Integration**
- Create React hooks for MIST.cash
- Build deposit UI component
- Build withdraw UI component
- Test user flows

**Day 5: End-to-End Testing**
- Test full privacy flow
- Test with multiple deposits
- Test with multiple withdrawals
- Performance testing

**Deliverables:**
- ✅ Privacy guarantees verified
- ✅ Frontend integration complete
- ✅ End-to-end testing done

---

### 4.6 Week 6: Strategy Router (Part 1)

**Day 1-2: Contract Design**
- Design StrategyRouter.cairo interface
- Plan protocol integrations
- Design allocation storage
- Design event structure

**Day 3-4: Core Logic**
- Implement `update_allocation()`
- Implement `get_allocation()`
- Test allocation updates
- Test event emission

**Day 5: Protocol Adapters**
- Research Starknet DeFi protocols
- Design adapter pattern
- Implement first adapter
- Test integration

**Deliverables:**
- ✅ Strategy router contract
- ✅ Core logic implemented
- ✅ First protocol adapter

---

### 4.7 Week 7: Strategy Router (Part 2)

**Day 1-2: Protocol Integrations**
- Integrate with Ekubo (DEX)
- Integrate with zkLend (lending)
- Integrate with Nostra (lending)
- Test each integration

**Day 3-4: Rebalancing Logic**
- Implement rebalancing algorithm
- Test rebalancing triggers
- Test execution flow
- Test error handling

**Day 5: Yield Tracking**
- Implement yield accrual
- Test yield calculation
- Test yield distribution
- Integration testing

**Deliverables:**
- ✅ Protocol integrations complete
- ✅ Rebalancing working
- ✅ Yield tracking working

---

### 4.8 Week 8: Frontend (Part 1)

**Day 1-2: Setup & Structure**
- Initialize Next.js project
- Set up Starknet provider
- Create component structure
- Set up routing

**Day 3-4: Dashboard UI**
- Design dashboard layout
- Build pool overview component
- Build allocation display
- Build AI decision history

**Day 5: Contract Integration**
- Create contract hooks
- Connect to RiskEngine
- Connect to StrategyRouter
- Test contract calls

**Deliverables:**
- ✅ Frontend structure
- ✅ Dashboard UI
- ✅ Contract integration

---

### 4.9 Week 9: Frontend (Part 2)

**Day 1-2: User Flows**
- Build deposit flow UI
- Build withdraw flow UI
- Build rebalance trigger UI
- Test user interactions

**Day 3-4: State Management**
- Set up state management
- Handle loading states
- Handle error states
- Handle success states

**Day 5: Polish & UX**
- Improve UI/UX
- Add loading indicators
- Add error messages
- Add success confirmations

**Deliverables:**
- ✅ User flows complete
- ✅ State management working
- ✅ UI polished

---

### 4.10 Week 10: Testing & Refinement

**Day 1-2: End-to-End Testing**
- Test full flow: deposit → AI → withdraw
- Test with multiple users
- Test edge cases
- Test error scenarios

**Day 3-4: Performance Testing**
- Test SHARP proving times
- Test transaction costs
- Test frontend performance
- Optimize bottlenecks

**Day 5: Bug Fixes**
- Fix identified bugs
- Improve error handling
- Add logging
- Final testing

**Deliverables:**
- ✅ End-to-end tests passing
- ✅ Performance acceptable
- ✅ Bugs fixed

---

### 4.11 Week 11: Documentation

**Day 1-2: Technical Documentation**
- Document architecture
- Document contract interfaces
- Document API endpoints
- Create diagrams

**Day 3-4: User Documentation**
- Write user guides
- Create tutorials
- Write FAQ
- Create video walkthrough

**Day 5: Developer Documentation**
- Write code examples
- Document integration patterns
- Create SDK documentation
- Update README

**Deliverables:**
- ✅ Technical docs complete
- ✅ User docs complete
- ✅ Developer docs complete

---

### 4.12 Week 12: Launch & Reporting

**Day 1-2: Deployment**
- Deploy to public testnet
- Verify contracts
- Test on testnet
- Monitor for issues

**Day 3-4: Community Launch**
- Write announcement blog post
- Post on Twitter/X
- Share in Discord
- Engage with community

**Day 5: Grant Report**
- Write grant report
- Document achievements
- Document learnings
- Submit report

**Deliverables:**
- ✅ POC deployed
- ✅ Community announcement
- ✅ Grant report submitted

---

## 5. Dependencies & Prerequisites

### 5.1 Technical Dependencies

**Required:**
- Rust 1.70+
- Cairo 2.0+
- Scarb 2.0+
- Node.js 18+
- Python 3.10+
- Starknet testnet access
- MIST.cash SDK access

**Optional:**
- Infura/Alchemy RPC endpoint
- StarkScan API key
- Pinata IPFS (for metadata)

### 5.2 External Dependencies

**MIST.cash:**
- SDK availability
- Documentation
- Support access

**Starknet DeFi Protocols:**
- Ekubo (DEX)
- zkLend (lending)
- Nostra (lending)

**SHARP:**
- Automatic proving (no action needed)
- Network availability

### 5.3 Knowledge Dependencies

**Required Knowledge:**
- Rust basics
- Cairo syntax
- Smart contract development
- TypeScript/React
- Python

**Helpful Knowledge:**
- Zero-knowledge proofs
- Starknet architecture
- MIST.cash SDK
- DeFi protocols

---

## 6. Risk Mitigation

### 6.1 Technical Risks

**Risk: Cairo port complexity**
- **Mitigation:** Start with simple arithmetic, test incrementally
- **Contingency:** Simplify algorithms if needed

**Risk: MIST.cash integration issues**
- **Mitigation:** Early integration, test thoroughly
- **Contingency:** Contact MIST.cash team for support

**Risk: SHARP proving delays**
- **Mitigation:** Test with small batches, monitor performance
- **Contingency:** Use alternative RPC if needed

**Risk: Protocol integration issues**
- **Mitigation:** Start with one protocol, expand gradually
- **Contingency:** Use mock protocols for testing

### 6.2 Timeline Risks

**Risk: Delays in development**
- **Mitigation:** 10% contingency buffer, prioritize core features
- **Contingency:** Cut non-essential features if needed

**Risk: Scope creep**
- **Mitigation:** Clear phase boundaries, strict feature freeze
- **Contingency:** Defer non-essential features to Phase 2

**Risk: Dependency delays**
- **Mitigation:** Early integration testing, maintain relationships
- **Contingency:** Use alternatives if available

### 6.3 Ecosystem Risks

**Risk: Protocol availability**
- **Mitigation:** Multiple protocol options, test early
- **Contingency:** Use mock protocols for POC

**Risk: Low user adoption**
- **Mitigation:** Clear value proposition, good UX
- **Contingency:** Focus on builder adoption

**Risk: Network issues**
- **Mitigation:** Monitor network status, use multiple RPCs
- **Contingency:** Deploy to alternative testnet if needed

---

## 7. Testing Strategy

### 7.1 Unit Testing

**Coverage:**
- All Cairo functions
- All edge cases
- All error conditions
- 100% code coverage target

**Tools:**
- Snforge (Starknet Foundry)
- Scarb test framework

**Timeline:**
- Week 3: Complete unit tests
- Ongoing: Update tests as code changes

### 7.2 Integration Testing

**Coverage:**
- Contract interactions
- MIST.cash integration
- Protocol integrations
- End-to-end flows

**Tools:**
- Snforge integration tests
- Custom test scripts

**Timeline:**
- Week 5: MIST.cash integration tests
- Week 7: Protocol integration tests
- Week 10: End-to-end tests

### 7.3 E2E Testing

**Coverage:**
- Full user flows
- Frontend interactions
- Contract interactions
- Privacy guarantees

**Tools:**
- Playwright (frontend)
- Custom test scripts

**Timeline:**
- Week 10: Complete E2E tests

### 7.4 Performance Testing

**Metrics:**
- SHARP proving times
- Transaction costs
- Frontend load times
- Contract execution times

**Tools:**
- Custom benchmarks
- Network monitoring

**Timeline:**
- Week 10: Performance testing

---

## 8. Deployment Plan

### 8.1 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Contracts verified
- [ ] Documentation complete
- [ ] Security review done
- [ ] Performance acceptable
- [ ] User guides ready
- [ ] Community announcement prepared

### 8.2 Deployment Steps

1. **Deploy Contracts:**
   ```bash
   ./scripts/deploy.sh testnet
   ```

2. **Verify Contracts:**
   ```bash
   ./scripts/verify.sh $CONTRACT_ADDRESS $CONTRACT_NAME
   ```

3. **Update Frontend:**
   - Update contract addresses
   - Deploy to Vercel/Netlify
   - Test on testnet

4. **Monitor:**
   - Check contract deployments
   - Monitor for errors
   - Test user flows

5. **Announce:**
   - Post announcement
   - Share on social media
   - Engage with community

### 8.3 Post-Deployment

**Monitoring:**
- Contract events
- User activity
- Error logs
- Performance metrics

**Support:**
- Answer questions
- Fix bugs
- Gather feedback
- Iterate

---

## 9. Success Metrics

### 9.1 Technical Metrics

- Contract deployment success rate: 100%
- Test coverage: >90%
- SHARP proving cost: <$0.01 per computation
- Transaction success rate: >95%
- Frontend load time: <3s

### 9.2 Functional Metrics

- Users can deposit: 100% success rate
- Users can withdraw: 100% success rate
- AI rebalancing works: >95% success rate
- Privacy guarantees: 100% verified

### 9.3 Ecosystem Metrics

- DAOs testing: 3+
- TVL on testnet: $100K+
- Builders using code: 10+
- Protocol integrations: 2+

### 9.4 Documentation Metrics

- Technical docs: Complete
- User guides: Complete
- Code examples: 5+
- Architecture diagrams: 3+

---

## 10. Budget Breakdown

| Phase | Duration | Cost | Notes |
|------|----------|------|-------|
| Phase 1: Foundation | 3 weeks | $10,000 | Cairo port, testing |
| Phase 2: Privacy | 2 weeks | $4,000 | MIST.cash integration |
| Phase 3: Router | 2 weeks | $4,000 | Strategy router, protocols |
| Phase 4: Frontend | 3 weeks | $4,000 | Dashboard, testing |
| Phase 5: Launch | 2 weeks | $2,000 | Documentation, deployment |
| Contingency | - | $1,000 | 4% buffer |
| **Total** | **12 weeks** | **$25,000** | |

---

## 11. Next Steps

### 11.1 Immediate Actions

1. **Create Repository:**
   ```bash
   mkdir obsqra-starknet-poc
   cd obsqra-starknet-poc
   git init
   ```

2. **Set Up Structure:**
   - Create directories
   - Initialize projects
   - Set up CI/CD

3. **Start Phase 1:**
   - Set up development environment
   - Port risk engine to Cairo
   - Write first tests

### 11.2 Week 1 Deliverables

- ✅ Repository created
- ✅ Development environment set up
- ✅ Project structure initialized
- ✅ First Cairo contract compiles

---

## 12. Resources & References

### 12.1 Documentation

- [Starknet Documentation](https://docs.starknet.io)
- [Cairo Book](https://book.cairo-lang.org)
- [MIST.cash SDK](https://github.com/mistcash/sdk)
- [Starknet Foundry](https://foundry-rs.github.io/starknet-foundry)

### 12.2 Community

- Starknet Discord
- MIST.cash Discord
- Cairo Telegram
- Obsqra Discord

### 12.3 Tools

- VS Code with Cairo extension
- Starknet Foundry
- Scarb
- StarkScan

---

## 13. Conclusion

This plan outlines a 12-week path to a production-ready POC demonstrating verifiable AI infrastructure on Starknet. The focus is on:

1. **On-chain AI computation** (Cairo vs off-chain Python)
2. **Automatic proving** (SHARP vs custom provers)
3. **Privacy integration** (MIST.cash SDK)
4. **End-to-end functionality** (deposit → AI → withdraw)

Follow this plan phase by phase, and refer to the implementation guide for detailed technical instructions.

**Ready to start?** Begin with Phase 1, Week 1: Environment Setup.

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Status:** Ready for Implementation

