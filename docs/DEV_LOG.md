# Dev Log: EVM to Starknet Migration Journey

> A candid account of building Obsqra on Starknet, coming from an EVM background.

---

## TL;DR

**The Good:** Once it clicks, Starknet's architecture is elegant. Automatic proving, native account abstraction, and Cairo's type safety are game-changers.

**The Painful:** Tooling fragmentation, version compatibility hell, and the account deployment chicken-and-egg problem will test your patience.

**The Verdict:** Worth it. The learning curve is steep but the tradeoffs could genuinely streamline development for complex DeFi applications.

---

## Day 1-2: Initial Setup & Contract Refactoring

### The Wake-Up Call

Started with contracts that referenced Aave, Lido, Compound, and ETH. Classic EVM brain. First realization:

> "Wait, Starknet has its own DeFi ecosystem. Why am I pretending this is Ethereum?"

**Lesson:** Starknet-native protocols exist and are production-ready:
- **Nostra** → Lending (like Aave)
- **zkLend** → Money market (like Compound)  
- **Ekubo** → DEX (like Uniswap)
- **STRK** → Native gas token (not ETH!)

### The Refactor

Changed all contract interfaces from EVM patterns to Starknet-native:

```cairo
// Before (EVM brain)
aave_address: ContractAddress,
lido_address: ContractAddress,
compound_address: ContractAddress,

// After (Starknet native)
nostra_address: ContractAddress,
zklend_address: ContractAddress,
ekubo_address: ContractAddress,
```

Cairo syntax took some getting used to, but the type safety is actually nice once you stop fighting it.

---

## Day 3: The Deployment Nightmare Begins

### "Just Deploy to Sepolia" - Famous Last Words

Attempted deployment with `starkli`. Got hit with:

```
Error: ContractNotFound
```

Tried `sncast`. Different error:

```
Error: Unknown RPC error: JSON-RPC error: code=-32602
```

### The Account Deployment Paradox

This is where Starknet fundamentally differs from EVM:

**EVM:** Wallets are just keypairs. Send ETH, start transacting.

**Starknet:** Wallets are smart contracts. They must be DEPLOYED before you can send transactions.

But wait...

> "To deploy my wallet, I need to send a transaction. But I can't send a transaction without a deployed wallet. WTF?"

### The Solution (That Took Hours to Figure Out)

The `DEPLOY_ACCOUNT` transaction type exists specifically for this:

1. **Calculate your account address** (deterministic from public key + class hash + salt)
2. **Fund that address** (can receive tokens even before deployment)
3. **Send DEPLOY_ACCOUNT** (special transaction that bootstraps the account)

