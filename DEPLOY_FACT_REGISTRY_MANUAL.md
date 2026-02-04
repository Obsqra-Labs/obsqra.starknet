# Deploy Your Own FactRegistry - Manual Steps

## Quick Note

**The existing contract DOES verify proofs!** But if you want your own deployment:

---

## Manual Deployment Steps

### Step 1: Fix RPC in integrity/snfoundry.toml

```bash
cd /opt/obsqra.starknet/integrity
# Update snfoundry.toml to use working RPC
# (Already done - using publicnode.com)
```

### Step 2: Declare Contract

```bash
cd /opt/obsqra.starknet/integrity
sncast --account deployer declare --contract-name FactRegistry
```

**Note**: May need to use a compatible RPC. If it fails, try:
- Use the same RPC URL as your contracts directory
- Or declare from contracts directory with correct contract file path

### Step 3: Deploy

```bash
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
sncast --account deployer deploy \
    --class-hash <class_hash_from_step_2> \
    --constructor-calldata $OWNER
```

### Step 4: Update Code

```python
# backend/app/services/integrity_service.py
INTEGRITY_VERIFIER_SEPOLIA = <your_deployed_address>
```

---

## Alternative: Use Existing Contract (Recommended)

**The existing contract at `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`:**

- ✅ **DOES verify proofs** (calls verifier first)
- ✅ **Public contract** (just pay gas)
- ✅ **No credits needed**
- ✅ **Already working**

**Test it first** - you might not need to deploy your own!
