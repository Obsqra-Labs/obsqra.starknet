# Canonical AIR Fallback Plan

**Date**: 2026-01-26  
**Status**: Step 3 - Fallback configuration ready

## Fallback Configuration (Small Layout)

If canonical AIR regeneration fails (Step 2), use this configuration for performance:

```python
# backend/app/config.py
INTEGRITY_LAYOUT: str = "small"  # Fast, reliable
INTEGRITY_HASHER: str = "keccak_160_lsb"
INTEGRITY_STONE_VERSION: str = "stone6"  # or keep stone5 if it works
INTEGRITY_MEMORY_VERIFICATION: str = "strict"
INTEGRITY_CAIRO_TIMEOUT: int = 120  # 2 minutes (sufficient for small layout)
```

## When to Use Fallback

1. **If Step 2 fails**: Canonical settings still produce `Invalid final_pc`
2. **If proof generation is too slow**: Recursive layout takes >5 minutes
3. **For local verification**: Don't need Integrity FactRegistry verification
4. **For development/testing**: Faster iteration

## Trade-offs

### Small Layout (Fallback)
- ✅ Fast proof generation (~2-3 seconds)
- ✅ Reliable (no timeouts)
- ✅ Good for local verification
- ❌ May not verify on Integrity FactRegistry (`Invalid final_pc`)

### Recursive Layout (Canonical)
- ✅ Matches Integrity's canonical settings
- ✅ May verify on Integrity FactRegistry
- ❌ Slow proof generation (may timeout)
- ❌ May still get `Invalid final_pc` (AIR mismatch)

## Quick Revert

To revert to small layout:

```bash
# Restore from backup
cp backend/app/config.py.backup_small backend/app/config.py

# Or manually update:
# INTEGRITY_LAYOUT: str = "small"
# INTEGRITY_CAIRO_TIMEOUT: int = 120
```

## Current Status

- ✅ Step 1: Hybrid (recursive + 300s timeout) - COMPLETED
- ✅ Step 2: Canonical (recursive + stone5) - COMPLETED
- ✅ Step 3: Fallback (small layout) - READY

**Next**: Test Step 2 (canonical settings). If it fails, revert to Step 3 (small layout).
