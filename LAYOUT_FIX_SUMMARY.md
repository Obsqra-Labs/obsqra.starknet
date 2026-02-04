# Layout Configuration Fix

**Date**: 2026-01-26  
**Status**: Fixed layout mismatch

## Issue Identified

**Mismatch between Cairo execution and Integrity contract configuration:**

1. **Cairo execution**: Uses `--layout small` (hardcoded in `risk_engine.py:195`)
2. **Config**: Was set to `INTEGRITY_LAYOUT = "recursive"`
3. **Calldata**: Was using config value ("recursive")

**Result**: Proof generated with "small" layout but contract told it's "recursive" → VERIFIER_NOT_FOUND

## Fix Applied

1. ✅ **Updated config**: `INTEGRITY_LAYOUT = "small"` (to match Cairo execution)
2. ✅ **Updated calldata**: Now uses `settings.INTEGRITY_LAYOUT` instead of hardcoded "small"
3. ✅ **Cairo execution**: Already uses `settings.INTEGRITY_LAYOUT` (after previous fix)

## Current Configuration

```python
INTEGRITY_LAYOUT: str = "small"  # Must match Cairo execution layout
INTEGRITY_HASHER: str = "keccak_160_lsb"
INTEGRITY_STONE_VERSION: str = "stone5"
INTEGRITY_MEMORY_VERIFICATION: str = "strict"
```

## Next Steps

1. **Verify verifier is registered**: Check if FactRegistry has verifier for `small/keccak_160_lsb`
2. **Test again**: Run E2E test to see if it works now
3. **If still fails**: May need to register verifier or use different layout

---

**Status**: Layout mismatch fixed ✅ | Testing in progress ⚠️
