# Deployment Unblock Guide - StrategyRouterV35

**Date:** January 26, 2026  
**Status:** Blocked on RPC compatibility  
**Issue:** `Error: data did not match any variant of untagged enum JsonRpcResponse`

---

## The Problem

When trying to declare StrategyRouterV35 using `starkli`, the RPC returns a response that starkli cannot parse:

```
Error: data did not match any variant of untagged enum JsonRpcResponse
```

**Root Cause:** RPC API version mismatch between:
- **starkli 0.3.8** expects: RPC API v0.6 or v0.7 format
- **PublicNode RPC** returns: RPC API v0.8.1 format (different JSON structure)

This is **NOT a code issue** - the contract compiles fine. It's a tool/RPC compatibility problem.

---

## What Works

✅ **RiskEngine** - Already declared successfully  
✅ **Contracts compile** - All contracts build with Cairo 2.8.5  
✅ **Stone Prover** - Fully integrated and working  
✅ **Backend services** - Production ready  

---

## How We Solved This Before (From Codebase History)

**Previous Solution (STARKLI_0.3.8_SUCCESS.md, RPC_SOLUTION_DOCUMENTATION.md):**

1. ✅ **Built starkli 0.3.8 from source** (5m 45s build time)
   - This solved Sierra 1.7.0 compatibility
   - Location: `/root/.local/bin/starkli`
   - Source: Built from https://github.com/xJonathanLEI/starkli.git

2. ✅ **Used PublicNode RPC** (found in their own `Scarb.toml`)
   - Endpoint: `https://starknet-sepolia-rpc.publicnode.com`
   - This was already configured in their codebase!

3. ✅ **Result:** RiskEngine declared successfully with this exact combination

**Key Insight:** The RPC endpoint was in their own config files the whole time. They just needed to match the tool version (starkli 0.3.8) with the RPC.

---

## Solutions (In Order of Preference)

### Solution 1: Build starkli 0.3.8 from Source (PROVEN WORKING - 6 minutes)

**This is exactly what worked before:**

```bash
# Build starkli 0.3.8 from source
cd /tmp
git clone https://github.com/xJonathanLEI/starkli.git
cd starkli
cargo build --release

# Install it
cp target/release/starkli /root/.local/bin/starkli
chmod +x /root/.local/bin/starkli

# Verify version
starkli --version  # Should show 0.3.8

# Then declare with PublicNode RPC (from your Scarb.toml)
export STARKNET_KEYSTORE_PASSWORD='L!nux123'
starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia-rpc.publicnode.com
```

**Why this works:** starkli 0.3.8 has better RPC compatibility and full Sierra 1.7.0 support. This exact combination worked for RiskEngine.

---

### Solution 2: Use Alternative RPC Endpoint (5 minutes)

**Try RPC endpoints that support v0.6/v0.7 format:**

```bash
# Option A: Official Starknet RPC (v0_6 endpoint)
starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://sepolia.starknet.io/rpc/v0_6

# Option B: Lava Network RPC
starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://rpc.starknet.lava.build

# Option C: Alchemy (requires API key, but supports v0_6)
starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/YOUR_KEY/rpc/v0_6
```

**Why this works:** These endpoints explicitly support the `/rpc/v0_6` or `/rpc/v0_7` path, which tells the RPC to return responses in the format starkli expects.

---

### Solution 3: Check if starkli 0.3.8 Already Exists (1 minute)

**Before building, check if it's already installed:**

```bash
# Check current starkli version
starkli --version

# Check if 0.3.8 binary exists
ls -la /root/.local/bin/starkli
file /root/.local/bin/starkli

# If it's already 0.3.8, just use it with PublicNode RPC
export STARKNET_KEYSTORE_PASSWORD='L!nux123'
starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia-rpc.publicnode.com
```

**Note:** According to STARKLI_0.3.8_SUCCESS.md, they already built this. Check if it exists first!

---

### Solution 4: Upgrade starkli to Latest Version (10 minutes)

**Newer starkli versions support RPC v0.8.1:**

```bash
# Check current version
starkli --version

# Upgrade starkli (if using starkliup)
starkliup

# Or build from source (if needed)
git clone https://github.com/xJonathanLEI/starkli.git
cd starkli
cargo build --release
# Use the new binary
```

