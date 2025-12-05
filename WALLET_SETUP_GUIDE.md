# Starknet Wallet Setup for Testing

## Recommended: ArgentX (Best for Development)

**ArgentX** is the most popular Starknet wallet and best for testing/development.

### Why ArgentX?
- ✅ Most widely supported
- ✅ Easy testnet switching
- ✅ Browser extension (works with your dApp)
- ✅ Good developer tools
- ✅ Works with all Starknet faucets

## Installation Steps

### 1. Install ArgentX

**Chrome/Brave:**
https://chrome.google.com/webstore/detail/argent-x/dlcobpjiigpikoobohmabehhmhfoodbb

**Firefox:**
https://addons.mozilla.org/en-US/firefox/addon/argent-x/

**Edge:**
https://microsoftedge.microsoft.com/addons/detail/argent-x/ajcicjlkibolbeaaagejfhnofogocgcj

### 2. Create Testnet Account

1. Open ArgentX extension
2. Click "Create new wallet"
3. **Save your seed phrase securely!**
4. Create password
5. Click on network dropdown (top right)
6. Select **"Sepolia Testnet"** (or Goerli if available)

### 3. Get Your Address

1. Click on your account name
2. Click "Copy address" 
3. Your address looks like: `0x04a7...8d3f`

### 4. Get Testnet Funds

**Option 1: Starknet Faucet (Recommended)**
```
https://starknet-faucet.vercel.app/
```
- Paste your address
- Request tokens
- Wait ~30 seconds
- Check balance in wallet

**Option 2: Blast API Faucet**
```
https://blastapi.io/faucets/starknet-sepolia-eth
```
- Connect wallet or paste address
- Request 0.001 ETH
- Good for multiple requests

**Option 3: Official Starknet Faucet**
```
https://faucet.starknet.io/
```
- May require GitHub verification
- Larger amounts available

### 5. Verify Setup

In ArgentX:
- ✅ Network: Sepolia Testnet
- ✅ Balance: >0 ETH (even 0.001 is enough)
- ✅ Account activated (first transaction activates it)

## Alternative: Braavos Wallet

If you want a backup or alternative:

**Install Braavos:**
```
https://braavos.app/download-braavos-wallet/
```

**Features:**
- Hardware wallet support
- Multi-sig support
- Similar to ArgentX

## For Mobile Testing

**Argent Mobile:**
```
iOS: https://apps.apple.com/app/argent/id1358741926
Android: https://play.google.com/store/apps/details?id=im.argent.contractwalletclient
```

## Connect to Your Frontend

### Using ArgentX with Next.js

Your frontend is already set up! In `/opt/obsqra.starknet/frontend`:

```typescript
// StarknetProvider.tsx already configured
import { StarknetConfig, publicProvider } from "@starknet-react/core";
import { sepolia } from "@starknet-react/chains";
```

### Test Connection

1. Start your frontend:
```bash
cd /opt/obsqra.starknet/frontend
npm run dev
```

2. Open http://localhost:3000

3. Click "Connect Wallet"

4. Select ArgentX

5. Approve connection

6. Your address should appear!

## Testing Checklist

- [ ] ArgentX installed
- [ ] Testnet account created
- [ ] Switched to Sepolia Testnet
- [ ] Got testnet ETH from faucet
- [ ] Balance shows in wallet
- [ ] Frontend connects to wallet
- [ ] Can sign test transactions

## Common Issues

### Issue: "Insufficient funds"
**Solution:** Get more from faucet. You need ~0.001 ETH for testing.

### Issue: "Account not deployed"
**Solution:** First transaction deploys your account. Try sending a tiny amount to yourself.

### Issue: "Wrong network"
**Solution:** Make sure both wallet and frontend are on **Sepolia Testnet**

### Issue: "Can't connect wallet"
**Solution:** 
1. Refresh page
2. Disconnect and reconnect
3. Check if extension is enabled
4. Try incognito/private window

## Network Configuration

### Testnet RPC URLs

If you need to configure manually:

**Sepolia Testnet:**
```
https://starknet-sepolia.public.blastapi.io
https://free-rpc.nethermind.io/sepolia-juno
```

**Goerli Testnet (older):**
```
https://starknet-goerli.public.blastapi.io
```

## Account Types

ArgentX creates an **Account Abstraction** wallet:
- No separate EOA (Externally Owned Account)
- Account IS a smart contract
- More flexible than traditional wallets
- Supports features like session keys, 2FA, etc.

## Best Practices for Testing

1. **Keep Separate Wallets**
   - Development wallet (ArgentX)
   - Production wallet (different seed phrase)

2. **Save Your Seed Phrase**
   - Write it down physically
   - Store in password manager
   - Never share it

3. **Use Testnet First**
   - Always test on testnet before mainnet
   - Testnet ETH is free
   - No risk of losing real funds

4. **Bookmark Useful Links**
   - Faucet
   - Block explorer (Voyager/Starkscan)
   - Your deployed contracts

## Block Explorers

View your transactions and contracts:

**Voyager:**
```
https://sepolia.voyager.online/
```

**Starkscan:**
```
https://sepolia.starkscan.co/
```

Paste your address or transaction hash to view details.

## Ready to Test!

Once you have:
1. ✅ ArgentX installed with testnet account
2. ✅ Testnet ETH in wallet
3. ✅ Frontend connecting to wallet

You can:
- Deploy contracts to testnet
- Test contract interactions
- Test the full user flow
- Prepare for grant submission

## Quick Start Commands

```bash
# Get your current setup
echo "Network: Sepolia Testnet"
echo "Wallet: ArgentX"
echo "Faucet: https://starknet-faucet.vercel.app/"
echo "Explorer: https://sepolia.voyager.online/"

# Start frontend
cd /opt/obsqra.starknet/frontend
npm run dev

# Deploy contracts (once wallet is ready)
cd /opt/obsqra.starknet/contracts
sncast account create --name my_testnet_account
```

---

**Next:** Install ArgentX and get testnet funds, then you're ready to test your dApp!

