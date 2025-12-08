# 🔌 Protocol Integration Guide

## 📊 **Current Status**

### What Your Contracts Do NOW:
✅ **Store protocol addresses** - Nostra, zkLend, Ekubo  
✅ **Track allocations** - 33.33% / 33.33% / 33.34%  
✅ **Calculate risk scores** - Working AI risk analysis  
✅ **Enforce DAO constraints** - Max single protocol, min diversification  

### What They DON'T Do Yet:
❌ **Actually deposit funds** into protocols  
❌ **Withdraw from protocols**  
❌ **Accrue real yields**  
❌ **Rebalance positions**  

**Your `accrue_yields` function literally says:**
```cairo
fn accrue_yields(ref self: ContractState) {
    // TODO: Implement yield accrual logic
    let total_yield = 0;
    // ...
}
```

---

## 🎯 **Three Integration Paths**

### **Path 1: Testnet Integration (Recommended Now)** 🧪

Some protocols have Sepolia testnet deployments:

#### **Ekubo** - ✅ Likely on Sepolia
- Ekubo is one of the most active testnet DEXs
- Search for: "Ekubo Sepolia contracts" or check their docs
- https://docs.ekubo.org/ (check for testnet section)

#### **Nostra** - ❓ Check Availability
- Nostra Finance testnet deployment status unclear
- https://docs.nostra.finance/

#### **zkLend** - ❓ Check Availability  
- zkLend testnet status needs verification
- https://docs.zklend.com/

**What you can do:**
1. Find testnet contract addresses
2. Update your StrategyRouter with real addresses
3. Implement actual deposit/withdraw logic
4. Test with testnet tokens

---

### **Path 2: Mock Contracts (Best for Testing)** 🎭

Create simple mock contracts that simulate the protocols:

```cairo
#[starknet::contract]
mod MockLendingProtocol {
    use starknet::ContractAddress;
    
    #[storage]
    struct Storage {
        balances: LegacyMap<ContractAddress, u256>,
        apy: u256, // Mock APY
    }
    
    #[external(v0)]
    fn deposit(ref self: ContractState, amount: u256) {
        let caller = get_caller_address();
        let current = self.balances.read(caller);
        self.balances.write(caller, current + amount);
    }
    
    #[external(v0)]
    fn withdraw(ref self: ContractState, amount: u256) -> u256 {
        let caller = get_caller_address();
        let balance = self.balances.read(caller);
        assert(balance >= amount, 'Insufficient balance');
        
        // Simulate yield accrual
        let yield_amount = amount * self.apy.read() / 10000;
        let total_withdrawal = amount + yield_amount;
        
        self.balances.write(caller, balance - amount);
        total_withdrawal
    }
    
    #[external(v0)]
    fn get_balance(self: @ContractState, user: ContractAddress) -> u256 {
        self.balances.read(user)
    }
}
```

**Benefits:**
- Full control
- Can simulate any behavior
- Test yield strategies
- No external dependencies

---

### **Path 3: Mainnet Only** 

Wait until mainnet deployment for real protocol integration.

**Pros:**
- Real liquidity
- Actual yields
- Production protocols

**Cons:**
- Can't test beforehand
- Higher risk
- Real money at stake

---

## 🛠️ **How to Add Real Integration**

### Step 1: Define Protocol Interfaces

```cairo
// contracts/src/interfaces/lending_protocol.cairo
#[starknet::interface]
pub trait ILendingProtocol<TContractState> {
    fn deposit(ref self: TContractState, token: ContractAddress, amount: u256);
    fn withdraw(ref self: TContractState, token: ContractAddress, amount: u256) -> u256;
    fn get_balance(self: @TContractState, user: ContractAddress, token: ContractAddress) -> u256;
    fn get_apy(self: @TContractState, token: ContractAddress) -> u256;
}

#[starknet::interface]
pub trait IDexProtocol<TContractState> {
    fn add_liquidity(ref self: TContractState, token_a: ContractAddress, token_b: ContractAddress, amount_a: u256, amount_b: u256);
    fn remove_liquidity(ref self: TContractState, pool_id: felt252, lp_amount: u256) -> (u256, u256);
    fn get_pool_balance(self: @TContractState, pool_id: felt252) -> u256;
}
```

