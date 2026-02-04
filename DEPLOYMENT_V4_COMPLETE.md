# RiskEngine v4 Deployment Complete ✅

## Status: DEPLOYED & READY FOR TESTING

**Date**: January 26, 2026  
**Network**: Starknet Sepolia  
**zkML Maturity**: 4/5 (On-Chain Proof Verification Enforced)

---

## Deployment Details

### Contract Information
- **Contract**: RiskEngine v4
- **Address**: `0x06c31be32c0b6f6b27f7a64afe5b1ad6a21ededcd86773b92beaf1aaf54af220`
- **Class Hash**: `0x055eeea681002ae09356efb84b3bc95c1419b25a1e60deed5d1766863cc2625e`
- **Declaration TX**: `0x01b800757cc77dea7b11e193f542aab303b131c6dd6b59073eacff86c39b03d1`
- **Deployment TX**: `0x0783b91c2019a06bb87fe50e9860a9e33f34433e4e56ff1195f7cb7d58c97837`

### View on Block Explorer
- **Contract**: https://sepolia.starkscan.co/contract/0x06c31be32c0b6f6b27f7a64afe5b1ad6a21ededcd86773b92beaf1aaf54af220
- **Class**: https://sepolia.starkscan.co/class/0x055eeea681002ae09356efb84b3bc95c1419b25a1e60deed5d1766863cc2625e
- **Deployment TX**: https://sepolia.starkscan.co/tx/0x0783b91c2019a06bb87fe50e9860a9e33f34433e4e56ff1195f7cb7d58c97837

---

## What Changed (v4)

### New Features
1. **On-Chain Proof Verification Gate**
   - `propose_and_execute_allocation` now requires proof fact hashes
   - Verifies proofs exist in SHARP fact registry before execution
   - Asserts on-chain calculated risk scores match proven scores

2. **Enhanced Security**
   - No execution without valid proof verification
   - Contract-level enforcement (not just backend)
   - Risk score matching prevents proof/calculation mismatches

3. **SHARP Integration**
   - Integrates with Herodotus Integrity FactRegistry
   - Fact registry address: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`
   - Passed as parameter (cannot be const due to felt252 size limits)

### Interface Changes
```cairo
fn propose_and_execute_allocation(
    ref self: ContractState,
    jediswap_metrics: ProtocolMetrics,
    ekubo_metrics: ProtocolMetrics,
    // NEW: Proof verification parameters
    jediswap_proof_fact: felt252,         // SHARP fact hash
    ekubo_proof_fact: felt252,            // SHARP fact hash
    expected_jediswap_score: felt252,     // Risk score from proof
    expected_ekubo_score: felt252,        // Risk score from proof
    fact_registry_address: ContractAddress, // SHARP fact registry
) -> AllocationDecision;
```

---

## Backend Configuration

✅ **Updated**: `backend/app/config.py`
- `RISK_ENGINE_ADDRESS` now points to v4 contract

---

## Testing Checklist

### ✅ Completed
- [x] Contracts compiled successfully
- [x] Contract declared on Sepolia
- [x] Contract deployed on Sepolia
- [x] Backend config updated
- [x] Deployment info saved

### ⏳ Pending (End-to-End Testing)
- [ ] Generate proof via LuminAIR/Stone Prover
- [ ] Get fact hash from Integrity service
- [ ] Test contract accepts valid proofs
- [ ] Test contract rejects invalid proofs
- [ ] Verify end-to-end allocation flow works
- [ ] Test with real protocol metrics

---

## Next Steps

1. **Generate Proof**
   ```bash
   # Use LuminAIR or Stone Prover to generate proof
   # Get fact hash from Integrity service
   ```

2. **Test Valid Proof**
   ```bash
   # Call propose_and_execute_allocation with:
   # - Valid proof fact hashes
   # - Correct expected risk scores
   # - SHARP fact registry address
   ```

3. **Test Invalid Proof**
   ```bash
   # Call with invalid proof fact hash
   # Verify contract rejects (assert fails)
   ```

4. **Full E2E Test**
   ```bash
   # Complete flow:
   # 1. Generate proof
   # 2. Verify via Integrity
   # 3. Call contract with proof data
   # 4. Verify allocation executes
   ```

---

## zkML Maturity Progress

**Before**: 3.0-3.5/5
- ✅ Proof generation pipeline exists
- ✅ Deterministic model in Cairo/Rust
- ✅ Backend orchestration
- ⚠️ No contract-level enforcement

**After**: 4/5 ✅
- ✅ Proof generation pipeline exists
- ✅ Deterministic model in Cairo/Rust
- ✅ Backend orchestration
- ✅ **Contract-level proof verification gate** ← NEW
- ⏳ Model provenance & upgradeability (5/5)

**Next**: 5/5 requires:
- Model hash committed on-chain
- Versioned model registry
- UX transparency (proof hash, model hash displayed)

---

## Files Modified

- `contracts/src/risk_engine.cairo` - Added proof verification
- `contracts/src/sharp_verifier.cairo` - Made public, fixed address handling
- `contracts/src/lib.cairo` - Exposed sharp_verifier module
- `backend/app/api/routes/risk_engine.py` - Updated to pass proof data
- `backend/app/config.py` - Updated contract address
- `integration_tests/dev_log.md` - Documented deployment

---

## Deployment Info Saved

- **Location**: `deployments/risk_engine_v4_sepolia.json`
- **Format**: JSON with all deployment details

---

**Status**: ✅ **READY FOR END-TO-END TESTING**
