# StrategyRouter Contract Reference

Complete reference for the StrategyRouter v3.5 contract, including address, interface, allocation execution, protocol integration, and events.

## Contract Address

**Sepolia Testnet:**
```
0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b
```

**Explorer:**
- Starkscan: https://sepolia.starkscan.co/contract/0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b

## Interface Definition

```cairo
#[starknet::interface]
pub trait IStrategyRouterV35<TContractState> {
    fn update_allocation(
        ref self: TContractState,
        jediswap_pct: felt252,
        ekubo_pct: felt252
    );
    
    fn deposit(ref self: TContractState, amount: u256);
    fn withdraw(ref self: TContractState, amount: u256) -> u256;
    fn get_user_balance(self: @TContractState, user: ContractAddress) -> u256;
    
    fn deploy_to_protocols(ref self: TContractState);
    fn accrue_yields(ref self: TContractState) -> u256;
    fn rebalance(ref self: TContractState);
    
    // MIST.cash Privacy Integration
    fn commit_mist_deposit(ref self: TContractState, commitment_hash: felt252, expected_amount: u256);
    fn reveal_and_claim_mist_deposit(ref self: TContractState, secret: felt252) -> (ContractAddress, u256);
}
```

## Key Functions

### update_allocation

Updates allocation percentages across protocols (RiskEngine only).

**Parameters:**
- `jediswap_pct`: JediSwap allocation percentage (0-10000)
- `ekubo_pct`: Ekubo allocation percentage (0-10000)

**Access Control:** RiskEngine contract only

**Process:**
1. Verify caller is RiskEngine
2. Update allocation percentages
3. Rebalance funds
4. Emit events

### deposit

User deposits STRK tokens into the strategy.

**Parameters:**
- `amount`: Deposit amount in STRK (u256)

**Process:**
1. Transfer STRK from user
2. Update user balance
3. Update total deposited
4. Does NOT automatically deploy to protocols

### withdraw

User withdraws funds plus accrued yield.

**Parameters:**
- `amount`: Withdrawal amount in STRK (u256)

**Returns:**
- `u256`: Actual withdrawal amount

**Process:**
1. Calculate proportional amounts from protocols
2. Withdraw from JediSwap and Ekubo
3. Transfer STRK + yield to user
4. Update user balance

### deploy_to_protocols

Deploys funds to protocols based on current allocation (separate action).

**Process:**
1. Read current allocation percentages
2. Allocate to JediSwap
3. Allocate to Ekubo
4. Create liquidity positions
5. Track positions

## Protocol Integration

### JediSwap Integration

**Functions:**
- Swap tokens
- Add liquidity
- Remove liquidity
- Collect fees
- Manage NFT positions

**Addresses:**
- Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- NFT Manager: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`

### Ekubo Integration

**Functions:**
- Add concentrated liquidity
- Remove liquidity
- Collect fees
- Manage positions

**Address:**
- Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`

## MIST.cash Privacy Integration

### commit_mist_deposit

Commits a private deposit using hash commitment.

**Parameters:**
- `commitment_hash`: Pedersen hash of (secret, amount)
- `expected_amount`: Expected deposit amount

**Process:**
1. Store commitment hash
2. Store expected amount
3. Emit commitment event
4. No funds transferred yet

### reveal_and_claim_mist_deposit

Reveals secret and claims committed deposit.

**Parameters:**
- `secret`: Secret used in commitment

**Returns:**
- `(ContractAddress, u256)`: Depositor address and amount

**Process:**
1. Calculate commitment hash from secret
2. Verify commitment exists
3. Transfer funds
4. Mark as claimed

## Events

### Deposit

```cairo
event Deposit {
    user: ContractAddress,
    amount: u256,
    total_deposited: u256
}
```

### Withdrawal

```cairo
event Withdrawal {
    user: ContractAddress,
    amount: u256,
    yield: u256
}
```

### AllocationUpdated

```cairo
event AllocationUpdated {
    jediswap_pct: felt252,
    ekubo_pct: felt252,
    decision_id: felt252
}
```

## Storage Layout

```cairo
struct Storage {
    owner: ContractAddress,
    risk_engine: ContractAddress,
    jediswap_router: ContractAddress,
    ekubo_core: ContractAddress,
    total_deposited: u256,
    jediswap_pct: felt252,
    ekubo_pct: felt252,
    user_balances: Map<ContractAddress, u256>,
    // ... protocol positions, yields, etc.
}
```

## Usage Examples

### Deposit

```python
from starknet_py.contract import Contract

contract = await Contract.from_address(
    address=strategy_router_address,
    provider=provider
)

result = await contract.functions["deposit"].invoke(
    amount=1000000000000000000,  # 1 STRK
    max_fee=max_fee
)
```

### Withdraw

```python
result = await contract.functions["withdraw"].invoke(
    amount=500000000000000000,  # 0.5 STRK
    max_fee=max_fee
)
```

## Access Control

**Owner Functions:**
- Update protocol addresses
- Update slippage tolerance
- Set MIST chamber

**RiskEngine Only:**
- `update_allocation()`: Only RiskEngine can call

**Public Functions:**
- `deposit()`: Anyone can deposit
- `withdraw()`: Users can withdraw their funds
- `get_user_balance()`: Public query

## Next Steps

- **[ModelRegistry](03-model-registry.md)** - Model provenance contract
- **[DAO Constraint Manager](04-dao-constraint-manager.md)** - Governance contract
- **[Architecture: Smart Contracts](../03-architecture/02-smart-contracts.md)** - Contract architecture

---

**StrategyRouter Summary:** Fund management and protocol execution contract with MIST.cash privacy integration, handling deposits, withdrawals, and allocation execution.