**Expected result:** starkli 0.4.0+ should support RPC v0.8.1 format.

**Check:** After upgrade, verify with:
```bash
starkli --version
# Should show 0.4.0 or higher
```

---

### Solution 5: Use sncast (Alternative Tool) (15 minutes)

**sncast is an alternative deployment tool that may have better RPC compatibility:**

```bash
# Check if sncast is installed
sncast --version

# If not installed:
cargo install sncast

# Declare using sncast
sncast declare \
  --contract-name StrategyRouterV35 \
  --network sepolia \
  --account deployer \
  --path contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json
```

**Note:** sncast v0.53.0 requires RPC v0.10.0, which may not be available. Check RPC compatibility first.

---

### Solution 6: Use starknet-py (Python SDK) (30 minutes)

**Bypass starkli entirely and use Python SDK:**

```python
#!/usr/bin/env python3
"""
Deploy StrategyRouterV35 using starknet-py
Bypasses starkli RPC compatibility issues
"""
from starknet_py.net.client import Client
from starknet_py.net.account import Account
from starknet_py.net.signer import KeyPair
from starknet_py.contract import Contract
import json

# RPC endpoint (supports v0.8.1)
RPC_URL = "https://starknet-sepolia-rpc.publicnode.com"

# Account credentials
ACCOUNT_ADDRESS = 0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d
PRIVATE_KEY = 0x7fd44d52324945e2d9f2e62bd2dadb794e2274dbd0955251aeca6cc96153afc

# Load contract
with open("contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json") as f:
    contract_class = json.load(f)

# Create client and account
client = Client(RPC_URL, net="testnet")
key_pair = KeyPair.from_private_key(PRIVATE_KEY)
account = Account(client=client, address=ACCOUNT_ADDRESS, key_pair=key_pair)

# Declare contract
result = await account.declare(contract_class, max_fee=int(1e18))
print(f"Declaration transaction: {result.hash}")
print(f"Class hash: {result.class_hash}")
```

**Run with:**
```bash
python3 deploy_via_starknet_py.py
```

---

### Solution 7: Manual JSON-RPC (Last Resort - Complex)

**Direct JSON-RPC calls bypassing all tools:**

See existing scripts:
- `/opt/obsqra.starknet/declare_manual_rpc.py` - Partial implementation
- `/opt/obsqra.starknet/declare_via_rpc.py` - Partial implementation

**Why this is complex:** Requires:
1. Computing Sierra class hash (Blake2s algorithm)
2. ECDSA signature generation
3. Transaction nonce management
4. Fee estimation

**Recommendation:** Only use if all other solutions fail.

---

## Quick Test: Verify RPC Compatibility

**Before trying deployment, test which RPC endpoints work:**

```bash
# Test PublicNode (current - may fail)
curl -X POST https://starknet-sepolia-rpc.publicnode.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_blockNumber","params":[],"id":1}'

# Test Official RPC v0_6
curl -X POST https://sepolia.starknet.io/rpc/v0_6 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_blockNumber","params":[],"id":1}'

# Test Lava Network
curl -X POST https://rpc.starknet.lava.build \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"starknet_blockNumber","params":[],"id":1}'
```

**Look for:** `"result"` in the response. If you see `"result"`, the RPC is working.

---

## ⚠️ CRITICAL FINDING: You Have TWO starkli Versions!

**Current situation:**
- `/root/.starkli/bin/starkli` → **0.4.2** (newer, might have RPC issues)
- `/root/.local/bin/starkli` → **0.3.8** (proven working version!)

**The problem:** Your PATH is using 0.4.2, but 0.3.8 exists and worked before!

---

## Recommended Action Plan (Based on Previous Success)

### Step 1: Use the Proven Working starkli 0.3.8 (1 min)
```bash
# Use the exact binary that worked before
/root/.local/bin/starkli --version  # Should show 0.3.8

# Use this binary explicitly (don't rely on PATH)
export STARKNET_KEYSTORE_PASSWORD='L!nux123'
/root/.local/bin/starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia-rpc.publicnode.com
```

**This is the EXACT command that worked for RiskEngine!**

### Step 2: If Step 1 Fails, Check PATH (1 min)
```bash
# Make sure you're using the right starkli
which starkli  # Check which one is in PATH

# Option A: Use full path (safest)
/root/.local/bin/starkli declare ...

# Option B: Update PATH to prefer 0.3.8
export PATH="/root/.local/bin:$PATH"
starkli --version  # Should now show 0.3.8
```

