# 🏗️ Starknet POC Build Roadmap

## ✅ Completed
- [x] Frontend setup (Next.js + Starknet React)
- [x] Wallet integration (Argent X, Braavos)
- [x] Basic UI/UX
- [x] CORS setup for local development
- [x] AI service backend
- [x] Cairo contract structure

## 🔨 Current Phase: Contract Deployment

### 1. Compile Cairo Contracts (15 min)
```bash
cd /opt/obsqra.starknet/contracts
scarb build
```

**Contracts to build:**
- `RiskEngine` - Portfolio risk calculations
- `StrategyRouter` - Strategy execution
- `DAOConstraintManager` - Governance constraints

### 2. Create Deployment Scripts (30 min)
- [ ] Setup account configuration
- [ ] Create declare scripts
- [ ] Create deploy scripts
- [ ] Save deployed addresses
- [ ] Update frontend .env.local

### 3. Deploy to Sepolia Testnet (20 min)
(You already have testnet ETH here!)

```bash
# Deploy to Sepolia
cd /opt/obsqra.starknet/scripts
./deploy-testnet.sh
```

### 4. Update Frontend (10 min)
- [ ] Update .env.local with deployed addresses
- [ ] Point to Sepolia RPC
- [ ] Test contract interactions

### 5. Implement Contract Calls (1-2 hours)
- [ ] `useRiskEngine` - Call calculate_allocation()
- [ ] `useStrategyRouter` - Execute strategies
- [ ] `useDAOConstraints` - Check/update constraints
- [ ] Add transaction feedback UI

## 🎨 Next Phase: Enhanced Features

### 6. AI Integration (1 hour)
- [ ] Connect AI service to frontend
- [ ] Real-time risk recommendations
- [ ] Strategy suggestions based on portfolio

### 7. Dashboard Enhancements (2 hours)
- [ ] Real-time portfolio tracking
- [ ] Transaction history
- [ ] Risk score visualization
- [ ] Strategy performance charts

### 8. Testing & Polish (2 hours)
- [ ] End-to-end flow testing
- [ ] Error handling
- [ ] Loading states
- [ ] Success/failure notifications
- [ ] Mobile responsiveness

## 🚢 Final Phase: Production Ready

### 9. Security Audit
- [ ] Contract review
- [ ] Frontend security
- [ ] API security

### 10. Documentation
- [ ] User guide
- [ ] Developer docs
- [ ] API documentation
- [ ] Deployment guide

### 11. Mainnet Deployment
- [ ] Final testing on testnet
- [ ] Deploy to Starknet mainnet
- [ ] Verify contracts
- [ ] Launch!

---

## 🎯 Immediate Next Steps (Start Here!)

**Today's Focus: Get Contracts Deployed to Sepolia**

1. **Compile Contracts**
   ```bash
   cd /opt/obsqra.starknet/contracts
   scarb build
   ```

2. **Setup Deployment Account**
   ```bash
   # Create account for Sepolia
   starkli account fetch <your-address> \
     --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7
   ```

3. **Deploy Contracts**
   ```bash
   cd /opt/obsqra.starknet/scripts
   ./deploy-testnet.sh
   ```

4. **Update Frontend**
   - Edit `.env.local`
   - Add deployed contract addresses
   - Test on Sepolia

---

## 📊 Time Estimates

| Phase | Time | Priority |
|-------|------|----------|
| Contract Compilation | 15 min | 🔴 Critical |
| Deployment Scripts | 30 min | 🔴 Critical |
| Deploy to Sepolia | 20 min | 🔴 Critical |
| Update Frontend | 10 min | 🔴 Critical |
| Contract Interactions | 2 hours | 🟡 High |
| AI Integration | 1 hour | 🟢 Medium |
| Dashboard Polish | 2 hours | 🟢 Medium |
| Testing | 2 hours | 🟡 High |

**Total Time to Working POC: ~4-5 hours**

---

## 🆘 Blockers to Resolve Later

- [ ] Katana local ETH funding (documented in ETH_FUNDING_NOTES.md)
- [ ] Starknet.py AccountClient compatibility warning

These don't block progress - we can test on Sepolia!
