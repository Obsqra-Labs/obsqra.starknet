# DAO Constraint Manager Contract Reference

Complete reference for the DAOConstraintManager contract, including address, constraint management, governance parameters, and validation logic.

## Contract Address

**Sepolia Testnet:**
```
0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856
```

**Explorer:**
- Starkscan: https://sepolia.starkscan.co/contract/0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856

## Interface Definition

```cairo
#[starknet::interface]
trait IDAOConstraintManager<TContractState> {
    fn get_max_single(self: @TContractState) -> felt252;
    fn get_min_diversification(self: @TContractState) -> felt252;
    fn get_max_volatility(self: @TContractState) -> felt252;
    fn get_min_liquidity(self: @TContractState) -> felt252;
    
    fn update_constraints(
        ref self: TContractState,
        max_single: felt252,
        min_diversification: felt252,
        max_volatility: felt252,
        min_liquidity: felt252
    );
}
```

## Key Functions

### get_max_single

Returns the maximum allocation per protocol.

**Returns:**
- `felt252`: Maximum single protocol allocation (0-10000)

**Example:** `7000` = 70% maximum

### get_min_diversification

Returns the minimum diversification requirement.

**Returns:**
- `felt252`: Minimum diversification (0-10000)

**Example:** `3000` = 30% minimum spread

### get_max_volatility

Returns the maximum volatility threshold.

**Returns:**
- `felt252`: Maximum volatility (0-10000)

**Example:** `5000` = 50% maximum volatility

### get_min_liquidity

Returns the minimum liquidity requirement.

**Returns:**
- `felt252`: Minimum liquidity score (1-5)

**Example:** `2` = Minimum liquidity score of 2

### update_constraints

Updates all governance constraints (owner only).

**Parameters:**
- `max_single`: Maximum single protocol allocation
- `min_diversification`: Minimum diversification
- `max_volatility`: Maximum volatility
- `min_liquidity`: Minimum liquidity

**Access Control:** Owner only

## Constraint Types

### Allocation Constraints

**max_single_protocol:**
- Limits maximum allocation to any single protocol
- Prevents over-concentration
- Example: 70% = no protocol can exceed 70%

**min_diversification:**
- Ensures minimum spread across protocols
- Prevents over-concentration
- Example: 30% = at least 30% must be in other protocol

### Risk Constraints

**max_volatility:**
- Maximum acceptable volatility
- Filters out high-risk protocols
- Example: 50% = protocols with >50% volatility rejected

**min_liquidity:**
- Minimum liquidity requirement
- Ensures sufficient liquidity
- Example: 2 = minimum liquidity score of 2

## Storage Layout

```cairo
struct Storage {
    owner: ContractAddress,
    max_single: felt252,
    min_diversification: felt252,
    max_volatility: felt252,
    min_liquidity: felt252,
}
```

## Usage Examples

### Read Constraints

```python
from starknet_py.contract import Contract

contract = await Contract.from_address(
    address=dao_manager_address,
    provider=provider
)

max_single = await contract.functions["get_max_single"].call()
min_diversification = await contract.functions["get_min_diversification"].call()
max_volatility = await contract.functions["get_max_volatility"].call()
min_liquidity = await contract.functions["get_min_liquidity"].call()
```

### Update Constraints

```python
result = await contract.functions["update_constraints"].invoke(
    max_single=7000,          # 70%
    min_diversification=3000, # 30%
    max_volatility=5000,      # 50%
    min_liquidity=2,          # Score 2
    max_fee=max_fee
)
```

## Validation Logic

### In RiskEngine

**Constraint Validation:**
```cairo
// Read constraints from DAO manager
let max_single = dao_manager.get_max_single();
let min_diversification = dao_manager.get_min_diversification();

// Validate allocation
assert(jediswap_pct <= max_single, 1);
assert(ekubo_pct <= max_single, 2);
// Diversification is implicit if both are below max_single
```

## Access Control

**Owner Functions:**
- `update_constraints()`: Only owner can update

**Public Functions:**
- All getter functions: Public queries
- Transparent governance parameters

## Next Steps

- **[Fact Registry](05-fact-registry.md)** - Proof verification contract
- **[RiskEngine](01-risk-engine.md)** - Core contract
- **[Architecture: Smart Contracts](../03-architecture/02-smart-contracts.md)** - Contract architecture

---

**DAO Constraint Manager Summary:** On-chain governance parameter storage with transparent constraint management and upgradeable parameters.
