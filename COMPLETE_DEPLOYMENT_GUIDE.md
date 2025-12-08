#  Complete Deployment Guide - Sepolia Testnet

## ✅ Current Status
- Your wallet: `0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027`
- Network: Starknet Sepolia Testnet
- Frontend: http://localhost:3002 (running)
- ⚠️ **IMPORTANT:** You need **STRK tokens** (not ETH) for gas fees on Starknet!

## 🪙 Step 0: Get STRK Tokens First!

**Before deploying, you need Sepolia STRK tokens for gas fees.**

Visit any of these faucets:
- https://starknet-faucet.vercel.app/
- https://blastapi.io/faucets/starknet-sepolia  
- https://www.alchemy.com/faucets/starknet-sepolia

See `/opt/obsqra.starknet/GET_STRK_TOKENS.md` for detailed instructions.

**Verify you have STRK:**
```bash
starkli balance 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7
```

## 🎯 Goal
Deploy your 3 Cairo contracts to Sepolia and connect them to the frontend.

---

## 📦 Step 1: Install Tools (5 minutes)

### Install Scarb (Cairo compiler)
```bash
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
scarb --version  # Should show version 2.x.x
```

### Install Starkli (Deployment tool)
```bash
curl https://get.starkli.sh | sh
starkliup
export PATH="$HOME/.starkli/bin:$PATH"
starkli --version  # Should show version
```

---

## 🔨 Step 2: Compile Contracts (2 minutes)

```bash
cd /opt/obsqra.starknet/contracts
scarb build
```

**Expected output:**
```
Compiling obsqra_contracts v0.1.0
   Finished release target(s) in X seconds
```

**Verify files were created:**
```bash
ls -la target/dev/*.contract_class.json
```

You should see:
- `obsqra_contracts_RiskEngine.contract_class.json`
- `obsqra_contracts_StrategyRouter.contract_class.json`
- `obsqra_contracts_DAOConstraintManager.contract_class.json`

---

## 🔑 Step 3: Setup Deployer Account (3 minutes)

### Create wallet directory
```bash
mkdir -p ~/.starkli-wallets/deployer
```

### Fetch your account from Sepolia
```bash
starkli account fetch \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --output ~/.starkli-wallets/deployer/account.json
```

**Expected output:**
```
Account contract type identified as: OpenZeppelin
Description: OpenZeppelin account contract v0.x.x
Downloaded new account config file: ~/.starkli-wallets/deployer/account.json
```

### Create keystore with your private key
```bash
starkli signer keystore from-key ~/.starkli-wallets/deployer/keystore.json
```

**You'll be prompted:**
1. **Enter private key:** Get this from Argent X (Settings → Export Private Key)
2. **Enter password:** Create a password for this keystore (remember it!)

---

##  Step 4: Deploy RiskEngine (5 minutes)

### Declare the contract
```bash
starkli declare \
  /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**Output will be:**
```
Declaring contract...
Class hash declared: 0x1234567890abcdef...
```

**📝 COPY THE CLASS HASH!**

### Deploy the contract
```bash
starkli deploy \
  <PASTE_CLASS_HASH_HERE> \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**Output will be:**
```
Deploying contract...
Contract deployed: 0xabcdef1234567890...
```

**📝 SAVE THIS CONTRACT ADDRESS!**

---

##  Step 5: Deploy StrategyRouter (5 minutes)

### Declare
```bash
starkli declare \
  /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouter.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**📝 COPY CLASS HASH**

### Deploy
```bash
starkli deploy \
  <STRATEGY_ROUTER_CLASS_HASH> \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**📝 SAVE CONTRACT ADDRESS**

---

##  Step 6: Deploy DAOConstraintManager (5 minutes)

### Declare
```bash
starkli declare \
  /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**📝 COPY CLASS HASH**

### Deploy
```bash
starkli deploy \
  <DAO_CLASS_HASH> \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**📝 SAVE CONTRACT ADDRESS**

---

## 📝 Step 7: Update Frontend Config (2 minutes)

Edit `/opt/obsqra.starknet/frontend/.env.local`:

```bash
cd /opt/obsqra.starknet/frontend
nano .env.local  # or use your preferred editor
```

**Replace with your deployed addresses:**
```env
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x<YOUR_RISK_ENGINE_ADDRESS>
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x<YOUR_STRATEGY_ROUTER_ADDRESS>
NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=0x<YOUR_DAO_CONSTRAINT_ADDRESS>
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
```

---

## 🔄 Step 8: Restart Frontend (1 minute)

```bash
pkill -f "PORT=3002"
cd /opt/obsqra.starknet/frontend
PORT=3002 npm run dev
```

---

## ✅ Step 9: Test! (5 minutes)

1. **Open:** http://localhost:3002
2. **Connect wallet** (Argent X on Sepolia)
3. **Try the dashboard features:**
   - Click "Update Allocation"
   - Should now work with real contracts!
   - Check transaction on Voyager

---

## 🔍 Verify Deployments

### View on Sepolia Explorer
```
https://sepolia.voyager.online/contract/<YOUR_CONTRACT_ADDRESS>
```

### Test contract call
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
Your account needs to be deployed on Sepolia first. Make a small transaction (like sending 0.001 ETH to yourself) to deploy it.

### "Insufficient fee" or "Insufficient balance"
Make sure you have enough **STRK tokens** (NOT ETH). Get more from these faucets:
- https://starknet-faucet.vercel.app/
- https://blastapi.io/faucets/starknet-sepolia
- https://www.alchemy.com/faucets/starknet-sepolia

### "Class already declared"
Someone else declared identical code. That's OK! Use the existing class hash returned in the error message.

### Compilation errors
```bash
cd /opt/obsqra.starknet/contracts
scarb check  # Check for errors
scarb clean  # Clean and rebuild
scarb build
```

---

## 📋 Deployment Checklist

- [ ] Scarb installed
- [ ] Starkli installed
- [ ] Contracts compiled
- [ ] Account fetched
- [ ] Keystore created
- [ ] RiskEngine declared & deployed
- [ ] StrategyRouter declared & deployed
- [ ] DAOConstraintManager declared & deployed
- [ ] Addresses saved
- [ ] .env.local updated
- [ ] Frontend restarted
- [ ] Connected wallet and tested
- [ ] Contracts verified on Voyager

---

## 📊 Expected Timeline

| Task | Time | Status |
|------|------|--------|
| Install tools | 5 min | ⏳ |
| Compile contracts | 2 min | ⏳ |
| Setup account | 3 min | ⏳ |
| Deploy RiskEngine | 5 min | ⏳ |
| Deploy StrategyRouter | 5 min | ⏳ |
| Deploy DAOConstraintManager | 5 min | ⏳ |
| Update frontend | 2 min | ⏳ |
| Test | 5 min | ⏳ |
| **Total** | **~30 min** | |

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ 3 live smart contracts on Sepolia
- ✅ Working frontend with real contract interactions
- ✅ Ability to test with testnet ETH
- ✅ Verifiable on-chain transactions
- ✅ A fully functional Starknet POC!

---

## 📝 Save Your Deployment Info

Create a file to track your deployment:

```bash
cat > /opt/obsqra.starknet/deployed-sepolia.json << EOF
{
  "network": "sepolia",
  "deployer": "0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
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
  }
}
EOF
```

---

**Ready to start? Run the deployment script:**

```bash
cd /opt/obsqra.starknet
chmod +x DEPLOY_TO_SEPOLIA.sh
./DEPLOY_TO_SEPOLIA.sh
```

Then follow the manual steps it provides! 
