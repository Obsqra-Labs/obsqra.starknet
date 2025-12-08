#  Quick Start: Build & Deploy Your Starknet POC

## 📋 What You Have

✅ **3 Cairo Contracts Ready:**
- `RiskEngine` - Risk scoring & allocation calculations
- `StrategyRouter` - Strategy execution logic
- `DAOConstraintManager` - Governance constraints

✅ **Frontend:** Next.js + Starknet React on port 3002

✅ **AI Service:** FastAPI backend on port 8001

✅ **Your Wallet:** `0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027`

---

## 🎯 Option 1: Deploy to Sepolia (RECOMMENDED - You Have ETH!)

### Step 1: Install Tools

```bash
# Install Scarb (Cairo compiler)
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Install Starkli (Starknet CLI)
curl https://get.starkli.sh | sh
starkliup
export PATH="$HOME/.starkli/bin:$PATH"

# Verify installations
scarb --version
starkli --version
```

### Step 2: Compile Contracts

```bash
cd /opt/obsqra.starknet/contracts
scarb build
```

**You should see:**
```
Compiling obsqra_contracts v0.1.0
   Finished release target(s) in X seconds
```

**Output files:**
- `target/dev/obsqra_contracts_RiskEngine.contract_class.json`
- `target/dev/obsqra_contracts_StrategyRouter.contract_class.json`
- `target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json`

### Step 3: Setup Starkli Account

```bash
# Fetch your account from Sepolia
starkli account fetch \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --output ~/.starkli-wallets/deployer/account.json

# Import your private key (you'll need it from Argent X)
starkli signer keystore from-key ~/.starkli-wallets/deployer/keystore.json
# Enter your private key when prompted
```

### Step 4: Declare Contracts

```bash
cd /opt/obsqra.starknet/contracts

# Declare RiskEngine
starkli declare \
  target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# Save the class hash that's returned!
# Example: 0x1234...

# Declare StrategyRouter
starkli declare \
  target/dev/obsqra_contracts_StrategyRouter.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# Declare DAOConstraintManager
starkli declare \
  target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

### Step 5: Deploy Contracts

```bash
# Deploy RiskEngine (replace CLASS_HASH with the one from declare)
starkli deploy \
  <RISK_ENGINE_CLASS_HASH> \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# Save the contract address!

# Deploy StrategyRouter
starkli deploy \
  <STRATEGY_ROUTER_CLASS_HASH> \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# Deploy DAOConstraintManager
starkli deploy \
  <DAO_CONSTRAINT_MANAGER_CLASS_HASH> \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

### Step 6: Update Frontend

```bash
cd /opt/obsqra.starknet/frontend

# Create/update .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA

# Replace with your deployed addresses:
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x...
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x...
NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=0x...

NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
EOF

# Restart frontend
pkill -f "PORT=3002"
PORT=3002 npm run dev
```

### Step 7: Test!

1. Make sure your wallet is on **Sepolia testnet**
2. Go to http://localhost:3002
3. Connect your wallet
4. You should see your ETH balance
5. Try calling contract functions!

---

## 🎯 Option 2: Quick Test Without Deployment

Just want to see the UI work?

```bash
# Start frontend (if not running)
cd /opt/obsqra.starknet/frontend
PORT=3002 npm run dev

# Open browser
# http://localhost:3002

# Connect wallet (even with 0 ETH on Katana)
# Test UI components!
```

---

## 📝 Contract Addresses to Save

Create a file: `/opt/obsqra.starknet/deployed-addresses-sepolia.json`

```json
{
  "network": "sepolia",
  "rpc": "https://starknet-sepolia.public.blastapi.io/rpc/v0_7",
  "deployer": "0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027",
  "contracts": {
    "riskEngine": {
      "classHash": "0x...",
      "address": "0x..."
    },
    "strategyRouter": {
      "classHash": "0x...",
      "address": "0x..."
    },
    "daoConstraintManager": {
      "classHash": "0x...",
      "address": "0x..."
    }
  },
  "deployed_at": "2025-12-05T..."
}
```

---

## 🔍 Verify Deployments

### On Voyager (Sepolia Explorer)
https://sepolia.voyager.online/contract/<YOUR_CONTRACT_ADDRESS>

### Using Starkli
```bash
starkli call \
  <RISK_ENGINE_ADDRESS> \
  calculate_risk_score \
  100 50 75 80 365 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7
```

---

## 🆘 Troubleshooting

### "Account not found"
Your wallet needs to be deployed on Sepolia. Make a transaction first (even a self-transfer).

### "Insufficient balance"
Make sure you have testnet ETH on Sepolia. You mentioned you have faucet Stark there!

### "Class already declared"
That's OK! Someone else declared the same code. Use the existing class hash.

### Compilation errors
Check Cairo syntax. Run: `scarb check`

---

## 📚 Resources

- **Scarb Docs:** https://docs.swmansion.com/scarb
- **Starkli Docs:** https://book.starkli.rs
- **Starknet Book:** https://book.starknet.io
- **Sepolia Explorer:** https://sepolia.voyager.online

---

## ✅ Success Checklist

- [ ] Scarb installed
- [ ] Starkli installed
- [ ] Contracts compiled
- [ ] Contracts declared
- [ ] Contracts deployed
- [ ] Addresses saved
- [ ] Frontend .env.local updated
- [ ] Frontend restarted
- [ ] Wallet connected on Sepolia
- [ ] Contract calls working

**Once deployed, you'll have a fully functional Starknet POC!** 🎉
