# OODS Debugging Improvements

**Date**: 2026-01-27  
**Status**: ✅ Implemented

---

## Overview

Implemented three critical improvements to diagnose and isolate OODS (Out-of-Distribution) failures:

1. **Hard logging at proof generation** - Dumps active settings + proof_parameters
2. **Enhanced layout mismatch guard** - Checks all verifier config fields
3. **One-shot canonical pipeline** - Uses Integrity's generate.py approach exactly

---

## 1. Hard Logging at Proof Generation ✅

### Location
- `backend/app/api/routes/risk_engine.py` - `_stone_integrity_fact_for_metrics()`
- `backend/app/services/stone_prover_service.py` - `generate_proof()`

### What Gets Logged

**Before Proof Generation**:
- Active Integrity settings (layout, stone_version, hasher, memory_verification, timeout)
- Stone prover parameters (FRI step_list, n_queries, log_n_cosets, channel_hash, commitment_hash, etc.)

**After Proof Generation**:
- Proof layout and n_steps
- FRI parameters from generated proof (reads from `proof_parameters` field, not `config`)
- Channel hash, commitment hash, pow hash
- n_verifier_friendly_commitment_layers
- All proof_parameters for comparison with canonical

**Note**: Stone proof JSON uses `proof_parameters` field, not `config`. The logging correctly reads from `proof_parameters` first, then falls back to `config` if needed.

### Example Output
```
================================================================================
🔍 PROOF GENERATION - ACTIVE SETTINGS
================================================================================
INTEGRITY_LAYOUT: recursive
INTEGRITY_STONE_VERSION: stone5
INTEGRITY_HASHER: keccak_160_lsb
INTEGRITY_MEMORY_VERIFICATION: strict
INTEGRITY_CAIRO_TIMEOUT: 300s
================================================================================

================================================================================
🔍 STONE PROVER - PARAMETERS
================================================================================
FRI step_list: [0, 4, 4, 2]
FRI last_layer_degree_bound: 128
Channel hash: poseidon3
Commitment hash: keccak256_masked160_lsb
n_verifier_friendly_commitment_layers: 9999
================================================================================

================================================================================
🔍 PROOF GENERATION - PROOF PARAMETERS
================================================================================
Proof Layout: recursive
Proof n_steps: 512
FRI step_list: [0, 4, 4, 2]
Channel hash: poseidon3
Commitment hash: keccak256_masked160_lsb
n_verifier_friendly_commitment_layers: 9999
================================================================================
```

---

## 2. Enhanced Layout Mismatch Guard ✅

### Location
- `backend/app/api/routes/risk_engine.py` - `_stone_integrity_fact_for_metrics()`

### What It Checks

**Before**: Only checked proof layout vs expected layout

**Now**: Checks all verifier config fields:
- `layout` (from proof JSON)
- `stone_version` (logged for comparison, in calldata)
- `hasher` (logged for comparison, in calldata)
- `memory_verification` (logged for comparison, in calldata)

### Behavior

- **Hard-fails immediately** if any mismatch detected
- **Logs all expected vs actual values** for debugging
- **Provides clear error message** with actionable guidance

### Example Error
```
Verifier config mismatch detected:
  - layout: proof='small' vs expected='recursive'
Expected verifier config:
  - layout: recursive
  - stone_version: stone5
  - hasher: keccak_160_lsb
  - memory_verification: strict
This will cause verification errors (Invalid builtin, OODS, etc.).
Check backend/.env settings and ensure cairo-run uses matching --layout.
```

---

## 3. One-Shot Canonical Pipeline ✅

### Location
- `backend/app/api/routes/risk_engine.py` - `_canonical_integrity_pipeline()`

### Purpose

Follows Integrity's `generate.py` approach **exactly** to isolate AIR and serialization mismatches. If this pipeline verifies successfully, the issue is in the Obsqra pipeline. If it fails, it's an AIR/version/stone mismatch.

### Steps (Matches Integrity's generate.py exactly)

