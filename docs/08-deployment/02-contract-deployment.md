# Contract Deployment Guide

Complete guide for deploying RiskEngine, StrategyRouter, ModelRegistry, DAOConstraintManager, and FactRegistry contracts.

## Prerequisites

### Required Tools

**1. Scarb:**
```bash
scarb --version  # Should be 2.x
```

**2. sncast or starkli:**
```bash
sncast --version  # Or
starkli --version
```

**3. Wallet:**
- Deployed Starknet account
- Private key or keystore
- STRK balance for gas

### Network Access

**RPC Endpoint:**
- Sepolia: `https://starknet-sepolia-rpc.publicnode.com`
- Or use other public RPC

## Deploying RiskEngine

### Step 1: Build Contract

```bash
cd contracts
scarb build
```

### Step 2: Declare Contract

```bash
sncast declare \
  --contract-name RiskEngine \
  --network sepolia \
  --account <account_name>
```

**Output:**
- Class hash (save this)
- Declaration transaction hash

### Step 3: Deploy Contract

```bash
sncast deploy \
  --class-hash <class_hash_from_step_2> \
  --constructor-calldata \
    <owner_address> \
    <strategy_router_address> \
    <dao_manager_address> \
  --network sepolia \
  --account <account_name>
```

**Output:**
- Contract address (save this)
- Deployment transaction hash

### Step 4: Verify Deployment

```bash
# Check on Starkscan
# https://sepolia.starkscan.co/contract/<address>

# Or query contract
sncast call \
  --contract-address <address> \
  --function get_contract_version \
  --network sepolia
```

## Deploying StrategyRouter

### Step 1: Build Contract

```bash
cd contracts
scarb build
```

### Step 2: Declare Contract

```bash
sncast declare \
  --contract-name StrategyRouterV35 \
  --network sepolia \
  --account <account_name>
```

### Step 3: Deploy Contract

```bash
sncast deploy \
  --class-hash <class_hash> \
  --constructor-calldata \
    <owner_address> \
    <jediswap_router> \
    <jediswap_nft_manager> \
    <ekubo_core> \
    <risk_engine_address> \
    <dao_manager_address> \
  --network sepolia \
  --account <account_name>
```

**Protocol Addresses (Sepolia):**
- JediSwap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- JediSwap NFT Manager: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`
- Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`

## Deploying ModelRegistry

### Step 1: Build Contract

```bash
cd contracts
scarb build
```

### Step 2: Declare Contract

```bash
sncast declare \
  --contract-name ModelRegistry \
  --network sepolia \
  --account <account_name>
```

### Step 3: Deploy Contract

```bash
sncast deploy \
  --class-hash <class_hash> \
  --constructor-calldata <owner_address> \
  --network sepolia \
  --account <account_name>
```

## Deploying DAOConstraintManager

### Step 1: Build Contract

```bash
cd contracts
scarb build
```

### Step 2: Declare Contract

```bash
sncast declare \
  --contract-name DAOConstraintManager \
  --network sepolia \
  --account <account_name>
```

### Step 3: Deploy Contract

```bash
sncast deploy \
  --class-hash <class_hash> \
  --constructor-calldata \
    <owner_address> \
    <max_single> \
    <min_diversification> \
    <max_volatility> \
    <min_liquidity> \
  --network sepolia \
  --account <account_name>
```

**Example Constraints:**
- `max_single`: 7000 (70%)
- `min_diversification`: 3000 (30%)
- `max_volatility`: 5000 (50%)
- `min_liquidity`: 2

## Deploying FactRegistry

### Option 1: Use Public SHARP Registry

**Address:**
```
0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64
```

**No deployment needed** - use public registry.

### Option 2: Deploy Custom FactRegistry

**See:** [Fact Registry Deployment Guide](04-fact-registry.md)

## Contract Initialization

### Update RiskEngine

After deploying all contracts, update RiskEngine references:

```bash
sncast call \
  --contract-address <risk_engine_address> \
  --function set_strategy_router \
  --calldata <strategy_router_address> \
  --network sepolia \
  --account <account_name>
```

### Update StrategyRouter

Set RiskEngine reference:

```bash
sncast call \
  --contract-address <strategy_router_address> \
  --function set_risk_engine \
  --calldata <risk_engine_address> \
  --network sepolia \
  --account <account_name>
```

## Address Management

### Save Deployment Info

**Create deployment file:**
```json
{
  "network": "sepolia",
  "deployed_at": "2026-01-26T12:00:00Z",
  "contracts": {
    "risk_engine": {
      "address": "0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4",
      "class_hash": "0x...",
      "tx_hash": "0x..."
    },
    "strategy_router": {
      "address": "0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b",
      "class_hash": "0x...",
      "tx_hash": "0x..."
    }
  }
}
```

### Update Configuration

**Backend:**
- Update `RISK_ENGINE_ADDRESS`
- Update `STRATEGY_ROUTER_ADDRESS`
- Update `MODEL_REGISTRY_ADDRESS`

**Frontend:**
- Update `NEXT_PUBLIC_RISK_ENGINE_ADDRESS`
- Update `NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS`

## Verification

### On Starkscan

**Verify Contracts:**
1. Visit https://sepolia.starkscan.co
2. Search contract address
3. Verify contract code (if source available)
4. Check transactions

### Functional Testing

**Test RiskEngine:**
```bash
sncast call \
  --contract-address <risk_engine_address> \
  --function get_contract_version \
  --network sepolia
```

**Test StrategyRouter:**
```bash
sncast call \
  --contract-address <strategy_router_address> \
  --function get_allocation \
  --network sepolia
```

## Troubleshooting

### Declaration Fails

**Issue:** Class already declared
**Solution:** Use existing class hash

### Deployment Fails

**Issue:** Insufficient balance
**Solution:** Fund wallet with STRK

### Contract Not Found

**Issue:** Address incorrect
**Solution:** Verify address on explorer

## Next Steps

- **[Backend Deployment](03-backend-deployment.md)** - Backend setup
- **[Fact Registry Deployment](04-fact-registry.md)** - Custom FactRegistry
- **[Deployment Overview](01-overview.md)** - Architecture

---

**Contract Deployment Summary:** Complete guide for deploying all contracts with proper initialization and verification.
