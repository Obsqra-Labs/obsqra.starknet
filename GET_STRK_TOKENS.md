# 🪙 Getting Sepolia STRK Tokens for Starknet

## ⚠️ Important: You Need STRK, Not ETH!

On **Starknet Sepolia testnet**, gas fees are paid in **STRK tokens**, not ETH.

Your wallet: `0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027`

---

## 🚰 Option 1: Official Starknet Faucet (Recommended)

### Starknet Sepolia Faucet
**URL:** https://starknet-faucet.vercel.app/

**How to use:**
1. Visit the faucet
2. Connect your Argent X wallet
3. Select "Sepolia Testnet"
4. Request STRK tokens
5. Wait for confirmation (usually instant)

**Amount:** Usually 0.001-0.01 STRK per request

---

## 🚰 Option 2: Blast API Faucet

**URL:** https://blastapi.io/faucets/starknet-sepolia

**How to use:**
1. Visit the faucet
2. Paste your wallet address: `0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027`
3. Complete CAPTCHA
4. Request STRK tokens
5. Tokens should arrive in 1-2 minutes

---

## 🚰 Option 3: Alchemy Starknet Faucet

**URL:** https://www.alchemy.com/faucets/starknet-sepolia

**How to use:**
1. Visit the faucet
2. Sign in with Alchemy account (free)
3. Enter your wallet address
4. Request STRK tokens

---

## 🚰 Option 4: Community Faucets

### Sepolia STRK Faucet by Starknet Foundation
**URL:** https://sepolia-faucet.starknet.io/

### Discord Faucet
Join Starknet Discord: https://discord.gg/starknet
- Go to #testnet-faucet channel
- Request STRK tokens

---

## ✅ Verify Your STRK Balance

### In Argent X Wallet:
1. Open Argent X
2. Make sure you're on "Starknet Sepolia" network
3. Check your STRK balance (should show after faucet request)

### Via Starkli:
```bash
starkli balance 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7
```

### Via Voyager Explorer:
Visit: https://sepolia.voyager.online/contract/0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027

---

## 💰 How Much STRK Do You Need?

| Operation | Estimated STRK Cost |
|-----------|---------------------|
| Declare contract | ~0.0001-0.001 STRK |
| Deploy contract | ~0.0001-0.001 STRK |
| Contract interaction | ~0.00001-0.0001 STRK |
| **Total for 3 contracts** | **~0.001-0.01 STRK** |

So **0.01 STRK** should be enough for deploying all 3 contracts + testing.

---

## 🆘 Troubleshooting

### "Insufficient balance for fee"
- You need more STRK tokens
- Try multiple faucets to accumulate enough
- Some faucets have rate limits (1 request per 24 hours)

### "Account not found"
- Your account needs to be deployed first
- Make a small transaction (even 0.001 STRK transfer to yourself) to deploy it
- Or the first contract deployment will deploy your account automatically

### Faucet not working?
- Try a different faucet from the list
- Check if you're on the correct network (Starknet Sepolia)
- Some faucets require social verification (Twitter, Discord)

---

## 🎯 Next Steps After Getting STRK

Once you have STRK tokens:

1. ✅ Verify balance in Argent X
2. 📦 Install Scarb and Starkli tools
3. 🔨 Compile contracts
4. 🚀 Deploy to Sepolia
5. 🎉 Test your dApp!

See: `/opt/obsqra.starknet/COMPLETE_DEPLOYMENT_GUIDE.md`

---

## 📊 Current Status

- [x] Wallet address ready
- [ ] STRK tokens acquired
- [ ] Tools installed
- [ ] Contracts compiled
- [ ] Contracts deployed

**Your next step:** Visit one of the faucets above and get some STRK! 🚰
