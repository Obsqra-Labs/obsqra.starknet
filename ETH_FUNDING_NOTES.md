# 💰 ETH Funding - To Complete Later

## Your Wallet Address
```
0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027
```

## Quick Commands to Fund Wallet

### Method 1: Python Script
```bash
# Terminal 1: Start Katana
cd /opt/obsqra.starknet
katana --dev --http.cors_origins "*"

# Terminal 2: Fund wallet
cd /opt/obsqra.starknet
python3 scripts/fund_user_wallet.py
```

### Method 2: Using sncast
```bash
# Install sncast
curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | sh
export PATH="$HOME/.foundry/bin:$PATH"

# Setup Katana account
sncast account add katana-dev \
  --address 0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71 \
  --private-key 0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b \
  --type oz \
  --add-profile \
  --rpc-url http://localhost:5050

# Transfer ETH
sncast --account katana-dev --url http://localhost:5050 invoke \
  --contract-address 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 \
  --function transfer \
  --calldata 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 0x8ac7230489e80000 0x0
```

## For Now: Test on Sepolia
You already have testnet ETH on Sepolia, so switch to that for testing with real transactions!
