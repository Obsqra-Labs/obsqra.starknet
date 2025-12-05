#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════"
echo "🚀 Starknet Contract Deployment - Step by Step"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Wallet: 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027"
echo "Network: Starknet Sepolia"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 1: Installing Tools${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Install Scarb
if ! command -v scarb &> /dev/null; then
    echo "📦 Installing Scarb..."
    curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo -e "${GREEN}✅ Scarb installed${NC}"
else
    echo -e "${GREEN}✅ Scarb already installed${NC}"
fi

# Install Starkli
if ! command -v starkli &> /dev/null; then
    echo "📦 Installing Starkli..."
    curl https://get.starkli.sh | sh
    $HOME/.starkli/bin/starkliup
    export PATH="$HOME/.starkli/bin:$PATH"
    echo -e "${GREEN}✅ Starkli installed${NC}"
else
    echo -e "${GREEN}✅ Starkli already installed${NC}"
fi

echo ""
scarb --version
starkli --version
echo ""

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 2: Compiling Contracts${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd /opt/obsqra.starknet/contracts
scarb build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Contracts compiled successfully${NC}"
    echo ""
    echo "📋 Compiled contracts:"
    ls -lh target/dev/*.contract_class.json | awk '{print "   " $9}'
else
    echo -e "${RED}❌ Compilation failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 3: Setup Deployer Account${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

mkdir -p ~/.starkli-wallets/deployer

echo "📥 Fetching account from Sepolia..."
starkli account fetch \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --output ~/.starkli-wallets/deployer/account.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Account fetched successfully${NC}"
else
    echo -e "${RED}❌ Failed to fetch account${NC}"
    exit 1
fi

echo ""
if [ ! -f ~/.starkli-wallets/deployer/keystore.json ]; then
    echo -e "${YELLOW}🔑 Creating keystore...${NC}"
    echo ""
    echo "You'll be prompted to:"
    echo "  1. Enter your PRIVATE KEY (from Argent X: Settings → Export Private Key)"
    echo "  2. Create a PASSWORD for this keystore"
    echo ""
    starkli signer keystore from-key ~/.starkli-wallets/deployer/keystore.json
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Keystore created${NC}"
    else
        echo -e "${RED}❌ Failed to create keystore${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Keystore already exists${NC}"
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 4: Ready to Deploy!${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Tools installed ✅"
echo "Contracts compiled ✅"
echo "Account setup ✅"
echo ""
echo -e "${GREEN}Ready to deploy contracts!${NC}"
echo ""
echo "════════════════════════════════════════════════════════"
echo "📝 Next: Deploy Each Contract"
echo "════════════════════════════════════════════════════════"
echo ""
echo "I'll now show you the commands to deploy each contract."
echo "You can run them one by one, or I can create deployment scripts."
echo ""

# Create deployment scripts
cat > /opt/obsqra.starknet/deploy-risk-engine.sh << 'EOFSCRIPT'
#!/bin/bash
echo "Deploying RiskEngine..."
cd /opt/obsqra.starknet/contracts

echo "1️⃣  Declaring contract..."
DECLARE_OUTPUT=$(starkli declare \
  target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json 2>&1)

echo "$DECLARE_OUTPUT"

CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'Class hash declared: \K0x[0-9a-fA-F]+' || echo "$DECLARE_OUTPUT" | grep -oP 'Class hash: \K0x[0-9a-fA-F]+')

if [ -z "$CLASS_HASH" ]; then
    echo "❌ Failed to extract class hash. Output was:"
    echo "$DECLARE_OUTPUT"
    exit 1
fi

echo "✅ Class hash: $CLASS_HASH"
echo ""

echo "2️⃣  Deploying contract..."
DEPLOY_OUTPUT=$(starkli deploy \
  $CLASS_HASH \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json 2>&1)

echo "$DEPLOY_OUTPUT"

CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -oP 'Contract deployed: \K0x[0-9a-fA-F]+')

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "❌ Failed to extract contract address"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "🎉 RiskEngine Deployed!"
echo "════════════════════════════════════════════════════════"
echo "Class Hash:       $CLASS_HASH"
echo "Contract Address: $CONTRACT_ADDRESS"
echo "Voyager:          https://sepolia.voyager.online/contract/$CONTRACT_ADDRESS"
echo "════════════════════════════════════════════════════════"

# Save to file
echo "$CONTRACT_ADDRESS" > /opt/obsqra.starknet/risk-engine-address.txt
echo "Saved to: /opt/obsqra.starknet/risk-engine-address.txt"
EOFSCRIPT

cat > /opt/obsqra.starknet/deploy-strategy-router.sh << 'EOFSCRIPT'
#!/bin/bash
echo "Deploying StrategyRouter..."
cd /opt/obsqra.starknet/contracts

echo "1️⃣  Declaring contract..."
DECLARE_OUTPUT=$(starkli declare \
  target/dev/obsqra_contracts_StrategyRouter.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json 2>&1)

echo "$DECLARE_OUTPUT"

CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'Class hash declared: \K0x[0-9a-fA-F]+' || echo "$DECLARE_OUTPUT" | grep -oP 'Class hash: \K0x[0-9a-fA-F]+')

if [ -z "$CLASS_HASH" ]; then
    echo "❌ Failed to extract class hash"
    exit 1
fi

echo "✅ Class hash: $CLASS_HASH"
echo ""

echo "2️⃣  Deploying contract..."
DEPLOY_OUTPUT=$(starkli deploy \
  $CLASS_HASH \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json 2>&1)

echo "$DEPLOY_OUTPUT"

CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -oP 'Contract deployed: \K0x[0-9a-fA-F]+')

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "❌ Failed to extract contract address"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "🎉 StrategyRouter Deployed!"
echo "════════════════════════════════════════════════════════"
echo "Class Hash:       $CLASS_HASH"
echo "Contract Address: $CONTRACT_ADDRESS"
echo "Voyager:          https://sepolia.voyager.online/contract/$CONTRACT_ADDRESS"
echo "════════════════════════════════════════════════════════"

echo "$CONTRACT_ADDRESS" > /opt/obsqra.starknet/strategy-router-address.txt
echo "Saved to: /opt/obsqra.starknet/strategy-router-address.txt"
EOFSCRIPT

cat > /opt/obsqra.starknet/deploy-dao-constraint.sh << 'EOFSCRIPT'
#!/bin/bash
echo "Deploying DAOConstraintManager..."
cd /opt/obsqra.starknet/contracts

echo "1️⃣  Declaring contract..."
DECLARE_OUTPUT=$(starkli declare \
  target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json 2>&1)

echo "$DECLARE_OUTPUT"

CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'Class hash declared: \K0x[0-9a-fA-F]+' || echo "$DECLARE_OUTPUT" | grep -oP 'Class hash: \K0x[0-9a-fA-F]+')

if [ -z "$CLASS_HASH" ]; then
    echo "❌ Failed to extract class hash"
    exit 1
fi

echo "✅ Class hash: $CLASS_HASH"
echo ""

echo "2️⃣  Deploying contract..."
DEPLOY_OUTPUT=$(starkli deploy \
  $CLASS_HASH \
  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json 2>&1)

echo "$DEPLOY_OUTPUT"

CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -oP 'Contract deployed: \K0x[0-9a-fA-F]+')

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "❌ Failed to extract contract address"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "🎉 DAOConstraintManager Deployed!"
echo "════════════════════════════════════════════════════════"
echo "Class Hash:       $CLASS_HASH"
echo "Contract Address: $CONTRACT_ADDRESS"
echo "Voyager:          https://sepolia.voyager.online/contract/$CONTRACT_ADDRESS"
echo "════════════════════════════════════════════════════════"

echo "$CONTRACT_ADDRESS" > /opt/obsqra.starknet/dao-constraint-address.txt
echo "Saved to: /opt/obsqra.starknet/dao-constraint-address.txt"
EOFSCRIPT

chmod +x /opt/obsqra.starknet/deploy-*.sh

echo "✅ Deployment scripts created:"
echo "   • /opt/obsqra.starknet/deploy-risk-engine.sh"
echo "   • /opt/obsqra.starknet/deploy-strategy-router.sh"
echo "   • /opt/obsqra.starknet/deploy-dao-constraint.sh"
echo ""
echo "Run them one by one:"
echo ""
echo "   bash /opt/obsqra.starknet/deploy-risk-engine.sh"
echo "   bash /opt/obsqra.starknet/deploy-strategy-router.sh"
echo "   bash /opt/obsqra.starknet/deploy-dao-constraint.sh"
echo ""
