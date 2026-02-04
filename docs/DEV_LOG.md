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

## December 8, 2025 - v2 Contracts Deployed (Full On-Chain Orchestration)

**v2 Contracts Deployed:**
| Contract | Address | Features |
|----------|---------|----------|
| RiskEngine v2 | `0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31` | Full on-chain orchestration, `propose_and_execute_allocation` |
| StrategyRouterV2 | `0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6` | Deposit/withdraw, performance tracking |
| DAOConstraintManager | `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` | (unchanged) |

**Previous v1 Contracts (deprecated):**
| Contract | Address |
|----------|---------|
| RiskEngine v1 | `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80` |
| StrategyRouter v1 | `0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a` |

---

## Wallet (current)

- Wallet UX: using the `obsqra.kit` wallet package for unified connect/disconnect, preferred connector, modal, and network guard rails (Argent X / Braavos via `@starknet-react/core`).
- Privacy: not included in the current build; plug in a privacy layer separately if needed.

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

## December 10, 2025: Strategy Router v3.5 - Unified Contract with MIST Integration

### The Problem: Contract Fragmentation

After deploying v2 and v3 contracts separately, we discovered a critical issue: **the frontend didn't know which contract to call**. Functions were split across versions:
- v2 had: `get_total_value_locked()`, `get_allocation()`
- v3 had: `get_protocol_tvl()`, `get_jediswap_tvl()`, `get_ekubo_tvl()`
- User balance tracking was broken (returned total deposits, not per-user)
- MIST.cash privacy integration was missing

### The Solution: Unified v3.5

Created a single, unified contract that combines everything:

**Key Improvements**:
1. **Fixed User Balance Tracking**
   - Added `user_balances: Map<ContractAddress, u256>` storage
   - `deposit()` now updates per-user balance
   - `withdraw()` checks per-user balance before allowing withdrawal
   - `get_user_balance()` returns actual per-user balance

2. **MIST.cash Privacy Integration**
   - Hash commitment pattern (Pattern 2 from research)
   - User commits hash of secret: `commit_mist_deposit(commitment_hash, expected_amount)`
   - User reveals secret when ready: `reveal_and_claim_mist_deposit(secret)`
   - Router verifies hash and claims from MIST chamber on behalf of user
   - Non-custodial: router never sees raw secret until user reveals

3. **All Functions Unified**
   - All v2 functions (backward compatible)
   - All v3 functions (TVL, yield accrual, slippage)
   - MIST functions (privacy integration)
   - Frontend intelligently queries available functions

**Contract Address**: `0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b`

**Class Hash**: `0x043acf130464d2a1325403f619a62480fd9d10a13941a81fcb2a491e2ec5bc28`

### Cairo Compilation Lessons

**Dispatcher Pattern**:
- Interfaces must be in separate files (`interfaces/mist.cairo`)
- Import both `Dispatcher` and `DispatcherTrait`
- Use: `let chamber = IMistChamberDispatcher { contract_address: addr };`

**Tuple Destructuring**:
- Cairo supports: `let (a, b) = dispatcher.call();`
- No `result.0` / `result.1` syntax (not supported)

**Doc Comments**:
- Cairo parser interprets certain words as macros
- Words like "deposit", "MIST", "transaction" in doc comments cause errors
- Solution: Use regular comments (`//`) instead of doc comments (`/** */`) for these cases

**Map Access**:
- Always use `.entry(key).read()` / `.entry(key).write()` for storage maps
- Direct `.read(key)` / `.write(key, value)` is deprecated

### Frontend Updates

- Renamed `useStrategyRouterV2` → `useStrategyRouter` (unified hook)
- Updated all components to use v3.5 ABI
- Added intelligent function detection (tries v3.5 first, falls back to v2)
- MIST functions restricted to testing panel (as requested)

### Deployment

Deployed to Sepolia using `sncast`:
```bash
sncast --account deployer deploy \
  --class-hash 0x043acf130464d2a1325403f619a62480fd9d10a13941a81fcb2a491e2ec5bc28 \
  --constructor-calldata [owner, jediswap_router, jediswap_nft, ekubo_core, ekubo_positions, risk_engine, dao_manager, asset_token, jediswap_pct, ekubo_pct, mist_chamber] \
  --network sepolia
```

