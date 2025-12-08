# Risk Engine Integration - Backend-Driven Architecture

**Date:** December 7, 2025  
**Status:** ✅ Live and Ready for Testing  
**Architecture:** Frontend → Backend → Starknet RPC → Risk Engine Contract

---

## Overview

The Risk Engine integration now properly separates frontend UI from contract interaction:

### **Before (❌ Issues)**
- Frontend tried to call Risk Engine contract directly
- Needed provider from wallet connection
- Type safety issues with Starknet.js
- Complex error handling in React hooks
- Mock SHARP proofs generated on frontend

### **After (✅ Clean)**
- **Frontend**: UI/UX only, calls REST API
- **Backend**: Handles all Starknet contract interactions
- **Contract**: Called via RPC by backend
- **No mocks**: Real contract calls, real results

---

## Architecture Diagram

```
┌─────────────────────┐
│   User Browser      │
│  https://starknet.  │
│  obsqra.fi          │
└──────────┬──────────┘
           │
           │ HTTP POST
           ↓
┌─────────────────────────────────────────┐
│  Frontend (Next.js)                     │
│                                         │
│  Dashboard.tsx                          │
│    └─ useRiskEngineBackend()           │
│        └─ fetch /api/v1/risk-engine/*  │
│                                         │
└──────────┬──────────────────────────────┘
           │ HTTP/REST
           │ /api/v1/risk-engine/
           │   - /calculate-risk
           │   - /calculate-allocation
           ↓
┌─────────────────────────────────────────┐
│  Backend (FastAPI + Python)             │
│  localhost:8001                         │
│                                         │
│  app/api/routes/risk_engine.py          │
│    ├─ POST /calculate-risk              │
│    │   └─ Contract.call()               │
│    │                                    │
│    └─ POST /calculate-allocation        │
│        └─ Contract.call()               │
│                                         │
│  Dependencies:                          │
│    - starknet_py 0.23.0                │
│    - FastAPI                            │
│                                         │
└──────────┬──────────────────────────────┘
           │ RPC Call
           │ (Starknet.py)
           ↓
┌─────────────────────────────────────────┐
│  Starknet Sepolia RPC                   │
│  publicnode.com                         │
│                                         │
│  Contract Address:                      │
│  0x008c3eff435e859e3b8e5cb12f837f4d    │
│  fa77af25c473fb43067adf9f557a3d80      │
│                                         │
└──────────┬──────────────────────────────┘
           │ Call Cairo contract
           ↓
┌─────────────────────────────────────────┐
│  Risk Engine Contract (Cairo)           │
│  Sepolia Testnet                        │
│                                         │
│  Functions:                             │
│    - calculate_risk_score()             │
│    - calculate_allocation()             │
│                                         │
│  Returns:                               │
│    - risk_score: felt252 (5-95)        │
│    - allocation: (jediswap%, ekubo%)   │
│                                         │
└─────────────────────────────────────────┘
```

---

## API Endpoints

### Calculate Risk Score

**Endpoint:** `POST /api/v1/risk-engine/calculate-risk`

**Request:**
```json
{
  "utilization": 6500,  // 65% in basis points
  "volatility": 3500,   // 35% in basis points
  "liquidity": 1,       // 0=High, 1=Medium, 2=Low, 3=VeryLow
  "audit_score": 98,    // 0-100
  "age_days": 800       // days since protocol launch
}
```

**Response:**
```json
{
  "score": 25,
  "category": "low",
  "description": "Low risk protocol - Safe for allocation"
}
```

---

### Calculate Allocation

**Endpoint:** `POST /api/v1/risk-engine/calculate-allocation`

**Request:**
```json
{
  "jediswap_risk": 25,    // risk score from calculate_risk_score()
  "ekubo_risk": 32,       // risk score from calculate_risk_score()
  "jediswap_apy": 850,    // 8.5% APY in basis points
  "ekubo_apy": 1210       // 12.1% APY in basis points
}
```

