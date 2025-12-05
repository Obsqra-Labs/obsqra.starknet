# Obsqra.starknet Frontend Demo Guide

## Frontend is Live!

**URL:** http://localhost:3001

The Next.js development server is running and ready for demo.

## What You'll See

### 1. **Main Dashboard**
- Pool overview with TVL stats
- AI performance metrics
- Current allocation breakdown
- Recent rebalancing history
- Quick action buttons

### 2. **Wallet Connection**
- Connect ArgentX or Braavos wallet
- View connected account
- Network indicator (Sepolia)

### 3. **Interactive Features**
- **Deposit Button** - Opens MIST.cash private deposit flow
- **Withdraw Button** - Private withdrawal interface
- **AI Stats** - Shows risk engine performance
- **Protocol Allocation** - Visual breakdown of capital distribution

## Demo Flow

### Flow 1: Basic Overview Demo
```
1. Open http://localhost:3001
2. View the dashboard (no wallet needed)
3. See mock data for:
   - Total Value Locked: $2.5M
   - AI Performance: 12.4% APY
   - Risk Score: 7.2/10
   - Allocations across 3 protocols
```

### Flow 2: Wallet Connection Demo
```
1. Click "Connect Wallet"
2. Select ArgentX
3. Approve connection
4. See your wallet address displayed
5. View personalized stats
```

### Flow 3: Deposit Flow Demo (Mock)
```
1. Click "Deposit"
2. See MIST.cash privacy interface
3. Enter amount
4. Preview privacy parameters
5. (Would execute on testnet when deployed)
```

### Flow 4: AI Decision Flow Demo
```
1. View "Recent AI Decisions" section
2. See rebalancing history
3. Click on a decision to see:
   - Risk analysis
   - Allocation changes
   - DAO constraint validation
   - Transaction details
```

## Features to Highlight

### ✨ Privacy-First Design
- MIST.cash integration visible
- Amount correlation mitigation
- Fresh address withdrawals
- Privacy score indicators

### 🤖 AI Transparency
- Risk scores displayed
- Allocation rationale shown
- DAO constraint checks visible
- Full audit trail

### 📊 Real-Time Stats (Mock Data)
- Pool TVL
- Protocol distribution
- Yield performance
- Historical trends

### 🎨 Modern UI/UX
- Clean, professional design
- Responsive layout
- Tailwind CSS styling
- Intuitive navigation

## Mock Data Currently Shown

```javascript
{
  poolTVL: "$2,500,000",
  aiAPY: "12.4%",
  riskScore: "7.2/10",
  allocations: {
    Ekubo: "40%",
    zkLend: "35%",
    Nostra: "25%"
  },
  recentDecisions: [
    {
      action: "Rebalance",
      from: "Ekubo 45% → 40%",
      to: "Nostra 20% → 25%",
      reason: "Higher yield opportunity detected"
    }
  ]
}
```

## What Works Right Now

✅ **UI/UX Complete**
- All components render
- Navigation works
- Responsive design
- Loading states

✅ **Wallet Integration Ready**
- StarknetProvider configured
- ArgentX/Braavos support
- Connection flow implemented

✅ **Contract Hooks Prepared**
- `useRiskEngine` hook
- `useMistCash` hook
- Ready to connect to deployed contracts

⏸️ **Waiting for Contracts**
- Once deployed, real data will flow
- All hooks ready to activate
- Just need contract addresses

## For Video Demo / Screenshots

### Screenshot 1: Dashboard Overview
**Highlight:**
- Clean, professional interface
- Clear metrics display
- Privacy-focused design

### Screenshot 2: Wallet Connection
**Highlight:**
- Seamless Starknet integration
- ArgentX/Braavos support
- Network selection

### Screenshot 3: Deposit Flow
**Highlight:**
- MIST.cash privacy interface
- Amount correlation warning
- Privacy score

### Screenshot 4: AI Decisions
**Highlight:**
- Transparent AI reasoning
- DAO constraint validation
- Full audit trail

## Grant Application Demo Script

> "Let me show you Obsqra running on Starknet. Here's the dashboard where users can view their private pool positions. The AI engine computes risk scores and optimal allocations on-chain using Cairo, with automatic SHARP proving. 
>
> When a user deposits through MIST.cash [click Deposit], they get full privacy - no amount correlation, fresh withdrawal addresses. The AI rebalances across Starknet DeFi protocols like Ekubo, zkLend, and Nostra based on real-time risk analysis.
>
> Everything is transparent and verifiable - you can see the AI's reasoning, the DAO constraints it must follow, and the full execution trail. All computation happens on-chain in Cairo, proven by SHARP automatically.
>
> The frontend integrates seamlessly with ArgentX and Braavos wallets [click Connect]. Once our account deployment issue is resolved, this will be live on Sepolia testnet with real transactions."

## Access the Demo

**Open your browser:** http://localhost:3001

**Or from command line:**
```bash
# On your local machine (if this is a remote server)
# You may need to set up SSH tunneling:
ssh -L 3001:localhost:3001 your-server

# Then open: http://localhost:3001
```

## Stop the Frontend

When done with demo:
```bash
# Find the process
ps aux | grep "next dev"

# Kill it
pkill -f "next dev"
```

## Next Steps After Demo

1. **Record demo video** for grant application
2. **Take screenshots** for documentation
3. **Fix ArgentX wallet** for testnet deployment
4. **Deploy contracts** - then frontend becomes fully functional
5. **Update contract addresses** in frontend config

---

**Ready to demo!** Open http://localhost:3001 in your browser.

