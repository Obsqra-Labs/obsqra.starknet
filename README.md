# Obsqra.starknet

**Verifiable AI Infrastructure for Private DeFi Capital Routing on Starknet**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Obsqra.starknet is a Starknet MVP/POC demonstrating verifiable AI infrastructure for private DeFi capital routing. This project showcases:

- **On-chain AI computation** (Cairo) vs off-chain Python
- **Automatic proving** via SHARP (no validator network needed)
- **Privacy integration** with MIST.cash SDK
- **End-to-end flow**: deposit → AI rebalance → withdraw

## Key Features

- ✅ **Cairo Risk Engine** - On-chain risk scoring and allocation calculation
- ✅ **MIST.cash Privacy** - Private deposits and withdrawals
- ✅ **Strategy Router** - Multi-protocol routing and rebalancing
- ✅ **DAO Constraints** - On-chain governance enforcement
- ✅ **Simplified Frontend** - User-friendly dashboard

## Quick Start

### Prerequisites

- Rust 1.70+
- Cairo 2.0+
- Scarb 2.0+
- Node.js 18+
- Python 3.10+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/obsqra.starknet.git
cd obsqra.starknet

# Set up Cairo contracts
cd contracts
scarb build

# Set up frontend
cd ../frontend
npm install

# Set up AI service
cd ../ai-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Development

```bash
# Build contracts
cd contracts && scarb build

# Run tests
cd contracts && snforge test

# Start frontend
cd frontend && npm run dev

# Start AI service
cd ai-service && python main.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              MIST.cash Privacy Layer                    │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          Cairo Contracts (On-Chain AI)                  │
│  • RiskEngine.cairo                                     │
│  • StrategyRouter.cairo                                 │
│  • DAOConstraintManager.cairo                           │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              SHARP (Automatic Proving)                  │
└─────────────────────────────────────────────────────────┘
```

## Documentation

- **[Project Plan](docs/PROJECT_PLAN.md)** - Complete 12-week implementation plan
- **[Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)** - Step-by-step instructions
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture details
- **[API Documentation](docs/API.md)** - API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Deployment procedures

## Project Status

**Current Phase:** Setup & Planning  
**Target:** Production-ready POC for Grant Application  
**Timeline:** 12 weeks  

## Contributing

This is an active development project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details

## Disclaimer

This software is provided for educational and experimental purposes only. It has NOT been professionally audited. Use at your own risk.

## Contact

- Website: [obsqra.fi](https://obsqra.fi)
- Twitter: [@obsqra](https://twitter.com/obsqra)
- GitHub: [github.com/obsqra](https://github.com/obsqra)

---

**Built for accessibility by Obsqra Labs**
