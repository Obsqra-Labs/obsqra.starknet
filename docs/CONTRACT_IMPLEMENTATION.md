# Cairo Contract Implementation Notes

**Date:** December 5, 2025  
**Status:** In Progress

## Overview

This document tracks the implementation of Cairo contracts for Obsqra.starknet, including fixes, patterns, and learnings.

## Contracts

### 1. RiskEngine.cairo

**Purpose:** On-chain risk scoring and allocation calculation

**Key Functions:**
- `calculate_risk_score()` - Multi-factor risk calculation
- `calculate_allocation()` - Risk-adjusted allocation percentages
- `verify_constraints()` - Validate allocation against constraints

**Implementation Notes:**
- Uses felt252 for all numeric values
- Integer division: multiply first, then divide for precision
- Comparison operations work directly with felt252
- Mutable variables require `let mut` syntax

**Status:** ✅ Compiles successfully

### 2. StrategyRouter.cairo

**Purpose:** Multi-protocol routing and rebalancing

**Key Functions:**
- `update_allocation()` - Update protocol allocations
- `get_allocation()` - Read current allocations
- `accrue_yields()` - Track yield accrual (TODO)

**Implementation Notes:**
- Storage access requires `StoragePointerWriteAccess` and `StoragePointerReadAccess` traits
- View functions use `#[external(v0)]` instead of `#[view]` in Cairo 2.0
- Events are properly defined with `#[derive(Drop, starknet::Event)]`

**Status:** ✅ Compiles successfully

### 3. DAOConstraintManager.cairo

**Purpose:** Governance constraints and validation

**Key Functions:**
- `set_constraints()` - Update DAO-defined constraints
- `validate_allocation()` - Verify allocation meets constraints
- `get_constraints()` - Read current constraints

**Implementation Notes:**
- Access control via owner check
- Constraint validation logic matches Python implementation
- Uses same diversification counting logic as RiskEngine

**Status:** ✅ Compiles successfully

## Cairo 2.0 Patterns Learned

### Storage Access
```cairo
use starknet::storage::StoragePointerWriteAccess;
use starknet::storage::StoragePointerReadAccess;

// Write
self.owner.write(owner);

// Read
let owner = self.owner.read();
```

### Division Operations
```cairo
// Integer division: multiply first for precision
let result = (value * multiplier) / divisor;
```

### Comparisons
```cairo
// Direct comparison works with felt252
if value > threshold {
    // ...
}
```

### Mutable Variables
```cairo
let mut count = 0;
count += 1;
```

### Return Values
```cairo
// Last expression is returned (no return keyword needed)
fn get_value() -> felt252 {
    value  // This is returned
}
```

### View Functions
```cairo
// Use #[external(v0)] instead of #[view]
#[external(v0)]
fn get_value(ref self: ContractState) -> felt252 {
    self.value.read()
}
```

## Testing

Tests are located in `contracts/tests/`:
- `test_risk_engine.cairo`
- `test_strategy_router.cairo`
- `test_dao_constraints.cairo`

Run tests with:
```bash
cd contracts
snforge test
```

## Next Steps

1. ✅ Fix compilation errors
2. ⏳ Write comprehensive unit tests
3. ⏳ Implement integration tests
4. ⏳ Add error handling and edge cases
5. ⏳ Optimize gas costs
6. ⏳ Document all functions

## References

- [Cairo Book](https://book.cairo-lang.org/)
- [Starknet Foundry](https://foundry-rs.github.io/starknet-foundry/)
- [Scarb Documentation](https://docs.swmansion.com/scarb/)

