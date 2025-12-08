# Obsqra.starknet MVP/POC

**Verifiable AI Infrastructure for Private DeFi on Starknet**

**LIVE ON STARKNET SEPOLIA** - Contracts deployed December 5, 2025

## 🌐 Deployed Contracts (Sepolia Testnet) - v2

| Contract | Address | Explorer |
|----------|---------|----------|
| **RiskEngine v2** | `0x0751c852...44d31` | [View on Starkscan](https://sepolia.starkscan.co/contract/0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31) |
| **StrategyRouterV2** | `0x0539d561...41d6` | [View on Starkscan](https://sepolia.starkscan.co/contract/0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6) |
| **DAOConstraintManager** | `0x010a3e7d...4c856` | [View on Starkscan](https://sepolia.starkscan.co/contract/0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856) |

> **Note:** v2 contracts include full on-chain AI orchestration and deposit/withdraw functionality. See [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md) for details.

Full deployment details: [`deployments/sepolia.json`](deployments/sepolia.json)

---

## Quick Start

### Prerequisites
- [Scarb](https://docs.swmansion.com/scarb/) 2.14.0+
- [Starknet Foundry](https://foundry-rs.github.io/starknet-foundry/) 0.53.0+
- Node.js 18+
- Python 3.10+

### Contracts
```bash
cd contracts
scarb build
snforge test
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

---

## Project Status

- ✅ **3 Cairo Contracts** - RiskEngine, StrategyRouter, DAOConstraintManager
- ✅ **Deployed to Sepolia** - Live on Starknet testnet
- ✅ **28 Unit Tests** - Comprehensive test suite
- ✅ **Next.js Frontend** - Starknet integration with starknet-react
- ✅ **FastAPI AI Service** - Contract client implemented
- ✅ **Starknet-Native Protocols** - Nostra, zkLend, Ekubo integration

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      OBSQRA PROTOCOL                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js)                                         │
│  └── starknet-react hooks                                   │
│      └── useRiskEngine, useStrategyRouter, useDAOConstraints│
├─────────────────────────────────────────────────────────────┤
│  AI Service (FastAPI)                                       │
│  └── Risk analysis, allocation optimization                 │
├─────────────────────────────────────────────────────────────┤
│  Cairo Contracts (Starknet Sepolia)                         │
│  ├── RiskEngine       → Risk scoring & allocation calc      │
│  ├── StrategyRouter   → Protocol routing (Nostra/zkLend/Ekubo)│
│  └── DAOConstraintManager → Governance constraints          │
├─────────────────────────────────────────────────────────────┤
│  Starknet Native Protocols                                  │
│  ├── Nostra    (Lending)                                    │
│  ├── zkLend    (Money Market)                               │
│  └── Ekubo     (DEX)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
obsqra.starknet/
├── contracts/              # Cairo smart contracts
│   ├── src/
│   │   ├── risk_engine.cairo
│   │   ├── strategy_router.cairo
│   │   └── dao_constraint_manager.cairo
│   ├── tests/
│   └── Scarb.toml
├── frontend/               # Next.js frontend
│   └── src/
│       ├── components/
│       └── hooks/          # Starknet hooks
├── ai-service/             # FastAPI AI service
├── deployments/            # Deployment configs
│   └── sepolia.json
├── scripts/                # Deployment scripts
├── docs/                   # Documentation
│   ├── DEV_LOG.md          # Development journey
│   └── IMPLEMENTATION_GUIDE.md
└── README.md
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [**Quick Reference**](docs/QUICK_REFERENCE.md) | ⚡ Common commands & workflows |
| [**Lessons Learned**](docs/LESSONS_LEARNED.md) | 🎓 Key insights from EVM → Starknet migration |
| [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md) |  Setup & deployment guide |
| [Dev Log](docs/DEV_LOG.md) | 📝 Development journey |
| [API Reference](docs/API.md) | 📚 Contract interfaces |
| [Starknet Protocols](docs/STARKNET_PROTOCOLS.md) | 🔗 Native protocol integration |
| [Architecture](docs/ARCHITECTURE.md) | 🏗️ System design |

---

## 🛠️ Development

### Testing
```bash
cd contracts
snforge test
```

### Declaring New Contracts
```bash
sncast --account deployer declare --contract-name <ContractName> --network sepolia
```

### Deploying
```bash
sncast --account deployer deploy --class-hash <CLASS_HASH> --arguments "<args>" --network sepolia
```

---

## 🔗 Resources

- [Starknet Documentation](https://docs.starknet.io)
- [Cairo Book](https://book.cairo-lang.org)
- [Starknet Foundry](https://foundry-rs.github.io/starknet-foundry/)
- [Starknet Compatibility Tables](https://docs.starknet.io/learn/cheatsheets/compatibility)

---

## 📝 License

MIT

---

**Built with Cairo on Starknet** 🔺
