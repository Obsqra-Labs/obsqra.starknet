# Obsqra.starknet POC/MVP - Next Steps Roadmap

**Current Status:** ✅ Frontend Working | ⏳ Contracts Not Deployed  
**Date:** December 5, 2025

---

## 🎯 Phase 1: Local Development Setup (1-2 hours)

### Step 1.1: Start Starknet Devnet
Set up a local Starknet node for testing.

```bash
# Option A: Use Katana (Dojo's Starknet devnet)
katana --accounts 10 --seed 0

# Option B: Use starknet-devnet-rs
starknet-devnet --seed 42 --port 5050 --accounts 10
```

**What it does:**
- Local Starknet blockchain
- Pre-funded test accounts
- Fast iteration without testnet fees

**Status Check:**
```bash
curl http://localhost:5050/is_alive
```

---

### Step 1.2: Compile Contracts
Build your Cairo contracts.

```bash
cd /opt/obsqra.starknet/contracts
scarb build
```

**Expected Output:**
```
Compiling obsqra_contracts v0.1.0
Finished release target(s) in 3.2s
```

**Artifacts Created:**
- `target/dev/obsqra_contracts_RiskEngine.contract_class.json`
- `target/dev/obsqra_contracts_StrategyRouter.contract_class.json`
- `target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json`

---

### Step 1.3: Deploy to Local Devnet
Deploy all contracts to your local network.

```bash
# Create deployment script
cd /opt/obsqra.starknet/scripts
```

**Create:** `deploy-local.sh`
```bash
#!/bin/bash
set -e

echo "Deploying Obsqra Contracts to Local Devnet..."

# Deploy RiskEngine
echo "Deploying RiskEngine..."
RISK_ENGINE=$(starkli declare target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --network http://localhost:5050 \
  --account ~/.starkli-wallets/account.json \
  --keystore ~/.starkli-wallets/keystore.json)

echo "RiskEngine deployed: $RISK_ENGINE"

# Deploy StrategyRouter
echo "Deploying StrategyRouter..."
STRATEGY_ROUTER=$(starkli declare target/dev/obsqra_contracts_StrategyRouter.contract_class.json \
  --network http://localhost:5050)

echo "StrategyRouter deployed: $STRATEGY_ROUTER"

# Save addresses
cat > ../deployed-addresses.json <<EOF
{
  "riskEngine": "$RISK_ENGINE",
  "strategyRouter": "$STRATEGY_ROUTER",
  "network": "devnet",
  "rpc": "http://localhost:5050"
}
EOF

echo "✅ Deployment complete! Addresses saved to deployed-addresses.json"
```

---

## 🎯 Phase 2: Configure Frontend (30 mins)

### Step 2.1: Create Environment File

**Create:** `/opt/obsqra.starknet/frontend/.env.local`
```bash
# Starknet Network
NEXT_PUBLIC_RPC_URL=http://localhost:5050
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA

# Contract Addresses (update after deployment)
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x...
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x...
NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=0x...

# MIST.cash Chamber (when available)
NEXT_PUBLIC_MIST_CHAMBER_ADDRESS=0x...

# API Endpoints
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
```

### Step 2.2: Update Contract ABIs

Extract ABIs from compiled contracts:
```bash
cd /opt/obsqra.starknet/contracts
scarb build
# ABIs will be in target/dev/*.contract_class.json
```

Copy to frontend:
```bash
mkdir -p /opt/obsqra.starknet/frontend/src/abis
cp target/dev/*.contract_class.json /opt/obsqra.starknet/frontend/src/abis/
```

### Step 2.3: Restart Frontend
```bash
# Kill and restart to pick up env vars
lsof -ti:3002 | xargs kill -9
cd /opt/obsqra.starknet/frontend
PORT=3002 npm run dev
```

---

## 🎯 Phase 3: Test Wallet Integration (30 mins)

### Step 3.1: Install Wallet Extension
- **Argent X:** https://www.argent.xyz/argent-x/
- **Braavos:** https://braavos.app/

### Step 3.2: Configure Wallet for Devnet
1. Open wallet extension
2. Add custom network:
   - Name: Local Devnet
   - RPC URL: http://localhost:5050
   - Chain ID: SN_SEPOLIA

### Step 3.3: Test Connection
1. Visit http://localhost:3002
2. Click "Connect Argent X" or "Connect Braavos"
3. Approve connection in wallet
4. Dashboard should appear

**Expected Result:**
- ✅ Wallet connected
- ✅ Address displayed in navbar
- ✅ Dashboard components visible

---

## 🎯 Phase 4: Implement Contract Interactions (2-3 hours)

### Step 4.1: Update Risk Engine Hook

**File:** `frontend/src/hooks/useRiskEngine.ts`

Add actual contract calls:
```typescript
import { useContract, useReadContract, useSendTransaction } from '@starknet-react/core';

export function useRiskEngine(contractAddress: string) {
  const { contract } = useContract({
    address: contractAddress,
    abi: RISK_ENGINE_ABI,
  });

  // Read risk score
  const { data: riskScore } = useReadContract({
    functionName: 'calculate_risk_score',
    args: [5000, 2000, 0, 95, 1000],
    address: contractAddress,
    abi: RISK_ENGINE_ABI,
  });

  // Write: Calculate allocation
  const { send: calculateAllocation } = useSendTransaction();

  const handleCalculateAllocation = async () => {
    const calls = [{
      contractAddress,
      entrypoint: 'calculate_allocation',
      calldata: [100, 150, 120, 500, 450, 400], // Example args
    }];
    
    await calculateAllocation({ calls });
  };

  return { riskScore, calculateAllocation: handleCalculateAllocation };
}
```