**Result**: Contract successfully deployed and verified on Starkscan.

### Next Steps

1. Update frontend environment variables
2. Test MIST integration in testing panel
3. Verify user balance tracking works correctly
4. Test backward compatibility with existing frontend code

---

*Updated December 10, 2025*

**From computation to settlement, everything is on-chain and auditable.** 🔺

---

## December 12, 2025 — Proof plumbing (L2 + optional L1)

- Added ProofJob L2/L1 verification fields (fact hashes, block numbers, Atlantic query, network flag) plus Alembic migration `003_add_proof_job_l1_l2_fields.py`.
- LuminAIR service now exposes `calculate_fact_hash` (SHA-256 stub) and `export_trace` (mock pie.zip with metrics/proof) to feed Integrity/Atlantic.
- Orchestration flow: computes fact hash, verifies on L2 via Integrity Verifier, records metadata, stores L2 block on receipt, and optionally submits to Atlantic on Sepolia when configured; uses network-aware chain ID.
- Atlantic worker stub: logs enqueues and can poll Atlantic to persist L1 verification status (ready to wire into Celery/APS).
- Env/config: `STARKNET_NETWORK`, `ATLANTIC_API_KEY`, `ATLANTIC_BASE_URL` already in config; migration required (`alembic upgrade head`).

Next steps:
- Run migration; wire scheduler to call `enqueue_atlantic_status_check`/`check_and_update_atlantic_status`.
- Swap SHA-256 fact hash + mock trace export for real LuminAIR outputs.
- Continue V1.3 cleanup: frontend proof badges/real data only; remove demo; analytics endpoints for real performance.

### Additional V1.3 plumbing
- Backend analytics: added `/api/v1/analytics/performance/real` returning real portfolio/timeline from ProofJob records (no demo).
- PerformanceService hardened to use ProofJob.status for verified counts.
- Frontend hook `useRealPerformance` to consume the real performance endpoint (polls every 30s) and wired indicator into Analytics dashboard.
- LuminAIR proof parsing now captures optional `fact_hash`/`trace_path` from the Rust operator output when present (fallback to calculated hash + mock trace otherwise).
- Tests/smoke: ran `alembic upgrade head`; local TestClient calls for `/api/v1/analytics/performance/real` (200) and `/api/v1/analytics/protocol-apys` (200, defaults due to no DefiLlama match). Production service still on older code—needs restart to pick up latest changes.
- Backend restarted on 8001 with latest code. Frontend analytics dashboard now surfaces proof-backed stats (total rebalances, verified count, latest tx, period) via `useRealPerformance`.
- Frontend: fixed strict typing in execute-as-owner API route; `npm run build` now passes. Restarted Next dev server on port 3003 (0.0.0.0) to clear 404s on `_next` assets.
- Frontend copy refresh: removed prototype wording in CTA/footer; added `allowedDevOrigins` for starknet.obsqra.fi to reduce dev asset warnings.
- Frontend demo mode removed (DemoModeContext/Toggle deleted). `npm run build` re-run after removal: OK.
- Backend: added Atlantic poller (background task started in main lifespan) to check pending L1 submissions when configured; health OK; `/api/v1/analytics/performance/real` still returns 30 ProofJob entries in TestClient; protocol APY endpoint returns defaults if DefiLlama lacks Starknet pools.
- Backend rebalance history now returns L2/L1 verification metadata (fact hashes, blocks, settlement flags) to surface verification in the UI.
- Frontend ProofBadge/RebalanceHistory updated to show L2/L1 hashes and verification timestamps; `npm run build` stays green.
- Frontend Dashboard now surfaces latest proof status (L2/L1 fact hashes, verified timestamps) using a shared proof history hook; build remains green.
- Frontend production start script added (`start:3003`) and start_3003.sh now runs `next start` on 3003 (with port cleanup via fuser/ss).
- Atlantic L1 settlement configured with provided API key (.env) and backend restarted; Atlantic poller running on startup (8001).
- Added safety for fact hashes: risk_engine now requires a real fact hash from LuminAIR unless `ALLOW_FAKE_FACT_HASH=True` (set in .env for now). Backend restarted with the flag set.

