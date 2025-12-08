# On-Chain Verification Options Explained

## Current State

**What We Have:**
- ✅ Local verification (LuminAIR `verify()` function)
- ✅ Proofs generated and verified in <1 second
- ✅ Proofs stored in database
- ✅ SHARP submission (for L1 settlement)

**What's Missing:**
- ❌ On-chain verification (trustless, public)
- ❌ Users must trust backend for verification
- ❌ No public way to verify proofs independently

## Option 2: On-Chain Verifier - Explained

### What is On-Chain Verification?

**Current Flow (Trust Required):**
```
User → Backend → Generate Proof → Verify Locally → Execute
                    ↓
              (User trusts backend)
```

**With On-Chain Verifier (Trustless):**
```
User → Backend → Generate Proof → Submit to Verifier Contract
                    ↓
              Verifier Contract → Verify On-Chain → Execute if Valid
                    ↓
              (No trust required - public verification)
```

### Why Do We Need It?

**Problem:** Users must trust the backend to verify proofs correctly.

**Solution:** Deploy a verifier contract on Starknet that anyone can call to verify proofs publicly.

**Benefits:**
- ✅ Trustless: No need to trust backend
- ✅ Public: Anyone can verify proofs
- ✅ Transparent: Verification happens on-chain
- ✅ Auditable: All verifications are public

## Verifier Options

### Option A: Custom LuminAIR Verifier (Recommended)

**What It Is:**
- Deploy a Cairo contract that verifies LuminAIR proofs
- Uses LuminAIR's verification logic in Cairo
- Directly verifies the proofs we generate

**Pros:**
- ✅ Works with our current LuminAIR setup
- ✅ No external dependencies
- ✅ Full control over verification logic
- ✅ Matches our proof format exactly

**Cons:**
- ❌ Need to implement Cairo verifier
- ❌ More complex than using existing service
- ❌ Requires Cairo expertise

**Implementation:**
```cairo
#[starknet::contract]
mod ProofVerifier {
    fn verify_proof(proof: Proof, settings: Settings) -> bool {
        // LuminAIR verification logic in Cairo
        // Returns true if proof is valid
    }
}
```

**Timeline:** 3-4 weeks (need to port LuminAIR verification to Cairo)

---

### Option B: Giza Protocol Verifier

**What It Is:**
- Use Giza's existing verifier infrastructure
- Submit proofs to Giza's verification service
- Giza handles on-chain verification

**Pros:**
- ✅ No need to build custom verifier
- ✅ Giza handles complexity
- ✅ Potentially faster to implement

**Cons:**
- ❌ External dependency on Giza
- ❌ May not support LuminAIR proofs directly
- ❌ Need Giza API key (we tried, couldn't get one)
- ❌ Less control over verification process
- ❌ May require different proof format

**Current Status:**
- We tried to get Giza API key but couldn't
- Giza's verifier may not support LuminAIR proofs
- Would need to check compatibility

**Timeline:** Unknown (depends on Giza support + API access)

---

### Option C: SHARP Verifier (StarkWare)

**What It Is:**
- Use StarkWare's SHARP (Shared Prover) verifier
- SHARP verifies proofs and publishes fact hashes to L1
- Contracts can verify fact hashes on-chain

**Pros:**
- ✅ Already integrated (we submit to SHARP)
- ✅ StarkWare's official solution
- ✅ Fact hashes can be verified on-chain
- ✅ Battle-tested infrastructure

**Cons:**
- ❌ 10-60 minute verification time
- ❌ Not suitable for instant verification
- ❌ Fact hash verification is indirect
- ❌ Requires L1 settlement

**Current Status:**
- We already submit proofs to SHARP
- Fact hashes are generated
- Can verify fact hashes on-chain (but slow)

**Timeline:** Already partially implemented (just need fact hash verification)

---

### Option D: Hybrid Approach (Best of Both Worlds)

**What It Is:**
- Use local verification for instant feedback (<1s)
- Use SHARP for L1 settlement (10-60 min)
- Optional: Add custom verifier for on-chain verification

**Flow:**
```
1. Generate proof → Verify locally (<1s) → Execute immediately
2. Submit to SHARP → Get fact hash (10-60 min) → Verify on L1
3. (Optional) Custom verifier for on-chain verification
```

**Pros:**
- ✅ Instant execution (local verification)
- ✅ L1 settlement (SHARP)
- ✅ Optional on-chain verification
- ✅ Best user experience

**Cons:**
- ❌ More complex architecture
- ❌ Multiple verification paths

**Timeline:** Already mostly implemented (just need fact hash verification)

---

## Recommendation

### For Immediate Needs: **Option D (Hybrid)**

**Why:**
- We already have local verification (instant)
- We already submit to SHARP (L1 settlement)
- Users get immediate feedback
- L1 settlement provides finality

**What's Missing:**
- Fact hash verification on-chain (easy to add)
- Optional: Custom verifier for on-chain verification (later)

### For Full Trustlessness: **Option A (Custom Verifier)**

**Why:**
- Complete control
- Works with our LuminAIR setup
- No external dependencies
- Public, trustless verification

**When:**
- After we have more time/resources
- When we need instant on-chain verification
- When we want full independence

### For Quick Solution: **Option C (SHARP Fact Hash Verification)**

**Why:**
- Already integrated
- Just need to verify fact hashes on-chain
- Provides L1 settlement proof
- Relatively easy to add

**Implementation:**
```cairo
#[starknet::contract]
mod FactHashVerifier {
    fn verify_fact_hash(fact_hash: felt252) -> bool {
        // Check if fact hash exists on L1
        // Returns true if SHARP verified the proof
    }
}
```

---

## Comparison Table

| Option | Speed | Trustless | Complexity | Status |
|--------|-------|-----------|------------|--------|
| **Local Verification** | <1s | ❌ | Low | ✅ Done |
| **SHARP Fact Hash** | 10-60 min | ✅ | Medium | 🟡 Partial |
| **Custom Verifier** | <1s | ✅ | High | ❌ Not Started |
| **Giza Verifier** | Unknown | ✅ | Medium | ❌ No API Key |
| **Hybrid** | <1s + 10-60 min | ✅ | Medium | 🟡 Mostly Done |

---

## Answer to Your Question

**"Do we need a verifier or can we use Giza or something later?"**

**Short Answer:** We don't *need* a custom verifier right now. We can use SHARP fact hash verification for trustless verification, or add a custom verifier later for instant on-chain verification.

**Long Answer:**

1. **For MVP/Current Needs:**
   - ✅ Local verification (instant feedback) - DONE
   - ✅ SHARP submission (L1 settlement) - DONE
   - 🟡 Fact hash verification (easy to add) - NOT DONE
   - This gives us trustless verification via SHARP (just slower)

2. **For Full Trustlessness:**
   - Custom verifier (instant on-chain verification)
   - Or Giza if they support LuminAIR (unlikely without API key)
   - This gives us instant trustless verification

3. **Recommendation:**
   - **Now:** Add SHARP fact hash verification (easy, 1-2 days)
   - **Later:** Build custom verifier if needed (3-4 weeks)
   - **Skip:** Giza (no API key, compatibility unknown)

---

## Next Steps

1. **Phase 2 (Now):** Verify allocation matches recommendation
2. **SHARP Fact Hash (Soon):** Add fact hash verification on-chain
3. **Custom Verifier (Later):** If we need instant on-chain verification

