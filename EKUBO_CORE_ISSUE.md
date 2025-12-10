# Ekubo Core Integration Issue

## Problem

The deployed Ekubo Core contract on Sepolia (`0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`) does not expose the `lock()` function as expected.

### Error Details

- **Error**: `ENTRYPOINT_NOT_FOUND`
- **Selector**: `0x3489279176b907a593d4cb9a52706930afa218af038a99b0917244c62ca1fff`
- **Expected selector for "lock"**: `0x168652c307c1e813ca11cfb3a601f1cf3b22452021a5052d8b05f1f1f8a3e92`
- **Mismatch**: The selectors don't match, indicating the function name or signature is different

### Root Cause

The deployed Ekubo Core contract on Sepolia appears to have a different interface than:
1. The GitHub repository (`https://github.com/EkuboProtocol/starknet-contracts`)
2. The interface we implemented based on the GitHub code

Possible reasons:
- Different contract version deployed on Sepolia
- `lock()` function not exposed publicly
- Function name or signature changed in deployed version
- Interface requires different access pattern

## Attempted Solutions

1. ✅ Updated interface to match GitHub repository exactly
2. ✅ Changed `Array` to `Span` for data parameters
3. ✅ Updated `lock()` signature: `fn lock(data: Span<felt252>) -> Span<felt252>`
4. ✅ Updated `locked()` callback: `fn locked(id: u32, data: Span<felt252>) -> Span<felt252>`
5. ✅ Updated `pay()` signature: `fn pay(token_address: ContractAddress)` (no amount)
6. ❌ Still fails with `ENTRYPOINT_NOT_FOUND`

## Alternative Approaches

### Option 1: Use Ekubo Router
- **Router Address (Sepolia)**: `0x9995855C00494d039aB6792f18e368e530DFf931`
- **Limitation**: Router is designed for swaps, not liquidity provision
- **Status**: Router also uses Core's lock pattern internally, so same issue

### Option 2: Skip Ekubo for Now
- Focus on JediSwap integration (which works)
- Add Ekubo later when Core interface is clarified
- Document that only JediSwap is active

### Option 3: Contact Ekubo Team
- Verify the correct Sepolia contract address
- Get the actual ABI/interface for Sepolia deployment
- Check if there's a different way to interact with Core

## Current Status

- ✅ Contract compiles with correct interface (based on GitHub)
- ✅ Contract deployed successfully
- ✅ Approval transactions work
- ❌ Ekubo Core `lock()` call fails
- ✅ JediSwap integration ready (not tested yet, but interface is correct)

## Next Steps

1. **Immediate**: Focus on JediSwap integration testing
2. **Short-term**: Contact Ekubo team or check their documentation for Sepolia-specific interface
3. **Long-term**: Implement Ekubo once Core interface is clarified

## Resources

- [Ekubo GitHub Repository](https://github.com/EkuboProtocol/starknet-contracts)
- [Ekubo Documentation](https://docs.ekubo.org/)
- [Ekubo Core Contract (Sepolia)](https://sepolia.starkscan.co/contract/0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384)
- [Ekubo Router Addresses](https://docs.ekubo.org/integration-guides/reference/contract-addresses)

