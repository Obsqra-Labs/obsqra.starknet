# Obsqra.starknet AI Service

Python off-chain service for monitoring protocols and triggering rebalances.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

- STARKNET_NETWORK
- STARKNET_RPC_URL
- Contract addresses
- Service configuration

## Running

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /health` - Health check
- `POST /trigger-rebalance` - Trigger AI rebalancing
- `POST /accrue-yields` - Accrue yields from protocols

