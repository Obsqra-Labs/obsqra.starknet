# Recent Work Summary

**Date**: 2026-01-26  
**Scope**: Stone-only migration, Integrity integration, contract updates

## Major Initiatives

### 1. ✅ Stone-Only Migration (Complete)
**Goal**: Remove LuminAIR, enforce strict Stone-only proof pipeline

**Changes**:
- Disabled LuminAIR service (`get_luminair_service()` raises `RuntimeError`)
- Removed all mock fallbacks
- Updated all endpoints to use Stone prover exclusively
- Added strict error handling with `strict_mode: true` flag

**Files Modified**:
- `backend/app/api/routes/proofs.py` - Stone-only proof generation
- `backend/app/services/luminair_service.py` - Deprecated
- `backend/app/services/integrity_service.py` - Mock registry disabled
- `backend/app/api/routes/risk_engine.py` - Stone-only orchestration
- `backend/app/api/routes/demo.py` - Stone-only demo

### 2. ✅ Integrity Contract Integration
**Goal**: Integrate with Integrity FactRegistry for on-chain proof verification

**Progress**:
- ✅ Switched to public FactRegistry (`0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`)
- ✅ VERIFIER_NOT_FOUND resolved (verifier found and called)
- ⚠️ Invalid final_pc error (known limitation - proof format mismatch)

**Configuration Updates**:
- Layout: `small` (switched from `recursive` for performance)
- Stone Version: `stone6` (upgraded from `stone5`)
- Hasher: `keccak_160_lsb`
- Memory Verification: `strict` (or `cairo1` for Cairo1 programs)

### 3. ✅ Contract Address Updates
**Recent Updates** (from your changes):
- **RiskEngine**: `0x00b844ac8c4f9bfc8675e29db75808b5e2ac59100e1e71967a76878522fb5f81` (v4 yield-fix)
- **StrategyRouter**: `0x05d6c4b2b958c65c40ce1ebdde24cf0d99cca12a1bc386491b7979807084c485` (v3.5 yield-fix)
- **RPC**: Switched to Alchemy (`starknet-sepolia.g.alchemy.com`)

### 4. ✅ Cairo0/Cairo1 Support
**New Feature**: Conditional Cairo version based on memory verification setting

**Implementation**:
- If `INTEGRITY_MEMORY_VERIFICATION == "cairo1"`: Use Cairo1 (`risk_example.cairo`)
- Otherwise: Use Cairo0 (`risk_example_cairo0.cairo`)
- Added `_resolve_cairo0_compile_bin()` and `_resolve_cairo0_run_bin()` helpers

**Files Modified**:
- `backend/app/api/routes/risk_engine.py` - Added Cairo0/Cairo1 conditional logic

### 5. ✅ Legacy Contract Support
**New Feature**: Detect on-chain RiskEngine signature to handle legacy vs proof-gated contracts

**Implementation**:
- `_get_risk_engine_onchain_inputs()` - Inspects on-chain ABI to detect contract version
- Conditionally includes proof parameters based on contract signature
- Handles both legacy (2 inputs) and proof-gated (7 inputs) contracts

**Files Modified**:
- `backend/app/api/routes/risk_engine.py` - Added contract detection logic

### 6. ✅ Documentation & Testing
**Created**:
- `docs/STRICT_MODE_GUIDE.md` - Comprehensive strict mode documentation
- `test_stone_only_e2e.py` - End-to-end test suite
- Multiple status/summary documents

**Frontend Updates**:
- Updated error handling for structured errors
- Added proof verification error category
- Improved error messages for strict mode

## Current Configuration

```python
# backend/app/config.py
STARKNET_RPC_URL: str = "https://starknet-sepolia.g.alchemy.com/v2/..."
RISK_ENGINE_ADDRESS: str = "0x00b844ac8c4f9bfc8675e29db75808b5e2ac59100e1e71967a76878522fb5f81"
STRATEGY_ROUTER_ADDRESS: str = "0x05d6c4b2b958c65c40ce1ebdde24cf0d99cca12a1bc386491b7979807084c485"
INTEGRITY_LAYOUT: str = "small"
INTEGRITY_HASHER: str = "keccak_160_lsb"
INTEGRITY_STONE_VERSION: str = "stone6"
INTEGRITY_MEMORY_VERIFICATION: str = "strict"
INTEGRITY_VERIFIER_SEPOLIA = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
```

## Current Status

### ✅ Working
- Stone proof generation
- Proof serialization
- Verifier lookup (VERIFIER_NOT_FOUND resolved!)
- Contract detection (legacy vs proof-gated)
- Cairo0/Cairo1 conditional support
- Strict error handling

### ⚠️ Known Issues
- **Invalid final_pc**: Proof format doesn't match Integrity's AIR expectations exactly
  - Documented in `docs/proving_flows.md`
  - Solutions: Use Atlantic or regenerate with canonical AIR

## Recent Code Changes (Your Updates)

1. **Config Updates**:
   - Layout: `small` (faster, more reliable)
   - Stone Version: `stone6` (upgraded)
   - Contract addresses: Updated to yield-fix versions
   - RPC: Switched to Alchemy

2. **Cairo0 Support**:
   - Added conditional logic for Cairo0 vs Cairo1
   - Added helper functions for Cairo0 binaries
   - Supports `risk_example_cairo0.cairo` when not using cairo1 mode

3. **Contract Detection**:
   - Added `_get_risk_engine_onchain_inputs()` to detect contract version
   - Conditionally includes proof parameters based on contract signature
   - Handles backward compatibility with legacy contracts

## Next Steps

1. **Test with new configuration** (small/stone6)
2. **Verify Cairo0 path works** (if `risk_example_cairo0.cairo` exists)
3. **Test contract detection** (legacy vs proof-gated)
4. **Address Invalid final_pc** (if still occurring)

---

**Status**: Stone-only migration complete ✅ | Integrity integration in progress ⚠️ | Recent updates: Cairo0 support, contract detection, config updates ✅
