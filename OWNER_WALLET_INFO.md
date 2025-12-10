# Owner Wallet Information

## V3 Contract Owner

**Address**: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`

**Private Key**: `0x7fd44d52324945e2d9f2e62bd2dadb794e2274dbd0955251aeca6cc96153afc`

## Contract Address

**V3 Contract**: `0x050a3a03cd3a504eb000c47b0fcfa34456f2f1918a75326f1499c345f0e11405`

## Usage

This is the owner wallet for the StrategyRouterV3 contract. It's used for:
- Owner-only functions (deploy_to_protocols, accrue_yields, update_slippage_tolerance, etc.)
- Backend API route (`/api/integration-tests/execute-as-owner`)
- Contract administration

## Import into Wallet

To import this wallet into Argent or Braavos:
1. Open your wallet
2. Go to Settings → Import Account
3. Select "Private Key"
4. Paste: `0x7fd44d52324945e2d9f2e62bd2dadb794e2274dbd0955251aeca6cc96153afc`
5. Confirm

## Security Note

⚠️ **Never commit this private key to version control!**
- This file should be in `.gitignore`
- Only share with trusted team members
- For production, use a hardware wallet or key management service

