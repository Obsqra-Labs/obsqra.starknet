# Deployment Overview

This document covers deployment architecture, network configuration, environment setup, and prerequisites.

## Deployment Architecture

### System Components

```
┌─────────────────────────────────────────┐
│         Frontend (Next.js)               │
│         - Static hosting (Vercel/CDN)   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Backend (FastAPI)                │
│         - Python service                 │
│         - PostgreSQL database            │
│         - Stone prover binary            │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│      Smart Contracts (Starknet)         │
│      - RiskEngine v4                    │
│      - StrategyRouter v3.5              │
│      - ModelRegistry                    │
│      - DAOConstraintManager             │
│      - FactRegistry                     │
└─────────────────────────────────────────┘
```

## Network Configuration

### Starknet Sepolia (Testnet)

**Current Deployment:**
- All contracts on Sepolia
- RPC: `https://starknet-sepolia-rpc.publicnode.com`
- Explorer: https://sepolia.starkscan.co
- Chain ID: `SN_SEPOLIA`

### Starknet Mainnet (Future)

**Planned:**
- Production deployment
- Mainnet RPC endpoints
- Production contracts
- Mainnet protocol integrations

## Environment Setup

### Backend Environment

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/obsqra_db

# Starknet
STARKNET_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
STARKNET_NETWORK=sepolia

# Contracts
RISK_ENGINE_ADDRESS=0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4
STRATEGY_ROUTER_ADDRESS=0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b
MODEL_REGISTRY_ADDRESS=0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc

# Backend Wallet
BACKEND_WALLET_ADDRESS=<wallet_address>
BACKEND_WALLET_PRIVATE_KEY=<private_key>

# Integrity Service
ATLANTIC_API_KEY=<api_key>  # Optional
```

### Frontend Environment

**Required Variables:**
```bash
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
NEXT_PUBLIC_BACKEND_URL=https://api.obsqra.fi
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4
NEXT_PUBLIC_NETWORK=sepolia
```

## Prerequisites

### Infrastructure

**1. Server/VPS:**
- Ubuntu 20.04+ or similar
- 4+ CPU cores
- 8+ GB RAM
- 50+ GB storage

**2. Database:**
- PostgreSQL 12+
- Database created
- User with permissions

**3. Starknet Access:**
- RPC endpoint access
- Wallet with STRK for gas
- Account deployed

### Software

**1. Python 3.11+**
```bash
python3 --version
pip3 --version
```

**2. Node.js 18+**
```bash
node --version
npm --version
```

**3. Scarb (Cairo)**
```bash
scarb --version
```

**4. Stone Prover (Optional)**
```bash
which cpu_air_prover
```

### Accounts and Keys

**1. Backend Wallet:**
- Starknet account deployed
- Private key secured
- STRK balance for gas

**2. Contract Owner:**
- Owner wallet for contracts
- Private key secured
- STRK balance for deployment

## Deployment Checklist

### Pre-Deployment

- [ ] All contracts compiled
- [ ] Contracts tested locally
- [ ] Backend tested
- [ ] Frontend tested
- [ ] Environment variables configured
- [ ] Database migrated
- [ ] Wallets funded
- [ ] RPC endpoints verified

### Deployment

- [ ] Contracts declared
- [ ] Contracts deployed
- [ ] Contract addresses recorded
- [ ] Backend configured
- [ ] Backend deployed
- [ ] Frontend built
- [ ] Frontend deployed
- [ ] Health checks passing

### Post-Deployment

- [ ] Contracts verified on explorer
- [ ] Backend API responding
- [ ] Frontend accessible
- [ ] End-to-end test passed
- [ ] Monitoring configured
- [ ] Logs accessible
- [ ] Documentation updated

## Next Steps

- **[Contract Deployment](02-contract-deployment.md)** - Deploying contracts
- **[Backend Deployment](03-backend-deployment.md)** - Backend setup
- **[Fact Registry Deployment](04-fact-registry.md)** - Custom FactRegistry

---

**Deployment Overview Summary:** Complete deployment architecture with network configuration, environment setup, and prerequisites for production deployment.
