# Obsqra.starknet Contracts

Cairo smart contracts for the Obsqra.starknet MVP/POC.

## Contracts

- **RiskEngine.cairo** - On-chain risk scoring and allocation calculation
- **StrategyRouter.cairo** - Multi-protocol routing and rebalancing
- **DAOConstraintManager.cairo** - Governance constraints and validation

## Building

```bash
scarb build
```

## Testing

```bash
snforge test
```

## Deployment

See [../scripts/deploy.sh](../scripts/deploy.sh) for deployment instructions.

