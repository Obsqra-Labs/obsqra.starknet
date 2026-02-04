# Solution: No Credits Needed - Deploy Your Own Verifier

## The Problem

**Herodotus Atlantic** (their managed service) requires credits to submit proofs.
- Atlantic = Managed service that handles proof submission
- Credits = Paid service (even on testnet, may need credits)

**But**: You don't need Atlantic! You can deploy your own verifier contract.

---

## Solution: Deploy Your Own Integrity Verifier

### What You Need

1. **Deploy Integrity FactRegistry contract** (your own deployment)
2. **Submit proofs directly** to your contract (no credits needed)
3. **Your contract verifies** proofs and stores fact hashes
4. **Your RiskEngine checks** your own FactRegistry

### The Flow

```
Your Proof → Your FactRegistry Contract → Fact Hash Registered → RiskEngine Checks Your Registry
```

**No credits needed** - you just pay gas (like any contract call).

---

## How to Deploy Your Own Verifier

### Step 1: Build Integrity Contract

```bash
cd /opt/obsqra.starknet/integrity
scarb build
```

This creates the FactRegistry contract you can deploy.

### Step 2: Deploy FactRegistry

```bash
# Declare the contract
sncast --account deployer declare \
  --contract-name FactRegistry \
  --network sepolia

# Deploy it
sncast --account deployer deploy \
  --class-hash <class_hash> \
  --constructor-calldata <owner_address> \
  --network sepolia
```

**Owner address**: Your deployer address (for admin functions)

### Step 3: Update Your Code

**Backend** (`backend/app/services/integrity_service.py`):
```python
# Change from:
INTEGRITY_VERIFIER_SEPOLIA = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c

# To your deployed address:
INTEGRITY_VERIFIER_SEPOLIA = 0x...your_deployed_address...
```

**Contract** (`contracts/src/sharp_verifier.cairo`):
```cairo
// Update the default address or pass it as parameter
const MY_FACT_REGISTRY: ContractAddress = 0x...your_deployed_address...;
```

**Backend Config** (`backend/app/config.py`):
```python
# Add new config
MY_FACT_REGISTRY_ADDRESS: str = "0x...your_deployed_address..."
```

### Step 4: Submit Proofs to Your Contract

**Backend** (`backend/app/api/routes/risk_engine.py`):
```python
# Already works! Just uses your deployed address
integrity = IntegrityService(rpc_url, network="sepolia")
# This will now call YOUR contract instead of Herodotus
result = await integrity.verify_proof_full_and_register_fact(
    verifier_config,
    stark_proof
)
```

---

## What This Gives You

### ✅ No Credits Needed
- You deploy the contract
- You submit proofs to YOUR contract
- You pay gas (like any transaction)
- No service fees, no credits

### ✅ Full Control
- Your own FactRegistry
- Your own verification
- Can customize if needed

### ✅ Same Functionality
- Same verification logic (open source)
- Same fact hash storage
- Same on-chain verification

---

## Alternative: Use Existing Contract (If It Works)

**Actually**: The Herodotus FactRegistry contract might work without credits!

**Check**: Try calling it directly:
```python
# In backend
integrity = IntegrityService(rpc_url, network="sepolia")
# This calls the PUBLIC contract - might work without credits
result = await integrity.verify_proof_full_and_register_fact(...)
```

**Why it might work**:
- FactRegistry is a **public contract**
- Calling it directly (not via Atlantic) might not need credits
- You just pay gas

**Test it first** before deploying your own!

---

## Recommendation

### Option A: Test Existing Contract First (Easiest)

1. **Try calling Herodotus FactRegistry directly**:
   ```python
   # In your backend
   integrity = IntegrityService(...)
   result = await integrity.verify_proof_full_and_register_fact(...)
   ```

2. **If it works**: You're done! No credits needed, no deployment needed.

3. **If it fails**: Move to Option B.

### Option B: Deploy Your Own (If Needed)

1. Deploy Integrity FactRegistry contract
2. Update addresses in code
3. Submit proofs to your contract
4. No credits needed

---

## Quick Test

```python
# Test if existing contract works without credits
from app.services.integrity_service import IntegrityService

integrity = IntegrityService(rpc_url="...", network="sepolia")

# Try submitting a proof
result = await integrity.verify_proof_full_and_register_fact(
    verifier_config=your_config,
    stark_proof=your_proof
)

if result:
    print("✅ Works! No credits needed")
else:
    print("❌ Need to deploy your own")
```

---

## Bottom Line

**You might not need credits at all!**

- **FactRegistry contract** = Public contract, just pay gas
- **Atlantic service** = Managed service, needs credits

**Try the contract first** - if it works, you're done. If not, deploy your own (same code, your deployment).

---

## Next Steps

1. **Test existing contract** (5 minutes)
2. **If it works**: Done! ✅
3. **If not**: Deploy your own (30 minutes)
