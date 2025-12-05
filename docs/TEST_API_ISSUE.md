# Test API Issue

## Problem

The `declare` and `declare_contract` functions are not found in snforge_std v0.53.0.

## Current Errors

- `error[E0006]: Identifier not found` for `declare_contract`
- `error[E0006]: Identifier not found` for `ContractClassTrait`
- Dispatchers not visible (even with `pub trait`)

## Possible Solutions

1. **Check snforge_std v0.53.0 API** - The function name might be different
2. **Use different import path** - Maybe it's in a different module
3. **Use macro instead of function** - `declare!` macro pattern
4. **Check if we need to use `declare` via trait method** - Different access pattern

## Next Steps

1. Check actual snforge_std v0.53.0 source/docs
2. Try alternative patterns
3. Consider using direct contract deployment without declare

## Progress

- Errors: 41 → 13 (68% reduction)
- Main blocker: `declare`/`declare_contract` function not found

