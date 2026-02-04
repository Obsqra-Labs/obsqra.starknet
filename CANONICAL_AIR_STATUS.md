# Canonical AIR Regeneration Status

**Date**: 2026-01-26  
**Status**: NOT currently attempting canonical AIR regeneration

## Current Configuration (Non-Canonical)

```python
# backend/app/config.py
INTEGRITY_LAYOUT: str = "small"           # ❌ NOT canonical (should be "recursive")
INTEGRITY_HASHER: str = "keccak_160_lsb"  # ✅ Correct
INTEGRITY_STONE_VERSION: str = "stone6"   # ❌ NOT canonical (should be "stone5")
INTEGRITY_MEMORY_VERIFICATION: str = "strict"  # ✅ Correct
```

## Canonical Integrity Settings (From docs/proving_flows.md)

According to `docs/proving_flows.md`, the canonical Integrity settings are:
- **Layout**: `recursive` (not `small`)
- **Hasher**: `keccak_160_lsb` ✅
- **Stone Version**: `stone5` (not `stone6`)
- **Memory Verification**: `strict` ✅

## Why We're NOT Using Canonical Settings

1. **Performance**: Recursive layout proof generation times out (>120s)
2. **Reliability**: Small layout is more reliable for local proof generation
3. **Stone Version**: Upgraded to `stone6` (may not be compatible with Integrity's verifier)

## What Canonical AIR Regeneration Would Require

### 1. Update Configuration
```python
INTEGRITY_LAYOUT: str = "recursive"        # Change from "small"
INTEGRITY_STONE_VERSION: str = "stone5"   # Change from "stone6"
```

### 2. Increase Timeout
- Current timeout: 120 seconds
- Recursive layout may need: 300+ seconds (or no timeout)

### 3. Potentially Use Full Trace
- Current: Small trace (8,192 steps)
- Canonical: May require full trace (131,072 steps)
- **Note**: Previous attempts with full trace resulted in `Signal(6)` errors

### 4. Update Cairo Execution
- Already uses `settings.INTEGRITY_LAYOUT` ✅
- Already uses `settings.INTEGRITY_STONE_VERSION` ✅
- Need to ensure Stone prover uses correct version

## Previous Attempts (From docs/proving_flows.md)

### Full-Trace Stone Proof (n_steps=131,072)
- **Result**: Aborted with `Signal(6)` (no stdout from sandbox)
- **Possible causes**: Resource limits or AIR/config mismatch
- **Status**: Not viable with current setup

### Recursive Layout with Small Trace
- **Result**: Times out (>120s)
- **Status**: Not viable with current timeout

## Options for Canonical AIR Regeneration

### Option 1: Recursive Layout + Increased Timeout
```python
INTEGRITY_LAYOUT: str = "recursive"
INTEGRITY_STONE_VERSION: str = "stone5"
# Increase timeout in _stone_integrity_fact_for_metrics
timeout=300  # or remove timeout
```

**Pros**: Matches canonical settings exactly  
**Cons**: May still timeout, may still get `Invalid final_pc`

### Option 2: Use Integrity's Example Script
- Integrity has example scripts for generating canonical proofs
- Check `integrity/examples/proofs/generate.py`
- Use their exact parameters and workflow

**Pros**: Guaranteed to match Integrity's expectations  
**Cons**: May need to adapt to our risk_example.cairo program

### Option 3: Atlantic Integration
- Use Atlantic to generate Integrity-compatible proofs
- Atlantic handles canonical AIR automatically

**Pros**: Guaranteed compatibility  
**Cons**: Requires Atlantic API credits

## Recommendation

**Current Approach** (Small Layout):
- ✅ Fast proof generation (~2-3 seconds)
- ✅ Reliable (no timeouts)
- ❌ May not verify on Integrity FactRegistry (`Invalid final_pc`)

**Canonical Approach** (Recursive Layout):
- ✅ Matches Integrity's canonical settings
- ❌ Slow proof generation (may timeout)
- ❌ May still get `Invalid final_pc` (AIR mismatch)

**Best Path Forward**:
1. **Short-term**: Continue with `small` layout for local verification
2. **Medium-term**: Try recursive layout with increased timeout (300s+)
3. **Long-term**: Use Atlantic for production Integrity verification

---

**Status**: NOT attempting canonical AIR regeneration currently. Using `small` layout for performance/reliability.
