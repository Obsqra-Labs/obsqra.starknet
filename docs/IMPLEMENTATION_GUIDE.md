# Obsqra.starknet Implementation Guide

**Version:** 2.0  
**Date:** December 5, 2025  
**Status:** ✅ Deployed to Starknet Sepolia

---

##  Live Deployment

Contracts are deployed on **Starknet Sepolia Testnet**:

| Contract | Address |
|----------|---------|
| **RiskEngine** | `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80` |
| **DAOConstraintManager** | `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` |
| **StrategyRouter** | `0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a` |

View on explorer: [Starkscan](https://sepolia.starkscan.co) | [Voyager](https://sepolia.voyager.online)

---

## Table of Contents

1. [Prerequisites & Setup](#1-prerequisites--setup)
2. [Development Environment](#2-development-environment)
3. [Contract Deployment](#3-contract-deployment)
4. [Frontend Integration](#4-frontend-integration)
5. [Testing](#5-testing)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Prerequisites & Setup

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Scarb | 2.14.0+ | Cairo package manager |
| Starknet Foundry | **0.53.0+** | Testing & deployment (critical!) |
| Node.js | 18+ | Frontend |
| Python | 3.10+ | AI service |

### Installation

```bash
# Scarb (Cairo)
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh

# Starknet Foundry (MUST be 0.53.0+)
curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh
snfoundryup

# Verify versions
scarb --version    # 2.14.0+
sncast --version   # 0.53.0+ (CRITICAL for Sepolia deployment)
```

### ⚠️ Version Compatibility Warning

Check the [Starknet Compatibility Tables](https://docs.starknet.io/learn/cheatsheets/compatibility) before deployment. Version mismatches cause cryptic errors.

| RPC Version | sncast Version |
|-------------|----------------|
| 0.8.x | 0.39.0 |
| 0.10.x | **0.53.0** ← Use this |

---

## 2. Development Environment

### Clone & Setup

```bash
git clone <repo-url>
cd obsqra.starknet

# Contracts
cd contracts
scarb build

# Frontend
cd ../frontend
npm install --legacy-peer-deps

# AI Service
cd ../ai-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Contract Deployment

### Option A: Use Existing Deployment (Recommended)

Contracts are already deployed. Just configure your frontend:

```bash
# Frontend environment
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80
NEXT_PUBLIC_DAO_MANAGER_ADDRESS=0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a
EOF
```

### Option B: Deploy Fresh Contracts

#### Step 1: Create & Fund Account

```bash
# Create new keystore
mkdir -p ~/.starkli-wallets/myaccount
starkli signer keystore new ~/.starkli-wallets/myaccount/keystore.json

# Initialize OpenZeppelin account
starkli account oz init ~/.starkli-wallets/myaccount/account.json

# Fund the account (copy the address shown above)
# Go to: https://starknet-faucet.vercel.app
# Paste your address and request STRK
```

**Important:** The faucet will automatically deploy your account when it sends STRK.

#### Step 2: Import Account to sncast

```bash
# After faucet funds arrive
sncast account import \
  --url https://starknet-sepolia.public.blastapi.io \
  --name deployer \
  --address YOUR_ACCOUNT_ADDRESS \
  --private-key YOUR_PRIVATE_KEY \
  --type oz
```

#### Step 3: Declare & Deploy

```bash
cd contracts

# Declare contracts (use --network sepolia, NOT custom RPC)
sncast --account deployer declare --contract-name RiskEngine --network sepolia
sncast --account deployer declare --contract-name DAOConstraintManager --network sepolia
sncast --account deployer declare --contract-name StrategyRouter --network sepolia

# Deploy instances
sncast --account deployer deploy \
  --class-hash <RISK_ENGINE_CLASS_HASH> \
  --arguments "YOUR_OWNER_ADDRESS" \
  --network sepolia

sncast --account deployer deploy \
  --class-hash <DAO_CLASS_HASH> \
  --arguments "YOUR_OWNER_ADDRESS, 6000, 3, 5000, 1000000" \
  --network sepolia

sncast --account deployer deploy \
  --class-hash <ROUTER_CLASS_HASH> \
  --arguments "YOUR_OWNER_ADDRESS, 0x456, 0x789, 0xabc, RISK_ENGINE_ADDRESS" \
  --network sepolia
```

---

## 4. Frontend Integration

### Configure Environment

```bash
cd frontend

# Create .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80
NEXT_PUBLIC_DAO_MANAGER_ADDRESS=0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
EOF
```

### Run Frontend

```bash
npm run dev
# Open http://localhost:3000
```

### Connect Wallet

1. Install [ArgentX](https://www.argent.xyz/argent-x/) or [Braavos](https://braavos.app/)
2. Switch to Sepolia testnet
3. Get testnet STRK from [faucet](https://starknet-faucet.vercel.app)
4. Connect wallet to the app

---

## 5. Testing

### Unit Tests

```bash
cd contracts
snforge test
```

### Integration Tests

```bash
# Test contract interactions
cd scripts
./test_integration.sh
```

---

## 6. Troubleshooting

### "Invalid transaction nonce"

Wait 15-30 seconds between transactions. Starknet blocks take time.

### "Mismatch compiled class hash"

Your sncast version doesn't match RPC version. Upgrade:

```bash
snfoundryup
sncast --version  # Must be 0.53.0+
```

### "ContractNotFound" when deploying

Your account isn't deployed on-chain. Use the faucet—it auto-deploys accounts.

### "Invalid params: missing field l1_data_gas"

RPC version mismatch. Use `--network sepolia` instead of custom RPC URLs:

```bash
# Wrong
sncast --account deployer declare --url https://... --contract-name Foo

# Right
sncast --account deployer declare --network sepolia --contract-name Foo
```

### Balance Shows 0 in starkli but Voyager Shows Tokens

`starkli balance` can be inaccurate. Trust Voyager/Starkscan for balance checks.

---

## Resources

- [Starknet Docs](https://docs.starknet.io)
- [Compatibility Tables](https://docs.starknet.io/learn/cheatsheets/compatibility) ← **Read this first**
- [Starknet Foundry](https://foundry-rs.github.io/starknet-foundry/)
- [Cairo Book](https://book.cairo-lang.org)
- [Sepolia Faucet](https://starknet-faucet.vercel.app)
- [Starkscan Explorer](https://sepolia.starkscan.co)

---

## Support

For issues, check the [Dev Log](DEV_LOG.md) for common problems and solutions from our deployment journey.
