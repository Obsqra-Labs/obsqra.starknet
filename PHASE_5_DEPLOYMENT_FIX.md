# Phase 5 Deployment Fix - The December Solution

**Date:** January 26, 2026  
**Source:** `docs/DEV_LOG.md` - "Day 5: Victory 🎉"  
**Status:** ✅ PROVEN SOLUTION FROM DECEMBER

---

## The "Gold" Dev Log Solution

From `docs/DEV_LOG.md` (December 5, 2025):

### Day 4: Version Compatibility Hell

They had the EXACT same issue:
- RPC compatibility problems
- Tool version mismatches
- CASM hash mismatches

### Day 5: Victory 🎉

**The Solution That Worked:**

```bash
# Upgrade sncast to 0.53.0
snfoundryup

# Use built-in network instead of custom RPC
sncast --account deployer declare --contract-name RiskEngine --network sepolia
```

**Result:**
```
Success: Declaration completed
Class Hash: 0x61febd39ccffbbd986e071669eb1f712f4dcf5e008aae7fa2bed1f09de6e304
```

**Key Lesson from Dev Log:**
> "Don't fight the tooling. Use `--network sepolia` and let sncast figure out the RPC."

---

## December 10, 2025 - v3.5 Deployment (Also Used sncast)

They deployed StrategyRouter v3.5 using:

```bash
sncast --account deployer deploy \
  --class-hash 0x043acf130464d2a1325403f619a62480fd9d10a13941a81fcb2a491e2ec5bc28 \
  --constructor-calldata [args...] \
  --network sepolia
```

**Result:** Contract successfully deployed and verified on Starkscan.

---

## The Fix for Phase 5

### Stop Using starkli - Use sncast Instead!

**Current Problem:**
- Using `starkli` with custom RPC URLs
- Getting `JsonRpcResponse` parsing errors
- RPC version mismatches

**The Solution (From December):**

```bash
# 1. Make sure sncast is 0.53.0+ (you have it!)
sncast --version  # Should show 0.53.0

# 2. Declare StrategyRouterV35 using sncast with --network sepolia
cd /opt/obsqra.starknet/contracts
sncast --account deployer declare \
  --contract-name StrategyRouterV35 \
  --network sepolia

# 3. Deploy the instance
sncast --account deployer deploy \
  --class-hash <CLASS_HASH_FROM_STEP_2> \
  --constructor-calldata [constructor_args] \
  --network sepolia
```

**Why This Works:**
- `sncast 0.53.0` handles RPC compatibility automatically
- `--network sepolia` lets sncast pick the right RPC endpoint
- No need to specify custom RPC URLs
- No need to worry about RPC API versions

---

## What the Dev Log Says

### Key Takeaways from `docs/DEV_LOG.md`:

1. **"Use sncast for deployment, especially version 0.53.0+"**
   - You have sncast 0.53.0 installed ✅

2. **"Use `--network sepolia` - Don't bother with custom RPCs initially"**
   - This is the key! Let sncast handle it

3. **"Don't fight the tooling"**
   - starkli is flaky for deployment
   - sncast is more reliable

4. **"Read the compatibility tables first"**
   - But with `--network sepolia`, you don't need to!

---

## Step-by-Step Deployment

### Step 1: Verify sncast Setup

```bash
# Check version
sncast --version  # Should be 0.53.0

# Check account config (from Scarb.toml)
cat contracts/Scarb.toml | grep -A 5 "\[tool.sncast.deployer\]"
```

Your `Scarb.toml` already has:
```toml
[tool.sncast.deployer]
account = "deployer"
accounts-file = "~/.starknet_accounts/starknet_open_zeppelin_accounts.json"
network = "alpha-sepolia"
```

### Step 2: Declare StrategyRouterV35

```bash
cd /opt/obsqra.starknet/contracts

# Build first (make sure it compiles)
scarb build

# Declare using sncast (the December way!)
sncast --account deployer declare \
  --contract-name StrategyRouterV35 \
  --network sepolia
```

**Expected Output:**
```
command: sncast declare
contract_name: StrategyRouterV35
class_hash: 0x...
```

### Step 3: Deploy Instance

