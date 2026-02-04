# Stage 3A: On-Chain Model (Option A — Parameterized Formula)

**Status**: NEXT (1-2 weeks)

---

## What Changes

- Formula **parameters** (weights, clamp bounds) move from literals to **contract storage**.
- Keyed by `model_version`; same Stone proof flow (prove execution of Cairo that reads params).
- Upgrade = `set_model_params(version, params)` (owner or DAO), not redeploy.

---

## Contract Changes (risk_engine.cairo)

### ModelParams Struct

```cairo
#[derive(Drop, Serde, starknet::Store)]
pub struct ModelParams {
    pub w_utilization: felt252,   // default 25
    pub w_volatility: felt252,   // default 40
    pub w_liquidity_0: felt252,   // default 0
    pub w_liquidity_1: felt252,   // default 5
    pub w_liquidity_2: felt252,   // default 15
    pub w_liquidity_3: felt252,   // default 30
    pub w_audit: felt252,        // default 3 (numerator for (100-audit)*3/10)
    pub w_age: felt252,          // default 10 (numerator for age risk)
    pub age_cap_days: felt252,   // default 730
    pub clamp_min: felt252,      // default 5
    pub clamp_max: felt252,      // default 95
}
```

### Storage

```cairo
model_params: Map<felt252, ModelParams>
```

### New Functions

- `set_model_params(version: felt252, params: ModelParams)` — owner only (or DAO when Stage 4).
- `get_model_params(version: felt252) -> ModelParams` — view for frontend/backend.

### calculate_risk_score_internal

- Signature: add `model_version: felt252` (or read from caller context).
- Read `params = self.model_params.read(model_version)`.
- If params are zero/default, fallback to current hardcoded behavior (Stage 2 compatibility).
- Otherwise: use `params.w_utilization`, `params.w_volatility`, etc., and `params.clamp_min`/`clamp_max`.

---

## Backend

- `model_service.py`: `get_model_params(version)`, `set_model_params(version, params)` (calls contract or DB cache).
- Config: `PARAMETERIZED_MODEL_ENABLED` flag.
- Proof flow unchanged: Stone trace must use same params as contract for given `model_version`.

---

## Frontend

- Feature flag: `NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL`.
- Components: ModelParamsViewer, ParamComparisonTool (Stage 3A demo).

---

## Value Prop

"On-chain AI with upgradeable models — transparent parameters, DAO governance."

**Proof system**: No change — Stone only.
