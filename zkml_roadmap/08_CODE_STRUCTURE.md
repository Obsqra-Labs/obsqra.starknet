# Code Structure: Monorepo + Feature Flags

**Strategy**: Single codebase with environment-based feature toggles for each stage.

---

## Frontend Config (frontend/src/lib/config.ts)

```typescript
export const FEATURES = {
  PROOF_GATED_EXECUTION: true,
  PARAMETERIZED_MODEL: process.env.NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL === 'true',
  MODEL_GOVERNANCE: process.env.NEXT_PUBLIC_ENABLE_MODEL_GOVERNANCE === 'true',
  ZKML_INFERENCE: process.env.NEXT_PUBLIC_ENABLE_ZKML === 'true',
  DAO_MODEL_APPROVAL: process.env.NEXT_PUBLIC_ENABLE_DAO_APPROVAL === 'true',
  AGENT_INTENTS: process.env.NEXT_PUBLIC_ENABLE_AGENT_INTENTS === 'true',
};

export const CONTRACTS = {
  RISK_ENGINE_V4: process.env.NEXT_PUBLIC_RISK_ENGINE_ADDRESS,
  RISK_ENGINE_V4_5: process.env.NEXT_PUBLIC_RISK_ENGINE_PARAMETERIZED,
  ZKML_VERIFIER: process.env.NEXT_PUBLIC_ZKML_VERIFIER,
  AGENT_ORCHESTRATOR: process.env.NEXT_PUBLIC_AGENT_ORCHESTRATOR,
};
```

---

## Frontend Component Layout

```
frontend/src/components/
├── stage2/   — Proof-Gated Execution
│   ├── ProofGenerator.tsx
│   ├── AllocationExecutor.tsx
│   └── DAOConstraintValidator.tsx
├── stage3a/  — On-Chain AI
│   ├── ModelParamsViewer.tsx
│   ├── ModelGovernance.tsx
│   └── ParamComparisonTool.tsx
├── stage3b/  — zkML (future)
├── stage4/   — Trustless AI
└── stage5/   — Agent
```

---

## Backend Config (backend/app/config.py)

- `PROOF_GATE_ENABLED: bool = True`
- `PARAMETERIZED_MODEL_ENABLED: bool = Field(False, env="PARAMETERIZED_MODEL_ENABLED")`
- `MODEL_PARAMS_TABLE: str = "model_parameters"`
- `ZKML_ENABLED: bool = Field(False, env="ZKML_ENABLED")`
- `DAO_GOVERNANCE_ENABLED: bool = Field(False, env="DAO_GOVERNANCE_ENABLED")`

---

## Contract Versioning

- **Option 1 (preferred for Stage 3A)**: Single RiskEngine with feature flag — if `model_params.read(version)` is default/zero, use hardcoded formula (Stage 2); else use params (Stage 3A).
- **Option 2**: Separate deployments (RISK_ENGINE_V4 vs RISK_ENGINE_V4_5) for A/B testing.
