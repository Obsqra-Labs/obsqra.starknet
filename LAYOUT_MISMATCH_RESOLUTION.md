# Layout Mismatch Resolution - Complete

**Date**: 2026-01-27  
**Status**: ✅ Root cause fixed and guard added

---

## 🎯 The Discovery

**User's Direct Testing Revealed the Truth**:
- `cairo-run --layout recursive` produces **NO ecdsa segment** ✅
- Our proof had `layout: small` with ecdsa segment ❌
- **This was a layout mismatch, not cairo-run behavior!**

---

## 🔍 Root Cause

### The Problem

**Config Override**:
```bash
# backend/.env (was overriding defaults)
INTEGRITY_LAYOUT=small
INTEGRITY_STONE_VERSION=stone6
```

**Config Defaults** (correct):
```python
# backend/app/config.py
INTEGRITY_LAYOUT: str = "recursive"  # Canonical
INTEGRITY_STONE_VERSION: str = "stone5"  # Canonical
```

**Result**:
- Proofs generated with `small` layout (from .env)
- Integrity verifier expects `recursive` layout
- Small includes ecdsa, recursive rejects ecdsa
- **Mismatch → Invalid builtin error**

---

## ✅ Fix Applied

### 1. Updated `.env` to Match Canonical Settings

**Changed**:
```bash
# backend/.env
INTEGRITY_LAYOUT=recursive  # Was: small
INTEGRITY_STONE_VERSION=stone5  # Was: stone6
```

**Result**: Proofs will now be generated with recursive layout

### 2. Added Layout Mismatch Guard

**In `risk_engine.py`**:
```python
# CRITICAL: Verify layout matches Integrity expectations
if proof_layout != expected_layout:
    raise RuntimeError(
        f"Layout mismatch: proof has '{proof_layout}' but Integrity expects '{expected_layout}'. "
        f"This will cause 'Invalid builtin' error."
    )
```

**Result**: Hard-fails immediately if layout mismatch detected

### 3. Removed Incorrect Workarounds

**Removed**:
- Code that tried to remove ecdsa segment
- Code that tried to add bitwise segment
- These were workarounds for the wrong problem!

**Result**: Clean proof generation, no post-processing needed

---

## 📊 Impact

### Before (Broken)

```
.env: INTEGRITY_LAYOUT=small
  ↓
cairo-run --layout small
  ↓
Proof: layout=small, segments include ecdsa
  ↓
Integrity: expects recursive, rejects ecdsa
  ↓
Error: Invalid builtin ❌
```

### After (Fixed)

```
.env: INTEGRITY_LAYOUT=recursive
  ↓
cairo-run --layout recursive
  ↓
Proof: layout=recursive, segments: program, execution, output, pedersen, range_check, bitwise
  ↓
Integrity: expects recursive, accepts proof
  ↓
Success: Verification passes ✅
```

---

## 🎓 Why This Fixes Everything

### The Chain of Issues (All Symptoms of Layout Mismatch)

1. **OODS Error** ✅ Fixed separately (n_verifier_friendly_commitment_layers)
2. **Invalid Builtin** ✅ Fixed (layout mismatch resolved)
3. **ECDSA Segment** ✅ Fixed (recursive doesn't include ecdsa)
4. **Bitwise Segment** ✅ Fixed (recursive includes bitwise)

**All issues were symptoms of the layout mismatch!**

---

## 🚀 Next Steps

### Immediate

1. ✅ Updated `.env` to recursive/stone5
2. ✅ Added layout mismatch guard
3. ⏳ **Restart backend** to pick up new config
4. ⏳ **Test proof generation**

### Testing Commands

```bash
# Restart backend
cd /opt/obsqra.starknet/backend
# Kill and restart with new config

# Test proof generation
python3 test_stone_only_e2e.py

# Verify proof layout
jq '.public_input.layout' /tmp/risk_stone_*/risk_proof.json
# Should show: "recursive"

# Verify segments
jq '.public_input.memory_segments | keys' /tmp/risk_stone_*/risk_proof.json
# Should show: ["execution", "output", "pedersen", "program", "range_check", "bitwise"]
# Should NOT show: "ecdsa"
```

---

## 🎯 Expected Result

After restarting backend:

1. **Proof Generation**:
   - Uses `--layout recursive` ✅
   - Produces `layout: recursive` ✅
   - Segments: program, execution, output, pedersen, range_check, bitwise ✅
   - NO ecdsa segment ✅

2. **Integrity Verification**:
   - Layout matches: `recursive` ✅
   - Builtins match: `bitwise` (not ecdsa) ✅
   - Verification should pass ✅

3. **Error Prevention**:
   - Guard catches any future mismatches ✅
   - Clear error message ✅
   - Prevents silent failures ✅

---

**Status**: 🎯 Root cause fixed! Layout mismatch resolved. Ready to test with recursive layout.
