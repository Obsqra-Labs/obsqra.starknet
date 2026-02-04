# Development Environment Setup

This guide covers development environment setup, prerequisites, repository structure, local development setup, and testing setup.

## Prerequisites

### Required Software

**1. Python 3.11+**
```bash
python3 --version  # Should be 3.11 or higher
```

**2. Node.js 18+**
```bash
node --version  # Should be 18 or higher
npm --version
```

**3. Scarb (Cairo Package Manager)**
```bash
scarb --version  # Should be 2.x
```

**4. PostgreSQL**
```bash
psql --version  # Should be 12 or higher
```

**5. Git**
```bash
git --version
```

### Optional but Recommended

**1. Stone Prover Binary**
- For local proof generation
- Download from StarkWare
- Place in PATH or configure path

**2. Docker (Optional)**
- For containerized development
- For local Starknet node (Katana)

## Repository Structure

```
obsqra.starknet/
├── backend/                 # Python/FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   ├── models.py       # Database models
│   │   └── config.py       # Configuration
│   ├── requirements.txt     # Python dependencies
│   └── main.py             # Application entry
├── contracts/              # Cairo smart contracts
│   ├── src/
│   │   ├── risk_engine.cairo
│   │   ├── strategy_router_v3_5.cairo
│   │   ├── model_registry.cairo
│   │   └── ...
│   └── Scarb.toml          # Cairo dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities
│   └── package.json
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/Obsqra-Labs/obsqra.starknet.git
cd obsqra.starknet
```

### 2. Backend Setup

**Install Dependencies:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Database Setup:**
```bash
# Create database
createdb obsqra_db

# Run migrations (if available)
alembic upgrade head
```

**Environment Variables:**
```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost/obsqra_db
STARKNET_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
STARKNET_NETWORK=sepolia
RISK_ENGINE_ADDRESS=0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4
STRATEGY_ROUTER_ADDRESS=0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b
BACKEND_WALLET_ADDRESS=<your_wallet_address>
BACKEND_WALLET_PRIVATE_KEY=<your_private_key>
EOF
```

**Run Backend:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend Setup

**Install Dependencies:**
```bash
cd frontend
npm install
```

**Environment Variables:**
```bash
# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4
NEXT_PUBLIC_NETWORK=sepolia
EOF
```

**Run Frontend:**
```bash
npm run dev
# Visit http://localhost:3003
```

### 4. Contracts Setup

**Install Scarb:**
```bash
# Follow Scarb installation guide
# https://docs.swmansion.com/scarb/
```

**Build Contracts:**
```bash
cd contracts
scarb build
```

**Test Contracts:**
```bash
scarb test
```

## Testing Setup

### Backend Tests

**Run Tests:**
```bash
cd backend
pytest tests/
```

**Test Coverage:**
```bash
pytest --cov=app tests/
```

### Frontend Tests

**Run Tests:**
```bash
cd frontend
npm test
```

### Contract Tests

**Run Tests:**
```bash
cd contracts
scarb test
```

## Development Tools

### Recommended IDE

**VS Code Extensions:**
- Python extension
- Cairo extension (StarkWare)
- ESLint
- Prettier

### Debugging

**Backend:**
- VS Code debugger
- Python debugger (pdb)
- FastAPI debug mode

**Frontend:**
- React DevTools
- Next.js debug mode
- Browser DevTools

**Contracts:**
- Scarb build output
- Starknet.py debugging
- Contract event logs

## Common Issues

### Python Dependencies

**Issue:** Import errors
**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Database Connection

**Issue:** Connection refused
**Solution:**
- Check PostgreSQL is running
- Verify DATABASE_URL
- Check credentials

### RPC Connection

**Issue:** RPC errors
**Solution:**
- Check network connectivity
- Try different RPC endpoint
- Verify STARKNET_RPC_URL

## Next Steps

- **[Contract Development](02-contract-development.md)** - Cairo contract development
- **[Backend Development](03-backend-development.md)** - Python service development
- **[Frontend Development](04-frontend-development.md)** - Next.js component development

---

**Setup Summary:** Complete development environment with Python backend, Next.js frontend, Cairo contracts, and testing infrastructure.