### December 13, 2025 — Real fact hash + trace wrapping
- LuminAIR service now derives `fact_hash` from proof bytes when the Rust operator does not emit one (no more stub unless explicitly allowed).
- Trace export wraps any raw proof/trace into a `*.pie.zip` before Atlantic submission so the poller only ships valid zip payloads.
- Risk engine uses the derived fact hash by default; `.env` flipped `ALLOW_FAKE_FACT_HASH` to `False`.
- Backend restarted (uvicorn on 8001) with the new env; Atlantic poller still running.

### December 13, 2025 — Integration dev-log API
- Added `/api/integration-tests/dev-log` (Next route) to serve `docs/DEV_LOG.md` for the integration panel; returns markdown with no-cache headers.
- Set Atlantic submission to use `cairoVersion=cairo1` to avoid 400 errors.

### December 13, 2025 — No silent mocks, clearer proof table
- LuminAIR proof generation now fails loudly when the binary errors (no auto-mock fallback when the binary exists).
- Integration Tests panel shows a proof table (time, proof hash, tx, L2 fact, L1 fact, Atlantic query, status) for up to the last 8 proofs.
- Integrity verifier ABI inspected: available functions are `verify_proof_*` (full/initial/step/final) plus `get_verification`—no `isCairoFactValid`, so L2 verification stays pending until we pass the proper Stark proof/config payload.

### December 13, 2025 — Proof summary endpoint
- Added `/api/v1/analytics/proof-summary` returning counts (total, pending, L2 verified, L1 verified) plus the latest proof metadata for dashboards/UI panels.

### December 14, 2025 — Chosen path: Atlantic as Stone/SHARP prover
- Decision: use Atlantic as the managed Stone/SHARP gateway for the `risk_engine` Cairo program. Rationale: Atlantic can produce the Stone-style proof (VerifierConfiguration + StarkProofWithSerde) required by Integrity and can also handle L1 verification (Sepolia is free; mainnet needs credits). Swiftness is a verifier only.
- Configuration to use (historical, canonical examples): layout=`recursive`, hasher=`keccak_160_lsb`, stone_version=`stone5`, memory_verification=`strict`.
- Expected flow:
  1) Compile `contracts/src/risk_engine.cairo` to Cairo program JSON (or pie.zip).
  2) POST to `https://atlantic.api.herodotus.cloud/v1/l2/atlantic-query?apiKey=<KEY>` with `programFile=@risk_engine.json`, `cairoVersion=1`, `layout=recursive` (or `auto`), `mockFactHash=false`.
  3) Poll `GET .../atlantic-query/{id}`; download the resulting Stone proof JSON.
  4) Backend parses the proof into VerifierConfiguration + StarkProofWithSerde and calls `verify_proof_full_and_register_fact`; success sets `l2_verified_at`, revert marks FAILED.
- Notes:
  - Swiftness is installed locally for verification, but it cannot generate proofs.
  - LuminAIR/stwo proofs remain for UX/local display; Atlantic/Stone proofs are the canonical path for Integrity and L1 settlement.
  - Mainnet Atlantic runs require credits; Sepolia is free.

### December 14, 2025 — Atlantic submission attempt
- Submitted `risk_engine` program JSON to Atlantic `/atlantic-query` with `layout=recursive`, `cairoVersion=cairo1`, `result=PROOF_GENERATION`, `declaredJobSize=XS/S`, `sharpProver=stone`, `network=TESTNET`, `mockFactHash=false`.
- Response: `INSUFFICIENT_CREDITS` (cannot generate proof without credits). Blocked until credits are added or a different proving path is provided.

### December 14, 2025 — Local Stone prover build (no Docker)
- Cloned `stone-prover` and built `cpu_air_prover` locally via Bazelisk (Bazel 6.4.0) after installing `elfutils-devel` (libdw). Binary located at `stone-prover/build/bazelbin/src/starkware/main/cpu/cpu_air_prover`.
- Blocker: to generate a proof we still need Cairo trace/memory + public/private inputs. That requires running the target Cairo program in proof mode (Stone README flow via `cairo1-run`/cairo-vm). `cairo1-run` is not installed here yet.
- Next step: install `cairo-vm`/`cairo1-run`, wrap `risk_engine.cairo` into a runnable Cairo1 program (or minimal wrapper) that emits trace/memory in proof_mode, then feed those into `cpu_air_prover` to produce a Stone proof. Atlantic path remains for L1 once credits are available.

