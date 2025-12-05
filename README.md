# Obsqra.starknet MVP/POC

**Verifiable AI Infrastructure for Private DeFi on Starknet**

**LIVE ON STARKNET SEPOLIA** - Contracts deployed December 5, 2025

## 🌐 Deployed Contracts (Sepolia Testnet)

| Contract | Address | Explorer |
|----------|---------|----------|
| **RiskEngine** | `0x008c3eff...7a3d80` | [View on Starkscan](https://sepolia.starkscan.co/contract/0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80) |
| **DAOConstraintManager** | `0x010a3e7d...4c856` | [View on Starkscan](https://sepolia.starkscan.co/contract/0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856) |
| **StrategyRouter** | `0x01fa59cf...df53a` | [View on Starkscan](https://sepolia.starkscan.co/contract/0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a) |

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
| [Dev Log](docs/DEV_LOG.md) | Development journey & lessons learned |
| [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md) | Setup & deployment guide |
| [Architecture](docs/ARCHITECTURE.md) | System design |
| [API Reference](docs/API.md) | Contract interfaces |
| [Starknet Protocols](docs/STARKNET_PROTOCOLS.md) | Native protocol integration |

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
