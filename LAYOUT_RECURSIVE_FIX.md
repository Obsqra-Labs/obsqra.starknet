# Layout Fix - Using Recursive Layout

**Date**: 2026-01-26  
**Status**: Updated to use recursive layout (canonical Integrity setting)

## Issue

From `docs/proving_flows.md`:
- **Canonical Integrity settings**: `recursive/keccak_160_lsb/stone5/strict`
- **Known issue**: Even with correct layout, `Invalid final_pc` can occur due to AIR mismatch

## Fix Applied

1. ✅ **Config updated**: `INTEGRITY_LAYOUT = "recursive"`
2. ✅ **Cairo execution updated**: Uses `settings.INTEGRITY_LAYOUT` instead of hardcoded "small"
3. ✅ **Calldata updated**: Already using config layout

## Current Configuration

```python
INTEGRITY_LAYOUT: str = "recursive"  # Canonical Integrity layout
INTEGRITY_HASHER: str = "keccak_160_lsb"
INTEGRITY_STONE_VERSION: str = "stone5"
INTEGRITY_MEMORY_VERIFICATION: str = "strict"
```

## Known Limitations

From `docs/proving_flows.md`:
> "To get a passing call, we need a proof generated with the exact Stone/Integrity settings (recursive/keccak_160_lsb/stone5/strict) for the target AIR. Options:
> - Regenerate proof with Integrity's canonical AIR/layout (potentially full trace or updated params).
> - Use Atlantic to produce an Integrity-compatible proof for the risk circuit."

**This means**: Even with correct layout, the proof might still fail if the Cairo program doesn't match Integrity's AIR expectations exactly.

## Next Steps

1. **Test with recursive layout** - See if it helps
2. **If still fails**: Consider using Atlantic for proof generation
3. **Alternative**: Regenerate proof with Integrity's canonical AIR/layout

---

**Status**: Layout updated to recursive ✅ | Testing needed 🔄