```bash
# Get constructor args (check contract source for constructor signature)
# Then deploy:
sncast --account deployer deploy \
  --class-hash <CLASS_HASH_FROM_STEP_2> \
  --constructor-calldata [owner, risk_engine, dao_manager, ...] \
  --network sepolia
```

---

## Why This Works (From Dev Log)

### The Compatibility Matrix Issue

From `docs/DEV_LOG.md`:
- `sncast 0.39.0` → expects RPC 0.7.0
- `sncast 0.53.0` → expects RPC 0.10.0
- But with `--network sepolia`, sncast handles this automatically!

### The CASM Hash Mismatch Issue

They had:
```
Error: Mismatch compiled class hash
Actual: 0x0614...
Expected: 0x32f5...
```

**Solution:** Use `sncast` instead of `starkli` - sncast's internal compiler matches what the network expects.

---

## What Changed Since December

**December:** They used this for RiskEngine and StrategyRouterV2  
**Now:** You need to deploy StrategyRouterV35 (same contract, just newer version)

**The method is identical!** Just use:
- `sncast` (not starkli)
- `--network sepolia` (not custom RPC)
- `--account deployer` (from your Scarb.toml config)

---

## Quick Reference

### December Success Pattern:
```bash
sncast --account deployer declare --contract-name <NAME> --network sepolia
sncast --account deployer deploy --class-hash <HASH> --constructor-calldata [args] --network sepolia
```

### Your Current Issue:
- Using `starkli` ❌
- Using custom RPC URLs ❌
- Getting JSON parsing errors ❌

### The Fix:
- Use `sncast` ✅
- Use `--network sepolia` ✅
- Let sncast handle RPC ✅

---

## Files to Reference

1. **`docs/DEV_LOG.md`** - The "gold" dev log with the full solution
   - Day 4: Version Compatibility Hell
   - Day 5: Victory 🎉
   - December 10: v3.5 Deployment

2. **`contracts/Scarb.toml`** - Your sncast config is already set up!

3. **`STRATEGYROUTER_V2_DEPLOYMENT.md`** - Shows December deployment pattern

---

## Bottom Line

**The December solution was:**
1. ✅ Use `sncast 0.53.0` (you have it)
2. ✅ Use `--network sepolia` (let sncast handle RPC)
3. ✅ Don't fight the tooling

**You're trying to use starkli with custom RPCs, but the proven solution is sncast with --network sepolia.**

**Just run:**
```bash
cd /opt/obsqra.starknet/contracts
sncast --account deployer declare --contract-name StrategyRouterV35 --network sepolia
```

That's it. This is exactly what worked in December. 🎯

---

**Status:** ✅ RPC ISSUE SOLVED - Just need to fund account  
**Confidence:** HIGH - This exact method worked for RiskEngine and StrategyRouterV2  
**Time:** < 5 minutes (after funding)

---

## ✅ BREAKTHROUGH: RPC Issue Solved!

**Just tested:** `sncast --account deployer declare --contract-name StrategyRouterV35 --network sepolia`

**Result:**
- ✅ Contract compiled successfully
- ✅ sncast connected to RPC (no JSON parsing errors!)
- ✅ Transaction prepared
- ⚠️ Insufficient balance for fees

**The RPC compatibility issue is SOLVED!** The December solution worked perfectly.

**Remaining Step:** Fund the account with more STRK

### How to Fund Account

From `docs/DEV_LOG.md`:
> "The faucet at [starknet-faucet.vercel.app](https://starknet-faucet.vercel.app) doesn't just send STRK—it actually triggers account deployment!"

**Option 1: Use Faucet**
1. Go to https://starknet-faucet.vercel.app
2. Connect your deployer wallet
3. Request STRK for Sepolia

**Option 2: Check Current Balance**
```bash
# Check account address from Scarb.toml config
# Then check balance on Starkscan or via RPC
```

**Option 3: Transfer from Another Account**
If you have another funded account, transfer STRK to the deployer account.

### After Funding

Once account is funded, run:
```bash
cd /opt/obsqra.starknet/contracts
sncast --account deployer declare --contract-name StrategyRouterV35 --network sepolia
```

**Expected:** Declaration will succeed (RPC issue is already solved!)
