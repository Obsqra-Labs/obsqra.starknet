# Allocation Execution Status

## ✅ Fixed: RPC & Port Issues

### RPC Failover  
- **Public Sepolia RPC** added as automatic fallback (`https://starknet-sepolia-rpc.publicnode.com`)
- **Retry attempts** increased from 2 to 3
- **Error handling** improved: transaction reverts now correctly distinguished from RPC failures  
- **Backend loads `.env.sepolia`** automatically when present

### Port Alignment
- **Backend**: `API_BASE_URL` default changed from 8000 → **8001**
- **Frontend**: default `backendUrl` changed from 8000 → **8001**

**Files Modified:**
- `backend/app/utils/rpc.py` (public Sepolia fallback, get_rpc_urls)
- `backend/app/config.py` (API_BASE_URL 8001, retries 3, .env.sepolia load, extra="ignore")
- `frontend/src/lib/config.ts` (backendUrl default 8001)

**Status:** ✅ Complete - RPC infrastructure is working, transactions can be submitted

---

## ✅ Fixed: StrategyRouter Wiring (2026-01-28)

### Was
**StrategyRouter was wired to an old RiskEngine address** (`0x00b844...`), not RiskEngine v4. When RiskEngine v4 called `StrategyRouter.update_allocation()`, the contract rejected with "Unauthorized".

### Fix
Called `StrategyRouter.set_risk_engine(0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab)` via sncast (deployer account). TX: `0x07c14de11715ec6dbaa0fbb86cad71312bb75828b67f7442eb5af675c6638355` (SUCCEEDED).

### Contract Addresses
- **RiskEngine v4**: `0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab` ✅ Deployed
- **StrategyRouter v3.5**: `0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73` ✅ Deployed (risk_engine updated)
- **DAO Manager**: `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` ✅ Deployed
- **Backend Wallet**: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d` ✅ Owner

### How it was fixed
Used **sncast** from `contracts/` with deployer account (`~/.starknet_accounts/starknet_open_zeppelin_accounts.json`):
```bash
cd contracts && sncast --account deployer invoke \\
  --contract-address 0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73 \\
  --function set_risk_engine \\
  --arguments 0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab \\
  --network sepolia
```

---

## Test After Fix

Once StrategyRouter's `risk_engine` is updated:

1. Generate allocation:
```bash
curl -X POST http://localhost:8001/api/v1/risk-engine/propose-from-market
```

2. Execute allocation (use `proof_job_id` from step 1):
```bash
curl -X POST http://localhost:8001/api/v1/risk-engine/execute-allocation \\
  -H "Content-Type: application/json" \\
  -d '{"proof_job_id": "YOUR_PROOF_JOB_ID"}'
```

Expected: Transaction submits successfully, allocation updates on-chain.

---

## Dev Log Entry

Added to `integration_tests/dev_log.md`:
- **2026-01-28**: RPC Unavailable & Port Confusion (Allocation Execute Unblock)  
  - ✅ Fixed: RPC failover (publicnode), retries (3), ports (8001), .env.sepolia load
  - ✅ StrategyRouter wiring to RiskEngine v4 (fixed 2026-01-28)

---

## Summary

**Infrastructure (RPC/ports)**: ✅ Fixed and tested  
**Contract wiring**: ✅ StrategyRouter.set_risk_engine() called (sncast)  
**Backend wallet**: ✅ Deployed, can send transactions (if it's the owner)  
**Next step**: Update StrategyRouter's risk_engine address using owner wallet
