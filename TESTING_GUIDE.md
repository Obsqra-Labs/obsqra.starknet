# 🧪 Obsqra.starknet - Testing & User Guide

**Status:** ✅ **LIVE AND FULLY OPERATIONAL**  
**Last Updated:** December 5, 2025

---

## 🎯 Integration Test Results

```
✅ PASS - RPC Connectivity (Block: 3620245)
✅ PASS - Contract Deployment (All 3 contracts callable)
✅ PASS - AI Service (Healthy & Connected)
✅ PASS - Frontend (Running on port 3003)
✅ PASS - Environment Config (All vars configured)

🎉 5/5 TESTS PASSED - ALL SYSTEMS OPERATIONAL!
```

Run the full test suite yourself:

```bash
cd /opt/obsqra.starknet
python3 test_integration.py
```

---

##  Quick Start Guide

### For Developers

#### 1. **Check System Status**

```bash
# Run integration tests
python3 test_integration.py

# Check services
curl http://localhost:8001/health
curl http://localhost:3003
```

#### 2. **Access Services**

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3003 | Web UI for contract interaction |
| AI Service | http://localhost:8001 | Backend service & APIs |
| Health Check | http://localhost:8001/health | Service status |

#### 3. **View Deployed Contracts**

All three contracts are live on **Starknet Sepolia**:

```bash
# Verify deployment
python3 << 'EOF'
from starknet_py.net.full_node_client import FullNodeClient
import asyncio

async def verify():
    client = FullNodeClient(node_url="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7")
    
    contracts = {
        "RiskEngine": "0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80",
        "DAOConstraintManager": "0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856",
        "StrategyRouter": "0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a",
    }
    
    for name, addr in contracts.items():
        class_hash = await client.get_class_hash_at(addr)
        print(f"✅ {name}: {hex(class_hash)}")

asyncio.run(verify())
EOF
```

---

## 🎮 Testing the Frontend UI

### Prerequisites

