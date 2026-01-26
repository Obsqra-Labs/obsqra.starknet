# Phase 5 Deployment Status - January 25, 2026

## Executive Summary
**Status**: 50% Complete - First contract declared, second blocked on Sierra compiler compatibility  
**RiskEngine**: ✅ Class declared on Sepolia  
**StrategyRouterV2**: ⚠️ Blocked on Sierra compiler version mismatch  

---

## Breakthrough: RPC Endpoint Discovery ✅

**Problem**: All public RPC endpoints appeared down (Blast, Infura, Reddio, Nethermind)  
**Root Cause**: JSON-RPC API version incompatibility (starkli v0.3.2 expects v0_6/v0_7, not v0_10+)  
**Solution**: Found **PublicNode RPC** in our own codebase configs:
- Location: `/opt/obsqra.starknet/contracts/Scarb.toml`
- URL: `https://starknet-sepolia-rpc.publicnode.com`
- Status: ✅ **WORKING** (Block 5,779,422+ responsive)

---

## Contract Declaration Status

### ✅ RiskEngine - DECLARED
- **Class Hash**: `0x03ea934f4442de174715b458377bf5d1900c2a7c2a1d5e7486fcde9e522e2216`
- **File**: `/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json`
- **Status**: Successfully declared on Sepolia testnet
- **Constructor**: Requires 3 parameters:
  - `owner`: Contract owner address
  - `strategy_router`: StrategyRouter contract address
  - `dao_manager`: DAOConstraintManager contract address
- **Next Step**: Deploy instance once dependencies are resolved

### ⚠️ StrategyRouterV2 - BLOCKED
- **Class Hash**: `0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d72b7`
- **File**: `/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json`
- **Status**: Cannot declare due to Sierra compiler version incompatibility
- **Error**: "Cannot compile Sierra version 1.7.0 with compiler supporting 1.5.0"

---

## Sierra Compiler Compatibility Issue

### Root Cause
- **scarb 2.11.0** generates **Sierra 1.7.0** (current installed)
- **starkli 0.3.2** compiler supports max **Sierra 1.5.0**
- Contracts are written for scarb 2.11 syntax, incompatible with scarb 2.6.x-2.7.x

### Attempted Solutions
1. ❌ **Downgrade scarb to 2.6.3**: Cairo code incompatible (Drop/Destruct trait errors)
2. ❌ **Downgrade scarb to 2.7.0**: Contract code uses `Vec::push()` API not available in 2.7.x
3. ❌ **Use starknet_py**: sympy/crypto_cpp_py dependency conflict
4. ⏳ **Need**: Either upgrade starkli or recompile with compatible cairogen

---

## Tooling Status

| Tool | Version | Status | Issue |
|------|---------|--------|-------|
| starkli | 0.3.2 | Working | Max Sierra 1.5.0 support |
| scarb | 2.11.0 | Builds contracts | Generates Sierra 1.7.0 |
| sncast | 0.53.0 | Available | RPC version mismatch warning |
| starknet_py | Latest | Installed | Dependency conflict (sympy) |
| cairo | 2.11.0 | Compiling | 2024_07 edition support |

---

## Working Credentials

**Network**: Sepolia  
**RPC**: `https://starknet-sepolia-rpc.publicnode.com`  
**Account**: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`  
**Account Class**: `0x5b4b537eaa2399e3aa99c4e2e0208ebd6c71bc1467938cd52c798c601e43564`  
**Keystore**: `/root/.starkli-wallets/deployer/keystore.json` (password: L!nux123)  

**sncast Config**: `~/.starknet_accounts/starknet_open_zeppelin_accounts.json`
- Named account: `deployer` (alpha-sepolia)
- Type: OpenZeppelin v1.0

---

## Files Created in Phase 5

1. **RPC_COMPATIBILITY_SOLUTION.md** - Documented JSON-RPC API version issue
2. **DEPLOYMENT_SUCCESS_PUBLICNODE.md** - Initial breakthrough documentation
3. **deploy_v2.sh** - Updated deployment script with PublicNode RPC
4. **deploy_risk_engine.sh** - RiskEngine-specific deployment script
5. **deploy_contracts_py.py** - Python starknet_py deployment (has dependency issues)

---

## Next Steps to Complete Deployment

### Option A: Use Existing Tools (Recommended)
1. **Find or patch starkli 0.4.x or newer** that supports Sierra 1.6+
2. **Redeclare both contracts** with newer starkli
3. **Deploy both instances** to testnet

### Option B: Workaround with Current Tools
1. **Deploy RiskEngine** with placeholder addresses (already declared)
2. **Manually patch one Sierra file** to downgrade version byte
3. **Declare StrategyRouterV2** with modified artifact
4. **Update backend** with addresses

### Option C: Python Script Fix
1. **Fix sympy/crypto_cpp_py conflict** in starknet_py environment
2. **Complete deploy_contracts_py.py** script
3. **Run full deployment** with Python

---

## Quick Deploy Commands

### RiskEngine Instance Deployment
```bash
cd /opt/obsqra.starknet
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
STRATEGY_ROUTER="0x0000000000000000000000000000000000000000000000000000000000000001"
DAO_MANAGER="0x0000000000000000000000000000000000000000000000000000000000000001"

starkli deploy \
  0x03ea934f4442de174715b458377bf5d1900c2a7c2a1d5e7486fcde9e522e2216 \
  "$OWNER" "$STRATEGY_ROUTER" "$DAO_MANAGER" \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia-rpc.publicnode.com
```

### StrategyRouterV2 Declaration (After Fix)
```bash
starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia-rpc.publicnode.com \
  --compiler-version 2.8.0  # Or newer starkli version
```

---

## Summary of Achievements This Session

✅ Found working RPC endpoint (PublicNode - was in our own configs!)  
✅ Successfully declared RiskEngine contract on Sepolia  
✅ Verified account authentication and funding  
✅ Updated deployment scripts with correct RPC  
✅ Identified exact Sierra compiler version blocker  
✅ Documented all endpoints tested and RPC compatibility issue  
✅ Created multiple deployment script variations  

**Progress**: 50% of contracts declared → 0 instances deployed (awaiting deployment)

---

## Estimated Time to Complete

- **RiskEngine deployment**: 5 minutes (ready now)
- **StrategyRouterV2 fix**: 10-20 minutes (requires starkli upgrade or workaround)
- **Full deployment**: 20-30 minutes total

**Current blocker**: Sierra compiler version mismatch between scarb (1.7.0 output) and starkli (1.5.0 max support)

---

## Key Insight

The RPC endpoints DO exist in our codebase. The issue was not missing endpoints, but:
1. **RPC API version incompatibility** (documented in our own .md files)
2. **Cairo compiler Sierra version mismatch** (starkli is too old for current scarb)

Both are solvable with the right tool versions or configurations.
