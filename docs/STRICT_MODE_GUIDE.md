# Strict Mode: Stone-Only Proof Pipeline

**Date**: 2026-01-26  
**Status**: Active - All systems enforce strict verification

## Overview

The system operates in **strict Stone-only mode**, where all proofs must be:
1. Generated using the Stone prover
2. Registered with the Integrity FactRegistry
3. Verified on-chain before execution

**No mock fallbacks or bypasses are available.** This ensures deterministic, trustless proof verification.

## Architecture

```
Protocol Metrics
    ↓
Cairo Execution (cairo1-run)
    ↓
Stone Prover (cpu_air_prover)
    ↓
Proof Serializer (Integrity format)
    ↓
Integrity FactRegistry (on-chain)
    ↓
RiskEngine Contract (verifies fact_hash)
    ↓
Execution (only if verified)
```

## Key Features

### 1. Single Proof Source
- **Only Stone prover** is used for proof generation
- LuminAIR is deprecated and disabled
- All proof endpoints use `_stone_integrity_fact_for_metrics()`

### 2. No Mock Fallbacks
- Mock registry is disabled (`mocked_registry_address = None`)
- `register_mocked_fact()` raises `RuntimeError`
- `ALLOW_FAKE_FACT_HASH` is deprecated
- `ALLOW_UNVERIFIED_EXECUTION` is ignored

### 3. Strict Verification
- Proofs must be verified in FactRegistry before execution
- Contract enforces verification (RiskEngine v4)
- Backend enforces verification (no bypasses)

### 4. Clear Error Messages
All errors include:
- Structured error format with `strict_mode: true`
- Clear failure reasons
- Fact hash when available
- Actionable guidance

## API Endpoints

### `/api/v1/proofs/generate`
Generates Stone proof and verifies on-chain.

**Request:**
```json
{
  "jediswap_metrics": {
    "utilization": 6500,
    "volatility": 3500,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800
  },
  "ekubo_metrics": {
    "utilization": 5000,
    "volatility": 2500,
    "liquidity": 2,
    "audit_score": 95,
    "age_days": 600
  }
}
```

**Success Response:**
```json
{
  "proof_hash": "0x...",
  "fact_hash": "0x...",
  "jediswap_score": 45,
  "ekubo_score": 38,
  "status": "verified",
  "verified": true,
  "message": "STARK proof generated using Stone prover and verified on-chain in 2.34s"
}
```

**Error Response (Strict Mode):**
```json
{
  "detail": {
    "error": "Proof verification failed",
    "message": "Proof was generated but not verified on-chain in FactRegistry. This is a strict error - no fallbacks allowed.",
    "fact_hash": "0x...",
    "fact_registry_address": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64",
    "strict_mode": true
  }
}
```

### `/api/v1/risk-engine/orchestrate-allocation`
Full orchestration: Stone proof → Integrity → RiskEngine.

**Behavior:**
- Generates Stone proof
- Registers with Integrity FactRegistry
- Verifies on-chain
- Creates allocation proposal (if verified)
- Returns proposal with verification status

**Error Handling:**
- If proof generation fails: Returns 500 with error details
- If verification fails: Returns 400 with `strict_mode: true`
- No execution if proof is not verified

## Error Handling

### Frontend Error Format
The frontend automatically handles structured errors:

```typescript
// Error response structure
{
  detail: {
    error: string,           // Error type
    message: string,          // Human-readable message
    fact_hash?: string,       // Fact hash (if available)
    fact_registry_address?: string,  // Registry address
    strict_mode: true        // Always true in strict mode
  }
}
```

### Error Categories
- **Proof Generation Failed**: Stone prover error or Cairo execution failure
- **Proof Verification Failed**: Proof generated but not verified on-chain
- **Invalid Metrics**: Input validation failure
- **Network Error**: RPC or network connectivity issue

## Testing

### End-to-End Test
Run the comprehensive E2E test:

```bash
python3 test_stone_only_e2e.py
```

This tests:
1. Backend health
2. Stone proof generation
3. Error handling (invalid metrics)
4. Full orchestration flow
5. Verification status endpoint

### Manual Testing
1. **Generate Proof:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/proofs/generate \
     -H "Content-Type: application/json" \
     -d '{
       "jediswap_metrics": {
         "utilization": 6500,
         "volatility": 3500,
         "liquidity": 1,
         "audit_score": 98,
         "age_days": 800
       },
       "ekubo_metrics": {
         "utilization": 5000,
         "volatility": 2500,
         "liquidity": 2,
         "audit_score": 95,
         "age_days": 600
       }
     }'
   ```

2. **Check Verification:**
   ```bash
   curl http://localhost:8001/api/v1/verification/verification-status/{proof_job_id}
   ```

## Configuration

### Required Settings
```python
# backend/app/config.py
ALLOW_UNVERIFIED_EXECUTION: bool = False  # Ignored in strict mode
ALLOW_FAKE_FACT_HASH: bool = False       # Deprecated
INTEGRITY_VERIFIER_SEPOLIA = 0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64
```

### Contract Addresses
- **RiskEngine v4**: `0x02c837cee833722038c168fe4087e956c2a303c001c1a43278a70575db5a9b09`
- **StrategyRouter v3.5**: `0x04842cb02df216cadc8ba1341bdd7626b8ccaaa666c1338c81557e9728deac2b`
- **FactRegistry**: `0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64`

## Troubleshooting

### Proof Generation Fails
**Symptoms:** 500 error with "Stone proof registration failed"

**Possible Causes:**
- Stone prover binary not found
- Cairo execution trace generation failed
- Integrity serializer error

**Solutions:**
1. Verify Stone prover is installed: `which cpu_air_prover`
2. Check Cairo program exists: `ls verification/risk_example.cairo`
3. Verify Integrity serializer: `ls integrity/target/release/proof_serializer`

### Proof Verification Fails
**Symptoms:** 400 error with "Proof verification failed" and `strict_mode: true`

**Possible Causes:**
- Fact hash not registered in FactRegistry
- FactRegistry contract call failed
- Network/RPC issue

**Solutions:**
1. Check FactRegistry address is correct
2. Verify RPC connection: `curl {STARKNET_RPC_URL}`
3. Check fact hash manually: `sncast call --contract-address {FACT_REGISTRY} --function isCairoFactValid --arguments {fact_hash}`

### LuminAIR Errors
**Symptoms:** `RuntimeError: get_luminair_service() is deprecated`

**Cause:** Code is trying to use deprecated LuminAIR service

**Solution:** All code should use Stone prover. Update any remaining LuminAIR references.

## Migration Notes

### Breaking Changes
1. **LuminAIR Deprecated**: `get_luminair_service()` raises `RuntimeError`
2. **No Mock Fallbacks**: System fails if proof generation/verification fails
3. **Strict Verification**: `ALLOW_UNVERIFIED_EXECUTION` is ignored

### Backward Compatibility
- Old API endpoints still work but enforce strict mode
- Frontend automatically handles new error format
- Error messages are backward compatible (fallback to old format)

## Future Enhancements

1. **Proof Caching**: Cache verified proofs to reduce regeneration
2. **Batch Verification**: Verify multiple proofs in one transaction
3. **Proof Compression**: Optimize proof size for faster transmission
4. **Monitoring**: Add metrics for proof generation/verification success rates

---

**Status**: ✅ Strict mode is active and enforced across all systems.
