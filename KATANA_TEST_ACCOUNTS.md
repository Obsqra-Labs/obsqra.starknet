# 🔑 Katana Local Devnet - Pre-Funded Test Accounts

These accounts are automatically created by Katana and come with **~1000 ETH each**.

---

## ✅ **Account #0** (Recommended)

```
Address:     0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71
Private Key: 0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b
Public Key:  0x4c0f884b8e5b4f00d97a3aad26b2e5de0c0c76a555060c837da2e287403c01d
Balance:     ~1000 ETH (on Katana devnet)
```

---

## ✅ **Account #1**

```
Address:     0x6677fe62ee39c7b07401f754138502bab7fac99d2d3c5d37df7d1c6fab10819
Private Key: 0x3e3979c1ed728490308054fe357a9f49cf67f80f9721f44cc57235129e090f4
Public Key:  0x1e8965b7d0b20b91a62fe515dd991dc9fcb748acddf6b2cf18cec3bdd0f9f9a
Balance:     ~1000 ETH (on Katana devnet)
```

---

## 📱 **How to Import into Your Wallet**

### **Option A: Argent X**

1. Open Argent X browser extension
2. Click **"+ New Account"** (or account menu)
3. Select **"Import Account"**
4. Choose **"Private Key"**
5. Paste the private key from **Account #0** above:
   ```
   0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b
   ```
6. **Add Custom Network:**
   - Network Name: `Local Katana`
   - RPC URL: `http://localhost:5050`
   - Chain ID: `KATANA` (or `0x4b4154414e41`)

7. Switch to the **Local Katana** network
8. You now have **~1000 ETH**! 🎉

---

### **Option B: Braavos**

1. Open Braavos browser extension
2. Click **"..."** menu → **"Import Wallet"**
3. Select **"Private Key"**
4. Paste the private key from **Account #0**:
   ```
   0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b
   ```
5. **Add Custom Network:**
   - Network Name: `Local Katana`
   - RPC URL: `http://localhost:5050`
   - Chain ID: `KATANA`

6. Switch to **Local Katana** network
7. You now have **~1000 ETH**! 🎉

---

## 🚀 **Next Steps**

1. Import Account #0 using the steps above
2. Connect your wallet to http://localhost:3002
3. Start testing your Starknet dApp with plenty of ETH!

---

## ⚠️ **Important Notes**

- These accounts are **ONLY for local development**
- **NEVER** use these private keys on mainnet or testnet
- The ETH only exists on your local Katana devnet (port 5050)
- Every time you restart Katana, the accounts reset with fresh ETH

---

## 🔄 **Restart Katana (if needed)**

```bash
cd /opt/obsqra.starknet
pkill -f katana
katana --dev --http.cors_origins "*"
```

The same accounts will be recreated with the same private keys and fresh ETH balances.
