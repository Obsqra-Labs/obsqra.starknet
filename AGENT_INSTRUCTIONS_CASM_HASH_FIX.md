# Agent Instructions: Fix CASM Hash Mismatch for StrategyRouterV2 Deployment

**Status:** URGENT - Blocking testnet deployment  
**Date:** January 26, 2026  
**Objective:** Find Cairo compiler version that produces CASM hash `0x4120dfff...` expected by PublicNode RPC

---

## The Problem (30-Second Version)

**What RPC Expects:** `0x4120dfff561b2868ae271da2cfb031a4c0570d5bb9afd2c232b94088f457492`  
**What We Produce:** `0x039bcde8fe0a75c690195698ac14248788b4304c9f23d22d19765c352f8b3b3f`  
**Sierra Class Hash:** `0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d42b7`  
**Current Toolchain:** Scarb 2.11.0 + Cairo 2.11.0 + sncast 0.53.0

**Error:** `Mismatch compiled class hash` - RPC rejects declaration before transaction submission

---

## Root Cause

This is **NOT a code bug**. This is a **compiler version lock**:

- CASM (Cairo Assembly) hashes are **deterministic per compiler version**
- PublicNode RPC was compiled with an older Cairo version
- Our Cairo 2.11.0 produces a different CASM hash than what RPC expects
- RPC does strict validation to prevent malicious sequencer behavior

**This is expected behavior in STARK-based systems** - determinism is a feature, not a bug.

---

## Solution Strategy

**Goal:** Binary search Cairo versions until CASM hash matches `0x4120dfff...`

**Stop Condition:** When `scarb build` produces CASM hash `0x4120dfff561b2868ae271da2cfb031a4c0570d5bb9afd2c232b94088f457492`

---

## Step-by-Step Instructions

### Step 1: Set Up Test Environment

```bash
cd /opt/obsqra.starknet/contracts

# Backup current Scarb.toml
cp Scarb.toml Scarb.toml.backup

# Create test script location
mkdir -p /tmp/cairo_version_test
```

### Step 2: Test Cairo Versions (In Priority Order)

**Test these versions in order (most likely first):**

1. **Cairo 2.10.1** (most likely match)
2. **Cairo 2.10.0**
3. **Cairo 2.9.2**
4. **Cairo 2.9.1**
5. **Cairo 2.8.4**
6. **Cairo 2.8.0**

**For each version, run:**

```bash
# Set Cairo version in Scarb.toml
# Edit Scarb.toml: change starknet dependency to match Cairo version
# Example for Cairo 2.10.1:
# [dependencies]
# starknet = ">=2.10.1"

# Clean build
scarb clean
rm -rf Scarb.lock target/

# Build
scarb build 2>&1 | tee /tmp/cairo_version_test/cairo_2.10.1_build.log

# Extract CASM hash from compiled contract
# The hash is in: target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json
# Look for "compiled_class_hash" field

# Compare to target: 0x4120dfff561b2868ae271da2cfb031a4c0570d5bb9afd2c232b94088f457492
```

### Step 3: Automated Test Script

**Create this script:** `/tmp/test_cairo_versions.sh`

```bash
#!/bin/bash

TARGET_HASH="0x4120dfff561b2868ae271da2cfb031a4c0570d5bb9afd2c232b94088f457492"
CONTRACT_NAME="StrategyRouterV2"
PROJECT_DIR="/opt/obsqra.starknet/contracts"

cd "$PROJECT_DIR"

# Versions to test (in priority order)
VERSIONS=("2.10.1" "2.10.0" "2.9.2" "2.9.1" "2.8.4" "2.8.0")

for version in "${VERSIONS[@]}"; do
    echo "=========================================="
    echo "Testing Cairo $version"
    echo "=========================================="
    
    # Update Scarb.toml with version
    # Note: This requires manual editing or sed replacement
    # For now, document the manual process
    
    # Clean
    scarb clean
    rm -rf Scarb.lock target/
    
    # Build
    echo "Building with Cairo $version..."
    if scarb build 2>&1 | tee /tmp/cairo_test_${version}.log; then
        # Extract CASM hash
        CASM_FILE="target/dev/obsqra_contracts_${CONTRACT_NAME}.compiled_contract_class.json"
        if [ -f "$CASM_FILE" ]; then
            HASH=$(jq -r '.compiled_class_hash' "$CASM_FILE" 2>/dev/null || \
                   grep -oP '"compiled_class_hash"\s*:\s*"\K0x[a-fA-F0-9]{64}' "$CASM_FILE" | head -1)
            
            echo "Cairo $version produces CASM hash: $HASH"
            
            if [ "$HASH" = "$TARGET_HASH" ]; then
                echo "✅ MATCH FOUND! Cairo $version produces the expected hash!"
                echo "Solution: Use Cairo $version for deployment"
                exit 0
            else
                echo "❌ Hash mismatch. Continuing..."
            fi
        else
            echo "⚠️  CASM file not found. Check build logs."
        fi
    else
        echo "❌ Build failed. Check logs: /tmp/cairo_test_${version}.log"
    fi
    
    echo ""
done

echo "=========================================="
echo "No matching version found in tested range."
echo "Next steps:"
echo "1. Check PublicNode RPC version directly"
echo "2. Try alternative RPC endpoints"
echo "3. Contact PublicNode support"
echo "=========================================="
```