### December 15, 2025 — Stone runner hooked, risk proof still pending
- Added a minimal Cairo1 program mirroring `calculate_risk_score_internal` (`verification/risk_example.cairo`) that returns `Array<felt252>` so `proof_mode` works.
- Installed `cairo-vm/cairo1-run` and verified `cargo run --help`. Generated risk trace/memory/public/private via:
  - `cargo run verification/risk_example.cairo --layout=small|all_cairo --proof_mode --air_public_input ... --air_private_input ... --trace_file ... --memory_file ... --print_output`
  - Program output `[34]`; files are under `verification/out/` (public/private/trace/memory).
- Validated the Stone prover binary on the bundled Fibonacci example:
  - Generated fib trace/memory/public/private; `cpu_air_prover` produced `stone-prover/e2e_test/Cairo/fib_proof.json` successfully using the sample params/config.
- Risk trace → prover initially failed: `cpu_air_prover` on `risk_*` (layout `all_cairo`, `n_steps` ≈ 131,072) with sample params died (Signal 6) because FRI params didn’t match the trace size.
- Fixed by tuning params and reducing layout: regenerated artifacts with `layout=small` (`n_steps` = 8,192) and a matching params file (`verification/out/risk_small_params.json` with `fri_step_list: [3,3,3,2]`, `last_layer_degree_bound: 64`). `cpu_air_prover` now succeeds, producing `verification/out/risk_small_proof.json` (~400 KB). This confirms the prover path works once params satisfy `log2(last_layer_degree_bound) + sum(fri_step_list) = log2(n_steps) + 4`.
- Next: either tune params for the `all_cairo` trace (n_steps ≈ 131,072) or decide if the `layout=small` trace is sufficient for the Integrity/Atlantic pilot. Then run Integrity’s proof_serializer on the Stone proof and call `verify_proof_full_and_register_fact` with the canonical tuple (recursive/keccak_160_lsb/stone5/strict).

### December 15, 2025 — Integrity serializer build + first pass
- Patched the Integrity repo to build locally (vendored `size-of`/`cairo-vm`, relaxed `deny(warnings)`); `cargo build --release -p proof_serializer` now succeeds (warnings only).
- Tried serializing `verification/out/risk_small_proof.json` via `proof_serializer`; parser rejected it (“Unexpected number of interaction elements: 0”). The Stone proof likely needs additional metadata (annotations/interactions) to match the Swiftness/Integrity schema. Added an empty `annotations` field to the proof; still fails. Need to regenerate proof with Integrity-compatible settings or adapt parser expectations.
- Action items: either (a) produce a Stone proof using Integrity’s example settings/layout so the serializer accepts it, or (b) adjust/provide a wrapper that fills the expected interaction metadata before feeding the serializer. Until then, backend wiring to `verify_proof_full_and_register_fact` remains blocked on a serializer-compatible proof payload.

### December 15, 2025 — Annotated Stone proof + serializer success
- Regenerated the small trace proof with `cpu_air_prover --generate_annotations` using the tuned params (n_steps=8,192, layout=small): output `verification/out/risk_small_proof_annotated.json`.
- `proof_serializer` now accepts it and emits calldata to `verification/out/risk_small_calldata.txt` (validated end-to-end through the Integrity serializer).
- Remaining decision: whether to also tune/serialize the full `all_cairo` trace (~131k steps) or stick with the small trace for the Integrity/Atlantic pilot. Full trace is heavier but closer to production; small trace proves the pipeline and unblocks backend wiring.

### December 16, 2025 — Dual proof lanes wired (Integrity helper)
- Added `backend/app/services/proof_loader.py` to normalize both local Stone proofs and Atlantic proofs through the Integrity `proof_serializer` binary (returns felt calldata list).
- Added `IntegrityService.verify_with_calldata` to accept pre-serialized calldata (either local Stone or Atlantic). This gives us a single entrypoint for both proof sources; existing structured/dict path remains.

