# Action Items: Get Real Proofs Working

## Immediate Blockers

### 1. **Atlantic Credits (Your Dec 14 Blocker)**
**Status:** BLOCKED - Requires external action
**Action:**
```bash
# Contact Herodotus
# Email: team@herodotus.cloud
# Or: https://herodotus.cloud/contact

# Sepolia typically has free tier, but you hit limits
# Request: Free Sepolia credits for proof generation testing
# Timeline: 1-2 days for response
```

**What You'll Get:**
- `ATLANTIC_API_KEY` for environment
- Ability to generate real Stone proofs
- Proofs automatically Integrity-compatible

**Cost:** Free on Sepolia (mainnet requires payment)

---

### 2. **RPC Block ID Issue (We Just Fixed)**
**Status:** FIXED - Integrity service improvements
**Action:** Already done
```python
# What we fixed:
# - Added Contract import
# - Better error messages
# - Graceful fallback handling
# - Shows exact point of failure

# Result: Clear visibility when proofs fail
# System doesn't crash, logs exactly why
```

**Remaining issue:** RPC itself has block_id incompatibility (not our code)
**Impact:** Verification still fails, but now we know why

---

## Implementation Path (When Credits Available)

### Step 1: Enable Atlantic in Backend
**File:** `backend/.env`
```bash
ATLANTIC_API_KEY=<from Herodotus>
ATLANTIC_BASE_URL=https://atlantic.api.herodotus.cloud
ALLOW_UNVERIFIED_EXECUTION=False  # Require verified proofs
```

**What changes:**
- `ProofJob` table already has `l1_verified_at` field
- Atlantic poller already running (started in Dec 13)
- Just need the API key

---

### Step 2: Deploy Risk Engine to Sepolia
**File:** `contracts/Scarb.toml`
```bash
# Compile risk_engine.cairo
scarb build

# Deploy to Sepolia
sncast declare --contract-name RiskEngine --network sepolia
sncast deploy --class-hash <returned-class-hash> ... --network sepolia
```

**What's needed:**
- Constructor args for Sepolia addresses
- Owner wallet (already set up)
- Gas for deployment (you have STRK)

---

### Step 3: Submit to Atlantic
**File:** `backend/app/workers/atlantic_worker.py` (already exists)
```python
# When ATLANTIC_API_KEY is set:
# 1. Compile risk_engine.cairo to JSON
# 2. POST to Atlantic API
# 3. Poll for completion
# 4. Download Stone proof
# 5. Parse to Integrity format
# 6. Call verify_proof_full_and_register_fact
```

**Current status:** Stubbed but not fully wired

**What to do:**
```bash
# In your worker service:
# 1. Uncomment Atlantic submission code (currently raises NotImplementedError)
# 2. Wire it to background task scheduler
# 3. Monitor proof generation in UI
```

---

### Step 4: Verify on Integrity
**File:** Backend `integrity_service.py` (just fixed)
```python
# When Atlantic proof arrives:
# 1. Deserialize to VerifierConfiguration
# 2. Deserialize to StarkProofWithSerde
# 3. Call verify_proof_full_and_register_fact
# 4. Store l2_verified_at timestamp
# 5. Update ProofJob status to VERIFIED
```

**Current status:** Ready to go
**Testing:** Can test manually with real proof data

---

## Testing Checklist

- [ ] Get Atlantic API key
- [ ] Set ATLANTIC_API_KEY in backend .env
- [ ] Deploy RiskEngine contract to Sepolia
- [ ] Test single proof generation + Atlantic submission
- [ ] Verify proof deserializes correctly
- [ ] Call Integrity verifier contract
- [ ] See `l2_verified_at` timestamp in ProofJob
- [ ] Set `ALLOW_UNVERIFIED_EXECUTION=False`
- [ ] Verify execution is now blocked without verified proof
- [ ] Set `ALLOW_UNVERIFIED_EXECUTION=True` again for demo mode

---

## What NOT to Do

### ❌ Don't Try Local Stone Pipeline
**Why:** 
- Requires `cairo1-run` installation
- Complex trace serialization
- No error messages if format wrong
- You already tried in Dec 14, documented it as not viable

### ❌ Don't Use LuminAIR for Real Proofs
**Why:**
- Proofs don't verify on Integrity
- RPC compatibility issues
- Format mismatch with verifier
- Keep for demo mode only

### ❌ Don't Build Custom Verifier in Cairo
**Why:**
- Porting LuminAIR verifier is 3-4 weeks
- Atlantic already handles this
- Unnecessary complexity

---

## Timeline

**Week 1:** Get Atlantic credits
```bash
Contact Herodotus (1 day response time)
Receive API key
```

**Week 2:** Wire Atlantic integration
```bash
Deploy RiskEngine contract (1 day)
Test proof generation flow (2 days)
Manual verification with Integrity (1 day)
```

**Week 3:** Full testing
```bash
End-to-end with real proofs (1 day)
Production hardening (3 days)
Documentation (1 day)
```

---

## Success Criteria

✅ `ALLOW_UNVERIFIED_EXECUTION=False` works
✅ Real proof generated for allocation decision
✅ Proof verified on Integrity contract
✅ `l2_verified_at` populated in database
✅ Frontend shows "Verified ✓" badge
✅ Can see execution gated by proof verification

---

## Questions to Ask Herodotus

When you contact them:
1. "Can we get free Sepolia credits for testing?"
2. "What's the proof generation latency (SLA)?"
3. "Can proofs be verified on Sepolia Integrity verifier?"
4. "What's the format of output proofs (VerifierConfiguration + StarkProofWithSerde)?"
5. "Is there sample code for proof deserialization?"

---

## Files That Already Support This

✅ `backend/app/workers/atlantic_worker.py` - Polling infrastructure
✅ `backend/app/services/integrity_service.py` - Verification (just fixed)
✅ `backend/app/models.py` - ProofJob has all needed fields
✅ `backend/app/api/routes/risk_engine.py` - Orchestration flow
✅ `integrity/` - Verifier contract deployed on Sepolia

**What's missing:** Atlantic API integration (low effort, just wire the call)

---

## You Were Right in December

Your assessment:
> "Only one can prove onchain idk about starknet review"

**Exactly right.** Atlantic is the only viable path. The blocker is credits, not architecture.

System is architecturally sound. Just needs:
1. Credits to generate proofs
2. Wire the API call (1 hour of work)
3. Test end-to-end

That's it. The heavy lifting is done.

