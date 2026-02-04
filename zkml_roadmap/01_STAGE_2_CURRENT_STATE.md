# Stage 2: Proof-Gated Execution (Current State)

**Status**: Production (4/5 zkML maturity)

---

## What's Working

- **STEP 0**: Verify proofs via FactRegistry (`verify_allocation_decision_with_proofs`)
- **STEP 0.5**: Model version enforcement (`approved_model_versions`)
- **STEP 0.6**: Constraint signature (user-signed constraints)
- **STEP 1-5**: Recompute scores, validate DAO constraints, execute via StrategyRouter

**Value Prop**: "Proof-gated execution infrastructure — no proof, no execution."

**Test Evidence**: TX `0x13531b39...` succeeded with 41.3% / 58.7% allocation (TRUSTLESS_AGENT_VERIFICATION_COMPLETE.md).

---

## Tech Stack

| Component | Implementation |
|-----------|----------------|
| Prover | Stone (production) |
| Verification | Integrity FactRegistry |
| Formula | Fixed in Cairo (hardcoded weights: 25, 40, categorical liquidity, audit, age) |
| Model | Model hash enforced; no parameterization |

---

## Contract Flow (risk_engine.cairo)

```
propose_and_execute_allocation(...)
  → STEP 0: verify_allocation_decision_with_proofs(...)
  → STEP 0.5: approved_model_versions.read(model_version)
  → STEP 0.6: record constraint_signature if signer != 0
  → STEP 1-2: calculate_risk_score_internal (fixed formula)
  → STEP 3-4: calculate_allocation_internal, DAO validate
  → STEP 5: StrategyRouter.update_allocation(...)
```

---

## Gaps Addressed by Stage 3A

- Formula weights are hardcoded (25, 40, 0/5/15/30, etc.).
- No on-chain upgrade path for "model" without contract redeploy.
- Stage 3A adds `ModelParams` in storage and `set_model_params()` for governance.
