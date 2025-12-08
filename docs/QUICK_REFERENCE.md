# Quick Reference Guide - Obsqra.starknet

##  Common Commands

### Contract Development

```bash
# Build contracts
cd contracts && scarb build

# Run tests
scarb test

# Format Cairo code
scarb fmt

# Check for issues
scarb check
```

### Deployment

```bash
# Deploy to Sepolia
./scripts/deploy.sh sepolia deployer

# Deploy to mainnet
./scripts/deploy.sh mainnet deployer
```

### Account Management

```bash
# Create new account
sncast account create --name my-account

# Import existing account
sncast account import --name my-account \
  --address 0x123... \
  --private-key 0xabc...

# List accounts
sncast account list

# Check balance
starkli balance 0x123...
```

### Contract Interaction

```bash
# Call view function
sncast call \
  --contract-address 0x123... \
  --function get_allocation \
  --network sepolia

# Invoke state-changing function
sncast --account deployer invoke \
  --contract-address 0x123... \
  --function update_allocation \
  --calldata 3333 3333 3334 \
  --network sepolia

# Get transaction status
sncast transaction-status \
  --hash 0xabc... \
  --network sepolia
```

---

## 📦 Project Structure

```
obsqra.starknet/
├── contracts/          # Cairo smart contracts
│   ├── src/
│   │   ├── risk_engine.cairo
│   │   ├── strategy_router.cairo
│   │   └── dao_constraint_manager.cairo
│   └── Scarb.toml
├── frontend/           # Next.js frontend
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── providers/
│   └── package.json
├── ai-service/         # Python AI service
│   ├── app.py
│   └── requirements.txt
├── scripts/            # Deployment scripts
├── deployments/        # Deployment records
└── docs/               # Documentation
```

---

## 🔧 Configuration Files

### `contracts/snfoundry.toml`
Sncast configuration for accounts and networks

```toml
[sncast.deployer]
account = "deployer"
url = "https://starknet-sepolia.g.alchemy.com/v2/YOUR_KEY"

[sncast.deployer.accounts.deployer]
address = "0x..."
private_key = "0x..."
```

### `frontend/.env.local`
Frontend environment variables

```env
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_NETWORK=sepolia
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.g.alchemy.com/v2/YOUR_KEY

NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x...
NEXT_PUBLIC_DAO_MANAGER_ADDRESS=0x...
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x...
```

---

## 🌐 Useful Links

### Explorers
- **Voyager (Sepolia)**: https://sepolia.voyager.online
- **Starkscan (Sepolia)**: https://sepolia.starkscan.co
- **Voyager (Mainnet)**: https://voyager.online
- **Starkscan (Mainnet)**: https://starkscan.co

### Faucets (Testnet STRK)
- **Official**: https://faucet.starknet.io
- **Alchemy**: https://www.alchemy.com/faucets/starknet-sepolia
- **Blast**: https://blastapi.io/faucets/starknet-sepolia

### RPC Endpoints
- **Alchemy**: https://starknet-sepolia.g.alchemy.com/v2/YOUR_KEY
- **Infura**: https://starknet-sepolia.infura.io/v3/YOUR_KEY
- **Public (read-only)**: https://starknet-sepolia.public.blastapi.io

### Documentation
- **Starknet Docs**: https://docs.starknet.io
- **Cairo Book**: https://book.cairo-lang.org
- **Starknet React**: https://starknet-react.com
- **Starknet Foundry**: https://foundry-rs.github.io/starknet-foundry

---

## 🐛 Troubleshooting

### "Account not found"
**Solution:** Your account isn't deployed yet. Make a transaction from your wallet to deploy it.

### "Invalid transaction nonce"
**Solution:** Wait for previous transaction to confirm before sending next one.

### "Mismatch compiled class hash"
**Solution:** 
1. Check compiler version compatibility
2. Rebuild: `scarb clean && scarb build`
3. Use `sncast` instead of `starkli`

### "CORS policy blocked"
**Solution:** Use Alchemy or Infura RPC in frontend, not public RPCs.

### "Insufficient balance"
**Solution:** Get testnet STRK from faucet.

### "Execute failed"
**Common causes:**
- No STRK for gas
- Account not deployed
- Invalid constructor arguments
- Contract logic error (check Voyager for details)

---

## 🎯 Development Workflow

### 1. Local Development
```bash
# Terminal 1: Start devnet
starknet-devnet --seed 0

# Terminal 2: Deploy to local
sncast --network devnet deploy ...

# Terminal 3: Run frontend
cd frontend && npm run dev

# Terminal 4: Run AI service
cd ai-service && python app.py
```

### 2. Test on Sepolia
```bash
# Build
cd contracts && scarb build

# Deploy
./scripts/deploy.sh sepolia deployer

# Update frontend env
# Edit frontend/.env.local with new addresses

# Test frontend
cd frontend && npm run dev
```

### 3. Deploy to Mainnet
```bash
# Final audit
# Security review
# Test with small amounts first

# Deploy
./scripts/deploy.sh mainnet mainnet-deployer

# Update production env
# Monitor closely
```

---

## 💡 Pro Tips

1. **Always fund accounts before deploying them**
2. **Use named accounts in snfoundry.toml for easy management**
3. **Check Voyager for detailed error messages**
4. **Pin your tool versions to avoid breaking changes**
5. **Test contract interactions with `sncast call` before `invoke`**
6. **Keep deployment records in `deployments/` directory**
7. **Use environment variables for contract addresses**
8. **Never commit private keys or API keys to git**

---

## 🆘 Need Help?

- **Starknet Discord**: https://discord.gg/starknet
- **Community Forum**: https://community.starknet.io
- **Stack Overflow**: Tag `starknet` or `cairo`
- **GitHub Issues**: Project-specific issues

---

**Last Updated**: 2025-12-05  
**Version**: 1.0.0

