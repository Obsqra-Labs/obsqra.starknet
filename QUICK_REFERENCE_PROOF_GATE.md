# Proof Gate - Quick Reference
## Fast Facts and Commands

**Date**: January 27, 2026  
**Status**: ✅ Operational

---

## Quick Facts

- **RiskEngine v4**: `0x00b844ac8c4f9bfc8675e29db75808b5e2ac59100e1e71967a76878522fb5f81`
- **StrategyRouter v3.5**: `0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73`
- **Authorization TX**: `0x01171cf26c22f17980023082d99ac8a3fb8bf48f31aaaaad0634ca2aef72ae6f`
- **Stone Version**: `stone6` (Stone v3 → stone6)
- **FactRegistry**: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`

---

## Quick Commands

### Verify Authorization
```bash
bash scripts/verify_authorization.sh
```

### Test Flow
```bash
bash scripts/test_proof_gate_flow.sh
```

### Set Authorization (if needed)
```bash
bash scripts/set_strategy_router_risk_engine.sh
```

---

## API Endpoints

### Generate Proof + Preview
```bash
POST /api/v1/risk-engine/propose-allocation
```

### Execute with Proof
```bash
POST /api/v1/risk-engine/execute-allocation
Body: { "proof_job_id": "..." }
```

---

## Flow Summary

```
Proof → Register → Execute → Verify → Allocate
```

1. Generate Stone proof (stone6)
2. Register with Integrity FactRegistry
3. Execute with proof parameters
4. RiskEngine verifies on-chain (STEP 0)
5. RiskEngine calculates allocation
6. RiskEngine calls StrategyRouter ✅

---

## Status

✅ **FULLY OPERATIONAL**

---

**For details, see**: `IMPLEMENTATION_FINAL_STATUS.md`
