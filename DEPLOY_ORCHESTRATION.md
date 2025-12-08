# Deploy On-Chain Orchestration Contracts

## Status: Ready to Deploy ✅

All contracts have been updated with full on-chain orchestration and are ready for deployment to Sepolia.

## What's Changed

### Contracts Updated:
1. **RiskEngine** - Added `propose_and_execute_allocation()` and full audit trail
2. **StrategyRouterV2** - Added performance tracking linked to decisions

### Files Ready:
- ✅ Contracts compiled successfully
- ✅ Deployment script created: `deploy-orchestration-contracts.sh`
- ✅ Frontend integration complete
- ✅ Backend API updated
- ✅ Documentation complete

## Deployment Steps

### 1. Push to GitHub (Requires Authentication)

```bash
cd /opt/obsqra.starknet
git push origin main
```

**Note:** If you get authentication errors, you'll need to:
- Set up GitHub credentials (SSH key or personal access token)
- Or push manually from your local machine

### 2. Deploy Contracts to Sepolia

```bash
cd /opt/obsqra.starknet
./deploy-orchestration-contracts.sh
```

This will:
- Build contracts
- Declare RiskEngine (updated)
- Deploy RiskEngine
- Declare StrategyRouterV2 (updated)
- Deploy StrategyRouterV2
- Update deployment files

### 3. Update Frontend Configuration

After deployment, update `frontend/.env.local`:

```env
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=<NEW_RISK_ENGINE_ADDRESS>
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=<NEW_STRATEGY_ROUTER_ADDRESS>
```

### 4. Restart Services

```bash
# Restart frontend
cd /opt/obsqra.starknet/frontend
npm run build
./start-frontend-3003.sh

# Restart backend (if needed)
cd /opt/obsqra.starknet/backend
# Your backend restart command
```

## Important Notes

### Contract Dependencies

The RiskEngine constructor requires:
- `owner`: Deployer address
- `strategy_router`: StrategyRouterV2 address (will be deployed)
- `dao_manager`: Existing DAO address

The StrategyRouterV2 constructor requires:
- `owner`: Deployer address
- `jediswap_router`: JediSwap router address
- `ekubo_core`: Ekubo core address
- `risk_engine`: NEW RiskEngine address
- `dao_manager`: Existing DAO address
- `asset_token`: STRK token address

### Deployment Order

1. Deploy RiskEngine first (needs StrategyRouter address - use placeholder or deploy StrategyRouter first)
2. Deploy StrategyRouterV2 (needs RiskEngine address)
3. Update RiskEngine with StrategyRouter address (if needed)

**Alternative:** Deploy StrategyRouterV2 first with existing RiskEngine, then deploy new RiskEngine, then redeploy StrategyRouterV2.

### After Deployment

1. **Verify contracts on Starkscan:**
   - Check RiskEngine: https://sepolia.starkscan.co/contract/<ADDRESS>
   - Check StrategyRouterV2: https://sepolia.starkscan.co/contract/<ADDRESS>

2. **Test the flow:**
   - Connect wallet
   - Click "🤖 AI Risk Engine: Orchestrate Allocation"
   - Verify transaction succeeds
   - Check events on Starkscan

3. **Monitor events:**
   - `AllocationProposed`
   - `AllocationExecuted`
   - `ProtocolMetricsQueried`
   - `APYQueried`
   - `DecisionRationale`
   - `ConstraintsValidated`
   - `PerformanceRecorded`

## Current Deployed Addresses (Before Update)

- RiskEngine: `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80`
- DAOConstraintManager: `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856`
- StrategyRouter: `0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a`

## Protocol Addresses (Sepolia)

- JediSwap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
- STRK Token: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`

## Troubleshooting

### Build Errors
```bash
cd /opt/obsqra.starknet/contracts
scarb build
```

### Deployment Errors
- Check account balance: `starkli account balance katana-0 --rpc <RPC_URL>`
- Check RPC connection: `curl <RPC_URL>`
- Verify account exists: `starkli account fetch katana-0`

### Frontend Errors
- Check environment variables
- Check contract addresses
- Check RPC connection
- Check browser console for errors

## Next Steps After Deployment

1. Test AI orchestration flow
2. Monitor events on Starkscan
3. Verify performance tracking
4. Test decision retrieval
5. Update keeper service (if applicable)

---

**Ready to roll! 🚀**

