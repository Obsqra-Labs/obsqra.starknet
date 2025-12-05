# Obsqra.starknet MVP/POC

**Verifiable AI Infrastructure for Private DeFi on Starknet**

## 🚀 Quick Start

### Contracts
```bash
cd contracts
scarb build
```

### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

### AI Service
```bash
cd ai-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 📊 Project Status

- ✅ **3 Cairo Contracts** - RiskEngine, StrategyRouter, DAOConstraintManager
- ✅ **28 Unit Tests** - Comprehensive test suite (578 lines)
- ✅ **Next.js Frontend** - Starknet integration ready
- ✅ **FastAPI AI Service** - Contract client implemented
- ✅ **14 Documentation Files** - Complete guides and analysis

## 📁 Structure

```
obsqra.starknet/
├── contracts/          # Cairo smart contracts
├── frontend/           # Next.js frontend
├── ai-service/        # FastAPI AI service
├── scripts/           # Deployment scripts
└── docs/              # Documentation
```

## 🔗 Links

- [Project Plan](docs/PROJECT_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Testing Strategy](docs/TESTING_STRATEGY.md)
- [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)

## 📝 Next Steps

1. Install dependencies (npm/pip)
2. Install snforge for testing
3. Deploy contracts to testnet
4. Configure environment variables
5. Run end-to-end tests

## 🎯 Goals

- On-chain AI computation (Cairo)
- Automatic proving (SHARP)
- Privacy integration (MIST.cash)
- End-to-end functionality

**Ready for development!** 🚀
