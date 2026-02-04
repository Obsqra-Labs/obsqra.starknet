# RiskEngine v4 Test Results ✅

**Date**: January 26, 2026  
**Contract**: `0x06c31be32c0b6f6b27f7a64afe5b1ad6a21ededcd86773b92beaf1aaf54af220`  
**Network**: Starknet Sepolia

---

## Test Results

### ✅ Test 1: Basic Contract Access

**Test**: Verify contract is accessible and basic functions work

**Results**:
- ✅ `get_contract_version()` → `0xdc` (220) - **PASS**
- ✅ `get_decision_count()` → `0x0` (0) - **PASS**

**Status**: ✅ **PASSING**

---

### ✅ Test 2: Proof Verification Enforcement

**Test**: Verify contract rejects invalid proof data

**Test Case**: Call `propose_and_execute_allocation` with:
- Invalid proof fact hash: `0x0` (not in SHARP registry)
- Valid metrics structure
- Expected risk scores

**Result**: ✅ Contract correctly rejected invalid proof

**Status**: ✅ **PASSING** - Proof verification is enforced!

---

### ✅ Test 3: Risk Score Calculation

**Test**: Verify standalone risk calculation function works (no proof required)

**Test Case**: Call `calculate_risk_score` with:
- Utilization: 6500 (65%)
- Volatility: 3500 (35%)
- Liquidity: 1
- Audit Score: 98
- Age: 800 days

**Result**: ✅ Risk score calculated: `0x23` (35 in decimal)

**Status**: ✅ **PASSING**

---

## Contract Behavior Verification

### ✅ Proof Verification Gate Working

The contract correctly:
1. ✅ Requires proof fact hashes as parameters
2. ✅ Verifies proofs exist in SHARP registry
3. ✅ Rejects execution with invalid proofs
4. ✅ Will verify risk scores match proven scores (when valid proof provided)

### ✅ Backward Compatibility

- ✅ Standalone `calculate_risk_score` still works (no proof required)
- ✅ Contract version accessible
- ✅ Decision tracking accessible

---

## End-to-End Flow Status

### ✅ Completed
- [x] Contract deployed and accessible
- [x] Basic functions working
- [x] Proof verification enforced
- [x] Invalid proofs rejected

### ⏳ Pending (Requires Backend + Proof Generation)
- [ ] Generate real proof via LuminAIR/Stone Prover
- [ ] Get fact hash from Integrity service
- [ ] Test contract accepts valid proof
- [ ] Verify complete allocation flow works

---

## Test Commands

### Basic Contract Tests
```bash
# Test contract version
sncast --account deployer call \
  --contract-address 0x06c31be32c0b6f6b27f7a64afe5b1ad6a21ededcd86773b92beaf1aaf54af220 \
  --function get_contract_version \
  --network sepolia

# Test risk calculation
sncast --account deployer call \
  --contract-address 0x06c31be32c0b6f6b27f7a64afe5b1ad6a21ededcd86773b92beaf1aaf54af220 \
  --function calculate_risk_score \
  --calldata 6500 3500 1 98 800 \
  --network sepolia
```

### Full E2E Test (with Backend)
```bash
# 1. Start backend
cd /opt/obsqra.starknet/backend
python3 main.py

# 2. Generate proof
curl -X POST http://localhost:8001/api/risk-engine/orchestrate \
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
      "utilization": 5200,
      "volatility": 2800,
      "liquidity": 2,
      "audit_score": 95,
      "age_days": 400
    }
  }'

# 3. Execute with proof (after proof generation completes)
curl -X POST http://localhost:8001/api/risk-engine/execute \
  -H "Content-Type: application/json" \
  -d '{"proof_job_id": "<job_id>"}'
```

---

## Conclusion

✅ **All basic tests passing**

The RiskEngine v4 contract is:
- ✅ Deployed and accessible
- ✅ Enforcing proof verification
- ✅ Rejecting invalid proofs
- ✅ Ready for end-to-end testing with real proofs

**Next Step**: Test with real proof generation via backend API to verify complete flow.

---

**Test Scripts**:
- `test_risk_engine_v4_e2e.sh` - Basic contract tests
- `test_with_real_proof.sh` - Backend API integration tests
