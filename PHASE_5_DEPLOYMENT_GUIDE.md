# Phase 5: Production Deployment to Testnet

**Status**: ✅ READY FOR DEPLOYMENT  
**Date**: January 25, 2026  
**Network**: Starknet Sepolia Testnet  
**Deployer Account**: 0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d

---

## Environment Verification

✅ **All checks passed:**
- Keystore found: `/root/.starkli-wallets/deployer/keystore.json`
- Account config found: `/root/.starkli-wallets/deployer/account.json`
- Contract artifacts found (2 files)
- starkli available: 0.3.2

---

## Deployment Steps

### Step 1: Declare RiskEngine Contract

```bash
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli declare \
  /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --network sepolia
```

**What this does:**
- Declares the RiskEngine contract class on Starknet Sepolia
- Returns a class hash (save this)
- Gas cost: ~100-200 STRK

**Output:**
```
Class hash: 0x[class_hash]
Transaction hash: 0x[tx_hash]
```

### Step 2: Declare StrategyRouter V2 Contract

```bash
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli declare \
  /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystone.json \
  --network sepolia
```

**What this does:**
- Declares the StrategyRouter V2 contract class
- Returns a class hash (save this)
- Gas cost: ~150-250 STRK

### Step 3: Deploy Contract Instances

After declaring, you need to deploy instances. Use the class hashes from above:

**Deploy RiskEngine Instance:**
```bash
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli deploy \
  [RISK_ENGINE_CLASS_HASH] \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystone.json \
  --network sepolia
```

**Deploy StrategyRouter Instance:**
```bash
STARKLI_KEYSTORE_PASSWORD="L!nux123" starkli deploy \
  [STRATEGY_ROUTER_CLASS_HASH] \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystone.json \
  --network sepolia
```

---

## Backend Services Deployment

✅ **All services found and ready:**
- stone_prover_service.py ✅
- allocation_proof_orchestrator.py ✅
- cairo_trace_generator_v2.py ✅
- allocation_proposal_service.py ✅

### Option 1: Local Development

```bash
cd /opt/obsqra.starknet
pip install -r requirements.txt
python -m backend.app.main
```

### Option 2: Docker (Recommended)

```bash
cd /opt/obsqra.starknet

# Build image
docker build -t obsqra-backend:latest .

# Run locally
docker run -p 8000:8000 obsqra-backend:latest

# Or push to registry
docker tag obsqra-backend:latest [your-registry]/obsqra-backend:latest
docker push [your-registry]/obsqra-backend:latest
```

### Option 3: Cloud Deployment

**Google Cloud Run:**
```bash
gcloud run deploy obsqra-backend \
  --image obsqra-backend:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars=STARKNET_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
```

**AWS Lambda:**
```bash
# Build for Lambda
docker build -t obsqra-backend:lambda -f Dockerfile.lambda .

# Deploy
aws lambda create-function \
  --function-name obsqra-backend \
  --role arn:aws:iam::[ACCOUNT]:role/lambda-role \
  --code ImageUri=[ACCOUNT].dkr.ecr.[REGION].amazonaws.com/obsqra-backend:lambda
```

---

## Environment Configuration

Create `.env` file in `/opt/obsqra.starknet/backend/`:

```env
# Starknet RPC
STARKNET_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7

# Contract Addresses (from deployment above)
RISK_ENGINE_ADDRESS=0x[deployed_address]
STRATEGY_ROUTER_ADDRESS=0x[deployed_address]

# Stone Prover
STONE_PROVER_BINARY=/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover
STONE_PROVER_PARAMS=/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json

# Atlantic Fallback
ATLANTIC_API_KEY=[your_atlantic_api_key]
ATLANTIC_ENABLED=true

# Database
DATABASE_URL=sqlite:///./obsqra.db
# Or PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/obsqra

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/obsqra-backend.log
```

---

## Integration Checklist

### Contract Deployment
- ☐ RiskEngine declared (save class hash)
- ☐ RiskEngine instance deployed (save address)
- ☐ StrategyRouter V2 declared (save class hash)
- ☐ StrategyRouter V2 instance deployed (save address)
- ☐ PoolFactory declared and deployed
- ☐ DAO Constraint Manager declared and deployed

### Backend Integration
- ☐ `.env` file created with contract addresses
- ☐ Stone prover binary verified working
- ☐ Atlantic API key configured
- ☐ Database initialized
- ☐ Backend service started and responding

### Frontend Integration
- ☐ RPC URL updated to Sepolia
- ☐ Contract addresses in frontend config
- ☐ Backend API endpoint configured
- ☐ Wallet connection tested
- ☐ Allocation UI working

