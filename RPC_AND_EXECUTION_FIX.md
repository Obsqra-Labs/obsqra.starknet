# RPC and Execution Fix - Summary

## Issues Found

1. **Wrong RISK_ENGINE_ADDRESS**: Config had old address `0x00b844ac8c4f9bfc8675e29db75808b5e2ac59100e1e71967a76878522fb5f81` instead of final v4 deployment `0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab`

2. **execute-allocation missing proof params**: Was building only 10-element calldata (metrics only) instead of 24-element calldata (metrics + proof + on-chain agent params)

3. **Port confusion**: Config shows API_PORT=8001 but API_BASE_URL=http://localhost:8000 - backend is correctly running on 8001

4. **RPC unavailable**: Error "Starknet RPC unavailable. Retried all endpoints" - RPC fallback should work but may need more retries or different endpoints

## Fixes Applied

### 1. RISK_ENGINE_ADDRESS Updated
- **File**: `backend/app/config.py`
- **Change**: Updated to `0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab` (final v4 deployment)

### 2. execute-allocation Fixed
- **File**: `backend/app/api/routes/risk_engine.py`
- **Change**: Now builds full 24-element calldata:
  - 10 elements: Protocol metrics (jediswap + ekubo)
  - 5 elements: Proof parameters (proof facts, expected scores, fact registry)
  - 9 elements: On-chain agent (model_version + ConstraintSignature struct)
- **Logic**: Same as `orchestrate-allocation` - extracts fact_hash from proof_job, calculates expected scores, detects ABI, builds full calldata

### 3. L1 Data Gas Bounds
- **Files**: `integrity_service.py`, `risk_engine.py`, `model_registry_service.py`
- **Change**: Increased `l1_data_gas` max_price_per_unit to 150 trillion (150000000000000)

### 4. Backend Restarted
- Restarted with correct RISK_ENGINE_ADDRESS
- Health check: ✅ PASS

## RPC Configuration

**Current RPC URLs** (from config):
- Primary: `https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7` (Alchemy)
- Fallback 1: `https://free-rpc.nethermind.io/sepolia-juno/v0_7` (Nethermind)
- Fallback 2: `https://starknet-sepolia-rpc.publicnode.com` (PublicNode)

**RPC Fallback Utility**: `backend/app/utils/rpc.py` - `with_rpc_fallback()` should retry across all URLs

## Testing

**To test execution**:
```bash
# 1. Generate proposal (proof + Integrity registration)
curl -X POST http://localhost:8001/api/v1/risk-engine/propose-from-market

# 2. Execute with proof_job_id from step 1
curl -X POST http://localhost:8001/api/v1/risk-engine/execute-allocation \
  -H "Content-Type: application/json" \
  -d '{"proof_job_id":"<proof_job_id>"}'
```

**Expected**: execute-allocation should now:
- ✅ Build 24-element calldata (not 10)
- ✅ Include proof facts from proof_job.fact_hash
- ✅ Include model_version and constraint_signature
- ✅ Use correct RISK_ENGINE_ADDRESS
- ✅ Retry across RPC URLs if one fails

## Next Steps

1. **Test execute-allocation** with a fresh proposal (propose-from-market → execute-allocation)
2. **If RPC still fails**: Check backend logs for which RPC URLs are being tried and why they're failing
3. **Port confusion**: API_BASE_URL in config shows 8000 but backend runs on 8001 - this may be for frontend proxy, not backend itself
