# Deposit Separation Architecture - Fixed Contract

## What We Found

**Contract that worked:**
- Address: `0x01888e3f3d6cd137e63ff1a090a1e2c9ed5754162a8d5739364aba657fab20e4`
- Class Hash: `0x0783c26c976b6bf96830f7efef3bc035b50adbac90216d4ecc54e310d25e365f`
- **Deposits worked** - Frontend could call `deposit()` successfully
- **Protocol integration failed** - But deposits succeeded, funds got locked

## The Problem

The original `deposit()` function tried to do everything in one transaction:
1. Transfer ETH from user ✅ (This worked!)
2. Swap ETH → STRK ❌ (This failed)
3. Add liquidity to JediSwap ❌ (This failed)
4. Deposit to Ekubo ❌ (This failed)

**Result:** ETH got transferred but protocol integration failed, leaving funds locked.

## The Solution

**Separate deposits from protocol integration into two distinct actions:**

### 1. `deposit()` - Simple, Reliable
```cairo
fn deposit(ref self: ContractState, amount: u256) {
    // ONLY transfers funds from user to contract
    token.transfer_from(caller, contract_addr, amount);
    
    // Track deposits
    total_deposits += amount;
    pending_deposits += amount;  // Funds waiting to be deployed
    
    // Emit event
    emit Deposit { user, amount, timestamp };
}
```

**What it does:**
- ✅ Transfers funds from user to contract
- ✅ Tracks total deposits
- ✅ Tracks pending deposits (funds waiting to be deployed)
- ✅ Emits deposit event
- ❌ **NO protocol integration** - That's separate!

**Why it works:**
- Simple, single operation
- No external protocol calls
- Can't fail due to protocol issues
- Reliable and fast

### 2. `deploy_to_protocols()` - Separate Action
```cairo
fn deploy_to_protocols(ref self: ContractState) {
    // Only owner/risk_engine can call (or make public)
    assert(caller == owner || caller == risk_engine, 'Unauthorized');
    
    let pending = pending_deposits.read();
    assert(pending > 0, 'No pending deposits');
    
    // Reset pending (we're deploying them)
    pending_deposits.write(0);
    
    // Calculate allocation
    let jediswap_amount = (pending * jediswap_pct) / 10000;
    let ekubo_amount = (pending * ekubo_pct) / 10000;
    
    // Deploy to JediSwap (swap, approve, add liquidity)
    // Deploy to Ekubo (swap, approve, deposit)
    
    emit ProtocolsDeployed { jediswap_amount, ekubo_amount, timestamp };
}
```

**What it does:**
- ✅ Takes pending deposits
- ✅ Deploys them to protocols (JediSwap + Ekubo)
- ✅ All protocol integration code is here
- ✅ Can be called separately by backend/orchestrator
- ✅ Can retry if it fails (deposits are already safe)

**Why it works:**
- Separate from user deposits
- Can be called by backend/orchestrator
- Can retry if protocol calls fail
- Deposits are already safe in contract

## New Architecture

### Flow 1: User Deposits (Frontend)
```
User → Frontend → deposit() → Contract stores funds → ✅ Success
```

### Flow 2: Protocol Deployment (Backend/Orchestrator)
```
Backend → deploy_to_protocols() → Swap ETH→STRK → Add liquidity → ✅ Success
```

### Combined Flow
```
1. User deposits ETH → deposit() → Funds stored ✅
2. Backend detects pending deposits → deploy_to_protocols() → Protocols ✅
3. Funds earning yield! 🎉
```

## Key Benefits

1. **Deposits always work** - No protocol integration to fail
2. **Funds are safe** - Even if protocol deployment fails, deposits are stored
3. **Retryable** - Can retry protocol deployment without affecting deposits
4. **Separate concerns** - User deposits vs. protocol deployment
5. **Backend orchestration** - Backend can control when to deploy

## Contract Changes

### Interface Updates
```cairo
pub trait IStrategyRouterV2<TContractState> {
    // User deposits (simple, no protocol integration)
    fn deposit(ref self: TContractState, amount: u256);
    
    // Protocol deployment (separate action)
    fn deploy_to_protocols(ref self: ContractState);
    
    // ... other functions
}
```

### Storage Updates
```cairo
struct Storage {
    total_deposits: u256,      // Total deposits ever made
    pending_deposits: u256,    // Funds waiting to be deployed
    // ... other storage
}
```

### Events
```cairo
enum Event {
    Deposit: Deposit,                    // User deposited funds
    ProtocolsDeployed: ProtocolsDeployed, // Funds deployed to protocols
    // ... other events
}
```

## Frontend Changes Needed

### Current (Broken)
```typescript
// Frontend calls deposit() which tries to do everything
await contract.deposit(amount);  // ❌ Fails if protocol integration fails
```

### New (Working)
```typescript
// Step 1: User deposits (always works)
await contract.deposit(amount);  // ✅ Always succeeds

// Step 2: Backend deploys (separate action)
// Backend calls deploy_to_protocols() separately
// Or frontend can call it if user has permission
```

## Backend Integration

The backend can now:
1. **Monitor deposits** - Watch for `Deposit` events
2. **Deploy to protocols** - Call `deploy_to_protocols()` when ready
3. **Retry on failure** - If deployment fails, retry without affecting deposits
4. **Batch deployments** - Deploy multiple deposits at once

## Next Steps

1. ✅ **Contract modified** - Deposits separated from protocol integration
2. ⏳ **Compile contract** - Test compilation
3. ⏳ **Deploy new contract** - Deploy with separated functions
4. ⏳ **Update frontend** - Use new `deposit()` (simple, no protocol calls)
5. ⏳ **Update backend** - Add `deploy_to_protocols()` orchestration
6. ⏳ **Test** - Verify deposits work, then protocol deployment

## Summary

**Before:** `deposit()` tried to do everything → Failed when protocol integration failed → Funds locked

**After:** `deposit()` only accepts funds → Always works → `deploy_to_protocols()` handles protocol integration separately → Can retry if needed

**Result:** Deposits work reliably, protocol deployment is separate and retryable! 🎉

