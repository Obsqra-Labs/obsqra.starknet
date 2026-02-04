# Do You Have to Use Herodotus? Alternatives Explained

## Short Answer: **No, but it's the easiest path**

---

## The Relationship: SHARP vs Herodotus

### SHARP (StarkWare's Shared Prover)
- **What it is**: StarkWare's internal proving service
- **What it does**: Batches proofs, aggregates them, publishes fact hashes to Ethereum L1
- **Access**: **NOT a public API** - it's internal to StarkWare
- **Timeline**: 10-60 minutes for L1 settlement

### Herodotus Integrity (FactRegistry)
- **What it is**: A **contract deployed on Starknet** that verifies proofs
- **What it does**: Verifies STARK proofs and stores fact hashes on-chain
- **Access**: **Public contract** - anyone can call it
- **Timeline**: Immediate (on-chain verification)

**Key Point**: Herodotus Integrity is **one way** to verify proofs on-chain. It's not the same as SHARP.

---

## Your Options for On-Chain Verification

### Option 1: Herodotus Integrity (Current Choice) ✅

**What it is**:
- FactRegistry contract on Starknet (deployed by Herodotus)
- Verifies proofs and stores fact hashes
- Public, trustless, battle-tested

**Pros**:
- ✅ Already deployed (no setup needed)
- ✅ Public and trustless
- ✅ Well-documented
- ✅ Already integrated in your codebase
- ✅ Works immediately

**Cons**:
- ⚠️ Requires submitting proof to their contract first
- ⚠️ You're using their infrastructure

**Address**: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c` (Sepolia)

---

### Option 2: Deploy Your Own Verifier Contract

**What it is**:
- Deploy the Integrity verifier contract yourself
- Full control over verification
- Your own FactRegistry

**Pros**:
- ✅ Full control
- ✅ No dependency on Herodotus
- ✅ Can customize verification logic

**Cons**:
- ❌ Need to deploy and maintain contract
- ❌ More complex setup
- ❌ You're essentially duplicating what Herodotus did

**How**:
```bash
# Use Integrity package to deploy your own FactRegistry
cd integrity
scarb build
sncast deploy --class-hash <verifier_class_hash>
```

---

### Option 3: Direct SHARP Integration (Not Available)

**What it is**:
- Submit proofs directly to SHARP
- Get fact hashes from SHARP
- Verify fact hashes on L1

**Reality**:
- ❌ **SHARP is NOT a public API**
- ❌ No direct access to SHARP
- ❌ Only StarkWare can submit to SHARP
- ❌ Fact hashes are on L1, not L2

**Why it doesn't work**:
- SHARP is StarkWare's internal service
- You can't call it directly
- Fact hashes go to Ethereum L1, not Starknet L2

---

### Option 4: Custom Verifier Contract

**What it is**:
- Build your own proof verifier in Cairo
- Verify proofs directly in your contract
- No external dependencies

**Pros**:
- ✅ Complete independence
- ✅ No external services
- ✅ Can optimize for your use case

**Cons**:
- ❌ **Very complex** (need to port verifier logic to Cairo)
- ❌ 3-4 weeks of development
- ❌ Large gas costs
- ❌ Need deep ZK expertise

**Effort**: High (not recommended unless you have specific requirements)

---

## Recommendation: **Use Herodotus Integrity**

### Why It's the Best Choice

1. **Already Working**: Your codebase already integrates it
2. **Public & Trustless**: Contract is deployed, anyone can verify
3. **No Setup**: Just use the contract address
4. **Battle-Tested**: Used by many projects
5. **Standard**: It's the de facto standard for proof verification on Starknet

### The Flow

```
Your Proof → Submit to Herodotus Integrity Contract → Fact Hash Registered → Your Contract Checks Registry
```

**You're not "using Herodotus"** - you're calling a **public contract** that happens to be deployed by Herodotus. It's like using Uniswap's contract - it's public infrastructure.

---

## What "Using Herodotus" Actually Means

### What You're NOT Doing:
- ❌ Not using their API
- ❌ Not depending on their backend
- ❌ Not trusting them with your data
- ❌ Not paying them fees (just gas)

### What You ARE Doing:
- ✅ Calling a public contract on Starknet
- ✅ Using open-source verification logic
- ✅ Storing fact hashes on-chain (public record)
- ✅ Anyone can verify independently

---

## Alternative: Deploy Your Own (If You Want)

If you want complete independence:

```bash
# 1. Clone Integrity repo
git clone https://github.com/HerodotusDev/integrity.git

# 2. Deploy your own FactRegistry
cd integrity
scarb build
sncast deploy --class-hash <your_verifier_hash>

# 3. Update your contract to use your address
# In risk_engine.cairo:
const MY_FACT_REGISTRY: ContractAddress = 0x...your_address...
```

**But**: This is the same code, just deployed by you. No functional difference.

---

## Bottom Line

**Do you have to use Herodotus?** 

**No** - but Herodotus Integrity is:
- ✅ The easiest path (already integrated)
- ✅ Public infrastructure (like Uniswap contract)
- ✅ Trustless (contract code is open source)
- ✅ Standard practice (what everyone uses)

**You're not "using Herodotus"** - you're using a **public contract** they deployed. It's infrastructure, not a service dependency.

---

## If You Want Independence

**Option**: Deploy the same Integrity contract yourself
- Same code (open source)
- Same functionality
- Your own deployment
- More setup work

**Verdict**: Not worth it unless you have specific requirements (e.g., custom verification logic, private deployment, etc.)
