# Obsqra.starknet Implementation Guide

**Version:** 1.0  
**Date:** December 2025

This guide provides step-by-step instructions for implementing the Obsqra.starknet MVP/POC.

## Table of Contents

1. [Prerequisites & Setup](#1-prerequisites--setup)
2. [Development Environment](#2-development-environment)
3. [Cairo Risk Engine Port](#3-cairo-risk-engine-port)
4. [MIST.cash Integration](#4-mistcash-integration)
5. [Strategy Router Implementation](#5-strategy-router-implementation)
6. [DAO Constraint Manager](#6-dao-constraint-manager)
7. [Frontend Integration](#7-frontend-integration)
8. [Testing Strategy](#8-testing-strategy)
9. [Deployment Guide](#9-deployment-guide)

## 1. Prerequisites & Setup

### Required Tools

```bash
# Rust (for Cairo)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Cairo
curl -L https://github.com/foundry-rs/starknet-foundry/releases/latest/download/starknet-foundry_linux_amd64.tar.gz | tar -xzf -
sudo mv starknet-foundry /usr/local/bin/

# Node.js (v18+)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python (3.10+)
sudo apt-get install python3.10 python3-pip
```

### Verify Installation

```bash
rustc --version      # Should be 1.70+
scarb --version      # Should be 2.0+
node --version       # Should be 18+
python3 --version    # Should be 3.10+
```

## 2. Development Environment

### Initialize Cairo Project

```bash
cd contracts
scarb init --name obsqra_contracts
```

### Initialize Frontend

```bash
cd frontend
npm init -y
npm install next@latest react@latest react-dom@latest
npm install @starknet-react/core @starknet-react/hooks
npm install @mistcash/sdk
```

### Initialize AI Service

```bash
cd ai-service
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn web3 requests
```

## 3. Cairo Risk Engine Port

See `contracts/src/risk_engine.cairo` for the complete implementation.

Key functions:
- `calculate_risk_score()` - Multi-factor risk calculation
- `calculate_allocation()` - Risk-adjusted allocation
- `verify_constraints()` - Constraint compliance checking

## 4. MIST.cash Integration

See `frontend/src/services/mist.ts` for integration patterns.

Key steps:
1. Install MIST.cash SDK
2. Initialize chamber
3. Implement deposit flow
4. Implement withdraw flow
5. Test privacy guarantees

## 5. Strategy Router Implementation

See `contracts/src/strategy_router.cairo` for the complete implementation.

Key functions:
- `update_allocation()` - Update protocol allocations
- `get_allocation()` - Get current allocations
- `accrue_yields()` - Track and accrue yields

## 6. DAO Constraint Manager

See `contracts/src/dao_constraint_manager.cairo` for the complete implementation.

Key functions:
- `set_constraints()` - Set governance constraints
- `validate_allocation()` - Validate allocation against constraints
- `get_constraints()` - Get current constraints

## 7. Frontend Integration

See `frontend/src/` for complete frontend implementation.

Key components:
- Dashboard page
- Contract hooks
- MIST.cash service
- Starknet provider setup

## 8. Testing Strategy

### Unit Tests

```bash
cd contracts
snforge test
```

### Integration Tests

```bash
./scripts/test_integration.sh
```

### E2E Tests

```bash
cd frontend
npm run test:e2e
```

## 9. Deployment Guide

### Deploy Contracts

```bash
./scripts/deploy.sh testnet
```

### Verify Contracts

```bash
./scripts/verify.sh $CONTRACT_ADDRESS $CONTRACT_NAME
```

### Deploy Frontend

```bash
cd frontend
npm run build
npm run deploy
```

For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