### Step 2: Implement Real Integration in StrategyRouter

```cairo
use interfaces::lending_protocol::{ILendingProtocolDispatcher, ILendingProtocolDispatcherTrait};

#[external(v0)]
fn deposit_to_protocols(
    ref self: ContractState,
    token: ContractAddress,
    total_amount: u256
) {
    let nostra_amount = (total_amount * self.nostra_allocation.read().into()) / 10000;
    let zklend_amount = (total_amount * self.zklend_allocation.read().into()) / 10000;
    let ekubo_amount = (total_amount * self.ekubo_allocation.read().into()) / 10000;
    
    // Deposit to Nostra
    let nostra = ILendingProtocolDispatcher { 
        contract_address: self.nostra_address.read() 
    };
    nostra.deposit(token, nostra_amount);
    
    // Deposit to zkLend
    let zklend = ILendingProtocolDispatcher { 
        contract_address: self.zklend_address.read() 
    };
    zklend.deposit(token, zklend_amount);
    
    // Add liquidity to Ekubo
    // ... implementation
}

#[external(v0)]
fn accrue_yields(ref self: ContractState) -> u256 {
    let nostra = ILendingProtocolDispatcher { 
        contract_address: self.nostra_address.read() 
    };
    let zklend = ILendingProtocolDispatcher { 
        contract_address: self.zklend_address.read() 
    };
    
    // Get current balances (includes accrued yields)
    let nostra_balance = nostra.get_balance(get_contract_address(), STRK_TOKEN);
    let zklend_balance = zklend.get_balance(get_contract_address(), STRK_TOKEN);
    
    let total_yield = nostra_balance + zklend_balance;
    
    self.emit(YieldsAccrued {
        total_yield: total_yield.try_into().unwrap(),
        timestamp: get_block_timestamp(),
    });
    
    total_yield
}
```

---

## 📝 **What You Can Do RIGHT NOW**

### Option A: Find Testnet Addresses ✅
```bash
# Research and find:
- Nostra Sepolia contract addresses
- zkLend Sepolia contract addresses  
- Ekubo Sepolia contract addresses

# Update StrategyRouter constructor params
# Redeploy with real testnet addresses
```

### Option B: Deploy Mock Contracts ✅
```bash
# Create mock_lending.cairo
# Create mock_dex.cairo
# Deploy mocks to Sepolia
# Point StrategyRouter to mocks
# Test full flow with fake yields
```

### Option C: Just Test What You Have ✅
```bash
# Your current contracts work for:
- Tracking allocations
- Calculating risk scores
- Enforcing constraints
- Frontend interaction

# Add real integration later!
```

---

## 🎯 **Recommended Approach**

### Phase 1: NOW (Testnet with Mocks)
1. ✅ Deploy mock lending protocol
2. ✅ Deploy mock DEX
3. ✅ Update StrategyRouter with mock addresses
4. ✅ Implement full deposit/withdraw flow
5. ✅ Test via frontend
6. ✅ Simulate yields

### Phase 2: Pre-Mainnet
1. Find real testnet protocol addresses OR
2. Wait for mainnet and integrate directly

### Phase 3: Mainnet
1. Deploy contracts with real protocol addresses
2. Audit integration code
3. Start with small amounts
4. Scale up gradually

---

## 💡 **Key Insight**

**You DON'T need real protocol integration to:**
- ✅ Test your frontend
- ✅ Test risk calculations
- ✅ Test DAO governance
- ✅ Test wallet connections
- ✅ Demo the system

**You DO need it to:**
- ❌ Actually earn yields
- ❌ Deploy real user funds
- ❌ Generate real returns

**Bottom Line**: Mock contracts give you 90% of testing capability with 10% of the complexity!

---

##  **Want Me To Build Mock Contracts Now?**

I can create:
1. `MockNostra.cairo` - Simulates Nostra lending
2. `MockZkLend.cairo` - Simulates zkLend lending
3. `MockEkubo.cairo` - Simulates Ekubo DEX
4. Updated `StrategyRouter` with full integration
5. Deploy script for all of them

These mocks will:
- Accept deposits
- Return withdrawals + simulated yield
- Track balances
- Let you test the full flow

**Want me to build this?** It'll take about 30 minutes and you'll have a fully working (simulated) system! 🎯