1. **Install Wallet Extension**
   - [Argent X](https://www.argent.xyz/argent-x/) (Chrome/Firefox)
   - [Braavos](https://braavos.app/) (Chrome/Firefox)

2. **Configure Wallet for Sepolia**
   - Open wallet extension
   - Click network selector
   - Choose "Starknet Sepolia" or "Sepolia"

3. **Get Testnet STRK**
   - Visit https://starknet-faucet.vercel.app/
   - Connect wallet
   - Request testnet STRK (usually 0.1-1 STRK)

### Step-by-Step Testing

#### Step 1: Open Frontend

```
URL: http://localhost:3003
```

You should see:
- ✅ Title: "Obsqra.starknet"
- ✅ Subtitle: "Verifiable AI Infrastructure for Private DeFi"
- ✅ Two wallet buttons: "Argent X" and "Braavos"

#### Step 2: Connect Wallet

1. Click "Connect Argent X" or "Connect Braavos"
2. Approve connection in wallet extension
3. Grant permissions when prompted

Expected result:
- Page transitions to dashboard
- Shows "Connecting to wallet..." briefly
- Displays wallet address in top right
- Dashboard loads with contract data

#### Step 3: Explore Dashboard (When Connected)

Once wallet is connected, you'll see:

- **Risk Engine Section**
  - Current risk metrics
  - Risk levels for different strategies
  
- **Strategy Router Section**
  - Current allocation percentages
  - Strategy breakdown

- **DAO Constraints Section**
  - DAO-set limits
  - Current utilization

- **Disconnect Button**
  - Top right corner
  - To switch wallets or disconnect

#### Step 4: Test Read Operations

Once connected, the frontend will:

✅ **Automatically fetch** data from all three contracts  
✅ **Display** real-time risk engine data  
✅ **Show** current strategy allocation  
✅ **Render** DAO constraints

No wallet transactions needed for read operations (queries are free!).

---

## 🔍 Troubleshooting

### Issue: "Wallet Not Installed"

**Cause:** Wallet extension not installed or not enabled  
**Solution:**
1. Install Argent X or Braavos from official sources
2. Refresh page (Ctrl+R or Cmd+R)
3. Check browser console for errors: Press F12

### Issue: Wallet Connected but Dashboard Doesn't Load

**Cause:** Possibly wrong network or RPC issue  
**Solution:**
1. Check wallet is on "Sepolia" network
2. Check browser console (F12) for errors
3. Verify RPC is accessible:
   ```bash
   curl https://starknet-sepolia.public.blastapi.io -d '{"jsonrpc":"2.0","id":1,"method":"starknet_chainId","params":[]}'
   ```

### Issue: "Not enough STRK" or Gas Errors

**Cause:** Wallet doesn't have testnet STRK  
**Solution:**
1. Go to https://starknet-faucet.vercel.app/
2. Request more testnet STRK
3. Wait for transaction to confirm (~1 minute)
4. Refresh dashboard

### Issue: Block Explorer Shows "Not Deployed"

**Cause:** Indexer lag (normal!)  
**Solution:**
This is expected. The contracts ARE deployed. You can verify:

```bash
python3 test_integration.py
```

or directly:

```bash
python3 << 'EOF'
from starknet_py.net.full_node_client import FullNodeClient
import asyncio

async def check():
    client = FullNodeClient(node_url="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7")
    addr = "0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
    class_hash = await client.get_class_hash_at(addr)
    print(f"✅ Contract exists with class hash: {hex(class_hash)}")

asyncio.run(check())
EOF
```

### Issue: Frontend Shows Blank Page

**Cause:** Build or runtime error  
**Solution:**
1. Check frontend logs:
   ```bash
   tail -50 /root/.cursor/projects/opt-obsqra-starknet/terminals/7.txt
   ```
2. Check AI service:
   ```bash
   curl http://localhost:8001/health
   ```
3. Restart frontend:
   ```bash
   pkill -f "next dev"
   cd /opt/obsqra.starknet/frontend && npm run dev &
   ```

---

## 📊 Contract Details

### RiskEngine Contract

**Address:** `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80`

**Purpose:** Calculate risk metrics and verify constraints

**Key Functions:**
- `calculate_allocation()` - Compute risk-based allocation
- `verify_constraints()` - Validate strategy constraints
- `get_risk_score()` - Get current risk score

**View on Explorers:**
- Voyager: https://sepolia.voyager.online/contract/0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80
- Starkscan: https://sepolia.starkscan.co/contract/0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80

### StrategyRouter Contract

**Address:** `0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a`

**Purpose:** Route funds between strategies

**Key Functions:**
- `get_allocation()` - Current allocation percentages
- `update_allocation()` - Rebalance strategies
- Supports Starknet-native protocols:
  - Nostra (Lending)
  - zkLend (Lending)
  - Ekubo (DEX)

### DAOConstraintManager Contract

**Address:** `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856`

**Purpose:** Manage DAO-imposed constraints

**Key Functions:**
- `get_constraints()` - View current limits
- `set_constraints()` - DAO updates constraints
- Validates against strategy allocations

---

## 🛠️ Advanced: Running Tests Locally

### Unit Tests

```bash
cd /opt/obsqra.starknet/contracts
scarb test
```

### Integration Tests

```bash
cd /opt/obsqra.starknet
python3 test_integration.py
```

### Contract Tests

```bash
# Verify contract on-chain
python3 test_contracts.py
```

---

## 📚 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│         FRONTEND (Next.js)                          │
│         http://localhost:3003                       │
│  ┌──────────────────────────────────────────────┐   │
│  │ @starknet-react/core (Wallet Connection)     │   │
│  │ useRiskEngine, useStrategyRouter, useDAO     │   │
│  │ Dashboard Component                          │   │
│  └──────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────┘
                         │ HTTP/RPC
┌────────────────────────┴────────────────────────────┐
│         AI SERVICE (FastAPI)                        │
│         http://localhost:8001                       │
│  ┌──────────────────────────────────────────────┐   │
│  │ Starknet RPC Client (starknet.py)            │   │
│  │ Contract Interaction Layer                   │   │
│  │ Risk Calculation Engine                      │   │
│  └──────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────┘
                         │ RPC
┌────────────────────────┴────────────────────────────┐
│    STARKNET SEPOLIA (Public Network)               │
│  ┌────────────────────────────────────────────┐    │
│  │ RiskEngine Contract                        │    │
│  │ 0x008c3eff...3d80                          │    │
│  └────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────┐    │
│  │ StrategyRouter Contract                    │    │
│  │ 0x01fa59cf...53a                           │    │
│  └────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────┐    │
│  │ DAOConstraintManager Contract              │    │
│  │ 0x010a3e7d...c856                          │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Key Technology Stack

- **Frontend:** Next.js 14, @starknet-react/core, TailwindCSS
- **Backend:** FastAPI (Python), starknet.py
- **Blockchain:** Starknet (Cairo), Sepolia Testnet
- **Protocols:** Nostra, zkLend, Ekubo (Starknet-native)
- **Token:** STRK (Starknet native token)

---

## 🎯 What's Next?

1. ✅ **Deploy contracts** (Done)
2. ✅ **Set up frontend** (Done)
3. ✅ **Run integration tests** (Done)
4. 🔄 **Test with wallet** (User responsibility)
5. 📈 **Monitor on-chain activity** (View in Voyager/Starkscan)
6.  **Add write operations** (Coming next)

---

## 📞 Support & Resources

### Starknet Resources
- [Starknet Docs](https://docs.starknet.io)
- [Cairo Documentation](https://book.cairo-lang.org/)
- [Starknet by Example](https://starknet-by-example.com/)

### Testnet Faucet
- [Starknet Faucet](https://starknet-faucet.vercel.app/)

### Block Explorers
- [Voyager (Sepolia)](https://sepolia.voyager.online/)
- [Starkscan (Sepolia)](https://sepolia.starkscan.co/)

### Community
- [Starknet Discord](https://discord.gg/starknet)
- [Cairo Book](https://book.cairo-lang.org/)

---

**🎉 Congratulations! Your Obsqra.starknet deployment is ready for testing!**

Connect your wallet and explore the Verifiable AI Infrastructure for Private DeFi.

