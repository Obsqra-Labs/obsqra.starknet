# Local Deployment - Quick Start

Deploy and test Obsqra contracts locally before hitting testnet.

## Prerequisites Check

```bash
# Check if required tools are installed
python3 --version          # Python 3.8+
pip install starknet-py    # Starknet Python SDK
npm --version              # Node.js 18+
```

## Installation

### Option A: Katana (Recommended - Fastest)

```bash
# Install Dojo/Katana
curl -L https://install.dojoengine.org | bash
dojoup

# Verify
katana --version
```

### Option B: Starknet Devnet

```bash
pip install starknet-devnet
devnet --version
```

## Quick Deployment

### Step 1: Start Local Node

```bash
# Terminal 1: Start Katana (recommended)
katana --host 0.0.0.0
# OR
devnet
```

You should see output like:
```
Listening on 0.0.0.0:5050
```

### Step 2: Build Contracts

```bash
# Terminal 2
cd /opt/obsqra.starknet/contracts
scarb build
```

### Step 3: Deploy

```bash
# Terminal 2 (in project root)
cd /opt/obsqra.starknet

# Option A: Using Python (recommended)
python3 scripts/deploy_local.py

# Option B: Using shell script
./scripts/deploy-local.sh
```

### Step 4: Verify Deployment

```bash
# Check .env.local was created
cat .env.local

# Output should show deployed addresses:
# RISK_ENGINE_ADDRESS=0x...
# DAO_MANAGER_ADDRESS=0x...
# STRATEGY_ROUTER_ADDRESS=0x...
```

## Test Locally

### Run Contract Unit Tests

```bash
cd contracts
snforge test
```

Expected: All 31 tests pass ✓

### Test via Frontend

```bash
# Terminal 3
cd /opt/obsqra.starknet/frontend

# Update .env.local with deployed addresses (optional)
npm run dev
```

Visit: http://localhost:3000

## Common Issues

### Error: "Connection refused"
- Check Katana is running: `ps aux | grep katana`
- Start it: `katana --host 0.0.0.0`

### Error: "Contract not found"
- Rebuild contracts: `cd contracts && scarb build`
- Check `.contract_class.json` files exist in `contracts/target/dev/`

### Error: "Sierra class not found"
- The contracts need to be declared first
- Use `deploy_local.py` which handles declaration

## What Gets Deployed Locally

| Contract | Address | Constructor Args |
|----------|---------|-----------------|
| RiskEngine | 0x... | owner: 0x123 |
| DAOConstraintManager | 0x... | owner, max_single(6000), min_div(3), max_vol(5000), min_liq(1M) |
| StrategyRouter | 0x... | owner, aave, lido, compound, risk_engine |

## Testing Workflows

### Workflow 1: Quick Contract Test
```bash
cd contracts
snforge test
# All 31 tests in ~2-3 seconds
```

### Workflow 2: Deploy + Frontend
```bash
# Terminal 1
katana --host 0.0.0.0

# Terminal 2
python3 scripts/deploy_local.py

# Terminal 3
cd frontend && npm run dev

# Then test at localhost:3000
```

### Workflow 3: End-to-End Local
```bash
# Test full flow: deposit → AI rebalance → withdraw
# Run via frontend with deployed contracts
```

## Performance

| Task | Time |
|------|------|
| scarb build | 2-4s |
| Deploy 3 contracts | 1-2s |
| Run 31 tests | 2-3s |
| Contract call | ~50ms |

## Next: Testnet Deployment

Once verified locally:

```bash
# 1. Get testnet funds
# Visit: https://starknet-faucet.vercel.app/

# 2. Deploy to testnet
export STARKNET_ACCOUNT=<your_account>
export STARKNET_KEYSTORE=<path_to_keystore>
./scripts/deploy.sh testnet
```

## Troubleshooting

### Python deployment fails
```bash
# Update starknet-py
pip install --upgrade starknet-py

# Or use shell script instead
./scripts/deploy-local.sh
```

### Contracts won't declare
- Ensure `contracts/target/dev/*.contract_class.json` exist
- Rebuild: `cd contracts && scarb build`

### Frontend can't connect to contracts
- Verify `.env.local` has correct addresses
- Check RPC URL is correct: `http://localhost:5050`
- Restart frontend: `npm run dev`

## Key Files

- `LOCAL_DEPLOYMENT_GUIDE.md` - Comprehensive guide
- `scripts/deploy_local.py` - Python deployment (recommended)
- `scripts/deploy-local.sh` - Bash deployment (alternative)
- `.env.local` - Generated after deployment with contract addresses

## Environment Variables

After deployment, `.env.local` contains:

```bash
RPC_URL=http://localhost:5050
ACCOUNT=katana_0
RISK_ENGINE_ADDRESS=0x...
DAO_MANAGER_ADDRESS=0x...
STRATEGY_ROUTER_ADDRESS=0x...
```

Use these in frontend and AI service configuration.

---

**Ready to start?** See `LOCAL_DEPLOYMENT_GUIDE.md` for detailed instructions.

