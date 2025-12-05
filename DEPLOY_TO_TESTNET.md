# Deploy to Starknet Testnet - Quick Guide

## Prerequisites Check

- [x] Wallet set up (ArgentX/Braavos)
- [ ] Wallet on Sepolia Testnet
- [ ] Have testnet ETH (>0.001 ETH)
- [ ] Contracts built (`scarb build`)

## Quick Deploy (3 Steps)

### Step 1: Import Your Wallet to sncast

```bash
cd /opt/obsqra.starknet/contracts

# Import your wallet (use your actual private key)
sncast account import \
  --url https://starknet-sepolia.public.blastapi.io \
  --name my_testnet \
  --address YOUR_WALLET_ADDRESS \
  --private-key YOUR_PRIVATE_KEY \
  --type oz

# Or create a new account just for deployment
sncast account create \
  --url https://starknet-sepolia.public.blastapi.io \
  --name my_testnet
```

**Get Private Key from ArgentX:**
1. Open ArgentX
2. Click on Settings (gear icon)
3. Select your account
4. Click "Export private key"
5. Enter password
6. Copy the key

### Step 2: Declare Contracts

```bash
# Set environment
export STARKNET_RPC=https://starknet-sepolia.public.blastapi.io

# Declare RiskEngine
sncast declare \
  --url $STARKNET_RPC \
  --account my_testnet \
  --contract-name RiskEngine

# Save the class hash from output
# Example: 0x04a7...8d3f

# Declare DAOConstraintManager
sncast declare \
  --url $STARKNET_RPC \
  --account my_testnet \
  --contract-name DAOConstraintManager

# Declare StrategyRouter
sncast declare \
  --url $STARKNET_RPC \
  --account my_testnet \
  --contract-name StrategyRouter
```

### Step 3: Deploy Contracts

```bash
# Deploy RiskEngine
RISK_ENGINE=$(sncast deploy \
  --url $STARKNET_RPC \
  --account my_testnet \
  --class-hash RISK_ENGINE_CLASS_HASH \
  --constructor-calldata YOUR_WALLET_ADDRESS)

echo "RiskEngine: $RISK_ENGINE"

# Deploy DAOConstraintManager
DAO_MANAGER=$(sncast deploy \
  --url $STARKNET_RPC \
  --account my_testnet \
  --class-hash DAO_MANAGER_CLASS_HASH \
  --constructor-calldata \
    YOUR_WALLET_ADDRESS \
    6000 \
    3 \
    5000 \
    1000000)

echo "DAOConstraintManager: $DAO_MANAGER"

# Deploy StrategyRouter
# Note: Use placeholder addresses for Aave, Lido, Compound (or real testnet addresses if you have them)
STRATEGY_ROUTER=$(sncast deploy \
  --url $STARKNET_RPC \
  --account my_testnet \
  --class-hash ROUTER_CLASS_HASH \
  --constructor-calldata \
    YOUR_WALLET_ADDRESS \
    0x456 \
    0x789 \
    0xabc \
    $RISK_ENGINE)

echo "StrategyRouter: $STRATEGY_ROUTER"
```

## Automated Deploy Script

I'll create a script that does all of this for you:

```bash
cd /opt/obsqra.starknet
./scripts/deploy-testnet.sh YOUR_WALLET_ADDRESS
```

## After Deployment

### Save Contract Addresses

```bash
# Addresses will be saved to .env.testnet
cat .env.testnet
```

### Verify on Block Explorer

Visit:
- Voyager: https://sepolia.voyager.online/
- Starkscan: https://sepolia.starkscan.co/

Paste your contract addresses to see them live!

### Update Frontend

```bash
cd /opt/obsqra.starknet/frontend

# Create .env.local with deployed addresses
cat > .env.local << EOF
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=$RISK_ENGINE
NEXT_PUBLIC_DAO_MANAGER_ADDRESS=$DAO_MANAGER
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$STRATEGY_ROUTER
EOF
```

## Test Your Deployment

```bash
# Call a contract function
sncast call \
  --url $STARKNET_RPC \
  --contract-address $DAO_MANAGER \
  --function get_constraints

# Should return: (6000, 3, 5000, 1000000)
```

## Costs

Testnet deployment costs (FREE testnet ETH):
- Declare contract: ~0.0001 ETH
- Deploy contract: ~0.0002 ETH
- Total for 3 contracts: ~0.001 ETH

## Troubleshooting

### "Insufficient funds"
Get more from faucet: https://starknet-faucet.vercel.app/

### "Account not found"
Make sure you imported your account correctly with `sncast account import`

### "Invalid class hash"
Make sure you used the class hash from the `declare` command output

### "Constructor arguments invalid"
Check that:
- Addresses are in hex format (0x...)
- Numbers are in decimal (6000, not 0x1770)
- Order matches constructor parameters

## Ready?

Run this to start deployment:

```bash
cd /opt/obsqra.starknet/contracts
# First, build contracts
scarb build

# Then deploy (I'll create a script for you)
```

Want me to create an automated deployment script that handles everything?

