# Deploy Your Own FactRegistry - Guide

## Quick Answer

**Actually, you might not need to deploy your own!**

The existing FactRegistry contract (`0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`) is public - you can call it directly with just gas.

**But if you want your own deployment**, here's how:

---

## Option 1: Use Existing Contract (Easiest) ✅

**Just use the existing address**:
```python
# In backend/app/services/integrity_service.py
INTEGRITY_VERIFIER_SEPOLIA = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
```

**Test it**:
```python
integrity = IntegrityService(rpc_url="...", network="sepolia")
result = await integrity.verify_proof_full_and_register_fact(
    verifier_config=your_config,
    stark_proof=your_proof
)
```

**If it works**: Done! No deployment needed.

---

## Option 2: Deploy Your Own

### Step 1: Build Contract
```bash
cd /opt/obsqra.starknet/integrity
scarb build
```

### Step 2: Declare
```bash
cd /opt/obsqra.starknet/contracts
# Copy the contract file
cp ../integrity/target/dev/integrity_FactRegistry.contract_class.json target/dev/

# Declare (may need to adjust contract name)
sncast --account deployer declare \
    --contract-name integrity_FactRegistry \
    --network sepolia
```

### Step 3: Deploy
```bash
OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
sncast --account deployer deploy \
    --class-hash <class_hash_from_declare> \
    --constructor-calldata $OWNER \
    --network sepolia
```

### Step 4: Update Code
```python
# backend/app/services/integrity_service.py
INTEGRITY_VERIFIER_SEPOLIA = <your_deployed_address>
```

---

## Recommendation

**Try Option 1 first** - the existing contract should work with just gas (no credits).

If it doesn't work, then deploy your own (Option 2).

---

## What `verify_proof_full_and_register_fact` Actually Does

Looking at the Integrity contract code:
```cairo
fn verify_proof_full_and_register_fact(...) -> FactRegistered {
    // 1. Verifies the proof (calls verifier contract)
    let result = verifier.verify_proof_full(...);
    
    // 2. Only registers if verification succeeds
    self._register_fact(result.fact, ...);
}
```

**It DOES verify** - it calls the verifier first, then registers the fact hash only if verification succeeds.

So the existing contract should work fine!
