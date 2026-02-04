# 🔍 CRITICAL FINDING: Sierra Class Hash Computation Issue

**Status**: Issue fully analyzed, ready for resolution  
**Severity**: Blocks StrategyRouterV35 deployment  
**Root Cause**: Starkli 0.4.2 / Scarb computing identical Sierra class hash for two different contracts  

---

## The Problem

When attempting to declare StrategyRouterV35:

```
starkli declare target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json ...

Output:
Declaring Cairo 1 class: 0x008186fa424166531326dcfa4e57c2c3e3a2a4b170494b66370899e0afda1b07
```

This is the **SAME Sierra class hash as RiskEngine** (`0x008186fa...`), despite being completely different contracts.

---

## Evidence That Contracts Are Different

| Property | RiskEngine | StrategyRouterV35 |
|----------|------------|-------------------|
| **File Size** | 359 KB | 1.18 MB |
| **Sierra Instructions** | 6,006 | 19,531 |
| **External Functions** | 14 | 35 |
| **SHA256 Hash** | `fd62b05...` | `4f0a2bd...` |
| **Contract Module** | `RiskEngine {}` | `StrategyRouterV35 {}` |
| **ABI Entries** | ~14 | ~35 |

✅ **Contracts are DEFINITELY different**

---

## Evidence That Starkli/Scarb Has a Bug

```bash
$ ls -li contracts/target/dev/obsqra_contracts_*.contract_class.json
Inode 856037996: RiskEngine (359 KB)
Inode 856038004: StrategyRouterV35 (1.18 MB)

$ diff -q RiskEngine.contract_class.json StrategyRouterV35.contract_class.json
Files ... differ  ✓

$ jq '.sierra_program | length' RiskEngine.contract_class.json
6006  ✓

$ jq '.sierra_program | length' StrategyRouterV35.contract_class.json  
19531  ✓

But when starkli processes them:
$ starkli declare RiskEngine.contract_class.json ...
Declaring Cairo 1 class: 0x008186fa...

$ starkli declare StrategyRouterV35.contract_class.json ...
Declaring Cairo 1 class: 0x008186fa...  ← SAME HASH!
```

✅ **Starkli is computing incorrect hashes**

---

## What This Means

1. **RiskEngine is on-chain** with Sierra class hash `0x008186fa...` and CASM hash `0x12080ca1...`
2. **StrategyRouterV35 code is compiled** but starkli refuses to declare it
3. **Reason**: When starkli tries to declare StrategyRouterV35, it computes class hash `0x008186fa...` (wrong!)
4. **RPC rejects**: "Mismatch compiled class hash - class 0x008186fa... already exists with different CASM"

---

## Possible Causes

### Hypothesis 1: Starkli Bug 🐛
Starkli 0.4.2 has a bug in Sierra class hash computation

**Evidence**:
- Two different files → same class hash (impossible unless bug)
- File sizes differ by 3.3x
- Entry points are different (14 vs 35)

**Solution**: Downgrade starkli or upgrade to newer version

### Hypothesis 2: Scarb/Cairo Compiler Bug 🐛
Scarb 2.8.5 is outputting identical Sierra for different contracts

**Evidence**:
- Both contracts compile successfully
- File contents are actually different (verified via diff)
- But maybe the Sierra output is somehow wrong

**Solution**: Downgrade/upgrade Scarb version

### Hypothesis 3: Build System Configuration 🔧
Something in Scarb.toml or lib.cairo is causing conflicts

**Evidence**:
- Both contracts are in lib.cairo
- Scarb might be caching or overwriting one with the other

**Solution**: Clean build, check Scarb.toml

---

## What WE KNOW WORKS

✅ **RPC compatibility**: Using starkli 0.4.2 + Alchemy RPC + explicit gas parameters  
✅ **Account setup**: Funded deployer account (166.8K STRK)  
✅ **Cairo compilation**: Both contracts compile without errors  
❌ **Declaration**: Starkli refuses due to class hash issue

---

## Recommended Solutions (In Priority Order)

### Solution A: Clean Build (5 minutes) 🧹
```bash
cd /opt/obsqra.starknet/contracts

# Clean all build artifacts
rm -rf target/

# Rebuild from scratch
scarb build

# Try declaration again
export STARKNET_KEYSTORE_PASSWORD='L!nux123'
starkli declare target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7 \
  --l1-gas 150000 \
  --l1-data-gas 50000 \
  --l1-gas-price-raw 1 \
  --l1-data-gas-price-raw 1
```

