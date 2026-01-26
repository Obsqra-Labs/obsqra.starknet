# Deployment Status - January 26, 2026

## ✅ What's Working

### Compilation
- ✅ Fixed PoolFactory to use Map instead of Vec (Cairo 2.8.5 compatible)
- ✅ **All contracts compile successfully with Cairo 2.8.5**:
  - RiskEngine
  - StrategyRouterV35 ← **Current version you're on**
  - StrategyRouterV3, V2 (legacy)
  - PoolFactory, DAOConstraintManager, etc.

### Backend  
- ✅ Backend running and operational
- ✅ Stone prover binary compiled (Dec 12) and ready
- ✅ StoneProverService integrated (361 lines)
- ✅ Settlement layer code in place

---

## ❌ Current Blocker: RPC Compatibility Issue

### Problem
When attempting to declare StrategyRouterV35 to Sepolia:
- **PublicNode RPC spec**: 0.8.1
- **starkli version**: 0.4.2
- **Error**: "data did not match any variant of untagged enum JsonRpcResponse"

**Root cause**: The RPC is returning a response format that starkli 0.4.2 cannot parse correctly, even though both report compatible versions.

### Evidence
```bash
$ starkli declare target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --rpc "https://starknet-sepolia-rpc.publicnode.com" ...

Declaring Cairo 1 class: 0x008186fa...
Compiling Sierra class to CASM with compiler version 2.9.4...
CASM class hash: 0x034076ef...
Error: data did not match any variant of untagged enum JsonRpcResponse ❌
```

---

## What We Know

### Deployed Classes (Already on-chain from Dec 8)
- **RiskEngine**: Class hash `0x03ea934f4442de174715b458377bf5d1900c2a7c2a1d5e7486fcde9e522e2216` ✅
- **StrategyRouterV2**: Class hash `0x0265b81aeb675e22c88e5bdd9621489a17d397d2a09410e016c31a7fa76af796` ✅

### Newly Compiled (Not Yet Deployed)
- **StrategyRouterV35**: Sierra class `0x008186fa424166531326dcfa4e57c2c3e3a2a4b170494b66370899e0afda1b07`
- **CASM hash**: `0x034076eff0cfc95e3ac7073df2383449fd21f2bc8239c98f54c0e78f3f1ca2cc`
- **Status**: Compiled successfully, declaration blocked by RPC issue

---

## Options to Resolve

### Option 1: Use Pre-Existing RiskEngine Class ⭐ (Recommended)
Since RiskEngine is already declared and you need a working settlement layer:
- Deploy instance using existing RiskEngine class hash
- This unblocks the backend immediately
- StrategyRouterV35 can be deployed once RPC issue is resolved

### Option 2: Fix RPC/starkli Mismatch
- Research starknet-rs or starknet.py RPC handling
- Try different RPC endpoint (Infura, custom Pathfinder node)
- Downgrade/upgrade starkli version

### Option 3: Wait for PublicNode Update
- They may fix their RPC response format
- Or switch to paid RPC that's more stable

---

## Summary

**We've completed**:
- ✅ Fixed compilation issues
- ✅ Built StrategyRouterV35 successfully
- ✅ Backend fully operational with stone prover

**We're stuck on**:
- ❌ Declaring StrategyRouterV35 due to RPC response parsing error
- ❌ RiskEngine can't be redeclared (hash mismatch - it's already on-chain from Dec 8)

**Recommendation**: Deploy RiskEngine instance using the existing class hash to get the sprint fully working while we investigate the RPC issue for V35.
