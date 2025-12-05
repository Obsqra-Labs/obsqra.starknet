# Local Deployment Guide

## Overview

This guide walks through deploying the Obsqra Starknet contracts locally using **Katana**, the fast local Starknet node from Dojo.

## Prerequisites

### Option 1: Using Katana (Recommended)

Katana is a fast local Starknet node optimized for development.

```bash
# Install Katana via dojoup
curl -L https://install.dojoengine.org | bash
dojoup
katana --version
```

### Option 2: Using Starknet Devnet

```bash
pip install starknet-devnet
devnet --version
```

## Step 1: Start Local Starknet Node

### Using Katana:

```bash
# Terminal 1: Start Katana (runs on http://localhost:5050)
katana --host 0.0.0.0
```

Output will show test accounts and their private keys.

### Using Devnet:

```bash
# Terminal 1: Start Devnet (runs on http://localhost:5050)
devnet
```

## Step 2: Build Contracts

```bash
cd /opt/obsqra.starknet/contracts
scarb build
```

This generates Sierra contract files in `target/dev/`:
- `obsqra_contracts_RiskEngine.contract_class.json`
- `obsqra_contracts_StrategyRouter.contract_class.json`
- `obsqra_contracts_DAOConstraintManager.contract_class.json`

## Step 3: Deploy Locally

### Using Starknet-rs CLI (Recommended)

```bash
cd /opt/obsqra.starknet

# Set environment
export STARKNET_RPC_URL=http://localhost:5050
export STARKNET_ACCOUNT=katana_0  # or use private key
export STARKNET_KEYSTORE=<path>   # if needed

# Deploy Risk Engine
starknet deploy \
  --contract contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --constructor-args 0x123

# Deploy DAO Constraint Manager
starknet deploy \
  --contract contracts/target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json \
  --constructor-args 0x123 6000 3 5000 1000000

# Deploy Strategy Router
starknet deploy \
  --contract contracts/target/dev/obsqra_contracts_StrategyRouter.contract_class.json \
  --constructor-args 0x123 0x456 0x789 0xabc 0xdef
```

### Using Python Script (Alternative)

```python
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer import PrivateKeySigner
from starknet_py.account.account import Account

# Connect to local Katana
client = FullNodeClient(node_url="http://localhost:5050")

# Use Katana test account
private_key = 0x1234567890abcdef  # From Katana output
signer = PrivateKeySigner(private_key)
account = Account(client, address=0x1, signer=signer)

# Deploy contracts...
```

## Step 4: Verify Deployment

```bash
# Check deployed contract at address
starknet call --function version --contract-address 0x...

# Call contract functions
starknet call \
  --function get_constraints \
  --contract-address 0x... \
  --abi contracts/target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json
```

## Testing Flow

### 1. Local Deployment Test

```bash
# Terminal 1: Start Katana
katana --host 0.0.0.0

# Terminal 2: Deploy and test
./scripts/deploy-local.sh

# This script will:
# - Declare contracts
# - Deploy all 3 contracts
# - Save addresses to .env.local
# - Run basic function calls to verify
```

### 2. Integration Testing

```bash
# Test contract interactions
cd /opt/obsqra.starknet/contracts
snforge test

# Test against deployed instance
npm run test:integration --from-deployed-local
```

### 3. End-to-End Flow

```bash
# Frontend connected to local backend
cd /opt/obsqra.starknet/frontend
export NEXT_PUBLIC_RPC_URL=http://localhost:5050
npm run dev

# Visit http://localhost:3000 and test deposit → AI → withdraw flow
```

## Common Issues & Solutions

### Issue: Connection refused
**Solution:** Ensure Katana/Devnet is running on the correct port:
```bash
netstat -tlnp | grep 5050
```

### Issue: "Contract not found" error
**Solution:** Use full path to compiled contract JSON file:
```bash
starknet deploy --contract $(pwd)/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json
```

### Issue: Gas fees during local deployment
**Solution:** Not an issue on local devnet - all deployments are instant and free.

## Next Steps: Testnet Deployment

Once verified locally:

1. Get Starknet testnet funds from [faucet](https://starknet-faucet.vercel.app/)
2. Update RPC URL: `https://starknet-testnet.public.blastapi.io`
3. Prepare testnet account with actual private key
4. Run deployment script with `testnet` argument:

```bash
./scripts/deploy.sh testnet 0x<your_account> 0x<aave> 0x<lido> 0x<compound>
```

## Useful Commands

```bash
# Check Katana account balances
curl -X POST http://localhost:5050 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_getBalance","params":["0x1"],"id":1}'

# Declare contract class
starknet declare --contract contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json

# Get contract details
starknet get-contract-by-address --contract-address 0x...

# Get block info
starknet get-block --block-number latest
```

## Environment Variables

Create `.env.local` for local development:

```bash
# Local Katana
STARKNET_RPC_URL=http://localhost:5050
STARKNET_ACCOUNT_ADDRESS=0x123...
STARKNET_PRIVATE_KEY=0xabc...

# Contract Addresses (populated after deployment)
RISK_ENGINE_ADDRESS=0x...
DAO_MANAGER_ADDRESS=0x...
STRATEGY_ROUTER_ADDRESS=0x...
```

## Performance Notes

- **Katana**: ~500ms per block (instant finality)
- **Devnet**: ~1-2s per block
- **Starknet Testnet**: ~12-30s per block
- **Starknet Mainnet**: ~6-10s per block

Use Katana for rapid local development and iteration.