### Step 4.2: Test Contract Reads
1. Open browser console at http://localhost:3002
2. Should see risk score fetched from contract
3. Verify no errors in console

### Step 4.3: Test Contract Writes
1. Click "Calculate Allocation" button
2. Wallet popup should appear
3. Sign transaction
4. Wait for confirmation

---

## 🎯 Phase 5: Connect AI Service to Contracts (1-2 hours)

### Step 5.1: Fix Python Dependencies

**File:** `/opt/obsqra.starknet/ai-service/requirements.txt`
```txt
fastapi==0.104.1
uvicorn==0.24.0
starknet-py==0.23.0
python-dotenv==1.0.0
```

Reinstall:
```bash
cd /opt/obsqra.starknet/ai-service
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5.2: Update Contract Client

**File:** `ai-service/contract_client.py`
```python
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract

class ContractClient:
    def __init__(self):
        self.client = FullNodeClient(node_url="http://localhost:5050")
        # Load from config or env
        
    async def get_risk_score(self, params):
        # Call RiskEngine.calculate_risk_score
        pass
        
    async def trigger_rebalance(self, allocation):
        # Call StrategyRouter.rebalance
        pass
```

### Step 5.3: Test AI → Contract Flow
```bash
# Restart AI service
lsof -ti:8001 | xargs kill -9
cd /opt/obsqra.starknet/ai-service
AI_SERVICE_PORT=8001 ./venv/bin/python3 main.py

# Test endpoint
curl -X POST http://localhost:8001/trigger-rebalance
```

---

## 🎯 Phase 6: Deploy to Sepolia Testnet (1 hour)

### Step 6.1: Get Testnet ETH
1. Visit Starknet Sepolia Faucet: https://faucet.goerli.starknet.io/
2. Request testnet ETH
3. Wait for confirmation

### Step 6.2: Create Deployer Account
```bash
# Create account
starkli account oz init ~/.starkli-wallets/account.json

# Deploy account
starkli account deploy ~/.starkli-wallets/account.json \
  --keystore ~/.starkli-wallets/keystore.json \
  --network sepolia
```

### Step 6.3: Deploy to Sepolia
```bash
cd /opt/obsqra.starknet/contracts
scarb build

# Deploy with sncast
sncast --profile my_testnet deploy \
  --class-hash <RISK_ENGINE_CLASS_HASH>
```

### Step 6.4: Update Frontend Config
Update `.env.local` with Sepolia addresses and RPC:
```
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=<deployed_address>
```

---

## 📋 Priority Order (What to Do Right Now)

### ⭐ Immediate (Today)
1. **Start Katana/Devnet** → Test local blockchain
2. **Compile Contracts** → `scarb build`
3. **Deploy Locally** → Get contract addresses
4. **Update .env.local** → Configure frontend
5. **Test Wallet Connection** → Verify Argent X/Braavos

### 🎯 Short Term (This Week)
6. **Fix Contract Interactions** → Wire up reads/writes
7. **Test End-to-End Flow** → Wallet → Frontend → Contract
8. **Update AI Service** → Fix starknet_py imports
9. **Test AI → Contract** → Automated rebalancing

### 🚀 Medium Term (Next Week)
10. **Deploy to Sepolia Testnet**
11. **Public Demo**
12. **Security Review**
13. **Documentation**

---

## 🛠️ Quick Start Commands

```bash
# 1. Start local devnet (Terminal 1)
katana --accounts 10

# 2. Compile contracts (Terminal 2)
cd /opt/obsqra.starknet/contracts && scarb build

# 3. Start frontend (Terminal 3)
cd /opt/obsqra.starknet/frontend && PORT=3002 npm run dev

# 4. Start AI service (Terminal 4)
cd /opt/obsqra.starknet/ai-service && AI_SERVICE_PORT=8001 ./venv/bin/python3 main.py

# 5. Open browser
# http://localhost:3002
```

---

## 📚 Useful Resources

- **Starknet Book:** https://book.starknet.io/
- **Cairo by Example:** https://cairo-by-example.com/
- **Starknet React Docs:** https://starknet-react.com/
- **Starkli Docs:** https://book.starkli.rs/
- **Scarb Docs:** https://docs.swmansion.com/scarb/

---

## ❓ Troubleshooting

### Issue: Wallet won't connect
- Check devnet is running on port 5050
- Verify RPC URL in wallet settings
- Try refreshing page and reconnecting

### Issue: Contract calls fail
- Verify contract addresses in .env.local
- Check account has testnet ETH
- Review transaction in block explorer

### Issue: AI service errors
- Check starknet_py version compatibility
- Verify contract addresses in config
- Review logs: `tail -f /tmp/starknet-ai.log`

---

**Next Command to Run:**
```bash
# Start with local devnet
katana --accounts 10 --seed 0
```

Then let me know when it's running, and we'll deploy the contracts! 🚀
