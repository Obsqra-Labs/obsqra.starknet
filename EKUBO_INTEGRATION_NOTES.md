# Ekubo Integration Notes

## 🔍 Key Discovery

From the [Ekubo documentation](https://docs.ekubo.org/integration-guides/reference/contract-addresses):

### Contract Address Confirmed ✅
- **Core (Sepolia)**: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
- This matches our configuration!

### Important: Ekubo Uses a Callback System ⚠️

Ekubo does **NOT** work like a simple `deposit_liquidity()` function call. Instead:

1. **Extension Registration**: Contracts must register as "extensions" with Ekubo Core
2. **Callback Pattern**: Ekubo uses a `locked` callback function that your contract must implement
3. **Different Architecture**: This is why `ENTRYPOINT_NOT_FOUND` occurred - our interface was incorrect

## What This Means

Our current interface in `ekubo.cairo`:
```cairo
fn deposit_liquidity(
    ref self: TContractState,
    token0: ContractAddress,
    token1: ContractAddress,
    amount0: u256,
    amount1: u256,
    fee: u128
) -> u256;
```

**This function doesn't exist on Ekubo Core!**

## Correct Integration Approach

Based on Ekubo's architecture:

1. **Register as Extension**: Your contract must call `registerExtension()` on Ekubo Core
2. **Implement `locked` Callback**: Ekubo will call your contract's `locked()` function
3. **Use Router**: For simpler operations, use Ekubo Router contracts instead of Core directly

## Next Steps

1. **Check Ekubo Router**: The Router contracts might have simpler interfaces
   - Router V3.0.13 (Sepolia): `0x0045f933adf0607292468ad1c1dedaa74d5ad166392590e72676a34d01d7b763`
   - Router V3.0.3 (Sepolia): `0x050d4da9f66589eadaa1d5e31cf73b08ac1a67c8b4dcd88e6fd4fe501c628af2`

2. **Review Ekubo Examples**: Check the `ekubo-101` repository for callback implementation examples

3. **Update Interface**: We need to implement the proper Ekubo extension pattern, not direct Core calls

## Resources

- [Ekubo Contract Addresses](https://docs.ekubo.org/integration-guides/reference/contract-addresses)
- [Ekubo Core Interfaces](https://docs.ekubo.org/integration-guides/reference/core-interfaces) (need to check this)
- [Ekubo Integration Examples](https://github.com/0xEniotna/ekubo-101)

