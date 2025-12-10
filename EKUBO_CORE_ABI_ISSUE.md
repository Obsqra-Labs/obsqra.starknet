# Ekubo Core ABI Issue

## Problem

When calling `ekubo.lock()` on Ekubo Core, we get:
```
ENTRYPOINT_NOT_FOUND
Selector: 0x3489279176b907a593d4cb9a52706930afa218af038a99b0917244c62ca1fff
```

## Analysis

The selector `0x3489279176b907a593d4cb9a52706930afa218af038a99b0917244c62ca1fff` does NOT match:
- `lock`: `0x168652c307c1e813ca11cfb3a601f1cf3b22452021a5052d8b05f1f1f8a3e92`
- `Lock`: `0x2061da06d9da7c1d2a497a320750161d58a0fc1d9a008f9c4f3d1606155d86f`
- `LOCK`: `0x530b24510b924664e4cc98bd27ba37fd804f8cb2b1743b1bc15525a944ae93`
- `lock_core`: `0x99df11da23bf9c0461d072e4c7b4d309cb073447139b89127caf0d31332fbb`
- `lock_with_data`: `0x749a1bb056cf9992c18476d31329655956db8a2406141df86d426d8184f746`

## Root Cause

**We don't have the actual Ekubo Core ABI!**

Our interface definition is based on documentation patterns, but the actual function signature on Ekubo Core might be:
- Different function name
- Different parameter types
- Different parameter order
- Or requires additional parameters

## Solution Options

### Option 1: Get Actual Ekubo Core ABI
1. Check Ekubo Core contract on Starkscan: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
2. Download the ABI if available
3. Or check Ekubo's GitHub repository for interface definitions
4. Or contact Ekubo team for the exact interface

### Option 2: Use Ekubo Router
Ekubo Router contracts might have simpler interfaces:
- Router V3.0.13 (Sepolia): `0x0045f933adf0607292468ad1c1dedaa74d5ad166392590e72676a34d01d7b763`
- Router V3.0.3 (Sepolia): `0x050d4da9f66589eadaa1d5e31cf73b08ac1a67c8b4dcd88e6fd4fe501c628af2`

### Option 3: Check Ekubo Examples
- Review `ekubo-101` repository: https://github.com/0xEniotna/ekubo-101
- Look for actual interface definitions in their code

## Current Status

- ✅ Contract compiles with our interface definition
- ✅ `locked()` callback function implemented
- ✅ Storage for tracking operations added
- ❌ `lock()` call fails with ENTRYPOINT_NOT_FOUND
- ⏳ Need actual Ekubo Core ABI to proceed

## Next Steps

1. **Immediate**: Test JediSwap integration (should work)
2. **Short-term**: Get actual Ekubo Core ABI from:
   - Starkscan contract page
   - Ekubo documentation
   - Ekubo GitHub repository
   - Ekubo team/Discord
3. **Alternative**: Explore Ekubo Router for simpler integration

## Resources

- [Ekubo Contract Addresses](https://docs.ekubo.org/integration-guides/reference/contract-addresses)
- [Ekubo Core Interfaces](https://docs.ekubo.org/integration-guides/reference/core-interfaces) (need to check this)
- [Ekubo Till Pattern](https://docs.ekubo.org/integration-guides/till-pattern)
- [ekubo-101 Examples](https://github.com/0xEniotna/ekubo-101)