**Make it executable:**
```bash
chmod +x /tmp/test_cairo_versions.sh
```

### Step 4: Manual Version Testing (If Script Fails)

**For each Cairo version:**

1. **Edit Scarb.toml:**
   ```toml
   [dependencies]
   starknet = ">=2.10.1"  # Change version here
   ```

2. **Clean and rebuild:**
   ```bash
   scarb clean
   rm -rf Scarb.lock target/
   scarb build
   ```

3. **Extract CASM hash:**
   ```bash
   # Method 1: Using jq
   jq -r '.compiled_class_hash' target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json
   
   # Method 2: Using grep
   grep -oP '"compiled_class_hash"\s*:\s*"\K0x[a-fA-F0-9]{64}' \
     target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json
   ```

4. **Compare to target:**
   ```bash
   if [ "$EXTRACTED_HASH" = "0x4120dfff561b2868ae271da2cfb031a4c0570d5bb9afd2c232b94088f457492" ]; then
       echo "✅ MATCH!"
   fi
   ```

### Step 5: When Match Is Found

**Once you find the matching Cairo version:**

1. **Document the version:**
   ```bash
   echo "Cairo $(grep 'starknet =' Scarb.toml) produces CASM hash 0x4120dfff..." > /tmp/cairo_match.txt
   ```

2. **Rebuild with that version:**
   ```bash
   scarb clean
   scarb build
   ```

3. **Declare with sncast:**
   ```bash
   sncast --account deployer declare \
     --contract-name StrategyRouterV2 \
     --network sepolia
   ```

4. **Expected result:** Declaration succeeds (no hash mismatch error)

---

## Alternative Solutions (If Version Match Fails)

### Option A: Query PublicNode RPC Version

```bash
# Try to get RPC version info
curl -X POST https://starknet-sepolia-rpc.publicnode.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "starknet_specVersion",
    "id": 1
  }'
```

**If they respond:** Use that Cairo version or compatible one.

### Option B: Try Alternative RPC Endpoints

**Test with other RPCs that might accept your hash:**

1. **Alchemy Starknet RPC** (if available)
2. **Infura Starknet RPC** (if available)
3. **Starknet Foundation RPC** (if available)

**Command:**
```bash
# Update Scarb.toml RPC URL
# Then redeclare
sncast --account deployer declare \
  --contract-name StrategyRouterV2 \
  --network sepolia
```

### Option C: Contact PublicNode Support

**Ask them:**
- "What Cairo compiler version does your Sepolia RPC use?"
- "Can you provide the expected CASM hash for Sierra class `0x065a9feb...`?"
- "When will you upgrade to support Cairo 2.11.0?"

---

## Success Criteria

✅ **Task Complete When:**
- You've identified the Cairo version that produces `0x4120dfff...`
- OR you've confirmed PublicNode's Cairo version
- OR you've found an alternative RPC that accepts your hash
- AND StrategyRouterV2 can be declared successfully

---

## Expected Timeline

- **Binary search through versions:** 30-45 minutes
- **Manual testing if script fails:** 45-60 minutes
- **Alternative RPC testing:** 15-30 minutes
- **PublicNode contact:** 15-30 minutes (if needed)

**Total:** 1-2 hours maximum

---

## What NOT to Do

❌ **Don't modify source code** - The code is correct  
❌ **Don't try to "force" the hash** - It's cryptographically derived  
❌ **Don't assume Starknet is broken** - This is expected behavior  
❌ **Don't wait for ecosystem convergence** - Fix it now

---

## Report Format

**When complete, report:**

```markdown
## CASM Hash Mismatch Resolution

### Cairo Version Tested
- Cairo 2.10.1: Produces hash 0x...
- Cairo 2.10.0: Produces hash 0x...
- [etc.]

### Solution Found
- **Matching Version:** Cairo X.Y.Z
- **CASM Hash:** 0x4120dfff... ✅
- **Action Taken:** [Rebuilt with X.Y.Z and declared successfully]

### Alternative (if no match)
- **PublicNode Response:** [What they said]
- **Alternative RPC:** [Which one worked]
- **Next Steps:** [What to do]
```

---

## Files to Reference

- `/opt/obsqra.starknet/contracts/Scarb.toml` - Update Cairo version here
- `/opt/obsqra.starknet/contracts/src/strategy_router_v2.cairo` - Source contract
- `/opt/obsqra.starknet/DEPLOYMENT_UNBLOCK_GUIDE.md` - Previous solutions
- `/opt/obsqra.starknet/docs/DEV_LOG.md` - Historical fixes

---

**Start Time:** [When you begin]  
**Expected Completion:** [Start time + 1-2 hours]  
**Status:** 🔴 IN PROGRESS
