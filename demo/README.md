# Obsqra Demo: Local Proof + Settlement Walkthrough

This is a minimal, “works-today” demo that exercises the stack end-to-end using the current components:

- **LuminAIR/stwo** for a local zk proof of the risk computation (what we already run in orchestration).
- **Backend orchestration** to store the proof job, execute the on-chain allocation, and mark status.
- **Mock settlement** (no Integrity/Atlantic) — because Stone/Atlantic proofs are still pending credits/resources. This keeps the demo runnable right now.

> Goal: show an agent call → LuminAIR proof generated locally → transaction sent → proof job recorded with status/error surfaced.

## Prerequisites
- Backend env set (`backend/.env` already populated in this repo).
- Postgres running with `obsqra` DB (default connection `postgresql://obsqra:obsqra@localhost:5432/obsqra` per `app/db/session.py`).
- Backend dependencies installed (`pip install -r backend/requirements.txt`).
- LuminAIR binary optional; if missing, the service falls back to mock proof (still demonstrates the flow).

## Run the demo
1) Start the backend API (from `/opt/obsqra.starknet/backend`):
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

2) Trigger orchestration (uses LuminAIR -> mock or real proof, then on-chain tx):
```bash
curl -X POST http://localhost:8001/api/v1/risk-engine/orchestrate-allocation \
  -H "Content-Type: application/json" \
  -d '{
        "jediswap_metrics": {"utilization":5000,"volatility":4000,"liquidity":1,"audit_score":95,"age_days":700},
        "ekubo_metrics": {"utilization":5500,"volatility":5700,"liquidity":2,"audit_score":95,"age_days":700}
      }'
```

3) Inspect proof jobs (backend truth):
```bash
curl http://localhost:8001/api/v1/analytics/rebalance-history | jq .
curl http://localhost:8001/api/v1/analytics/proof-summary | jq .
```
Fields to check:
- `status` (SUBMITTED/FAILED/VERIFIED) — currently SUBMITTED because Integrity/Atlantic is not active.
- `proof_hash`, `fact_hash` (mock if LuminAIR mock), `tx_hash` (on-chain invoke), `error` (if verification failed), `proof_source` (luminair/luminair_mock).

## What this proves today
- Agent inputs → LuminAIR proof (mock or real stwo) → stored proof job → transaction executed on Starknet (Sepolia) → proof job status visible via API/UI.
- UI can display proof source + errors; no silent PENDING.

## What is *not* covered (pending)
- **Integrity/Atlantic verification**: requires a Stone/Atlantic proof of the risk circuit and credits. Until then, `l2_verified_at`/`l1_verified_at` stay null.
- **L1 fact registration**: blocked on Atlantic credits and a Stone proof.

## Next steps to upgrade the demo
- Swap the mock fact for a real Stone/Atlantic fact once credits land: submit the risk program/pie to Atlantic, run `proof_serializer`, call `verify_proof_full_and_register_fact`, then re-run the demo to see VERIFIED status and fact hashes.
- Add a “proof source” badge in the UI integration panel to differentiate luminair vs stone/atlantic lanes.

