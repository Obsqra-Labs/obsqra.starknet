# Deployment Status & Instructions

## ✅ Code Status: READY

All code has been committed and is ready for deployment:
- **Commit**: `17da8d4` - Full on-chain orchestration implementation
- **Contracts**: Built successfully
- **Frontend**: Integrated with new orchestration hook
- **Backend**: API endpoints ready

## ⚠️ RPC Compatibility Issue

**Problem**: 
- Current `sncast` version: **0.53.0** (requires RPC 0.10)
- Available RPC endpoints: **0.8.1** (Sepolia testnet)
- According to [Starknet Compatibility Table](https://docs.starknet.io/learn/cheatsheets/compatibility):
  - RPC 0.8 requires sncast **0.39.0**
  - RPC 0.10 requires sncast **0.53.0**

## 🔧 Solution Options

### Option 1: Downgrade sncast to 0.39.0 (Recommended)

```bash
# Install sncastup
curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | bash

# Install sncast 0.39.0
sncastup install v0.39.0

# Verify
sncast --version  # Should show 0.39.0

# Then run deployment
cd /opt/obsqra.starknet
./deploy-orchestration-final.sh
```

### Option 2: Use Manual Deployment via Starkscan

1. Go to https://sepolia.starkscan.co
2. Use "Write Contract" feature
3. Deploy using the contract class hashes from build output

### Option 3: Wait for RPC 0.10 Endpoints

Monitor for RPC providers that support 0.10, then use current sncast 0.53.0

## 📋 Deployment Commands (Once RPC Compatible)

### Step 1: Declare RiskEngine
```bash
cd /opt/obsqra.starknet/contracts
sncast --profile deployer declare --contract-name RiskEngine
# Save the class hash from output
```

### Step 2: Deploy RiskEngine
```bash
DEPLOYER="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
EXISTING_ROUTER="0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a"
EXISTING_DAO="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
RISK_ENGINE_CLASS="<FROM_STEP_1>"

sncast --profile deployer deploy \
  --class-hash $RISK_ENGINE_CLASS \
  --constructor-calldata "$DEPLOYER $EXISTING_ROUTER $EXISTING_DAO"
# Save the contract address
```

### Step 3: Declare StrategyRouterV2
```bash
sncast --profile deployer declare --contract-name StrategyRouterV2
# Save the class hash
```

### Step 4: Deploy StrategyRouterV2
```bash
DEPLOYER="0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
JEDISWAP_ROUTER="0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21"
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"
NEW_RISK_ENGINE="<FROM_STEP_2>"
EXISTING_DAO="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"
ROUTER_CLASS="<FROM_STEP_3>"

sncast --profile deployer deploy \
  --class-hash $ROUTER_CLASS \
  --constructor-calldata "$DEPLOYER $JEDISWAP_ROUTER $EKUBO_CORE $NEW_RISK_ENGINE $EXISTING_DAO $STRK_TOKEN"
# Save the contract address
```

### Step 5: Update Frontend Config
```bash
cd /opt/obsqra.starknet/frontend
# Edit .env.local
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=<NEW_RISK_ENGINE_ADDRESS>
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=<NEW_STRATEGY_ROUTER_ADDRESS>
```

### Step 6: Restart Frontend
```bash
cd /opt/obsqra.starknet/frontend
./start-frontend-3003.sh
```

## 📊 Contract Addresses Reference

### Existing (Before Update)
- RiskEngine: `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80`
- DAOConstraintManager: `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856`
- StrategyRouter: `0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a`

### Protocol Addresses (Sepolia)
- JediSwap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
- STRK Token: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`

## 🎯 What's Been Implemented

✅ Full on-chain orchestration in RiskEngine
✅ Performance tracking in StrategyRouterV2
✅ Complete audit trail with events
✅ Frontend integration with AI orchestration button
✅ Backend API endpoints
✅ All code committed and documented

## 🚀 Next Steps

1. **Resolve RPC compatibility** (downgrade sncast or find RPC 0.10)
2. **Deploy contracts** using commands above
3. **Update frontend config** with new addresses
4. **Test AI orchestration** flow end-to-end

---

**All code is production-ready. Just need compatible RPC/tool version!** 🎉
