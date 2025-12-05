# 💰 Get ETH on Katana Devnet - STEP BY STEP

## Your Wallet Address
```
0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027
```

---

## 🚀 Method 1: Simple Python Script (EASIEST)

### Step 1: Start Katana

Open Terminal 1 and run:
```bash
cd /opt/obsqra.starknet
katana --dev --http.cors_origins "*"
```

**Keep this terminal open!**

### Step 2: Run Funding Script

Open Terminal 2 and run:
```bash
cd /opt/obsqra.starknet
python3 scripts/fund_user_wallet.py
```

**Expected output:**
```
💰 Funding Your Wallet with Test ETH
====================================
From:   0x5b6b8189...
To:     0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027
Amount: 10 ETH

✅ Transaction sent!
🎉 SUCCESS! Your wallet has been funded!
```

### Step 3: Verify

Check your wallet balance:
```bash
starkli balance 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc http://localhost:5050
```

Or just refresh your Argent X wallet (make sure you're on Local Katana network)!

---

## 🚀 Method 2: Using Starknet Foundry (sncast)

If Python fails, use sncast:

### Install sncast
```bash
curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh
snfoundryup
export PATH="$HOME/.foundry/bin:$PATH"
```

### Setup Katana Account
```bash
sncast account add katana-dev \
  --address 0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71 \
  --private-key 0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b \
  --type oz \
  --rpc-url http://localhost:5050
```

### Transfer ETH
```bash
sncast --account katana-dev \
  --url http://localhost:5050 \
  invoke \
  --contract-address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 \
  --function transfer \
  --calldata 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 0x8ac7230489e80000 0x0
```

---

## 🚀 Method 3: Direct RPC Call (Advanced)

If both above fail, here's a direct approach:

```bash
# Create transfer transaction
curl -X POST http://localhost:5050 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "starknet_addInvokeTransaction",
    "params": {
      "invoke_transaction": {
        "type": "INVOKE",
        "sender_address": "0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71",
        "calldata": [
          "0x1",
          "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
          "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e",
          "0x3",
          "0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027",
          "0x8ac7230489e80000",
          "0x0"
        ],
        "max_fee": "0x0",
        "version": "0x1",
        "signature": [],
        "nonce": "0x0"
      }
    },
    "id": 1
  }'
```

---

## ✅ Checklist

Before running:
- [ ] Katana is running on port 5050
- [ ] Your wallet is set to "Local Katana" network
- [ ] You have Python 3 or sncast installed

After running:
- [ ] Script completed successfully
- [ ] Wallet shows 10 ETH
- [ ] Ready to deploy contracts!

---

## 🆘 Troubleshooting

### "Connection refused"
Katana isn't running. Start it:
```bash
katana --dev --http.cors_origins "*"
```

### "Module not found: starknet_py"
Install dependencies:
```bash
pip install starknet-py
```

### "Account not deployed"
That's fine for Katana! The pre-funded accounts work without deployment.

### Still not working?
Check Katana logs:
```bash
tail -f /tmp/katana-running.log
```

---

## 🎯 Once You Have ETH

1. ✅ Compile contracts: `cd /opt/obsqra.starknet/contracts && scarb build`
2. ✅ Deploy contracts: `cd /opt/obsqra.starknet/scripts && ./deploy-local.sh`
3. ✅ Update frontend with deployed addresses
4. ✅ Test contract interactions!
