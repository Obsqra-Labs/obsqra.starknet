# How to Bridge Sepolia ETH to Starknet Sepolia

## Quick Guide

### Step 1: Get Sepolia ETH

1. **Go to Chainstack Faucet**: https://chainstack.com/faucets/
2. **Click "Sepolia testnet faucet"**
3. **Connect your Ethereum wallet** (MetaMask, etc.)
4. **Make sure wallet is on Sepolia network**:
   - Network: Sepolia
   - Chain ID: 11155111
5. **Click "Claim test tokens"**
6. **Wait for ETH** (usually instant)

**Alternative**: Alchemy Sepolia Faucet
- https://sepoliafaucet.com/
- Requires Alchemy account
- Up to 0.5 ETH per day

---

### Step 2: Bridge ETH to Starknet

#### Recommended: Rhino.fi Bridge

**URL**: https://app.rhino.fi/bridge?token=ETH&chainOut=STARKNET

**Step-by-Step**:

1. **Visit Rhino.fi Bridge**
   - Go to: https://app.rhino.fi/bridge
   - Or: https://app.rhino.fi/bridge?token=ETH&chainOut=STARKNET

2. **Connect Ethereum Wallet**
   - Click "Connect Wallet" (top right)
   - Choose MetaMask or your Ethereum wallet
   - **Important**: Make sure wallet is on **Sepolia network**
   - If not, switch network in MetaMask

3. **Connect Starknet Wallet**
   - Click "Connect Starknet Wallet"
   - Choose ArgentX or Braavos
   - **Important**: Make sure wallet is on **Starknet Sepolia testnet**
   - If not, switch network in your Starknet wallet

4. **Select Networks**
   - **From**: Sepolia (should auto-detect)
   - **To**: Starknet Sepolia (should auto-detect)
   - **Token**: ETH

5. **Enter Amount**
   - Enter how much ETH you want to bridge
   - Check minimum/maximum limits
   - Review fees (usually minimal on testnet)

6. **Approve (First Time Only)**
   - If first time bridging, you'll need to approve the bridge contract
   - Sign the approval transaction in MetaMask
   - Wait for approval to confirm

7. **Bridge**
   - Click "Bridge" button
   - Sign the bridge transaction in MetaMask
   - Wait for transaction to confirm on Sepolia

8. **Wait for Bridge**
   - Bridge usually takes 5-15 minutes
   - You'll see status updates on Rhino.fi
   - ETH will appear in your Starknet wallet when complete

9. **Verify**
   - Check your Starknet wallet (ArgentX/Braavos)
   - You should see ETH balance
   - Token address: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`

---

## Alternative: Swap STRK to ETH on JediSwap

**If bridging is complicated, you can swap STRK to ETH directly on Starknet:**

1. **Get STRK** from https://faucet.starknet.io/
2. **Go to JediSwap** (testnet)
3. **Swap STRK → ETH**
4. **Now you have ETH on Starknet!**

This is actually **easier** than bridging and works perfectly for testing.

---

## Troubleshooting

### "Network not supported"
- Make sure both wallets are on **testnet** (Sepolia, not mainnet)
- Check network settings in both MetaMask and Starknet wallet

### "Insufficient balance"
- Make sure you have enough Sepolia ETH for gas fees
- Bridge requires ETH for gas on both networks

### "Bridge not available"
- Some bridges only support mainnet
- Try Rhino.fi - they support testnet
- Or just swap STRK → ETH on JediSwap instead

### "Transaction stuck"
- Check transaction on Sepolia explorer
- Bridge can take 10-20 minutes on testnet
- Be patient!

---

## Quick Reference

**Faucets:**
- STRK: https://faucet.starknet.io/
- Sepolia ETH: https://chainstack.com/faucets/

**Bridges:**
- Rhino.fi: https://app.rhino.fi/bridge
- StarkGate: https://starkgate.starknet.io/ (check testnet support)

**Token Addresses (Starknet Sepolia):**
- ETH: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`
- STRK: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`

---

## ⭐ Recommended Approach for Testing (EASIEST!)

**Simple 3-Step Method:**
1. Get STRK from Starknet faucet ✅
   - https://faucet.starknet.io/
   - Connect wallet, request STRK
   
2. Swap STRK → ETH on JediSwap testnet ✅
   - Go to JediSwap (testnet)
   - Connect wallet
   - Swap half your STRK to ETH
   
3. Done! You have both tokens ✅
   - No bridging needed!
   - Faster and simpler
   - Ready to test!

**See `GET_TESTNET_TOKENS_EASY.md` for detailed step-by-step guide.**

---

## References

- [Rhino.fi Bridge Guide](https://support.rhino.fi/en/article/bridging-to-starknet-1y0sjax/)
- [Chainstack Faucet](https://chainstack.com/faucets/)
- [Starknet Sepolia Faucet](https://faucet.starknet.io/)

