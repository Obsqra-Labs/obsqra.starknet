# Canonical AIR Regeneration Test Plan

**Date**: 2026-01-26  
**Status**: Step 1 in progress (Hybrid: Recursive + Increased Timeout)

## Test Plan (3 Steps)

### Step 1: Hybrid Approach ✅ IN PROGRESS
**Goal**: Test recursive layout with increased timeout

**Changes Applied**:
- ✅ Config: `INTEGRITY_LAYOUT = "recursive"`
- ✅ Config: `INTEGRITY_CAIRO_TIMEOUT = 300` (5 minutes, was 120s)
- ✅ Code: Updated `cairo1-run` and `cairo-run` to use configurable timeout
- ⏳ Still using `stone6` (will switch to `stone5` in Step 2)

**Expected Behavior**:
- Proof generation may take longer (up to 5 minutes)
- Should complete without timeout
- May still get `Invalid final_pc` (AIR mismatch)

**Test Command**:
```bash
# Test via API
curl -X POST http://localhost:8000/api/v1/proofs/generate \
  -H "Content-Type: application/json" \
  -d '{"jediswap_metrics": {...}, "ekubo_metrics": {...}}'
```

**Success Criteria**:
- ✅ Proof generation completes (no timeout)
- ✅ Proof serializes correctly
- ⚠️ Integrity verification may still fail (`Invalid final_pc`)

---

### Step 2: Full Canonical Settings
**Goal**: Switch to canonical settings (recursive + stone5)

**Changes**:
- `INTEGRITY_LAYOUT: str = "recursive"` (already set)
- `INTEGRITY_STONE_VERSION: str = "stone5"` (change from stone6)

**Expected Behavior**:
- Matches Integrity's canonical settings exactly
- May resolve `Invalid final_pc` error
- Proof generation may still be slow

**Test Command**: Same as Step 1

**Success Criteria**:
- ✅ Proof generation completes
- ✅ Integrity verification succeeds (no `Invalid final_pc`)
- ✅ Fact hash registered on-chain

---

### Step 3: Fallback to Small Layout
**Goal**: Keep small layout for performance (if canonical fails)

**Changes**:
- Revert to `INTEGRITY_LAYOUT: str = "small"`
- Keep timeout at 300s (or revert to 120s)
- Document canonical attempt results

**When to Use**:
- If Step 2 still fails with `Invalid final_pc`
- If proof generation is too slow for production
- For local verification (not Integrity FactRegistry)

**Success Criteria**:
- ✅ Fast proof generation (~2-3 seconds)
- ✅ Reliable (no timeouts)
- ⚠️ May not verify on Integrity (known limitation)

---

## Current Status

### Step 1: Hybrid Test ✅ COMPLETED
- ✅ Config updated to `recursive` layout
- ✅ Timeout increased to 300s
- ✅ Code updated to use configurable timeout
- ✅ Stone prover timeout also configurable

### Step 2: Canonical Settings ✅ COMPLETED
- ✅ Config updated to `stone5` (canonical)
- ✅ All settings match Integrity's canonical: `recursive/keccak_160_lsb/stone5/strict`
- ✅ Ready for testing

### Step 3: Fallback ✅ READY
- ✅ Backup configuration saved (`config.py.backup_small`)
- ✅ Fallback documentation created (`CANONICAL_AIR_FALLBACK.md`)
- ✅ Can revert to `small` layout if canonical fails

### Next Steps
1. **Test Step 2**: Run proof generation with canonical settings (recursive + stone5)
2. **If successful**: Canonical AIR regeneration works! ✅
3. **If fails**: Revert to Step 3 (small layout) for performance

---

## Configuration History

### Before (Small Layout)
```python
INTEGRITY_LAYOUT: str = "small"
INTEGRITY_STONE_VERSION: str = "stone6"
Timeout: 120s
```

### Step 1 (Hybrid)
```python
INTEGRITY_LAYOUT: str = "recursive"  # Changed
INTEGRITY_STONE_VERSION: str = "stone6"  # Keep for now
INTEGRITY_CAIRO_TIMEOUT: int = 300  # Increased
```

### Step 2 (Canonical)
```python
INTEGRITY_LAYOUT: str = "recursive"
INTEGRITY_STONE_VERSION: str = "stone5"  # Change
INTEGRITY_CAIRO_TIMEOUT: int = 300
```

### Step 3 (Fallback)
```python
INTEGRITY_LAYOUT: str = "small"  # Revert
INTEGRITY_STONE_VERSION: str = "stone6"  # Keep
INTEGRITY_CAIRO_TIMEOUT: int = 300  # Keep or revert
```

---

**Status**: Step 1 configured and ready for testing ✅