### December 16, 2025 — Integrity call test (small Stone proof)
- Built prefixed calldata (layout=recursive, hasher=keccak_160_lsb, stone_version=stone5, memory_verification=strict) + serialized proof from `risk_small_proof_annotated.json` -> `verification/out/risk_small_calldata_prefixed.txt` (canonical example path).
- Invoked `verify_proof_full_and_register_fact` on Sepolia Integrity verifier via starknet_py. Result: revert `invalid final_pc` (ENTRYPOINT_FAILED). Proof shape now passes serializer, but verifier rejected the proof (likely AIR/layout mismatch).
- Logged full steps/results in `docs/proving_flows.md`. Next: regenerate an Integrity-compatible proof (either tune local Stone with canonical config or use Atlantic-generated proof) and re-run the call.

### December 17, 2025 — Full-trace Stone attempt (all_cairo)
- Tried proving the full trace (layout=all_cairo, n_steps=131,072) with two param sets satisfying the FRI degree equation:
  - (64, [3,3,3,3,3], n_queries=18, pow=24) and (128, [3,3,3,3,2], n_queries=16, pow=24).
- Added a third variant: (256, [3,3,3,2], n_queries=12, pow=24). Also aborted with `Signal(6)` even with `--v=1` and `--logtostderr`.
- Retried with explicit `GLOG_log_dir=/tmp --v=2 --logtostderr=1`; still `Signal(6)` and no new logs beyond prior small-trace runs. Likely resource/AIR mismatch. Logged in proving_flows.md. Next fallback: run outside sandbox with deeper logs or pivot to Atlantic for an Integrity-compatible proof.
- Another verbose attempt with `GLOG_v=3 GLOG_logtostderr=1 --n_threads=2` still died with `Signal(6)` and produced no new prover logs (only older small-trace logs are present).
- Next options: run with richer logging outside sandbox to see the exact abort, or pivot to Atlantic to produce the Integrity proof for this circuit. Logged details in `docs/proving_flows.md`.

### December 18, 2025 — Proof visibility hardening
- Added `proof_source` field on proof jobs (luminair vs stone/atlantic) and surfaced source/error in analytics responses (rebalance-history, proof-summary).
- Orchestration now marks failed verifications as `FAILED` with error text instead of leaving them `PENDING`; metrics carry verification_error for UI.
- Waiting on Atlantic credits; kept curl template ready to resubmit once credits land.

### January 27, 2026 — OODS resolution (Stone v3 → stone6) ✅ RESOLVED

**Issue**: OODS failures when verifying Stone v3 proofs as `stone5`.

**Root Cause**: Stone v3 (`1414a545...`) produces **stone6** semantics. The public input hash calculation includes `n_verifier_friendly_commitment_layers` in stone6, but not in stone5. This mismatch causes OODS failures.

**Resolution**:
- ✅ Confirmed Stone v3 → stone6 mapping
- ✅ Updated `INTEGRITY_STONE_VERSION = "stone6"` in production config
- ✅ OODS now passes when verifying Stone v3 proofs as stone6
- ✅ Dropped Stone v2 path (no longer needed)
- ✅ Cleaned up temporary Stone v2 worktree

**Production Configuration**:
- `layout=recursive`
- `hasher=keccak_160_lsb`
- `stone_version=stone6` ← **CRITICAL: Must use stone6 for Stone v3 proofs**
- `memory_verification=strict`

**Canonical Examples**:
- Integrity's canonical example proofs use `stone5`
- Use `stone5` **only** when replaying Integrity's canonical examples
- **All Obsqra production proofs must use `stone6`**

**Files Modified**:
- `backend/app/config.py` - Updated `INTEGRITY_STONE_VERSION = "stone6"`
- `STONE_VERSION_MAPPING_ANALYSIS.md` - Documented resolution
- `docs/proving_flows.md` - Clarified canonical vs production paths
- `docs/DEV_LOG.md` - This entry (resolution logged)

**Status**: ✅ **RESOLVED** - Stone v3 → stone6 is now canonical production path
