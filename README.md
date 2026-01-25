# Obsqura — Verifiable AI Execution Layer for DeFi

**AI execution you can *prove* followed the rules (STARK proofs, optional L1 settlement via SHARP)**

Obsqura turns “trust me, the agent respected constraints” into “here’s the proof.”

---

## What you get

- **Constraint-proofed decisions**: every allocation / execution decision can come with a **STARK proof** that it complied with DAO/user-defined constraints.
- **Verify before you execute**: proofs can be verified locally *prior* to sending the transaction.
- **Clear audit trail**: metrics → scores → allocation → proof hash → tx hash.

## Why it matters

DeFi agents are powerful and dangerous: if the policy is violated, losses are real. Obsqura makes the *policy enforcement verifiable*, not just promised.

## How it works (high level)

```
Constraints + Inputs
        ↓
	Risk engine proposes allocation (deterministic scoring)
        ↓
Generate STARK proof (constraint adherence)
        ↓
Verify locally (pre-execution)
        ↓
Execute transaction
        ↓
	(Optional) submit to SHARP → anchor fact hash on Ethereum (L1)
```

## Live system (V1.2)

- **API**: `https://starknet.obsqra.fi/api/v1/proofs/generate`
- **Current performance**: ~2–3s proof generation (production)

## Try it (local)

### 1) Run the backend

```bash
cd backend
pip install -r requirements.txt

createdb obsqra
psql obsqra < migrations/001_initial.sql

cat > .env << EOF
DATABASE_URL=postgresql://obsqra:password@localhost/obsqra
STARKNET_RPC_URL=https://starknet-sepolia.public.blastapi.io
BACKEND_PRIVATE_KEY=0x...
BACKEND_ACCOUNT_ADDRESS=0x...
SHARP_GATEWAY_URL=https://sharp.starkware.co/api/v1
EOF

alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 8001
```

### 2) Generate a proof

```bash
curl -X POST http://localhost:8001/api/v1/proofs/generate \
  -H "Content-Type: application/json" \
  -d '{
    "jediswap_metrics": {"utilization":6500,"volatility":3500,"liquidity":1,"audit_score":98,"age_days":800},
    "ekubo_metrics":    {"utilization":5000,"volatility":2500,"liquidity":2,"audit_score":95,"age_days":600}
  }'
```

## Repo map

```
backend/    FastAPI API + proof jobs + workers
contracts/  Cairo contracts (risk engine / routing / constraints)
luminair/   Custom AIR/operator implementation
frontend/   Next.js UI
scripts/    Integration/testing scripts
```

## Start here (docs)

- [Architecture](ARCHITECTURE.md)
- [Production Deployment](PRODUCTION_LIVE.md)
- [SHARP Integration](SHARP_ARCHITECTURE.md)
- [LuminAIR Implementation Status](LUMINAIR_IMPLEMENTATION_STATUS.md)

## Contributing

PRs welcome. Keep changes small, add tests for behavior changes, and update docs when interfaces change.

## License

MIT — see [LICENSE](LICENSE)

## Links

- Repo: https://github.com/Obsqra-Labs/obsqra.starknet
- Issues: https://github.com/Obsqra-Labs/obsqra.starknet/issues
