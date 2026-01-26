# Deployment Blockers - Technical Assessment

## Current Status
- ✅ **RiskEngine**: Class declared on Sepolia (hash: 0x03ea934f4442de174715b458377bf5d1900c2a7c2a1d5e7486fcde9e522e2216)
- ⏳ **StrategyRouterV2**: Cannot declare due to Sierra compiler version issue
- 🚀 **RPC**: PublicNode working (https://starknet-sepolia-rpc.publicnode.com)

---

## Root Issue: Sierra Compiler Incompatibility

### The Problem
```
scarb 2.11.0 → generates Sierra 1.7.0
starkli 0.3.2 → supports max Sierra 1.5.0
```

### Solution Options

#### ✅ **OPTION A: Use starkli 0.3.8** (BEST - but requires wait)
- **starkli v0.3.8** explicitly supports Sierra 1.7.0
- Release notes: "Support for Sierra v1.7.0 is also added"
- Status: Available but slow to build from source
- **Time needed**: 15-20 minutes (cargo build from source)
- **Command to complete**:
  ```bash
  # After build completes:
  cp /tmp/starkli-repo/target/release/starkli /root/.local/bin/starkli
  cd /opt/obsqra.starknet/contracts
  starkli declare target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
    --account /root/.starkli-wallets/deployer/account.json \
    --keystore /root/.starkli-wallets/deployer/keystore.json \
    --rpc https://starknet-sepolia-rpc.publicnode.com
  ```

#### ⚠️ **OPTION B: Use sncast (Starknet Foundry)**
- **sncast v0.53.0** already installed
- Issue: Requires complex account config in TOML
- Status: Partially working, needs account authentication resolution
- **Time needed**: 10-15 minutes (to fix config)
- **Blocker**: sncast account config parsing not working as expected

#### ⏭️ **OPTION C: Skip StrategyRouterV2 for now**
- Deploy RiskEngine immediately (already declared)
- Redeploy StrategyRouterV2 later when tool issue resolved
- **Time needed**: 5 minutes (to deploy RiskEngine)
- **Limitation**: Only 1 of 2 contracts deployed

#### 🔧 **OPTION D: Modify Sierra artifact**
- Manually edit StrategyRouterV2.contract_class.json to downgrade Sierra version field
- Force starkli 0.3.2 to accept it
- **Risk**: Could corrupt contract bytecode
- **Time needed**: 5 minutes
- **Not recommended** without validation

---

## Recommended Path: Go with Option A

The cleanest solution is waiting for starkli 0.3.8 to build from source since:
1. It's the proper tool for the job
2. No workarounds or hacks needed  
3. Both contracts will deploy cleanly
4. Takes ~15-20 minutes

**Next steps if you choose Option A**:
1. Monitor cargo build completion (should finish soon or restart if needed)
2. Once binary is ready, move to /root/.local/bin/
3. Verify: `starkli --version` should show 0.3.8
4. Redeclare StrategyRouterV2 - should work immediately
5. Deploy both instances

---

## What's Ready Right Now

**RiskEngine deployment (can do immediately):**
```bash
# RiskEngine is already DECLARED
# Constructor params needed:
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
STRATEGY_ROUTER="0x0000000000000000000000000000000000000000000000000000000000000001"  # placeholder
DAO_MANAGER="0x0000000000000000000000000000000000000000000000000000000000000001"   # placeholder

# Then deploy with starkli 0.3.2 (or 0.3.8 once ready):
starkli deploy 0x03ea934f4442de174715b458377bf5d1900c2a7c2a1d5e7486fcde9e522e2216 \
  "$OWNER" "$STRATEGY_ROUTER" "$DAO_MANAGER" \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia-rpc.publicnode.com
```

---

## Files & Locations

| What | Where |
|------|-------|
| RiskEngine compiled | /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json |
| StrategyRouterV2 compiled | /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json |
| starkli source (v0.3.8) | /tmp/starkli-repo/ |
| Account credentials | /root/.starkli-wallets/deployer/ |
| Account info (sncast) | ~/.starknet_accounts/starknet_open_zeppelin_accounts.json |

---

## Summary

**You are at 50% completion:**
- ✅ Phase 5a: RPC endpoint found & working
- ✅ Phase 5b: RiskEngine declared on-chain
- ⏳ Phase 5c: StrategyRouterV2 declaration (blocked on tooling)
- ⏳ Phase 5d: Both contract instances deployment
- ⏳ Phase 5e: Backend integration

**Recommendation**: Wait for starkli 0.3.8 build to complete OR proceed with RiskEngine deployment using current tools + come back to StrategyRouterV2 once 0.3.8 is ready.

**Estimated completion with Option A**: 25-30 minutes from now
**Estimated completion with Option C**: 5 minutes now + 20 minutes later

---

## What Would Help

If you want immediate full deployment:
- Manually restart cargo build for starkli 0.3.8 with more resources
- OR provide access to precompiled starkli 0.3.8 binary
- OR authorize manual Sierra artifact modification

Otherwise, continuing with Option A is safest path.
