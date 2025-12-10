# Get Testnet Tokens - Easy Way ✅

## Simple 3-Step Process

### Step 1: Get STRK (Gas Token)

1. **Go to Starknet Faucet**: https://faucet.starknet.io/
2. **Connect your Starknet wallet** (ArgentX or Braavos)
3. **Make sure you're on Sepolia testnet** in your wallet
4. **Request STRK tokens**
5. **Wait a few minutes** for tokens to arrive

**You'll get**: ~0.1-1 STRK (enough for testing)

---

### Step 2: Swap STRK → ETH on JediSwap

1. **Go to JediSwap** (testnet):
   - Testnet URL: Check JediSwap docs or use their testnet interface
   - Or use: https://app.jediswap.xyz/ (switch to Sepolia testnet)

2. **Connect your Starknet wallet** (same one with STRK)

3. **Make swap**:
   - **From**: STRK
   - **To**: ETH
   - **Amount**: Half of your STRK (e.g., if you have 1 STRK, swap 0.5 STRK)
   - **Click "Swap"**

4. **Approve and confirm**:
   - Approve STRK spending (first time only)
   - Confirm swap transaction
   - Wait for transaction to complete

5. **Done!** You now have both STRK and ETH in your wallet

---

### Step 3: Test Your Contract

Now you have:
- ✅ STRK (for gas fees)
- ✅ ETH (for DeFi operations)

**You're ready to test!**

1. Deploy your StrategyRouter contract
2. Call `deposit()` with a small amount (e.g., 0.1 STRK)
3. Watch it:
   - Swap half to ETH
   - Add liquidity to both protocols
   - Store position IDs

---

## Token Addresses (For Reference)

**Starknet Sepolia:**
- STRK: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`
- ETH: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`

---

## Troubleshooting

### "Can't find JediSwap testnet"
- Check JediSwap documentation for testnet URL
- Make sure your wallet is on Starknet Sepolia
- Try: https://app.jediswap.xyz/ and switch network

### "Swap fails"
- Make sure you have enough STRK for gas
- Check slippage settings (try 1-2%)
- Verify you're on testnet, not mainnet

### "No liquidity on testnet"
- Testnet pools might have low liquidity
- Try smaller amounts
- Or bridge ETH from Sepolia if swap doesn't work

---

## Quick Checklist

- [ ] Get STRK from https://faucet.starknet.io/
- [ ] Swap STRK → ETH on JediSwap testnet
- [ ] Verify you have both tokens in wallet
- [ ] Ready to test deposit() function!

---

## That's It!

No bridging needed. Just:
1. Faucet → STRK ✅
2. Swap → ETH ✅
3. Test! ✅

**Total time**: ~5-10 minutes


