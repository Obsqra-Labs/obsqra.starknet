# Calldata Format Analysis

## Current Format

The calldata is correctly flattened:
- jediswap_metrics: 5 felt252 values
- ekubo_metrics: 5 felt252 values  
- jediswap_proof_fact: 1 felt252
- ekubo_proof_fact: 1 felt252
- expected_jediswap_score: 1 felt252
- expected_ekubo_score: 1 felt252
- fact_registry_address: 1 felt252 (ContractAddress)

**Total: 15 elements** - This should be fine.

## "Input too long" Error

The error suggests the account contract is rejecting the calldata. Possible causes:

1. **Account contract limitation** - Some account contracts have calldata size limits
2. **Struct serialization** - Maybe Cairo expects a different format
3. **Selector mismatch** - Wrong function selector

## Next Steps

1. Verify backend is using correct RiskEngine address
2. Check if account contract has calldata size limits
3. Test with simpler call first (fewer parameters)
4. Verify function selector is correct