1. **Compile Cairo0 program** using `cairo-compile` (canonical approach)
2. **Run Cairo0 program** using `cairo-run` to generate traces with canonical layout
3. **Extract n_steps** and compute FRI step_list using Integrity's exact formula:
   ```python
   n_steps_log = ceil(log(n_steps, 2))
   last_layer_log = ceil(log(last_layer_degree_bound, 2))
   sigma = n_steps_log + 4 - last_layer_log
   q, r = divmod(sigma, 4)
   fri_step_list = [0] + [4] * q + ([r] if r > 0 else [])
   ```
4. **Run Stone prover** with canonical parameters from `integrity/examples/proofs/cpu_air_params.json`
5. **Verify proof structure** and log all parameters
6. **Serialize and register** with Integrity FactRegistry

### Usage

```python
from app.api.routes.risk_engine import _canonical_integrity_pipeline

fact_hash, proof_path, output_dir, proof_hash = await _canonical_integrity_pipeline(
    jediswap_metrics={
        "utilization": 7500,
        "volatility": 3000,
        "liquidity": 1,
        "audit_score": 85,
        "age_days": 365,
    },
    ekubo_metrics={
        "utilization": 6000,
        "volatility": 2500,
        "liquidity": 0,
        "audit_score": 90,
        "age_days": 500,
    },
)
```

### Expected Behavior

- **If successful**: Proof verifies on-chain → Issue is in Obsqra pipeline
- **If fails**: AIR/version/stone mismatch → Need to investigate Stone binary version or AIR config

---

## Next Steps for OODS Diagnosis

### 1. Confirm Backend Restart
```bash
# Check if backend process is using old settings
ps aux | grep uvicorn
# Restart backend to ensure new settings are active
systemctl restart obsqra-backend  # or your restart command
```

### 2. Compare Proof Parameters
After generating a proof, compare logged parameters against canonical:
- `fri_step_list` - Should match canonical calculation
- `channel_hash` - Should be `poseidon3` (canonical)
- `commitment_hash` - Should be `keccak256_masked160_lsb` (canonical)
- `n_verifier_friendly_commitment_layers` - Should be `9999`

### 3. Test Canonical Pipeline
```python
# Run canonical pipeline to isolate issue
result = await _canonical_integrity_pipeline(jediswap_metrics, ekubo_metrics)
if result[0]:  # fact_hash is not None
    print("✅ Canonical pipeline verifies - issue is in Obsqra pipeline")
else:
    print("❌ Canonical pipeline fails - AIR/version/stone mismatch")
```

### 4. Check Stone Binary Version
```bash
# Verify Stone binary version matches verifier setting
# If verifier is stone5, binary should be stone5
# Check binary commit or version
cd /opt/obsqra.starknet/stone-prover
git log --oneline -1
```

### 5. Compare with Canonical Example
```bash
# Compare proof structure with Integrity's canonical example
diff -u \
  /tmp/canonical_integrity_*/risk_proof.json \
  integrity/examples/proofs/recursive/cairo1_stone5_keccak_160_lsb_example_proof.json
```

---

## Files Modified

- `backend/app/api/routes/risk_engine.py`
  - Added hard logging in `_stone_integrity_fact_for_metrics()`
  - Enhanced layout mismatch guard
  - Added `_canonical_integrity_pipeline()` function (uses Cairo0, matches Integrity's generate.py)
  - Fixed proof parameter logging to read from `proof_parameters` field (not `config`)
  - Added `_resolve_cairo1_compile_bin()` helper

- `backend/app/services/stone_prover_service.py`
  - Added hard logging in `generate_proof()`

## Critical Fixes Applied

### Fix 1: Canonical Pipeline Uses Cairo0 ✅
- **Before**: Used Cairo1 (`risk_example.cairo` + `cairo1-run`)
- **After**: Uses Cairo0 (`risk_example_cairo0.cairo` + `cairo-compile` + `cairo-run`)
- **Matches**: Integrity's `generate.py` exactly (Cairo0 CPU AIR proofs)

### Fix 2: Proof Parameter Logging Reads Correct Field ✅
- **Before**: Read from `proof_data.get("config", {})` (empty in Stone proofs)
- **After**: Reads from `proof_data.get("proof_parameters", {})` first, fallback to `config`
- **Matches**: Stone proof JSON structure (uses `proof_parameters` field)

---

## Status

✅ All three improvements implemented and ready for testing.

**Next**: Run proof generation and review logs to identify OODS root cause.
