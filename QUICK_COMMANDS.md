# Quick Commands

## Restart Frontend on Port 3001
```bash
bash /opt/obsqra.starknet/restart_frontend.sh
```

Or manually:
```bash
pkill -9 -f "next dev"
cd /opt/obsqra.starknet/frontend
PORT=3001 npm run dev
```

Then open: **http://localhost:3001**

---

## Deploy Contracts to Starknet
```bash
cd /opt/obsqra.starknet
python3 scripts/full_deploy.py
```

This will:
- Create new wallet
- Fund it from your ArgentX (if deployed)  
- Deploy all contracts
- Save addresses

---

## Check What's Running
```bash
# Check frontend
ps aux | grep "next dev"

# Check if port 3001 is responding
curl http://localhost:3001

# View frontend logs
tail -f /tmp/frontend_3001.log
```

---

## Contract Tests
```bash
cd /opt/obsqra.starknet/contracts
snforge test
```

All 31 tests should pass.

---

## Your Next Steps

1. **Fix Python script issue** (StarknetChainId - already fixed)
2. **Run deployment**: `python3 scripts/full_deploy.py`
3. **Start frontend**: `bash restart_frontend.sh`
4. **Demo on http://localhost:3001**

---

## What's Ready

✅ Contracts compiled (31/31 tests passing)
✅ Python deployment script (fixed)
✅ Frontend code (with mock MIST.cash)
✅ Infura API configured
⏸️ Need to deploy contracts
⏸️ Need to restart frontend cleanly

## Current Wallet Info

**Your ArgentX:**
- Address: 0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd
- Balance: 800 STARK
- Issue: Account not deployed on-chain

**New Wallet (created by script):**
- Will be saved to `.deployer_wallet.json`
- Script will fund it automatically
- Script will deploy it automatically

