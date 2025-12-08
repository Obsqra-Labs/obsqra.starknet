# Manual Deployment Guide - On-Chain Orchestration

## Status: Ready for Manual Deployment ✅

Due to RPC compatibility issues with automated scripts, here's the manual deployment process.

## Prerequisites

1. **Account Setup:**
   - Deployer account: `0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b`
   - Ensure account has sufficient STRK for deployment

2. **RPC Endpoint:**
   - Use a compatible RPC (0.10.0) or update sncast/starkli version
   - Recommended: `https://starknet-sepolia.public.blastapi.io`

## Deployment Steps

### Step 1: Build Contracts

```bash
cd /opt/obsqra.starknet/contracts
scarb build
```

### Step 2: Declare RiskEngine

```bash
cd /opt/obsqra.starknet/contracts

# Using sncast
sncast --profile deployer declare --contract-name RiskEngine

# Or using starkli (if available)
starkli declare target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io \
  --account deployer
```

**Save the class hash from output**

### Step 3: Deploy RiskEngine

```bash
# Constructor args: owner, strategy_router, dao_manager
DEPLOYER="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
EXISTING_ROUTER="0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a"
EXISTING_DAO="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
RISK_ENGINE_CLASS_HASH="<FROM_STEP_2>"

# Using sncast
sncast --profile deployer deploy \
  --class-hash $RISK_ENGINE_CLASS_HASH \
  --constructor-calldata "$DEPLOYER $EXISTING_ROUTER $EXISTING_DAO"

# Or using starkli
starkli deploy $RISK_ENGINE_CLASS_HASH \
  $DEPLOYER $EXISTING_ROUTER $EXISTING_DAO \
  --rpc https://starknet-sepolia.public.blastapi.io \
  --account deployer
```

**Save the contract address from output**

### Step 4: Declare StrategyRouterV2

```bash
cd /opt/obsqra.starknet/contracts

# Using sncast
sncast --profile deployer declare --contract-name StrategyRouterV2

# Or using starkli
starkli declare target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io \
  --account deployer
```

**Save the class hash from output**

### Step 5: Deploy StrategyRouterV2

```bash
# Constructor args: owner, jediswap_router, ekubo_core, risk_engine, dao_manager, asset_token
DEPLOYER="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
JEDISWAP_ROUTER="0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21"
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"
NEW_RISK_ENGINE="<FROM_STEP_3>"
EXISTING_DAO="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"
ROUTER_CLASS_HASH="<FROM_STEP_4>"

# Using sncast
sncast --profile deployer deploy \
  --class-hash $ROUTER_CLASS_HASH \
  --constructor-calldata "$DEPLOYER $JEDISWAP_ROUTER $EKUBO_CORE $NEW_RISK_ENGINE $EXISTING_DAO $STRK_TOKEN"

# Or using starkli
starkli deploy $ROUTER_CLASS_HASH \
  $DEPLOYER $JEDISWAP_ROUTER $EKUBO_CORE $NEW_RISK_ENGINE $EXISTING_DAO $STRK_TOKEN \
  --rpc https://starknet-sepolia.public.blastapi.io \
  --account deployer
```

**Save the contract address from output**

### Step 6: Update Deployment Files

After deployment, update these files with the new addresses:

1. **`contracts/deployments/sepolia.json`**
2. **`deployed-sepolia.json`**

### Step 7: Update Frontend Config

Update `frontend/.env.local`:

```env
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=<NEW_RISK_ENGINE_ADDRESS>
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=<NEW_STRATEGY_ROUTER_ADDRESS>
```

### Step 8: Restart Frontend

```bash
cd /opt/obsqra.starknet/frontend
./start-frontend-3003.sh
```

## Contract Addresses Reference

### Existing (Before Update)
- RiskEngine: `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80`
- DAOConstraintManager: `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856`
- StrategyRouter: `0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a`

### Protocol Addresses (Sepolia)
- JediSwap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
- STRK Token: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`

## Troubleshooting

### RPC Compatibility Issues
- Update sncast to latest version: `sncastup`
- Or use starkli instead
- Try different RPC endpoints

### Account Issues
- Check account balance
- Verify account is deployed
- Check account configuration in `snfoundry.toml`

### Build Issues
```bash
cd /opt/obsqra.starknet/contracts
scarb build
```

## After Deployment

1. Verify contracts on Starkscan
2. Test AI orchestration flow
3. Monitor events
4. Update documentation with new addresses

---

**All code is committed and ready. Just need to deploy! 🚀**

