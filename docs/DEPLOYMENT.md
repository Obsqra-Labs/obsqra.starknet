# Obsqra.starknet Deployment Guide

**Version:** 1.0  
**Date:** December 2025

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Contracts verified
- [ ] Documentation complete
- [ ] Security review done
- [ ] Performance acceptable
- [ ] User guides ready
- [ ] Community announcement prepared

## Deployment Steps

### 1. Deploy Contracts

```bash
cd /opt/obsqra.starknet
./scripts/deploy.sh testnet
```

This will:
- Deploy RiskEngine.cairo
- Deploy StrategyRouter.cairo
- Deploy DAOConstraintManager.cairo
- Save contract addresses to `.env.deployed`

### 2. Verify Contracts

```bash
./scripts/verify.sh $CONTRACT_ADDRESS $CONTRACT_NAME
```

### 3. Update Environment Variables

Update `.env` with deployed contract addresses:

```bash
RISK_ENGINE_ADDRESS=0x...
STRATEGY_ROUTER_ADDRESS=0x...
DAO_CONSTRAINT_MANAGER_ADDRESS=0x...
```

### 4. Deploy Frontend

```bash
cd frontend
npm run build
npm run deploy
```

### 5. Start AI Service

```bash
cd ai-service
source venv/bin/activate
python main.py
```

## Post-Deployment

### Monitoring

- Contract events
- User activity
- Error logs
- Performance metrics

### Support

- Answer questions
- Fix bugs
- Gather feedback
- Iterate

## Troubleshooting

### Contract Deployment Fails

- Check RPC endpoint
- Verify account has funds
- Check contract compilation

### Frontend Not Connecting

- Verify contract addresses
- Check network configuration
- Verify RPC endpoint

### AI Service Not Responding

- Check service logs
- Verify Starknet connection
- Check environment variables

