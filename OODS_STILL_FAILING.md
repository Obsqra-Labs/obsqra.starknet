# OODS Still Failing - After Layout Fix

**Date**: 2026-01-27  
**Status**: Layout fixed, nonce fixed, but OODS still failing

---

## ✅ What's Fixed

### 1. Layout Mismatch ✅
- Proof layout: `recursive` (was: `small`)
- Segments: `bitwise, execution, output, pedersen, program, range_check`
- No ecdsa segment
- Matches Integrity's recursive verifier expectations

### 2. Nonce Management ✅
- Nonce retry logic working
- Logs show: `pending_nonce=None, latest_nonce=701-706, used_nonce=701-706`
- Nonce errors resolved

---

## ❌ What's Still Failing

### OODS Error: Invalid OODS

**Error**: `Invalid OODS - The proof's OODS values do not match the verifier's expectations. This may indicate an AIR/public input mismatch.`

**Context**:
- Layout: `recursive` ✅
- Builtins: `bitwise` (no ecdsa) ✅
- `n_verifier_friendly_commitment_layers`: `9999` ✅
- **But OODS still fails**

**This confirms**: Layout fixed ≠ Verification guaranteed

---

## 🔍 What OODS Error Means

**OODS = Out-of-Domain Sampling**

The error indicates:
- Proof structure is correct (layout, builtins)
- But the OODS values in the proof don't match what Integrity's verifier expects
- This suggests AIR configuration or public input hash mismatch

**Possible Causes**:
1. **AIR parameters mismatch** - FRI steps, degree bounds, etc.
2. **Public input hash mismatch** - Despite n_verifier_friendly_commitment_layers fix
3. **Channel hash/seed mismatch** - Different Fiat-Shamir channel state
4. **Serialization mismatch** - Proof serializer format differences

---

## 📊 Current Proof State

**Latest Proof**:
- Layout: `recursive` ✅
- `n_verifier_friendly_commitment_layers`: `9999` ✅
- Segments: `bitwise, execution, output, pedersen, program, range_check` ✅
- No ecdsa ✅

**But OODS still fails** ❌

---

## 🎯 Next Investigation Steps

### 1. Compare with Integrity's Canonical Example

- [ ] Compare proof structure with Integrity's recursive example
- [ ] Check AIR parameters (FRI steps, degree bounds)
- [ ] Verify public input hash calculation
- [ ] Check channel hash/seed generation

### 2. Check Serialization

- [ ] Verify proof serializer output format
- [ ] Compare with Integrity's expected format
- [ ] Check calldata structure

### 3. Verify AIR Configuration

- [ ] Compare Stone's AIR with Integrity's canonical AIR
- [ ] Check if AIR parameters match exactly
- [ ] Verify FRI configuration

---

## 🎓 Key Insight

**As you said**: "Layout fixed ≠ Verification guaranteed"

**What we've proven**:
- ✅ Layout mismatch was causing Invalid builtin
- ✅ Nonce management was causing transaction failures
- ❌ But OODS can still fail for AIR/params/serialization reasons

**The OODS error is the real proof verification challenge now.**

---

**Status**: Layout and nonce fixed. OODS verification still failing - need to investigate AIR/public input consistency.
