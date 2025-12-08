#!/bin/bash
# Your Account: 0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd
# Copy and paste these commands into your terminal

echo "════════════════════════════════════════════════════════"
echo " Starknet Contract Deployment"
echo "════════════════════════════════════════════════════════"
echo "Account: 0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd"
echo ""

cat << 'EOF'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: Install Tools
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Install Scarb
curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Install Starkli
curl https://get.starkli.sh | sh
$HOME/.starkli/bin/starkliup
export PATH="$HOME/.starkli/bin:$PATH"

# Verify installation
scarb --version
starkli --version


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2: Compile Contracts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd /opt/obsqra.starknet/contracts
scarb build

# Verify compiled files
ls -la target/dev/*.contract_class.json


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: Setup Deployer Account
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

mkdir -p ~/.starkli-wallets/deployer

# Fetch your account from Sepolia
starkli account fetch \
  0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --output ~/.starkli-wallets/deployer/account.json

# Create keystore (you'll enter your private key)
starkli signer keystore from-key ~/.starkli-wallets/deployer/keystore.json


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4: Deploy RiskEngine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd /opt/obsqra.starknet/contracts

# Declare the contract
starkli declare \
  target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# ⬇️ SAVE THE CLASS HASH FROM ABOVE OUTPUT! ⬇️
# Then deploy (replace <CLASS_HASH> with the actual hash):

starkli deploy \
  <CLASS_HASH> \
  0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# ⬇️ SAVE THE CONTRACT ADDRESS FROM ABOVE OUTPUT! ⬇️


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5: Deploy StrategyRouter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Declare
starkli declare \
  target/dev/obsqra_contracts_StrategyRouter.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# Deploy (replace <CLASS_HASH>):
starkli deploy \
  <CLASS_HASH> \
  0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# ⬇️ SAVE THE CONTRACT ADDRESS! ⬇️


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 6: Deploy DAOConstraintManager
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Declare
starkli declare \
  target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# Deploy (replace <CLASS_HASH>):
starkli deploy \
  <CLASS_HASH> \
  0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# ⬇️ SAVE THE CONTRACT ADDRESS! ⬇️


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 7: Update Frontend .env.local
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd /opt/obsqra.starknet/frontend

# Edit .env.local with your deployed addresses
nano .env.local

# Or use this command (replace the addresses):
cat > .env.local << 'ENVEOF'
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x<YOUR_RISK_ENGINE_ADDRESS>
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x<YOUR_STRATEGY_ROUTER_ADDRESS>
NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=0x<YOUR_DAO_ADDRESS>
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
ENVEOF


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 8: Restart Frontend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

pkill -f "PORT=3002"
PORT=3002 npm run dev

# Open: http://localhost:3002


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Done!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your contracts are now live on Starknet Sepolia!

View them on Voyager:
https://sepolia.voyager.online/contract/<YOUR_CONTRACT_ADDRESS>

EOF
