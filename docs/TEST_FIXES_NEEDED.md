# Test Fixes Needed

## Current Issues

1. **Dispatcher Visibility**: Dispatchers are auto-generated from interfaces but not accessible
2. **Deployment Syntax**: Need to use snforge's `declare()` and `deploy()` pattern
3. **Deprecated Syntax**: `contract_address_const` is deprecated
4. **Comparison Operations**: `felt252` doesn't support `>=` and `<=` directly

## Solutions

### 1. Dispatcher Access
Dispatchers are auto-generated from `#[starknet::interface]` traits. They should be accessible via:
- `use obsqra_contracts::module_name::DispatcherName;`

### 2. Deployment Pattern
Use snforge's deployment pattern:
```cairo
let declared = declare("ContractName").unwrap();
let (contract_address, _) = deploy(@declared).unwrap();
```

### 3. Address Creation
Replace deprecated `contract_address_const` with proper address creation or use test helpers.

### 4. Comparisons
Use u256 conversions for comparisons (already implemented in helpers).

## Status

- ✅ Comparison helpers created
- ✅ Deployment pattern updated in test_risk_engine.cairo
- ⏳ Need to update test_strategy_router.cairo and test_dao_constraints.cairo
- ⏳ Need to verify dispatcher imports work

## Next Steps

1. Verify dispatcher imports are correct
2. Update all test files to use `declare()` and `deploy()`
3. Remove deprecated `contract_address_const` usage
4. Run full test suite

