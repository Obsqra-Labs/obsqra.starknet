# 🎮 Demo Mode - Testing Guide

## What Just Got Fixed

✅ Demo mode now actually works!  
✅ Shows different data in demo vs live mode  
✅ Transaction history works properly  
✅ Simulated transactions with instant feedback  

---

##  How to Test

### 1. Access the App
```
https://starknet.obsqra.fi
```

### 2. Connect Your Wallet
- Click "Connect Argent X"
- Approve connection

### 3. Toggle Demo Mode
- Click the **🎮 DEMO MODE** button in navbar
- Should see it activate with purple indicator

### 4. Test Features in Demo Mode

#### **Overview Tab** - Main Dashboard
- See mock allocation: 40% Nostra, 35% zkLend, 25% Ekubo
- Risk Score shows: 4500/10000 (Medium)
- All sections show "🎮 Demo Mode" indicator

#### **Update Allocation** (Demo Mode)
1. Adjust the sliders:
   - Nostra: try 50%
   - zkLend: try 30%
   - Ekubo: try 20%
2. Click "🔄 Update Allocation"
3. Get instant popup with simulated TX hash
4. Check **History tab** - transaction appears!
5. After 3 seconds, transaction auto-confirms

#### **Analytics Tab** - Performance Dashboard
- Portfolio value: 1000 STRK
- Weighted APY calculations
- Protocol breakdown with APYs
- Risk analysis charts
- Performance projections

#### **History Tab** - Transaction Tracking
- See all your demo transactions
- Filter by: All / Pending / Confirmed / Failed
- Expand transactions for details
- Click hash to view on Voyager (mock hash)

### 5. Switch to Live Mode
- Click **🔌 LIVE MODE** toggle
- Data changes to real contract data
- Transactions require real STRK

---

## 📊 What You Should See

### In Demo Mode:
```
Current Allocation 🎮 Demo Mode
├─ Nostra: 40.00%
├─ zkLend: 35.00%
└─ Ekubo: 25.00%

Risk Score: 4500/10000
🎮 Demo

DAO Constraints 🎮 Demo Mode
├─ Max Single Protocol: 60%
├─ Min Protocols: 2
├─ Max Volatility: 30%
└─ Min Liquidity: 1.0 STRK
```

### In Live Mode:
```
Current Allocation
├─ Nostra: [from contract]
├─ zkLend: [from contract]
└─ Ekubo: [from contract]

Risk Score: [from contract]
Live

DAO Constraints
[Real data from deployed contracts]
```

---

## 🎯 Features to Test

### ✅ Working Now:
1. **Demo Mode Toggle** - Actually switches data
2. **Transaction Simulation** - Creates fake TX in demo
3. **Transaction History** - Tracks all interactions
4. **Analytics Dashboard** - Shows portfolio metrics
5. **Tab Navigation** - Overview / Analytics / History

### 🔄 What Happens in Demo Mode:
- Allocation updates → Simulated instantly
- No gas fees required
- Transactions auto-confirm after 3s
- All data is mock/realistic
- No blockchain interaction

### 🔌 What Happens in Live Mode:
- Allocation updates → Real blockchain TX
- Requires STRK for gas
- Transactions need confirmation
- Real contract data
- Full blockchain interaction

---

## 🐛 Troubleshooting

### Demo Mode Not Working?
1. Hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R`)
2. Clear cache
3. Check toggle is purple/active

### History Empty?
1. Make a transaction first (demo or live)
2. Refresh page - history persists in localStorage
3. Try updating allocation

### No Data Showing?
1. Make sure wallet is connected
2. Toggle demo mode on/off
3. Check browser console (F12)

---

## 💡 Pro Tips

1. **Test in Demo First** - Learn the UI without spending gas
2. **History Persists** - Your demo transactions stay until you clear them
3. **Analytics Are Live** - Even in demo, shows realistic projections
4. **Easy Reset** - Clear history with "Clear History" button
5. **Mix Modes** - Can switch between demo/live anytime

---

##  Next Steps

Once you have STRK:
1. Test in demo mode first
2. Switch to live mode
3. Make a real transaction
4. Watch it appear in history
5. View on Voyager explorer

---

**Demo mode is now fully functional!** 🎉  
Go test it: https://starknet.obsqra.fi