**Response:**
```json
{
  "jediswap_pct": 4800,   // 48% of capital
  "ekubo_pct": 5200       // 52% of capital
}
```

**Note:** Percentages are in basis points (10000 = 100%)

---

## Frontend Hook: `useRiskEngineBackend`

**Location:** `frontend/src/hooks/useRiskEngineBackend.ts`

**Usage:**
```typescript
const riskEngine = useRiskEngineBackend();

// Calculate single protocol risk
const jediswapRisk = await riskEngine.calculateRiskScore({
  utilization: 6500,
  volatility: 3500,
  liquidity: 1,
  auditScore: 98,
  ageDays: 800,
});

// Calculate optimal allocation
const allocation = await riskEngine.calculateAllocation(
  jediswapMetrics,
  ekuboMetrics,
  { jediswap: 850, ekubo: 1210 }
);

// Access results
console.log(riskEngine.lastAllocation);
console.log(riskEngine.error);
console.log(riskEngine.isLoading);
```

---

## Backend Implementation

**Location:** `backend/app/api/routes/risk_engine.py`

### Key Components

1. **RiskMetricsRequest** - Validates input metrics
2. **AllocationRequest** - Validates allocation inputs
3. **Risk Engine ABI** - Contract interface definition
4. **starknet_py Integration** - Contract calls via RPC

### How It Works

```python
# 1. Receive request from frontend
@router.post("/calculate-risk")
async def calculate_risk_score(request: RiskMetricsRequest):
    # 2. Create RPC client
    client = Client(node_url=settings.STARKNET_RPC_URL)
    
    # 3. Create contract instance
    contract = Contract(
        address=int(settings.RISK_ENGINE_ADDRESS, 16),
        abi=RISK_ENGINE_ABI,
        client=client
    )
    
    # 4. Call contract function
    result = await contract.functions["calculate_risk_score"].call(
        utilization=request.utilization,
        volatility=request.volatility,
        liquidity=request.liquidity,
        audit_score=request.audit_score,
        age_days=request.age_days,
    )
    
    # 5. Parse and validate result
    risk_score = int(result.risk_score)
    risk_score = max(5, min(95, risk_score))  # Clip to [5, 95]
    
    # 6. Return JSON response
    return RiskScoreResponse(...)
```

---

## Environment Configuration

### Backend (.env)
```bash
STARKNET_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
RISK_ENGINE_ADDRESS=0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_BACKEND_URL=https://starknet.obsqra.fi
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80
```

---

## Testing

### 1. Test Backend Directly

```bash
# Health check
curl http://localhost:8001/health

# Calculate risk
curl -X POST http://localhost:8001/api/v1/risk-engine/calculate-risk \
  -H "Content-Type: application/json" \
  -d '{
    "utilization": 6500,
    "volatility": 3500,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800
  }'

# Calculate allocation
curl -X POST http://localhost:8001/api/v1/risk-engine/calculate-allocation \
  -H "Content-Type: application/json" \
  -d '{
    "jediswap_risk": 25,
    "ekubo_risk": 32,
    "jediswap_apy": 850,
    "ekubo_apy": 1210
  }'
```

### 2. Test Frontend UI

1. Visit: https://starknet.obsqra.fi
2. Go to "Risk" tab
3. Click "Calculate Risk & Allocation"
4. Watch browser console for logs
5. Check browser Network tab for API calls

---

## Data Flow for Allocation Calculation

### Step 1: Frontend calls calculateAllocation()
```
Frontend → POST /api/v1/risk-engine/calculate-risk (JediSwap metrics)
           ↓ Response: { score: 25, category: "low", ... }
```

### Step 2: Backend calculates JediSwap risk
```
Backend → Starknet RPC → Risk Engine Contract.calculate_risk_score()
          ↓ Response: 25 (felt252)
```

