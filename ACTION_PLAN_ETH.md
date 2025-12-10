# Action Plan: Bridge Your 0.5 ETH to Starknet

## Current Situation ✅

- **You have**: 0.5 ETH on Ethereum Sepolia
- **Address**: `0x8f2c8b79b24122e189966d8a041af49a9f9ec7d9`
- **Network**: Ethereum Sepolia (needs bridging)

---

## Step 1: Bridge ETH to Starknet Sepolia

### Using Rhino.fi Bridge (Recommended)

1. **Go to**: https://app.rhino.fi/bridge
   - Or direct link: https://app.rhino.fi/bridge?token=ETH&chainOut=STARKNET

2. **Connect Ethereum Wallet**:
   - Click "Connect Wallet" (top right)
   - Choose MetaMask or your wallet
   - **Make sure it's on Sepolia network** (not mainnet!)
   - Network: Sepolia
   - Chain ID: 11155111

3. **Connect Starknet Wallet**:
   - Click "Connect Starknet Wallet"
   - Choose ArgentX or Braavos
   - **Make sure it's on Starknet Sepolia testnet**
   - If not, switch network in wallet settings

4. **Select Networks**:
   - **From**: Sepolia (should auto-detect)
   - **To**: Starknet Sepolia (should auto-detect)
   - **Token**: ETH

5. **Enter Amount**:
   - Amount: 0.4 ETH (keep 0.1 for gas fees on Ethereum side)
   - Or bridge less if you want to keep more for gas

6. **Approve (First Time)**:
   - If first time, approve the bridge contract
   - Sign transaction in MetaMask
   - Wait for approval (~30 seconds)

7. **Bridge**:
   - Click "Bridge" button
   - Sign transaction in MetaMask
   - Wait for confirmation

8. **Wait for Bridge**:
   - Usually takes 5-15 minutes
   - You'll see status on Rhino.fi
   - ETH will appear in your Starknet wallet

---

## Step 2: Get STRK for Gas Fees

While waiting for bridge (or after):

1. **Go to**: https://faucet.starknet.io/
2. **Connect your Starknet wallet** (same one you bridged to)
3. **Select**: Sepolia testnet
4. **Request STRK tokens**
5. **Wait a few minutes** for tokens

**You need STRK** to pay for transactions on Starknet!

---

## Step 3: Verify You're Ready

**Check your Starknet wallet:**
- ✅ ETH balance: ~0.4 ETH (after bridge)
- ✅ STRK balance: Some amount (from faucet)

**If both show up, you're ready to test!**

---

## Step 4: Test Your Contract

### Option A: Using Frontend

1. **Make sure StrategyRouter is deployed** with:
   - NFT Position Manager address: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`
   - Ekubo Core address: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`

2. **Connect wallet** to your frontend
3. **Call deposit()** with small amount (e.g., 0.1 ETH worth)
4. **Watch it**:
   - Swap half to ETH (if depositing STRK)
   - Add liquidity to JediSwap
   - Add liquidity to Ekubo
   - Store position IDs

### Option B: Using CLI (starkli/sncast)

```bash
# 1. Make sure contract is deployed
# 2. Call deposit function

# Example with starkli:
starkli call <STRATEGY_ROUTER_ADDRESS> deposit \
  --args <amount_in_wei> \
  --account <your_account_file> \
  --network sepolia
```

---

## Quick Checklist

- [ ] Bridge 0.4 ETH to Starknet (keep 0.1 for gas)
- [ ] Get STRK from faucet
- [ ] Verify both tokens in Starknet wallet
- [ ] Deploy StrategyRouter (if not deployed)
- [ ] Test deposit() function
- [ ] Verify positions created

---

## Troubleshooting

### "Bridge not working"
- Make sure both wallets are on **testnet** (not mainnet!)
- Check network settings in both MetaMask and Starknet wallet
- Try smaller amount first (0.1 ETH)

### "No STRK for gas"
- Get from: https://faucet.starknet.io/
- You need STRK to pay for transactions

### "Contract call fails"
- Check you have STRK for gas
- Verify contract is deployed correctly
- Check NFT Position Manager address is correct

---

## Expected Result

After successful deposit():
- ✅ Transaction confirmed on Starknet
- ✅ Position NFT created on JediSwap
- ✅ Position created on Ekubo
- ✅ Position IDs stored in contract
- ✅ Funds actually earning yield!

---

## Next Steps After Testing

1. **Verify positions**:
   - Check JediSwap position NFT
   - Check Ekubo position
   - Query position values

2. **Test withdrawal** (once implemented)
3. **Test yield accrual** (once implemented)
4. **Monitor performance**

---

## Links

- **Rhino.fi Bridge**: https://app.rhino.fi/bridge
- **Starknet Faucet**: https://faucet.starknet.io/
- **StarkScan (Explorer)**: https://sepolia.starkscan.co/

Good luck! Let me know once you've bridged and we can test the contract! 🚀


