# Allocation Update Flow - Verified

## Current Flow

**✅ The flow is correct:**

1. **Frontend** → Calls `/api/v1/risk-engine/orchestrate-allocation`
2. **Backend** → Calls `RiskEngine.propose_and_execute_allocation()`
3. **RiskEngine** → Calls `StrategyRouter.update_allocation()` (line 637)
4. **StrategyRouter** → Updates allocations (RiskEngine is authorized)

## Why It Might Not Be Working

**Possible issues:**

1. **RiskEngine not authorized**: Check if RiskEngine address matches what StrategyRouter expects
   - StrategyRouter checks: `caller == owner || caller == risk_engine`
   - RiskEngine address must match `risk_engine` storage in StrategyRouter

2. **Transaction failing silently**: The backend might not be catching errors
   - Check backend logs for transaction failures
   - Verify RiskEngine transaction succeeds

3. **Transaction not confirmed**: Allocation update might be pending
   - Check if transaction is confirmed on-chain
   - Frontend might be reading before update completes

## Verification Steps

1. **Check RiskEngine address in StrategyRouter:**
   ```bash
   # Query StrategyRouter's risk_engine storage
   ```

2. **Check if RiskEngine calls are succeeding:**
   - Look at backend logs
   - Check transaction hashes
   - Verify on Starkscan

3. **Check if allocations are actually updating:**
   - Query contract after AI orchestration
   - Compare before/after values

## Next Steps

Since the flow is correct, the issue is likely:
- RiskEngine address mismatch
- Transaction failures not being caught
- Timing issue (reading before update)

**For now, let's focus on protocol integration** - that's the bigger blocker (funds not earning yield).