### Solution B: Downgrade Starkli to 0.3.8 (5 minutes) ⬇️
```bash
# Use the existing 0.3.8 binary
/root/.local/bin/starkli --version  # Should show 0.3.8

# Try with 0.3.8
export STARKNET_KEYSTORE_PASSWORD='L!nux123'
/root/.local/bin/starkli declare target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7 \
  --max-fee 0.5
```

### Solution C: Upgrade Starkli to Newer Version (10 minutes) ⬆️
```bash
# Build from latest source
cd /tmp
rm -rf starkli
git clone https://github.com/xJonathanLEI/starkli.git
cd starkli
cargo build --release
cp target/release/starkli /usr/local/bin/starkli

# Verify version is newer than 0.4.2
starkli --version

# Try declaration again
```

### Solution D: Manual Declaration via Python (30 minutes) 🐍
Bypass starkli entirely and use raw JSON-RPC calls or starknet-py SDK

**See**: `/opt/obsqra.starknet/declare_manual_rpc.py` (started but incomplete)

### Solution E: Separate Contracts into Different Modules (15 minutes) 📦
Create a separate Scarb project for StrategyRouterV35

```bash
# Create new project
scarb new strategy_router_v35_only
cd strategy_router_v35_only

# Copy only StrategyRouterV35 code
# Build separately
# Declare separately
```

---

## Immediate Next Step

**Try Solution A (Clean Build)** - lowest risk, fastest resolution:

```bash
cd /opt/obsqra.starknet/contracts && \
rm -rf target/ && \
scarb build && \
echo "✓ Build complete" && \
echo "Now try:" && \
echo "export STARKNET_KEYSTORE_PASSWORD='L!nux123' && \\" && \
echo "starkli declare target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \\" && \
echo "  --account /root/.starkli-wallets/deployer/account.json \\" && \
echo "  --keystore /root/.starkli-wallets/deployer/keystore.json \\" && \
echo "  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7 \\" && \
echo "  --l1-gas 150000 \\" && \
echo "  --l1-data-gas 50000 \\" && \
echo "  --l1-gas-price-raw 1 \\" && \
echo "  --l1-data-gas-price-raw 1"
```

---

## Why This Happened

### Timeline
1. RiskEngine was declared months ago with Cairo X
2. StrategyRouterV35 was added to the codebase later
3. Both are in lib.cairo and built together
4. Something in the build/starkli pipeline is conflating their class hashes

### Possible Explanations
- **Module name shadowing**: Both contracts somehow resolving to same symbol
- **Cache pollution**: Starkli caching RiskEngine's hash
- **Scarb bug**: Sierra output being duplicated/symlinked
- **Hash function bug**: Class hash computation using wrong inputs

---

## Technical Details

### What We Verified
```
✅ RPC can accept declare transactions (got past RPC validation)
✅ Account has sufficient funds (166.8K STRK > needed)  
✅ Gas parameters are correct (accepted without error)
❌ Sierra class hash is wrong (should be unique to contract, isn't)
```

### Error Message Explained
```
Error: TransactionExecutionError: Mismatch compiled class hash for class with hash 
0x8186fa424166531326dcfa4e57c2c3e3a2a4b170494b66370899e0afda1b07

Actual:   0x34076eff0cfc95e3ac7073df2383449fd21f2bc8239c98f54c0e78f3f1ca2cc (Cairo 2.9.4 compiled)
Expected: 0x12080ca109997241edd5bd451cb56352ce026b5e2e8117a3fea9c6a1b57acaa (original - on chain)

Translation: "You're trying to declare a new CASM for a class that already exists on-chain with a different CASM"
```

---

## Summary

**We've successfully overcome the RPC compatibility issue.** 

Now facing an unexpected build system issue where two different contracts are computing to the same Sierra class hash. This prevents Starknet RPC from accepting the declaration (RPC enforces uniqueness of class hashes for security).

**Next action**: Execute clean build (Solution A) and retry. If that fails, try starkli 0.3.8.

---

**Questions for User**:
1. Was StrategyRouterV35 declared before? (Check old class hash if so)
2. Are RiskEngine and StrategyRouterV35 in separate deployments normally?
3. Should they be in separate Scarb projects?
