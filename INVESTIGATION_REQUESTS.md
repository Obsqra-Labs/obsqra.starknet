# Investigation Requests - JediSwap Router Integration

**Date**: December 10, 2025  
**Issue**: JediSwap V2 Router `exact_input_single()` failing with `ENTRYPOINT_NOT_FOUND`  
**Contract**: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21` (Sepolia)

---

## What I Need From You

Please share the following links/information to help investigate the JediSwap router integration issue:

### 1. JediSwap Router Contract ABI (CRITICAL)

**What I Need**: The actual ABI (Application Binary Interface) of the deployed router contract on Sepolia.

**Where to Find**:
- Starkscan contract page: https://sepolia.starkscan.co/contract/0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21
- Look for "Read/Write Contract" tab or "ABI" section
- Or check "Code" tab for verified source code

**What to Share**: 
- Direct link to the ABI JSON
- Or copy/paste the ABI JSON
- Or screenshot of the function signatures

**Why**: Need to verify the exact function signature and parameter order for `exact_input_single()`.

---

### 2. JediSwap Router Source Code (If Available)

**What I Need**: The actual Cairo source code of the router contract, especially the `exact_input_single` function.

**Where to Find**:
- JediSwap GitHub: https://github.com/jediswaplabs/JediSwap
- Look for `swap_router.cairo` or similar file
- Check if contract is verified on Starkscan (Code tab)

**What to Share**:
- GitHub link to the router contract file
- Or link to verified source on Starkscan

**Why**: Need to see the exact struct definition and parameter order.

---

### 3. JediSwap V2 Router Documentation

**What I Need**: Official documentation for the V2 Swap Router, specifically:
- Function signatures
- Parameter struct definitions
- Example usage

**Where to Find**:
- https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_swap_router
- Or any other official JediSwap documentation

**What to Share**:
- Direct link to the router documentation
- Or copy/paste the relevant sections

**Why**: Compare our implementation with official docs.

---

### 4. Successful Swap Transaction Example

**What I Need**: A successful transaction hash where someone called `exact_input_single()` on the Sepolia router.

**Where to Find**:
- Starkscan: Search for transactions to the router contract
- Look for successful swap transactions
- Check transaction calldata

**What to Share**:
- Transaction hash
- Or Starkscan link to a successful swap

**Why**: Can reverse-engineer the correct calldata format from a working example.

---

### 5. JediSwap Sepolia Contract Addresses (Verification)

**What I Need**: Confirmation that the router address we're using is correct for Sepolia.

**Where to Find**:
- https://docs.jediswap.xyz/for-developers/jediswap-v2/contract-addresses
- JediSwap official documentation or GitHub

**What to Share**:
- Link to official contract addresses page
- Or confirmation that `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21` is correct

**Why**: Verify we're using the right contract address.

---

### 6. Fee Tier Information

**What I Need**: What fee tiers are available for STRK/ETH pair on JediSwap V2.

**Where to Find**:
- JediSwap docs or interface
- Check pool factory for available fee tiers

**What to Share**:
- List of available fee tiers (e.g., 500, 3000, 10000)
- Or confirmation that 3000 (0.3%) exists for STRK/ETH

**Why**: We're using fee tier 3000, but it might not exist for this pair.

---

### 7. STRK/ETH Pool Information

**What I Need**: Information about the STRK/ETH liquidity pool on JediSwap V2 Sepolia.

**Where to Find**:
- JediSwap interface: https://app.jediswap.xyz/
- Or query the factory contract for pool address

**What to Share**:
- Pool address
- Fee tier used
- Whether pool exists and is active

**Why**: Need to verify the pool exists and what fee tier it uses.

---

## Current Error Details

**Error**: `ENTRYPOINT_NOT_FOUND`  
**Selector**: `0x3276861cf5e05d6daf8f352cabb47df623eb10c383ab742fcc7abea94d5c5cc`  
**Function**: `exact_input_single`  
**Contract**: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`

**Our Implementation**:
```cairo
pub struct ExactInputSingleParams {
    pub token_in: ContractAddress,
    pub token_out: ContractAddress,
    pub fee: u128,              // 3000 = 0.3%
    pub recipient: ContractAddress,
    pub deadline: u64,
    pub amount_in: u256,
    pub amount_out_minimum: u256,
    pub sqrt_price_limit_x96: u256,
}
```

**Possible Issues**:
1. Struct field order might be wrong
2. Fee tier 3000 might not exist for STRK/ETH
3. Function signature might be different than documented
4. Router might be V1, not V2 (but docs say Sepolia has V2)

---

## What I'll Do With This Information

Once I have the above, I will:
1. Compare our struct definition with the actual ABI
2. Fix any field order or type mismatches
3. Verify the fee tier is correct
4. Test with corrected implementation
5. Update the contract and redeploy

---

## Quick Links Summary

Please share links to:
1. ✅ Router ABI on Starkscan
2. ✅ Router source code (GitHub or verified)
3. ✅ Router documentation
4. ✅ Successful swap transaction example
5. ✅ Official contract addresses page
6. ✅ Fee tier information
7. ✅ STRK/ETH pool information

**Priority**: Items 1, 2, and 4 are most critical.

---

Thank you! Once I have these, I can quickly fix the integration.

