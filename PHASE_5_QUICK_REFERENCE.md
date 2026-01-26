# Phase 5 Quick Reference: Testnet Deployment Commands

**Network**: Starknet Sepolia  
**Keystore Password**: L!nux123  
**Account**: 0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d

---

## Copy-Paste Ready Commands

### 1. Declare RiskEngine Contract

```bash
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli declare \
  /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --network sepolia
```

**Save the output**: This gives you the RiskEngine CLASS_HASH

### 2. Declare StrategyRouter V2

```bash
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli declare \
  /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --network sepolia
```

**Save the output**: This gives you the StrategyRouter CLASS_HASH

### 3. Deploy RiskEngine Instance

```bash
# Replace [RISK_ENGINE_CLASS_HASH] with the hash from step 1
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli deploy \
  [RISK_ENGINE_CLASS_HASH] \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --network sepolia
```

**Save the output**: This gives you the RISK_ENGINE_ADDRESS

### 4. Deploy StrategyRouter Instance

```bash
# Replace [STRATEGY_ROUTER_CLASS_HASH] with the hash from step 2
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli deploy \
  [STRATEGY_ROUTER_CLASS_HASH] \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --network sepolia
```

**Save the output**: This gives you the STRATEGY_ROUTER_ADDRESS

---

## Backend Deployment

### Start Backend (Development)

```bash
cd /opt/obsqra.starknet
python -m backend.app.main
```

Accessible at: `http://localhost:8000`

### Start Backend with Docker

```bash
cd /opt/obsqra.starknet

# Build
docker build -t obsqra-backend:latest .

# Run
docker run -p 8000:8000 \
  -e RISK_ENGINE_ADDRESS=[ADDRESS_FROM_STEP_3] \
  -e STRATEGY_ROUTER_ADDRESS=[ADDRESS_FROM_STEP_4] \
  obsqra-backend:latest
```

### Verify Backend is Running

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

---

## Testing

### Test Stone Prover Integration

```bash
python3 << 'PYEOF'
import asyncio
from backend.app.services.stone_prover_service import StoneProverService

async def test():
    service = StoneProverService()
    result = await service.generate_proof(
        '/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_private.json',
        '/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_public.json'
    )
    if result.success:
        print(f"✅ Proof generated: {result.proof_size_kb}KB in {result.generation_time_ms:.0f}ms")
    else:
        print(f"❌ Failed: {result.error}")

asyncio.run(test())
PYEOF
```

### Test E2E Allocation Flow

```bash
python3 << 'PYEOF'
import asyncio
from backend.app.services.allocation_proposal_service import AllocationProposalService

async def test():
    service = AllocationProposalService()
    
    allocation = {
        'user_id': 'test-user',
        'pools': [
            {'pool': 'jediswap', 'allocation_pct': 50},
            {'pool': 'ekubo', 'allocation_pct': 50}
        ],
        'total_value': 10000
    }
    
    result = await service.propose_and_prove_allocation(allocation)
    print(f"✅ Complete flow tested successfully")
    print(f"   Proof hash: {result.proof_hash}")
    print(f"   Cost estimate: ${result.cost_estimate}")

asyncio.run(test())
PYEOF
```

---

## Configuration

### Create .env File

```bash
cat > /opt/obsqra.starknet/backend/.env << 'EOF'
# Starknet
STARKNET_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
RISK_ENGINE_ADDRESS=0x[ADDRESS_FROM_STEP_3]
STRATEGY_ROUTER_ADDRESS=0x[ADDRESS_FROM_STEP_4]

# Stone Prover
STONE_PROVER_BINARY=/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover
STONE_PROVER_PARAMS=/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json

# Atlantic Fallback (optional)
ATLANTIC_API_KEY=[YOUR_KEY]
ATLANTIC_ENABLED=true

# Database
DATABASE_URL=sqlite:///./obsqra.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/obsqra-backend.log
EOF
```

---

## Monitoring

### Check Deployment Status

```bash
# Check if contract is deployed
curl -X POST https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "starknet_getClassAt",
    "params": ["0x[RISK_ENGINE_ADDRESS]"]
  }'
```

### Monitor Proof Generation

```bash
# Get metrics from backend
curl http://localhost:8000/api/metrics

# Expected response:
# {
#   "total_proofs": 100,
#   "success_rate": 100.0,
#   "avg_time_ms": 4027,
#   "cost": 0.0
# }
```

### View Logs

```bash
# Development
tail -f /tmp/obsqra-backend.log

# Docker
docker logs -f [CONTAINER_ID]

# Production
tail -f /var/log/obsqra-backend.log
```

---

## Troubleshooting

### "Keystore password incorrect"

```bash
# Try with single quotes (to prevent shell interpretation of special chars)
STARKLI_KEYSTORE_PASSWORD='L!nux123' starkli ...
```

### "Insufficient funds"

1. Get testnet STRK from faucet: https://starknet-sepolia.public.blastapi.io/
2. Wait for transaction confirmation (~10 seconds)
3. Check balance: 
```bash
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli account fetch \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json
```

### "Stone prover not found"

```bash
# Verify binary exists
ls -la /opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover

# If not, rebuild
cd /opt/obsqra.starknet/stone-prover
bazel build //src/starkware/main/cpu:cpu_air_prover
```

### "Backend service not responding"

```bash
# Check if port 8000 is in use
lsof -i :8000

# Restart backend
pkill -f "python -m backend.app.main"
python -m backend.app.main
```

---

## Expected Timeline

| Step | Command | Time | Result |
|------|---------|------|--------|
| 1 | Declare RiskEngine | 30-60s | Class hash + TX hash |
| 2 | Declare StrategyRouter | 30-60s | Class hash + TX hash |
| 3 | Deploy RiskEngine | 30-60s | Contract address |
| 4 | Deploy StrategyRouter | 30-60s | Contract address |
| 5 | Start backend | Immediate | Service running |
| **Total** | **All steps** | **~5 minutes** | **Ready for use** |

---

## Success Checklist

After running all commands:

```
☐ Step 1: RiskEngine declared (saved class hash)
☐ Step 2: StrategyRouter declared (saved class hash)
☐ Step 3: RiskEngine deployed (saved address)
☐ Step 4: StrategyRouter deployed (saved address)
☐ Step 5: Backend service running
☐ Step 6: curl http://localhost:8000/health returns OK
☐ Step 7: Test allocation flow works
☐ Step 8: Proof generation succeeds
☐ Step 9: Costs tracked correctly
☐ Step 10: Documentation updated
```

When all boxes checked: **Ready for integration testing** ✅

---

## Quick Links

- **RPC Endpoint**: https://starknet-sepolia.public.blastapi.io/rpc/v0_7
- **Testnet Explorer**: https://sepolia.starkscan.co/
- **Starkli Docs**: https://book.starkli.rs/
- **Backend Logs**: `/var/log/obsqra-backend.log`
- **Docker Hub**: [your-registry]/obsqra-backend

---

## Emergency Rollback

If something breaks:

```bash
# Stop backend
pkill -f "python -m backend.app.main"

# Remove Docker container (if using Docker)
docker rm -f [CONTAINER_NAME]

# Check previous version
git log --oneline

# Revert if needed
git checkout [PREVIOUS_COMMIT]

# Restart
python -m backend.app.main
```

---

**Status**: All commands ready to execute.  
**Next Step**: Run Step 1 above.  
**Expected Result**: Contract class hash returned.