### Testing
- ☐ Unit tests passing
- ☐ Integration tests passing
- ☐ E2E tests passing
- ☐ Manual allocation proposal test
- ☐ Proof generation test
- ☐ Cost tracking verification

### Monitoring
- ☐ Logs accessible
- ☐ Error tracking configured
- ☐ Metrics collection working
- ☐ Alerts configured
- ☐ Dashboard created

---

## Testing Deployment

### 1. Verify Contract Deployment

```bash
# Check RiskEngine
curl https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "starknet_getClass",
    "params": ["0x[RISK_ENGINE_ADDRESS]"],
    "id": 1
  }'
```

### 2. Test Stone Prover

```bash
cd /opt/obsqra.starknet
python3 -c "
from backend.app.services.stone_prover_service import StoneProverService
import asyncio

async def test():
    service = StoneProverService()
    result = await service.generate_proof(
        '/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_private.json',
        '/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_public.json'
    )
    print('✅ Proof generated!' if result.success else '❌ Failed')

asyncio.run(test())
"
```

### 3. Test Backend API

```bash
# Start backend
cd /opt/obsqra.starknet && python -m backend.app.main &

# Test health endpoint
curl http://localhost:8000/health

# Test proof generation endpoint
curl -X POST http://localhost:8000/api/allocations \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test@example.com",
    "pools": [
      {"symbol": "JEDISWAP", "allocation_pct": 50},
      {"symbol": "EKUBO", "allocation_pct": 50}
    ]
  }'
```

### 4. Test End-to-End Flow

```bash
python3 -c "
import asyncio
from backend.app.services.allocation_proposal_service import AllocationProposalService

async def test():
    service = AllocationProposalService()
    
    # Create allocation proposal
    allocation = {
        'user_id': 'test-user',
        'pools': [
            {'pool': 'jediswap', 'allocation_pct': 50},
            {'pool': 'ekubo', 'allocation_pct': 50}
        ],
        'total_value': 10000
    }
    
    result = await service.propose_and_prove_allocation(allocation)
    print(f'Proof generated: {result.proof_hash}')
    print(f'Cost: {result.cost_estimate}')

asyncio.run(test())
"
```

---

## Cost Tracking

### Expected Costs (Sepolia Testnet)

| Item | Cost | Notes |
|------|------|-------|
| RiskEngine declare | ~150 STRK | One-time |
| StrategyRouter declare | ~200 STRK | One-time |
| Per proof (Stone) | $0 | Free (local) |
| Per proof (Atlantic fallback) | $0.75 | Only for failures |
| Hosting (Cloud Run) | ~$5-20/month | Pay-as-you-go |
| Hosting (Lambda) | ~$0.50/month | Very cheap |

### Monitoring Costs

```bash
# Track proof generation costs
curl http://localhost:8000/api/metrics/costs

# Expected output:
{
  "period": "2026-01-25",
  "total_proofs": 100,
  "stone_success": 100,
  "atlantic_fallback": 0,
  "cost": 0.0,
  "savings": 75.0
}
```

---

## Troubleshooting

### Issue: "Keystore password incorrect"

**Solution:**
```bash
# Verify password
echo "L!nux123" | xxd -p

# Try again with escaped special characters if needed
STARKLI_KEYSTORE_PASSWORD='L!nux123' starkli ...
```

### Issue: "Insufficient funds for deployment"

**Solution:**
- Check account balance on [Sepolia Faucet](https://starknet-sepolia.public.blastapi.io/)
- Get testnet STRK tokens
- Wait for balance to reflect

### Issue: "Stone prover not found"

**Solution:**
```bash
# Verify binary path
ls -la /opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover

# Rebuild if missing
cd /opt/obsqra.starknet/stone-prover
bazel build //src/starkware/main/cpu:cpu_air_prover
```

### Issue: "Atlantic API key invalid"

**Solution:**
1. Get API key from [Atlantic](https://www.atlantic.starkware.co/)
2. Set in `.env`: `ATLANTIC_API_KEY=your_key`
3. Test: `curl https://api.atlantic.starkware.co/v1/version`

---

## Next Steps

1. **Execute declare commands** (Step 1-2 above)
2. **Note class hashes** returned from declare
3. **Deploy instances** using class hashes
4. **Update contract addresses** in `.env` and frontend
5. **Start backend service**
6. **Run integration tests**
7. **Monitor metrics** on testnet
8. **Prepare mainnet deployment** (Phase 6)

---

## Success Criteria

✅ **Phase 5 Complete When:**
- RiskEngine contract deployed to Sepolia
- StrategyRouter V2 deployed to Sepolia
- Backend service running and healthy
- Stone prover generating proofs
- Integration tests passing (100%)
- Cost tracking operational
- Monitoring and alerting configured
- Documentation complete

**Status**: Ready to begin deployment.