### Step 3: Frontend calls calculateAllocation() again for Ekubo
```
Frontend → POST /api/v1/risk-engine/calculate-risk (Ekubo metrics)
           ↓ Response: { score: 32, category: "low", ... }
```

### Step 4: Backend calculates Ekubo risk
```
Backend → Starknet RPC → Risk Engine Contract.calculate_risk_score()
          ↓ Response: 32 (felt252)
```

### Step 5: Frontend calls allocation endpoint
```
Frontend → POST /api/v1/risk-engine/calculate-allocation
           { jediswap_risk: 25, ekubo_risk: 32, ... }
           ↓
```

### Step 6: Backend calculates allocation
```
Backend → Starknet RPC → Risk Engine Contract.calculate_allocation()
          ↓ Response: (4800, 5200) - JediSwap 48%, Ekubo 52%
```

### Step 7: Frontend receives allocation
```
Frontend: Sets lastAllocation = { jediswapPct: 4800, ekuboPct: 5200 }
          Displays in UI
          Adds to transaction history
```

---

## Error Handling

### Frontend Errors
- Network failure → Shows user message
- Backend HTTP error → Shows detailed error from API
- Missing metrics → Form validation catches it

### Backend Errors
- Contract call fails → Returns 500 with detail
- Invalid RPC → Returns 500 with detail
- Contract address invalid → Returns 500 with detail

---

## Dependencies Added

### Backend
- `starknet-py==0.23.0` - Starknet contract interaction

### Frontend
- No new dependencies (uses existing `fetch` API)

---

## Protocols on Testnet

**Currently Supported:**
- ✅ JediSwap (DEX)
- ✅ Ekubo (DEX)

**Not Supported (Mainnet Only):**
- ❌ Nostra (Lending)
- ❌ zkLend (Lending)
- ❌ MIST.cash (Privacy - coming later)

---

## What's Next

### 1. JediSwap Integration Contract
- Deploy wrapper to route STRK to JediSwap
- Implement `deposit()`, `withdraw()`, `get_yield()`

### 2. Ekubo Integration Contract
- Deploy wrapper to route STRK to Ekubo
- Implement `deposit()`, `withdraw()`, `get_yield()`

### 3. Strategy Router Integration
- Update Strategy Router to call wrappers
- Split deposits based on allocation percentages

### 4. Rebalancing
- Periodically call Risk Engine again
- Auto-move funds between protocols if needed

### 5. Auto-Compounding
- Track yield generation
- Reinvest gains automatically (DAO decision)

---

## Verification

To verify everything is working:

```bash
# 1. Check backend is running
curl -s http://localhost:8001/health | python -m json.tool

# 2. Check frontend is running
curl -s -I http://localhost:3003 | head -1

# 3. Check Risk Engine contract exists on Sepolia
# Visit: https://sepolia.starkscan.co/contract/0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80

# 4. Test in browser console
# Go to https://starknet.obsqra.fi and open DevTools
# Click "Calculate Risk & Allocation" and watch Network tab
```

---

## Files Modified

### Frontend
- ✅ `/frontend/src/hooks/useRiskEngineBackend.ts` - NEW
- ✅ `/frontend/src/components/Dashboard.tsx` - Updated to use backend
- ✅ `/frontend/src/hooks/useRiskEngine.ts` - Deprecated (kept for reference)

### Backend
- ✅ `/backend/app/api/routes/risk_engine.py` - NEW
- ✅ `/backend/app/api/__init__.py` - Added route registration
- ✅ `/backend/requirements.txt` - Added starknet-py

---

## Performance Notes

- **Risk calculation latency:** ~2-3 seconds (RPC call)
- **Allocation calculation latency:** ~4-6 seconds (2x risk + allocation)
- **No caching:** Each call is fresh (intentional for testnet)

---

**Status:** Ready for testing. Click "Calculate Risk & Allocation" in the Risk tab to see it in action!

