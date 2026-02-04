# StrategyRouter Authorization Guide
## Setting risk_engine to Authorize RiskEngine v4

**Date**: January 27, 2026  
**Status**: ✅ **COMPLETE** - Authorization Successful  
**Transaction**: `0x01171cf26c22f17980023082d99ac8a3fb8bf48f31aaaaad0634ca2aef72ae6f`

---

## ✅ Solution Applied

**Used**: `sncast --network sepolia` (proven workaround from `docs/DEV_LOG.md`)

**Why This Works**: 
- `sncast` with `--network sepolia` automatically figures out compatible RPC
- Avoids RPC version compatibility issues
- Same approach that worked for RiskEngine deployment

**Command**:
```bash
bash scripts/set_strategy_router_risk_engine.sh
```

**Result**: ✅ Transaction submitted successfully
- Transaction Hash: `0x01171cf26c22f17980023082d99ac8a3fb8bf48f31aaaaad0634ca2aef72ae6f`
- Status: Confirmed
- RiskEngine v4 is now authorized

---

## Previous Problem (Resolved)

The Python script encountered RPC compatibility issues:
- RPC nodes using version 0.8.1
- starknet.py expects version 0.10.0
- Block tag compatibility issues

**Solution**: Use `sncast --network sepolia` instead (proven workaround)

---

## Alternative Solutions (For Reference)

### Option 1: Use Backend API

The backend can execute this transaction. Create a simple endpoint or use existing infrastructure.

**Quick Fix**: Add endpoint to backend:
```python
# backend/app/api/routes/admin.py (or create new file)
@router.post("/admin/set-strategy-router-risk-engine")
async def set_strategy_router_risk_engine(db: Session = Depends(get_db)):
    # Use same logic as script but via backend RPC utilities
    ...
```

---

### Option 2: Manual Execution via Starkli/sncast

**Using sncast**:
```bash
cd /opt/obsqra.starknet/contracts

# Set risk_engine address
sncast --account deployer invoke \
  --contract-address 0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73 \
  --function set_risk_engine \
  --arguments 0x00b844ac8c4f9bfc8675e29db75808b5e2ac59100e1e71967a76878522fb5f81 \
  --network sepolia
```

**Using starkli**:
```bash
starkli invoke \
  0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73 \
  set_risk_engine \
  0x00b844ac8c4f9bfc8675e29db75808b5e2ac59100e1e71967a76878522fb5f81 \
  --network sepolia \
  --account deployer
```

---

### Option 3: Fix RPC Compatibility

**Update RPC URLs** to use compatible endpoints:
- Use RPC nodes with version 0.10.0
- Or downgrade starknet.py to compatible version

**Check RPC version**:
```bash
curl -X POST https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_specVersion","params":[],"id":1}'
```

---

## Contract Details

**StrategyRouter v3.5**:
- Address: `0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73`
- Function: `set_risk_engine(risk_engine: ContractAddress)`
- Access: Owner-only

**RiskEngine v4**:
- Address: `0x00b844ac8c4f9bfc8675e29db75808b5e2ac59100e1e71967a76878522fb5f81`
- Needs to be set as `risk_engine` in StrategyRouter

---

## Verification

After setting, verify with:
```python
# Python
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient

client = FullNodeClient(node_url="https://starknet-sepolia.g.alchemy.com/v2/...")
contract = Contract(
    address=0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73,
    abi=abi,
    provider=client
)

# If get_risk_engine exists:
result = await contract.functions["get_risk_engine"].call()
print(f"Current risk_engine: {hex(result[0])}")
```

---

## Status

**Script**: ✅ Ready (`scripts/set_strategy_router_risk_engine.py`)  
**RPC**: ⚠️ Compatibility issues  
**Alternative**: Use sncast/starkli or backend API

**Next Action**: Execute via Option 1 (backend API) or Option 2 (sncast/starkli)

---

**Once authorized, RiskEngine v4 can call `StrategyRouter.update_allocation()`**
