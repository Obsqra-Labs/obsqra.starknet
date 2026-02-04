# Stone E2E Test Issues - Root Cause Analysis

**Date**: 2026-01-26  
**Status**: Identified Issues

## Problem Summary

The E2E test is failing because:
1. **No fact_hash returned** - Integrity registration is failing
2. **Response format mismatch** - Server returning old format (missing `fact_hash`, `verified` fields)
3. **VERIFIER_NOT_FOUND error** - Integrity contract call failing

## Root Cause

### Issue 1: Integrity Registration Failing
```
Error: VERIFIER_NOT_FOUND (0x56455249464945525f4e4f545f464f554e44)
Location: backend/app/services/integrity_service.py:325
Function: register_calldata_and_get_fact()
```

**What's happening:**
- Stone proof is generated successfully ✅
- Proof is serialized correctly ✅
- Integrity contract call fails with `VERIFIER_NOT_FOUND` ❌
- Exception is caught, returns `None` for fact_hash
- Endpoint should raise HTTPException but server may be running old code

### Issue 2: Server Running Old Code
**Evidence:**
- Response missing `fact_hash` and `verified` fields
- Response has old format: `proof_hash, jediswap_score, ekubo_score, zkml, status, message`
- Status is "generated" not "verified"
- Message is "Proof generated successfully" (old message)

**Expected response:**
```json
{
  "proof_hash": "0x...",
  "fact_hash": "0x...",  // MISSING
  "verified": true,      // MISSING
  "status": "verified",
  "message": "STARK proof generated using Stone prover and verified on-chain in X.XXs"
}
```

**Actual response:**
```json
{
  "proof_hash": "0xb067fc56a972c0aa",
  "jediswap_score": 4564,
  "ekubo_score": 3499,
  "zkml": {...},
  "status": "generated",
  "message": "Proof generated successfully"
}
```

## Possible Causes

### 1. Integrity Contract Address/Function Issue
- Contract address: `0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64`
- Function: `verify_proof_full_and_register_fact`
- Error: `VERIFIER_NOT_FOUND`

**Possible reasons:**
- Contract not deployed at that address
- Function doesn't exist in deployed contract
- Contract is a proxy and function selector is wrong
- Calldata format is incorrect

### 2. Server Not Restarted
- Code was updated but server is running old version
- Need to restart backend server to pick up changes

### 3. Exception Handling
- Exception is being caught and returning fallback response
- Old code path is being executed instead of new strict mode

## Solutions

### Immediate Fixes

1. **Restart Backend Server**
   ```bash
   # Stop current server
   # Restart with new code
   cd /opt/obsqra.starknet/backend
   # Restart uvicorn/gunicorn
   ```

2. **Verify Integrity Contract**
   ```bash
   # Check if contract exists at address
   sncast call \
     --contract-address 0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64 \
     --function get_all_verifications_for_fact_hash \
     --arguments 0x1 \
     --network sepolia
   ```

3. **Check Function Exists**
   ```bash
   # Verify function selector
   python3 -c "
   from starknet_py.hash.selector import get_selector_from_name
   print(hex(get_selector_from_name('verify_proof_full_and_register_fact')))
   "
   ```

### Code Fixes Applied

1. ✅ **Better Error Handling** - Updated `proofs.py` to catch exceptions and provide clear error messages
2. ✅ **Better Test Reporting** - Updated test to show missing fields clearly
3. ✅ **Strict Mode Enforcement** - Code now raises HTTPException when fact_hash is None

## Next Steps

1. **Restart backend server** to pick up new code
2. **Verify Integrity contract** is deployed and has the function
3. **Check contract ABI** matches the deployed contract
4. **Test again** with updated code

## Testing

After fixes, run:
```bash
python3 test_stone_only_e2e.py
```

Expected behavior:
- Should fail with clear error if Integrity registration fails
- Should return fact_hash and verified=true if successful
- Should not return old format response

---

**Status**: Issues identified. Need to restart server and verify Integrity contract.
