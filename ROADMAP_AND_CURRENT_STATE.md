# Roadmap and Current State

**Last Updated**: December 9, 2024

## Current State

### ✅ What's Working

1. **Deposit Flow**: Users can deposit ETH to the StrategyRouterV2 contract
   - Contract accepts ETH deposits
   - Funds are stored in the contract
   - Allocation percentages are tracked (currently defaulting to 50/50)

2. **Allocation Management**: 
   - Allocation percentages can be updated via `update_allocation()`
   - AI Risk Engine can propose and execute allocations
   - Frontend displays allocations (though currently showing 50/50 from contract)

3. **Contract Infrastructure**:
   - StrategyRouterV2 deployed with ETH as deposit token
   - Protocol addresses configured (JediSwap, Ekubo)
   - Risk Engine and DAO Manager integrated

### ⚠️ What's Not Working Yet

1. **Protocol Integration (COMMENTED OUT)**:
   - The `deposit()` function has protocol integration code **commented out**
   - Funds currently just sit in the StrategyRouter contract
   - No actual deployment to JediSwap or Ekubo yet
   - No yield generation happening

2. **Allocation Display Mismatch**:
   - Contract stores 50/50 (default initialization)
   - Frontend/process shows different allocations (from AI decisions)
   - Allocation updates may not be persisting to contract

3. **Withdrawal**:
   - Withdrawal function exists but won't work until protocol integration is complete
   - Can't withdraw from positions that don't exist yet

## What Happens After Deposit (Current)

**Right Now:**
1. User deposits ETH → Funds go to StrategyRouterV2 contract
2. Contract calculates allocation (50% JediSwap, 50% Ekubo by default)
3. **STOPS HERE** - Protocol integration code is commented out
4. Funds just sit in the contract, not earning yield

**What Should Happen (Once Protocol Integration is Uncommented):**
1. User deposits ETH → Funds go to StrategyRouterV2 contract
2. Contract calculates allocation based on current percentages
3. For JediSwap allocation:
   - Swap half of allocated ETH to STRK
   - Add liquidity to ETH/STRK pool via JediSwap V2 NFT Position Manager
   - Store position NFT token ID
4. For Ekubo allocation:
   - Swap half of allocated ETH to STRK  
   - Deposit both tokens to Ekubo Core
   - Store position ID
5. Yield accrues automatically in the protocols
6. User can withdraw (contract removes liquidity and returns funds)

## Roadmap: What's Next

### Phase 1: Protocol Integration (IMMEDIATE PRIORITY) 🔴

**Goal**: Actually deploy funds to DeFi protocols and generate yield

**Tasks**:
1. **Uncomment and Fix Protocol Integration Code**
   - Uncomment the swap and liquidity provision logic in `deposit()`
   - Verify JediSwap V2 NFT Position Manager interface
   - Verify Ekubo Core interface
   - Test with small amounts on Sepolia

2. **Implement Position Tracking**
   - Store LP token IDs / position IDs from protocols
   - Track which positions belong to which users
   - Enable querying position values

3. **Test End-to-End Deposit Flow**
   - Deposit ETH
   - Verify swap happens (ETH → STRK)
   - Verify liquidity is added to JediSwap
   - Verify deposit to Ekubo
   - Check that positions are tracked

**Estimated Time**: 2-3 days

### Phase 2: Yield Tracking & Display 🟡

**Goal**: Show users their actual yield earnings

**Tasks**:
1. **Query Position Values**
   - Query JediSwap position value (LP tokens)
   - Query Ekubo position value
   - Calculate total portfolio value

2. **Calculate Yield**
   - Track initial deposit amount
   - Compare to current position value
   - Calculate APY based on time elapsed

3. **Display in Frontend**
   - Show current portfolio value
   - Show yield earned
   - Show APY (from DefiLlama + on-chain calculation)

**Estimated Time**: 1-2 days

### Phase 3: Withdrawal Implementation 🟡

**Goal**: Users can withdraw their funds

**Tasks**:
1. **Implement Withdrawal Logic**
   - Remove liquidity from JediSwap (burn LP tokens)
   - Withdraw from Ekubo positions
   - Swap STRK back to ETH (if needed)
   - Return funds to user

2. **Handle Partial Withdrawals**
   - Allow withdrawing percentage of position
   - Calculate proportional amounts

3. **Test Withdrawal Flow**
   - Test full withdrawal
   - Test partial withdrawal
   - Verify funds are returned correctly

**Estimated Time**: 2-3 days

### Phase 4: SHARP Integration (Proof Generation) 🟢

**Goal**: Generate STARK proofs for allocation decisions and submit to SHARP

**Tasks**:
1. **Integrate LuminAIR Operator**
   - Set up Rust operator for proof generation
   - Configure proof job submission
   - Track proof job status

2. **Submit Proofs to SHARP Gateway**
   - Submit allocation decision proofs
   - Submit risk calculation proofs
   - Get fact hashes back

3. **Store Fact Hashes On-Chain**
   - Store proof fact hashes in contract
   - Enable verification of decisions

**Estimated Time**: 3-5 days

### Phase 5: On-Chain Verification 🟢

**Goal**: Verify proofs on-chain and use them for decision validation

**Tasks**:
1. **Verify Fact Hashes**
   - Check fact hashes against SHARP registry
   - Validate proof correctness

2. **Use Proofs for Decisions**
   - Require valid proof for allocation updates
   - Enable trustless decision validation

**Estimated Time**: 2-3 days

### Phase 6: zkML Integration (Future) 🔵

**Goal**: Use zero-knowledge machine learning for risk calculations

**Tasks**:
1. **Research zkML Frameworks**
   - Evaluate EZKL, Giza, etc.
   - Determine best fit for risk calculations

2. **Convert Risk Model to zkML**
   - Port risk calculation logic
   - Generate proofs for ML inferences

3. **Integrate with Allocation System**
   - Use zkML proofs for risk scores
   - Enable verifiable AI decisions

**Estimated Time**: 1-2 weeks (research + implementation)

## Current Blockers

1. **Protocol Integration Code Commented Out**
   - Need to verify protocol interfaces match actual contracts
   - Need to test swap and liquidity provision calls
   - Cairo 2 compilation issues with `Span<u256>` storage

2. **Allocation Updates Not Persisting**
   - Contract shows 50/50 even after allocation updates
   - Need to verify `update_allocation()` is being called correctly
   - May need to check if updates are going to wrong contract

## Next Immediate Steps

1. **Fix Allocation Display Issue**
   - Verify `update_allocation()` is updating the correct contract
   - Check if allocation updates are succeeding
   - Add better logging to track allocation updates

2. **Uncomment Protocol Integration**
   - Start with JediSwap V2 interface verification
   - Test swap functionality first
   - Then test liquidity provision
   - Repeat for Ekubo

3. **Test Small Deposit**
   - Deposit 0.001 ETH
   - Verify it gets deployed to protocols
   - Check position tracking works

## Questions to Answer

- [ ] Are allocation updates actually calling the contract?
- [ ] Why is contract stuck at 50/50?
- [ ] Do JediSwap/Ekubo interfaces match our code?
- [ ] Can we test swaps on Sepolia?
- [ ] How do we track position values?


