# Getting Started with Obsqra.starknet

Quick start guide for developers.

## Prerequisites

Install required tools:

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Scarb (Cairo package manager)
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python 3.10+
sudo apt-get install python3.10 python3-pip
```

## Setup

### 1. Contracts

```bash
cd contracts
scarb build
snforge test
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. AI Service

```bash
cd ai-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Development Workflow

1. **Contracts**: Edit `.cairo` files in `contracts/src/`, run `scarb build` and `snforge test`
2. **Frontend**: Edit React components in `frontend/src/`, run `npm run dev`
3. **AI Service**: Edit Python files in `ai-service/`, restart the service

## Testing

```bash
# Contract tests
cd contracts && snforge test

# Integration tests
./scripts/test_integration.sh
```

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## Next Steps

- Read [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for the 12-week implementation plan
- Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Check [docs/API.md](docs/API.md) for API reference