**Key insight:** The faucet at [starknet-faucet.vercel.app](https://starknet-faucet.vercel.app) doesn't just send STRK—it actually triggers account deployment! This saved us.

---

## Day 4: Version Compatibility Hell

### The Compatibility Matrix

Discovered [the compatibility tables](https://docs.starknet.io/learn/cheatsheets/compatibility). This should be required reading.

| Tool | RPC 0.8 | RPC 0.10 |
|------|---------|----------|
| sncast | 0.39.0 | **0.53.0** |
| starknet.py | 0.26.0 | 0.29.0 |

Our Alchemy RPC was 0.8.1. Our sncast was 0.39.0. Should work, right?

**WRONG.**

```
Error: Mismatch compiled class hash
Actual: 0x0614...
Expected: 0x32f5...
```

The CASM (Cairo Assembly) hash computed by starkli's internal compiler didn't match what the network expected.

### The Fix

```bash
# Upgrade sncast to 0.53.0
snfoundryup

# Use built-in network instead of custom RPC
sncast --account deployer declare --contract-name RiskEngine --network sepolia
```

**Lesson:** Don't fight the tooling. Use `--network sepolia` and let sncast figure out the RPC.

---

## Day 5: Victory 🎉

### Successful Deployment

After upgrading sncast to 0.53.0 and using the built-in Sepolia network:

```bash
$ sncast --account deployer declare --contract-name RiskEngine --network sepolia

Success: Declaration completed
Class Hash: 0x61febd39ccffbbd986e071669eb1f712f4dcf5e008aae7fa2bed1f09de6e304
```

All three contracts deployed:

| Contract | Address |
|----------|---------|
| RiskEngine | `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80` |
| DAOConstraintManager | `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` |
| StrategyRouter | `0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a` |

---

## Key Takeaways for EVM Developers

### 1. Accounts Are Smart Contracts
Not just keypairs. This enables account abstraction natively but requires explicit deployment.

### 2. STRK, Not ETH
Starknet uses STRK for gas. Stop looking for ETH faucets.

### 3. Tooling Is Fragmented
- `starkli` - Official CLI (sometimes flaky)
- `sncast` - Starknet Foundry (more reliable for deployment)
- `starknet.py` - Python SDK (good for scripting)

**Recommendation:** Use `sncast` for deployment, especially version 0.53.0+

### 4. RPC Version Matters A LOT
Check the [compatibility tables](https://docs.starknet.io/learn/cheatsheets/compatibility). Match your tool versions to your RPC version.

### 5. The Faucet Is Your Friend
[starknet-faucet.vercel.app](https://starknet-faucet.vercel.app) handles account deployment automatically. Use it.

### 6. Class Hash ≠ Contract Address
In Starknet:
- **Declare** uploads the contract code (returns class hash)
- **Deploy** creates an instance (returns contract address)

This is actually cleaner than EVM's single-step deployment.

---

## What I'd Do Differently

1. **Start with sncast 0.53.0** - Don't waste time with older versions
2. **Use `--network sepolia`** - Don't bother with custom RPCs initially
3. **Read the compatibility tables first** - Would have saved hours
4. **Use the faucet for account deployment** - It handles the bootstrap problem

---

## The Starknet Value Proposition

After this journey, I get why Starknet exists:

| Feature | EVM | Starknet |
|---------|-----|----------|
| Account Abstraction | EIP-4337 (complex) | Native |
| Proving | Off-chain, trust required | Automatic (SHARP) |
| Privacy | Requires mixers | Native (future: MIST.cash) |
| Type Safety | Solidity (weak) | Cairo (strong) |
| Upgrades | Proxy patterns | Built-in |

The initial friction is real, but the architecture is genuinely better for complex DeFi.

---

## Next Steps

- [ ] Configure frontend with deployed contract addresses
- [ ] Implement actual protocol integrations (Nostra, zkLend, Ekubo)
- [ ] Add privacy layer with MIST.cash
- [ ] Deploy to mainnet

---

## Resources That Actually Helped

1. [Starknet Compatibility Tables](https://docs.starknet.io/learn/cheatsheets/compatibility) - **READ THIS FIRST**
2. [Starknet Foundry Book](https://foundry-rs.github.io/starknet-foundry/)
3. [Cairo Book](https://book.cairo-lang.org)
4. [Voyager Explorer](https://voyager.online) - For debugging transactions

---

*Written after deploying to Sepolia, December 5, 2025*

**The learning curve is steep. The view from the top is worth it.** 🔺

---

## December 2025: Full On-Chain Orchestration Implementation

### The Vision: 100% On-Chain Auditability

After initial deployment, we realized a critical gap: **users were directly updating allocations**, which bypassed the AI Risk Engine entirely. This broke the core value proposition: **verifiable AI decisions from computation to settlement**.

### The Problem

The original flow was:
```
User → Frontend → StrategyRouter.update_allocation()
```

This meant:
- ❌ No AI involvement
- ❌ No risk calculation
- ❌ No DAO validation
- ❌ No audit trail
- ❌ Users could set arbitrary allocations

### The Solution: RiskEngine Orchestration

We implemented `RiskEngine.propose_and_execute_allocation()` - a single function that orchestrates the **entire flow on-chain**:

```cairo
fn propose_and_execute_allocation(
    jediswap_metrics: ProtocolMetrics,
    ekubo_metrics: ProtocolMetrics,
) -> AllocationDecision
```

**The Complete Flow:**
1. **Calculate Risk Scores** (on-chain Cairo computation)
   - JediSwap risk: utilization, volatility, liquidity, audit, age
   - Ekubo risk: same factors
   - Emits: `ProtocolMetricsQueried` events

2. **Query Protocol APY** (on-chain)
   - JediSwap APY from stored values (ready for oracle integration)
   - Ekubo APY from stored values (ready for oracle integration)
   - Emits: `APYQueried` events

3. **Calculate Allocation** (on-chain Cairo computation)
   - Risk-adjusted score = (APY * 10000) / (Risk + 1)
   - Allocates based on risk-adjusted returns
   - Emits: `DecisionRationale` event with calculation hash

4. **Validate with DAO** (on-chain)
   - Checks max single protocol constraint
   - Checks minimum diversification
   - Emits: `ConstraintsValidated` event

5. **Execute on StrategyRouter** (on-chain)
   - RiskEngine calls `StrategyRouter.update_allocation()`
   - RiskEngine is authorized caller (no user permissions needed)
   - Emits: `AllocationProposed` and `AllocationExecuted` events

6. **Store Decision** (on-chain)
   - Full decision record with all inputs/outputs
   - Links to block number and timestamp
   - Emits: Complete audit trail

### Audit Trail Events

Every step emits an event, creating a **complete on-chain audit trail**:

- `ProtocolMetricsQueried` - Risk scores calculated
- `APYQueried` - APY values fetched
- `DecisionRationale` - Calculation details and hash
- `ConstraintsValidated` - DAO validation results
- `AllocationProposed` - Decision proposed
- `AllocationExecuted` - Execution confirmed
- `PerformanceRecorded` - Performance linked to decision

### Performance Tracking

Added `record_performance_snapshot()` to link performance to decisions:
- Tracks total value, protocol values, yields
- Calculates performance delta vs previous snapshot
- Links to `decision_id` for full traceability

**Result:** You can now see "Decision #5 → +5% yield" or "Decision #7 → -2% yield"

### Frontend Integration

Created `useRiskEngineOrchestration()` hook:
- Calls `propose_and_execute_allocation()` directly from frontend
- Handles transaction signing and confirmation
- Fetches decision record after execution
- Updates UI with AI-managed allocation

**Changed UI:**
- Removed manual allocation sliders (for AI-managed mode)
- Added "🤖 AI Risk Engine: Orchestrate Allocation" button
- Shows decision history with full audit trail
- Displays performance linked to decisions

### Backend API Updates

Added `/orchestrate-allocation` endpoint:
- Accepts protocol metrics
- Returns orchestration response structure
- Note: Actual execution happens on-chain via frontend (requires account)

### What's Next

1. **On-Chain APY Queries:**
   - Integrate JediSwap pool contracts for real-time APY
   - Integrate Ekubo Price Fetcher/Oracle for real-time APY
   - Currently using stored values updated by keepers

2. **Keeper Service:**
   - Periodically call `propose_and_execute_allocation()`
   - Update APY values via `update_protocol_apy()`
   - Monitor performance and trigger rebalancing

3. **Full Decision History:**
   - Currently storing latest decision (MVP)
   - Can expand to full history with Map storage
   - Index by block number for efficient queries

4. **Performance Analytics:**
   - Link decisions to performance changes
   - Show "what decision caused this performance"
   - Build recommendation engine based on historical decisions

### Key Learnings

1. **On-Chain Orchestration is Powerful:**
   - Every step is auditable
   - No trust required in backend
   - SHARP automatically proves computations

2. **Events are Your Friend:**
   - Rich event structure enables full audit trail
   - Can reconstruct entire flow from events
   - Perfect for analytics and debugging

3. **User Experience Matters:**
   - Users shouldn't need to understand Cairo
   - Hide complexity behind simple "AI Orchestrate" button
   - Show results in human-readable format

4. **Storage Trade-offs:**
   - Map storage is complex in Cairo
   - For MVP, storing latest is sufficient
   - Can expand to full history later

### Files Changed

**Contracts:**
- `contracts/src/risk_engine.cairo` - Added orchestration function and events
- `contracts/src/strategy_router_v2.cairo` - Added performance tracking

**Frontend:**
- `frontend/src/hooks/useRiskEngineOrchestration.ts` - New orchestration hook
- `frontend/src/components/Dashboard.tsx` - Updated to use AI orchestration

**Backend:**
- `backend/app/api/routes/risk_engine.py` - Added orchestration endpoint

**Documentation:**
- `docs/DEV_LOG.md` - This entry

---

*Updated December 2025*

**From computation to settlement, everything is on-chain and auditable.** 🔺

