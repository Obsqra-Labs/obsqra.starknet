# n_verifier_friendly_commitment_layers Value Mismatch

**Date**: 2026-01-27  
**Status**: Potential root cause identified

---

## Correction (2026-01-27)

**This only affects Stone6.**  
In `integrity/src/air/public_input.cairo`, `n_verifier_friendly_commitment_layers` is added to the
public input hash **only when `settings.stone_version == StoneVersion::Stone6`**.  
For **Stone5**, this value is **not** included in the public input hash, so a 1000 vs 9999
difference does **not** change the channel seed or OODS point under Stone5 verification.

**Implication**:
- ✅ Relevant if verifying as Stone6 (or if proof was generated with Stone6 semantics).
- ❌ **Not** the root cause of current OODS failures when verifying as Stone5.
- ✅ Still worth aligning for reproducibility, but not the blocker for Stone5 OODS.

---

## Critical Finding ✅

### From Integrity Source Code
`integrity/src/air/public_input.cairo` line 81:
```cairo
hash_data.append(n_verifier_friendly_commitment_layers);
```

**This means:**
- This value is included in the public input hash **only for Stone6**.
- Different values → Different hash → Different channel seed → OODS mismatch **(Stone6 only)**.

---

## The Mismatch

### Values
- **Example (canonical)**: `9999`
- **Actual (our proof)**: `1000`
- **Our base params file**: `1000`

### Impact
1. **Different public input hash**
   - Example hash includes `9999`
   - Our hash includes `1000`
   - Different hash values

2. **Different channel seed**
   - Public input hash affects Fiat-Shamir channel seed
   - Different seed → Different random values

3. **Different OODS point**
   - OODS point is drawn from channel
   - Different channel seed → Different OODS point

4. **Different composition polynomial reconstruction**
   - Verifier reconstructs at different OODS point
   - Different point → Different reconstruction
   - → **OODS mismatch!**

---

## Root Cause

**Our base params file has `n_verifier_friendly_commitment_layers = 1000`**
**But Integrity's canonical recursive example uses `9999`**

This value difference causes:
- Different public input hash
- Different channel seed
- Different OODS point
- OODS mismatch

---

## Fix

### Option 1: Update Base Params File
Change `integrity/examples/proofs/cpu_air_params.json`:
- `n_verifier_friendly_commitment_layers: 1000` → `9999`

### Option 2: Use Correct Params File
Use the params file that matches Integrity's canonical example.

---

## Next Steps

1. **Check where 1000 comes from** → Our base params file
2. **Update to 9999** → Match canonical example
3. **Regenerate proof** → With correct value
4. **Test verification** → Should pass OODS

---

**Status**: ⚠️ Correction applied — this mismatch only affects **Stone6**. It is **not** the root cause for current **Stone5** OODS failures.
