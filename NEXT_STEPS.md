#  Starknet POC - Next Steps

You now have test ETH! Here's what to do next:

---

## ✅ **Phase 1: Test Basic Connectivity** (10 minutes)

### 1. Access the Frontend
- Open: http://localhost:3002
- You should see the Starknet dashboard

### 2. Connect Your Wallet
- Click **"Connect Argent X"** (or Braavos)
- Approve the connection
- Your imported test account should show ~1000 ETH

### 3. Verify Connection
- Check that your wallet address displays correctly
- Confirm you're on the **Local Katana** network
- Dashboard should show "Connected" status

---

## 🔨 **Phase 2: Deploy Real Contracts** (30 minutes)

Right now, the contracts are placeholders. Let's deploy real ones:

### 1. Compile Contracts
```bash
cd /opt/obsqra.starknet
scarb build
```

### 2. Check Contract Structure
```bash
ls -la target/dev/
```

### 3. Deploy Strategy (2 options)

**Option A: Quick Deploy with Starkli**
```bash
# Deploy RiskEngine
starkli declare target/dev/obsqra_starknet_RiskEngine.contract_class.json \
  --rpc http://localhost:5050 \
  --account <your_account>

# Deploy StrategyRouter
starkli declare target/dev/obsqra_starknet_StrategyRouter.contract_class.json \
  --rpc http://localhost:5050 \
  --account <your_account>
```

**Option B: Automated Deploy Script**
We'll create a proper deployment script with:
- Contract compilation
- Declaration
- Deployment
- Address saving to `.env.local`

### 4. Update Frontend Config
Once deployed, update `/opt/obsqra.starknet/frontend/.env.local` with real addresses.

---

## 🧪 **Phase 3: Test Contract Interactions** (30 minutes)

### 1. Test Risk Engine
- Call `calculate_allocation()` from the frontend
- Verify risk scores are calculated
- Check volatility metrics

### 2. Test Strategy Router
- Execute a strategy
- Verify routing logic
- Check gas estimates

### 3. Test DAO Constraints
- Set risk thresholds
- Verify constraint enforcement
- Test governance controls

---

## 🎨 **Phase 4: Enhance Frontend** (1-2 hours)

### Priority Improvements:
1. **Real-time Data**: Connect to live contract state
2. **Transaction Feedback**: Show pending/confirmed status
3. **Error Handling**: Better user messages for failed txs
4. **Portfolio View**: Show user's positions
5. **Strategy Visualization**: Charts for risk/return

---

## 🤖 **Phase 5: AI Integration** (1 hour)

Connect the AI service to provide:
- Risk recommendations
- Strategy suggestions
- Market analysis
- Portfolio optimization

### Update AI Service Endpoint
In `/opt/obsqra.starknet/frontend/.env.local`:
```
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
```

---

## 🧪 **Phase 6: End-to-End Testing** (1 hour)

### Test Scenarios:
1. **User Onboarding**: Connect wallet → View dashboard
2. **Risk Assessment**: Submit portfolio → Get allocation
3. **Strategy Execution**: Choose strategy → Execute on-chain
4. **DAO Voting**: Propose constraint → Vote → Execute
5. **Emergency Stop**: Test circuit breakers

---

## 🚢 **Phase 7: Deploy to Testnet** (2 hours)

When local testing is complete:

### 1. Configure Testnet
- Switch to Sepolia or Goerli
- Get testnet ETH from faucet
- Update RPC endpoints

### 2. Deploy Contracts
```bash
# Deploy to Starknet Sepolia
starkli declare <contract> --network sepolia
starkli deploy <class_hash> --network sepolia
```

### 3. Update Frontend
- Point to testnet contracts
- Update RPC to public endpoint
- Test with real testnet transactions

### 4. Verify on Explorer
- Check contracts on Voyager/Starkscan
- Verify source code
- Test transactions publicly

---

## 📊 **Current Status**

✅ **Completed:**
- Frontend running on port 3002
- Katana devnet running on port 5050
- CORS configured
- Test accounts with ETH
- Basic UI scaffolding
- Wallet integration (Argent X, Braavos)

⏳ **In Progress:**
- Real contract deployment
- Contract interaction from frontend

🔜 **Next Up:**
- Compile and deploy real contracts
- Test risk engine calculations
- Connect AI service

---

## 🛠️ **Quick Commands**

### Start All Services
```bash
# Terminal 1: Katana
cd /opt/obsqra.starknet
katana --dev --http.cors_origins "*"

# Terminal 2: Frontend
cd /opt/obsqra.starknet/frontend
PORT=3002 npm run dev

# Terminal 3: AI Service
cd /opt/obsqra.starknet/ai-service
AI_SERVICE_PORT=8001 python main.py
```

### Check Status
```bash
# Check running processes
ps aux | grep -E "(katana|next|python)" | grep -v grep

# Check ports
netstat -tlnp | grep -E "(3002|5050|8001)"

# Test connectivity
curl http://localhost:3002
curl http://localhost:5050
curl http://localhost:8001/health
```

### Rebuild Contracts
```bash
cd /opt/obsqra.starknet
scarb clean
scarb build
```

---

## 📝 **Documentation to Create**

1. **User Guide**: How to use the dApp
2. **Developer Guide**: How to extend functionality
3. **Contract Docs**: Function signatures and usage
4. **API Docs**: AI service endpoints
5. **Deployment Guide**: Mainnet deployment checklist

---

## 🎯 **Success Criteria**

By the end of development, you should have:

- ✅ Fully functional local testnet environment
- ✅ Deployed and tested smart contracts
- ✅ Working frontend with wallet integration
- ✅ AI-powered risk recommendations
- ✅ End-to-end transaction flow
- ✅ Ready for testnet deployment

---

## 🆘 **Need Help?**

- **Contracts not compiling?** Check Scarb version and Cairo syntax
- **Frontend errors?** Check browser console and RPC connection
- **Wallet not connecting?** Verify network settings and CORS
- **Transactions failing?** Check gas fees and account balance

---

**Ready to start? Let's deploy those contracts! **