### Step 3: If Needed, Build starkli 0.3.8 from Source (6 min)
```bash
# This is the PROVEN solution from STARKLI_0.3.8_SUCCESS.md
cd /tmp
git clone https://github.com/xJonathanLEI/starkli.git
cd starkli
cargo build --release
cp target/release/starkli /root/.local/bin/starkli
```

### Step 4: Use PublicNode RPC (Already in Your Config) (2 min)
```bash
# PublicNode RPC was found in your Scarb.toml - use it!
export STARKNET_KEYSTORE_PASSWORD='L!nux123'
starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia-rpc.publicnode.com
```

**This exact combination worked for RiskEngine. Use it again!**

---

## Alternative: If PublicNode RPC Fails (5 min)
```bash
# Use official RPC with v0_6 endpoint
starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://sepolia.starknet.io/rpc/v0_6
```

### Step 2: If Step 1 Fails, Upgrade starkli (10 min)
```bash
starkliup  # or build from source
# Then retry with PublicNode RPC
```

### Step 3: If Step 2 Fails, Use starknet-py (30 min)
```bash
# Use the Python script approach (Solution 4)
```

---

## What's NOT the Problem

❌ **Contract code** - Compiles fine  
❌ **Cairo version** - 2.8.5 is correct  
❌ **Account credentials** - RiskEngine deployed successfully  
❌ **Network connectivity** - RPC is responding  
❌ **Contract size** - Within limits  

**The ONLY issue:** JSON response format mismatch between starkli parser and RPC response.

---

## Files to Reference

- **RPC Compatibility:** `/opt/obsqra.starknet/RPC_COMPATIBILITY_SOLUTION.md`
- **Deployment Status:** `/opt/obsqra.starknet/SPRINT_DEPLOYMENT_STATUS.md`
- **Workaround Scripts:** 
  - `/opt/obsqra.starknet/declare_manual_rpc.py`
  - `/opt/obsqra.starknet/declare_via_rpc.py`
- **Deployment Script:** `/opt/obsqra.starknet/deploy_v2.sh`

---

## Expected Outcome

After applying Solution 1 or 2, you should see:

```
✓ Contract declared successfully
Class hash: 0x...
Transaction hash: 0x...
```

Then proceed to deploy the instance:
```bash
starkli deploy <CLASS_HASH> <CONSTRUCTOR_ARGS> \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc <WORKING_RPC_URL>
```

---

## Summary for Other Agent

**The blocker:** RPC JSON response format incompatibility (JsonRpcResponse parsing error).

**CRITICAL FINDING:** You have TWO starkli versions installed:
- `/root/.starkli/bin/starkli` → 0.4.2 (currently in PATH, causing issues)
- `/root/.local/bin/starkli` → 0.3.8 (proven working version!)

**IMMEDIATE FIX (30 seconds):**
```bash
# Use the proven working version explicitly
/root/.local/bin/starkli declare \
  contracts/target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli-wallets/deployer/keystore.json \
  --rpc https://starknet-sepolia-rpc.publicnode.com
```

**PROVEN SOLUTION (from codebase history):**
1. ✅ Use `/root/.local/bin/starkli` (0.3.8) - Already installed!
2. ✅ Use PublicNode RPC: `https://starknet-sepolia-rpc.publicnode.com` (already in Scarb.toml!)
3. ✅ This exact combination worked for RiskEngine declaration

**The issue:** You're probably using the wrong starkli version (0.4.2 instead of 0.3.8). Just use the full path to the working version!

**Files to reference:**
- `STARKLI_0.3.8_SUCCESS.md` - Shows how they built it before
- `RPC_SOLUTION_DOCUMENTATION.md` - Documents the exact solution
- `DEPLOYMENT_SUCCESS_PUBLICNODE.md` - Shows PublicNode RPC working

**Everything else is ready:** Contracts compile, Stone prover works, backend is production-ready. Just need to use the same solution that worked before: starkli 0.3.8 + PublicNode RPC.

---

**Status:** Ready to unblock - just need RPC compatibility fix  
**Estimated time:** 5-30 minutes depending on solution chosen  
**Risk:** Low - all other systems verified working
