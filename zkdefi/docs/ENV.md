# zkde.fi environment variables

Copy these into `backend/.env` and `frontend/.env.local` (create files if missing). Do not commit `.env` or `.env.local`.

## Backend (`zkdefi/backend/.env`)

```bash
# RPC and prover
STARKNET_RPC_URL=https://starknet-sepolia.public.blastapi.io
OBSQRA_PROVER_API_URL=https://obsqra.fi/api/v1/prove
OBSQRA_API_KEY=

# Deployed contract addresses (Starknet Sepolia)
PROOF_GATED_AGENT_ADDRESS=
SELECTIVE_DISCLOSURE_ADDRESS=
CONFIDENTIAL_TRANSFER_ADDRESS=
GARAGA_VERIFIER_ADDRESS=

# Server
PORT=8003
```

## Frontend (`zkdefi/frontend/.env.local`)

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8003

# Deployed contract addresses (Starknet Sepolia)
NEXT_PUBLIC_PROOF_GATED_AGENT_ADDRESS=
NEXT_PUBLIC_SELECTIVE_DISCLOSURE_ADDRESS=
NEXT_PUBLIC_CONFIDENTIAL_TRANSFER_ADDRESS=
```

## Deployment script env (for `scripts/deploy_sepolia.sh`)

Set before running the deploy script (or in `.env` at repo root):

- `INTEGRITY_FACT_REGISTRY_ADDRESS` — Integrity fact registry on Sepolia (Obsqra prover submits proofs here).
- `ERC20_TOKEN_ADDRESS` — ERC20 token contract address on Sepolia.
- `ADMIN_ADDRESS` — Admin address for contracts (optional; deployer used if unset).
- `GARAGA_VERIFIER_ADDRESS` — Garaga Groth16 verifier address (required to deploy ConfidentialTransfer; deploy from `circuits/` first).

See [SETUP.md](SETUP.md) for deployment order and constructor calldata.
