# Obsqura: Autonomous Yield Optimization with Verifiable AI

**Transparent, auditable, and constraint-governed yield optimization protocol on Starknet**

## Overview

Obsqura implements an autonomous yield optimization system where AI-driven allocation decisions are executed on-chain with full transparency and governance oversight. The protocol combines on-chain risk assessment, verifiable computation, and DAO-configurable constraints to ensure automated strategies remain within acceptable risk parameters.

## Key Features

- **Autonomous Execution**: Backend service signs and submits allocation decisions without manual intervention
- **On-Chain Risk Assessment**: All risk calculations performed in Cairo contracts on Starknet
- **DAO Governance**: Configurable constraints ensure decisions remain within approved bounds
- **Complete Audit Trail**: Every decision recorded on-chain with cryptographic proofs
- **Multi-Protocol Support**: Integration with JediSwap and Ekubo (extensible to additional protocols)

## Architecture

```
Frontend (Next.js) → Backend API (FastAPI) → Starknet Contracts (Cairo)
                                               ├─ RiskEngine
                                               ├─ StrategyRouterV2  
                                               └─ DAOConstraintManager
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Deployed Contracts

### Starknet Sepolia Testnet

| Contract | Address |
|----------|---------|
| RiskEngine v2 | `0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31` |
| StrategyRouterV2 | `0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6` |
| DAOConstraintManager | `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` |

Explorer: [View on Starkscan](https://sepolia.starkscan.co/contract/0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Starknet Foundry (snforge, sncast)
- Scarb 2.14.0+

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with contract addresses and wallet configuration

# Start service
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with contract addresses

# Development
npm run dev

# Production
npm run build
npm start
```

### Contract Development

```bash
cd contracts
scarb build
snforge test
```

## API Documentation

### Orchestrate Allocation

**Endpoint**: `POST /api/v1/risk-engine/orchestrate-allocation`

Executes an autonomous allocation decision based on current protocol metrics.

**Request**:
```json
{
  "jediswap_metrics": {
    "utilization": 6500,
    "volatility": 3500,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800
  },
  "ekubo_metrics": {
    "utilization": 5200,
    "volatility": 2800,
    "liquidity": 2,
    "audit_score": 95,
    "age_days": 400
  }
}
```

**Response**:
```json
{
  "decision_id": 1,
  "block_number": 12345,
  "timestamp": 1702000000,
  "jediswap_pct": 6000,
  "ekubo_pct": 4000,
  "jediswap_risk": 35,
  "ekubo_risk": 28,
  "rationale_hash": "0x...",
  "strategy_router_tx": "0x...",
  "message": "Decision executed successfully"
}
```

See full API documentation in [ARCHITECTURE.md](ARCHITECTURE.md).

## Project Structure

```
.
├── contracts/          # Cairo smart contracts
│   ├── src/
│   │   ├── risk_engine.cairo
│   │   ├── strategy_router_v2.cairo
│   │   └── dao_constraint_manager.cairo
│   └── tests/
├── backend/            # Python FastAPI service
│   ├── app/
│   │   ├── api/
│   │   ├── ml/
│   │   └── config.py
│   └── main.py
├── frontend/           # Next.js application
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── app/
│   └── public/
└── scripts/            # Deployment and utility scripts
```

## Development Workflow

### Contract Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Testing

```bash
# Contract tests
cd contracts && snforge test

# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

### Code Quality

```bash
# Cairo formatting
scarb fmt

# Python linting
cd backend && pylint app/

# TypeScript type checking
cd frontend && npm run type-check
```

## Security

### Access Control

- RiskEngine owner: Controls execution authority
- StrategyRouter owner: Manages protocol integrations
- DAO governance: Configures operational constraints

### Audit Trail

All decisions recorded on-chain with:
- Sequential decision ID
- Block number and timestamp
- Input metrics and calculated risks
- Allocation percentages
- Cryptographic proof hash

### Fund Security

- No custody of user funds by backend service
- All fund movements through audited contracts
- DAO constraint validation at contract level

## Roadmap

### Current Implementation (V1.2)

- On-chain risk assessment and allocation
- Autonomous backend execution
- DAO constraint validation
- Complete audit trail
- Governance interface

### Planned Features

1. **Zero-Knowledge Machine Learning**
   - Cairo ML model implementation
   - SHARP proof generation
   - Verifiable off-chain computation

2. **Enhanced Governance**
   - Multi-signature controls
   - Timelocks for parameter changes
   - Community voting mechanisms

3. **Protocol Expansion**
   - Additional DeFi protocol integrations
   - Cross-chain optimization
   - Advanced rebalancing strategies

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) for details

## Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Contract Migration Notes](CONTRACT_MIGRATION_V2.md)
- [Starknet Documentation](https://docs.starknet.io)
- [Cairo Book](https://book.cairo-lang.org)

## Contact

- GitHub: https://github.com/obsqra-labs
- Issues: https://github.com/obsqra-labs/obsqra.starknet/issues

---

Built on Starknet with Cairo for verifiable computation and SHARP for zero-knowledge proofs.
