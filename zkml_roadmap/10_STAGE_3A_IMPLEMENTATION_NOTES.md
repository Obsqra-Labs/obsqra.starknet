# Stage 3A Implementation Notes

**Audience**: Developers and stakeholders.  
**Purpose**: Technical and narrative summary of what was built for Stage 3A (On-Chain Parameterized Model) and how to verify it.

---

## What Stage 3A Delivers

- **Contract**: RiskEngine stores per-version `ModelParams` (weights + clamp bounds). `calculate_risk_score_internal` reads params by `model_version`; version `0` or unset uses hardcoded Stage 2 defaults.
- **Backend**: `GET /api/v1/risk-engine/model-params/{version}` returns on-chain parameters (or defaults). Feature flag: `PARAMETERIZED_MODEL_ENABLED`.
- **Frontend**: Obsqra Labs landing; Stage 3A section (ModelParamsViewer, ParamComparisonTool) when `NEXT_PUBLIC_ENABLE_PARAMETERIZED_MODEL=true`.
- **Deployment**: RiskEngine v4 (Stage 3A) deployed on Sepolia; StrategyRouter wired to it. Landing domain: **starknet.obsqra.fi**.

---

## Key Files

| Layer | File | Role |
|-------|------|------|
| Contract | `contracts/src/risk_engine.cairo` | `ModelParams` struct, `model_params` storage, `set_model_params` / `get_model_params`, `calculate_risk_score_internal(model_version)` |
| Backend | `backend/app/config.py` | `PARAMETERIZED_MODEL_ENABLED`, `RISK_ENGINE_ADDRESS` |
| Backend | `backend/app/services/model_service.py` | `get_model_params(version)`, `set_model_params` (admin script guidance) |
| Backend | `backend/app/api/routes/risk_engine.py` | `GET /model-params/{version}` |
| Frontend | `frontend/src/lib/config.ts` | `FEATURES.PARAMETERIZED_MODEL`, `CONTRACTS.RISK_ENGINE_V4_5` |
| Frontend | `frontend/src/components/stage3a/` | `ModelParamsViewer`, `ParamComparisonTool` |
| Frontend | `frontend/src/app/page.tsx` | Obsqra Labs hero, Research Areas, Products & Demos (Stage 3A conditional) |

---

## Integration Status

| Path | Status | Notes |
|------|--------|------|
| **Contract** | Integrated | `propose_and_execute_allocation` takes `model_version` and passes it to `calculate_risk_score_internal`; params read from `model_params` or defaults. |
| **Backend API** | Tested | `GET /api/v1/risk-engine/model-params/{version}` returns params (or defaults). Verified with backend started via `python3 -m uvicorn main:app` (must use `main:app`, not `app.main:app`). |
| **Backend → allocation** | Integrated | Orchestrate/execute calls RiskEngine with `model_version` from model registry; contract uses it for risk scoring. |
| **Frontend** | Wired | `ModelParamsViewer` fetches from backend; shown in Products when `FEATURES.PARAMETERIZED_MODEL`. Run frontend with `NEXT_PUBLIC_BACKEND_URL=http://localhost:8001` (or your backend port) to hit the API. |
| **Full E2E (UI)** | Manual | Backend + frontend must both run with current code; then open home page and confirm "On-Chain AI" section and params table load. |

---

## How to Verify (E2E)

1. **Backend**: From repo root, start backend with current code:
   ```bash
   cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
   ```
   (Use `main:app` when running from `backend/`; the API router includes the model-params route.)
2. **Model params API**:
   ```bash
   curl -s http://localhost:8001/api/v1/risk-engine/model-params/0
   ```
   Expected: JSON with `w_utilization`, `w_volatility`, `w_liquidity_*`, `w_audit`, `w_age`, `age_cap_days`, `clamp_min`, `clamp_max` (defaults when version 0 or unset).
3. **Frontend**: Run `npm run dev` in `frontend` with `NEXT_PUBLIC_BACKEND_URL` pointing at your backend (e.g. `http://localhost:8002`). Ensure backend CORS includes the frontend origin (e.g. `http://localhost:3004` is in `backend/app/config.py` CORS_ORIGINS). Open home page → scroll to Products; the "On-Chain AI" (BETA) card and "Current model params (v0)" table should load.

---

## Narrative Summary

Stage 3A moves the risk formula from fully hardcoded (Stage 2) to **parameterized on-chain**: the same Cairo formula runs, but weights and bounds are read from contract storage by version. Operators can ship new behavior by calling `set_model_params` (e.g. via admin script) without redeploying the contract. The API and UI expose these parameters so users and integrators can see exactly which model version and constants are in use. This sets the base for Stage 3B (real zkML inference) and Stage 4 (trustless artifacts and governance).
