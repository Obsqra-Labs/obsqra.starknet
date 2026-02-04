# Final Fix Applied - Using Public FactRegistry

**Date**: 2026-01-26  
**Status**: Switched to public FactRegistry with registered verifiers

## Issue Root Cause

**VERIFIER_NOT_FOUND** error was caused by:
- Using custom FactRegistry (`0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64`)
- This registry doesn't have verifiers registered
- Public FactRegistry (`0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`) has all verifiers registered

## Fix Applied

**Changed FactRegistry address** in `integrity_service.py`:
- **Before**: Custom FactRegistry (no verifiers)
- **After**: Public FactRegistry (has all verifiers registered)

**Available Verifiers** (from `deployed_contracts.md`):
- `small/keccak`: `0x00024e90555503d1c05070beeb1102c77c8e73b6193544d0e8613dcb7917151c`
- `recursive/keccak`: `0x04fef1cabed83adeb23b69e09fbdcf493d6ede214a353c5c08af6696c34c797b`
- And many more...

## Configuration

Current settings (should work with public FactRegistry):
- Layout: `small` or `recursive` (both have verifiers)
- Hasher: `keccak_160_lsb`
- Stone Version: `stone5`
- Memory Verification: `strict`

## Next Steps

1. ✅ Server restarted with new FactRegistry address
2. 🔄 Test proof generation
3. ⚠️ If "Invalid final_pc" persists, check Cairo program output format

---

**Status**: FactRegistry switched ✅ | Testing in progress 🔄
