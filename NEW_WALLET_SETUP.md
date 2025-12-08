# 🆕 New Wallet Setup Guide

## Your New Sepolia Wallet

**Address:** `0x0199F1c59ffb4403E543B384f8BC77cF390A8671FBBC0F6f7eae0D462b39B777`

**Status:**
- ✅ Fresh wallet (untouched)
- ⏳ Not yet deployed (will auto-deploy on first transaction)
- 💰 Balance: 0 STRK (needs funding)

---

##  Quick Setup (3 Steps)

### Step 1: Get Testnet STRK

**Option A: Official Faucet** (Recommended)
```
https://faucet.starknet.io
```
1. Paste your address: `0x0199F1c59ffb4403E543B384f8BC77cF390A8671FBBC0F6f7eae0D462b39B777`
2. Click "Send"
3. Receive 2 STRK instantly

**Option B: Alchemy Faucet**
```
https://www.alchemy.com/faucets/starknet-sepolia
```

**Option C: Blast Faucet**
```
https://blastapi.io/faucets/starknet-sepolia
```

### Step 2: Connect to Frontend

1. Open http://localhost:3003
2. Click "Connect Argent X" (or "Connect Braavos")
3. Select this wallet in the extension
4. Approve connection

### Step 3: Make First Transaction

Any transaction will trigger account deployment:
- Click "Update Allocation" button
- Or try making a deposit
- Your account will auto-deploy using ~0.001 STRK for gas

---

## 🎮 Try Demo Mode First (No STRK Needed!)

While waiting for faucet:

1. Click the **"DEMO MODE"** toggle in the navbar (🎮 icon)
2. Explore all features with mock data:
   - View analytics
   - See transaction history (simulated)
   - Test UI interactions
3. Switch back to **"LIVE MODE"** when ready

---

## 📊 What You Can Do Once Funded

### View Analytics
- Protocol allocation breakdown
- APY calculations
- Risk analysis
- Performance projections

### Interact with Contracts
- **Update Allocation**: Change distribution across Nostra, zkLend, Ekubo
- **View Constraints**: See DAO-set risk limits
- **Check Risk Scores**: AI-calculated risk metrics
- **Make Deposits**: Add funds via MIST.cash privacy protocol

### Track Activity
- All transactions logged in History tab
- Click any transaction to view on Voyager
- Real-time status updates

---

## 🔍 Verify Your Wallet

### Check Balance
```bash
starkli balance 0x0199F1c59ffb4403E543B384f8BC77cF390A8671FBBC0F6f7eae0D462b39B777 \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```

### Check if Deployed
```bash
starkli class-hash-at 0x0199F1c59ffb4403E543B384f8BC77cF390A8671FBBC0F6f7eae0D462b39B777 \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```

### View on Voyager
```
https://sepolia.voyager.online/contract/0x0199F1c59ffb4403E543B384f8BC77cF390A8671FBBC0F6f7eae0D462b39B777
```

---

## 🎯 Expected Behavior

### Before Funding
- ❌ "Account not found" when trying transactions
- ✅ Can view contract data (read operations)
- ✅ Demo mode works perfectly

### After Funding (but before first transaction)
- ✅ Wallet shows STRK balance
- ❌ Still "Account not found" (not deployed yet)
- ✅ Ready to deploy with first transaction

### After First Transaction
- ✅ Account deployed on-chain
- ✅ Can send transactions
- ✅ Full functionality unlocked
- 🎉 You're live on Starknet Sepolia!

---

## 💡 Pro Tips

1. **Start with demo mode** to familiarize yourself with the UI
2. **Keep some STRK in reserve** for gas fees (~0.001 STRK per transaction)
3. **Check Voyager** if transactions seem stuck
4. **Use History tab** to track all your interactions
5. **Test with small amounts** first

---

## 🆘 Troubleshooting

### "Account not found"
→ Your account isn't deployed yet. Get STRK, then make any transaction to deploy it.

### "Insufficient balance"
→ Need more STRK. Revisit faucet (24h cooldown) or ask in Discord.

### Transaction fails silently
→ Check Voyager for error details using transaction hash.

### "Execute failed"
→ Usually means: no gas, not deployed, or invalid parameters.

---

## 📞 Need STRK Urgently?

If faucets aren't working:

1. **Starknet Discord**: https://discord.gg/starknet
   - Ask in #faucet channel
   - Community members often help

2. **Twitter**: Tag @StarknetFdn
   - Sometimes they do manual drops

3. **Alternative**: Wait 24h for faucet cooldown

---

**Ready to go!**  Get those STRK tokens and let's test everything!

