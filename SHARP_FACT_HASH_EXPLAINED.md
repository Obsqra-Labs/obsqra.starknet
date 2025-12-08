# SHARP Fact Hash Verification Explained

## What We Have Now

### Current Flow (Local Verification)
```
1. AI generates allocation decision
2. LuminAIR generates STARK proof (<1s)
3. Local verification (<1s) ✅
4. Execute transaction on Starknet
5. Submit proof to SHARP (background)
6. SHARP verifies and publishes fact hash to L1 (10-60 min)
```

**What's Missing:**
- ❌ No on-chain verification of fact hash
- ❌ Users must trust backend for verification
- ❌ No public way to verify proofs independently

---

## What is SHARP Fact Hash Verification?

### SHARP (Shared Prover) Overview

**SHARP** = StarkWare's Shared Prover service that:
1. Batches multiple proofs together
2. Generates a single aggregated proof
3. Publishes a "fact hash" to Ethereum L1
4. Anyone can verify the fact hash on L1

### Fact Hash Explained

**Fact Hash** = Cryptographic commitment to a verified computation

```
Proof → SHARP → Aggregated Proof → Fact Hash → Ethereum L1
```

**What it proves:**
- ✅ The computation was executed correctly
- ✅ The proof is valid
- ✅ The result is cryptographically guaranteed

**How it works:**
1. SHARP receives our proof
2. SHARP batches it with other proofs
3. SHARP generates aggregated proof
4. SHARP publishes fact hash to L1
5. Fact hash is stored on Ethereum (permanent record)

---

## What We Have vs What's Missing

### ✅ What We Have (Current)

**Local Verification:**
- Proof generated locally (<1s)
- Proof verified locally (<1s)
- Immediate execution
- Fast user experience

**SHARP Submission:**
- Proofs submitted to SHARP
- Fact hashes generated
- Stored in database
- Background process

### ❌ What's Missing

**On-Chain Fact Hash Verification:**
- No Cairo contract to verify fact hash
- No public verification endpoint
- Users can't independently verify
- Must trust backend

---

## How Fact Hash Verification Works

### Step-by-Step

1. **Proof Generation** (We do this)
   ```
   AI Decision → LuminAIR → STARK Proof
   ```

2. **SHARP Submission** (We do this)
   ```
   STARK Proof → SHARP Gateway → Job ID
   ```

3. **SHARP Verification** (SHARP does this)
   ```
   Job ID → SHARP Prover → Fact Hash
   ```

4. **L1 Publication** (SHARP does this)
   ```
   Fact Hash → Ethereum L1 → Permanent Record
   ```

5. **On-Chain Verification** (We need this)
   ```
   Fact Hash → Cairo Verifier Contract → Verified ✅
   ```

### The Missing Piece

**Cairo Verifier Contract:**
```cairo
#[starknet::contract]
mod FactHashVerifier {
    fn verify_fact_hash(fact_hash: felt252) -> bool {
        // Check if fact hash exists on L1
        // Returns true if SHARP verified the proof
    }
}
```

**What it does:**
- Checks if fact hash was published to L1
- Verifies the fact hash is valid
- Returns true/false
- Public, trustless verification

---

## Comparison: Local vs Fact Hash Verification

| Aspect | Local Verification | Fact Hash Verification |
|--------|-------------------|------------------------|
| **Speed** | <1 second | 10-60 minutes |
| **Trust** | Requires backend | Trustless (L1) |
| **Public** | No | Yes |
| **Permanent** | No | Yes (on L1) |
| **Cost** | Free | SHARP fees |
| **Use Case** | Instant execution | Final settlement |

---

## What's on ETH Version (obsqura.fi)

**ETH Version (obsqura.fi):**
- Uses Ethereum mainnet
- Different proving infrastructure
- May use different verification method
- Privacy pool focus (MIST integration)

**Starknet Version (starknet.obsqura.fi):**
- Uses Starknet L2
- LuminAIR + SHARP
- Faster, cheaper
- Yield optimizer focus

**Key Difference:**
- ETH: L1 verification (slower, more expensive)
- Starknet: L2 + SHARP (faster, cheaper, then L1 settlement)

---

## Implementation Plan

### Phase 1: Fact Hash Tracking (Done ✅)
- ✅ Submit proofs to SHARP
- ✅ Store fact hashes in database
- ✅ Monitor SHARP status

### Phase 2: Fact Hash Verification (Next)
- ⏳ Create Cairo verifier contract
- ⏳ Check fact hash on L1
- ⏳ Display verification status in UI

### Phase 3: On-Chain Integration (Future)
- ⏳ Require fact hash verification before execution
- ⏳ Store fact hash in contract
- ⏳ Public verification endpoint

---

## Why We Need Both

### Local Verification (Current)
- **Purpose:** Instant execution
- **Speed:** <1 second
- **Trust:** Backend (acceptable for MVP)
- **Use:** Immediate user feedback

### Fact Hash Verification (Missing)
- **Purpose:** Final settlement
- **Speed:** 10-60 minutes
- **Trust:** L1 (trustless)
- **Use:** Permanent record, audit trail

### Hybrid Approach (Best)
- Execute immediately (local verification)
- Verify on L1 later (fact hash)
- Best of both worlds

---

## Summary

**What SHARP Fact Hash Verification Is:**
- Public, trustless verification on Ethereum L1
- Permanent record of proof validity
- Anyone can verify independently

**What We Have:**
- Local verification (fast, but requires trust)
- SHARP submission (background process)
- Fact hash storage (database)

**What We Need:**
- On-chain fact hash verification contract
- Public verification endpoint
- UI display of verification status

**Difference from ETH Version:**
- ETH: Direct L1 verification
- Starknet: L2 execution + L1 settlement via SHARP

