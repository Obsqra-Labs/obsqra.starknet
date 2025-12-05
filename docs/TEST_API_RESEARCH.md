# Test API Research

## Current Issue

The `declare` function is not found in snforge_std v0.53.0.

## Research Findings

Based on Starknet Foundry documentation and GitHub:
- `declare` might be a macro, not a function
- May need different import path
- Could require trait methods instead of direct function calls

## Attempted Solutions

1. ✅ `declare("ContractName")` - Not found
2. ✅ `declare_contract("ContractName")` - Not found  
3. ✅ `declare("ContractName").unwrap()` - Not found
4. ⏳ Need to check if it's a macro: `declare!("ContractName")`

## Next Steps

1. Check if `declare` is a procedural macro
2. Look for alternative deployment patterns
3. Check if contracts can be deployed directly without explicit declaration in tests
4. Review snforge_std source code for correct API

## References

- [Starknet Foundry GitHub](https://github.com/foundry-rs/starknet-foundry)
- [Starknet Documentation](https://docs.starknet.io/build/quickstart/appendix)
- [Cairo Book](https://www.starknet.io/cairo-book/)

