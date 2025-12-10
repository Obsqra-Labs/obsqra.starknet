#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Deploy StrategyRouterV2 to Starknet Sepolia (UPDATED: ETH as asset_token)
# 
# Lessons Learned Applied:
# - Use sncast --network sepolia (handles RPC compatibility automatically)
# - Build with scarb build first
# - Use ETH as asset_token (not STRK)
# - Use real protocol addresses from protocol_addresses_sepolia.json
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Deploy StrategyRouterV2 (ETH as asset_token) to Starknet Sepolia${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"

# Configuration
# Using sncast --network sepolia (handles RPC compatibility automatically)
DEPLOYER_ADDRESS="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
ACCOUNT_PROFILE="deployer"  # From Scarb.toml [tool.sncast.deployer]

# Contract addresses (existing deployments)
RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
DAO_MANAGER="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"

# Protocol addresses from protocol_addresses_sepolia.json
JEDISWAP_ROUTER="0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21"  # JediSwap Swap Router
JEDISWAP_NFT_MANAGER="0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399"  # JediSwap V2 NFT Position Manager
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"

# Tokens (from protocol_addresses_sepolia.json)
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"
ETH_TOKEN="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"  # ETH (NEW: asset_token)

echo ""
echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
echo -e "  Owner:           ${CYAN}$DEPLOYER_ADDRESS${NC}"
echo -e "  JediSwap Router: ${CYAN}$JEDISWAP_ROUTER${NC}"
echo -e "  JediSwap NFT:    ${CYAN}$JEDISWAP_NFT_MANAGER${NC}"
echo -e "  Ekubo Core:      ${CYAN}$EKUBO_CORE${NC}"
echo -e "  Risk Engine:     ${CYAN}$RISK_ENGINE${NC}"
echo -e "  DAO Manager:     ${CYAN}$DAO_MANAGER${NC}"
echo -e "  Asset Token:     ${CYAN}$ETH_TOKEN${NC} ${GREEN}(ETH - NEW!)${NC}"
echo ""

# Step 1: Check deployer balance (skip - will fail during deploy if insufficient)
echo -e "${YELLOW}Step 1: Skipping balance check (will fail during deploy if insufficient)${NC}"
echo -e "${YELLOW}⚠️  Ensure deployer has STRK for gas:${NC}"
echo -e "  Address: ${CYAN}$DEPLOYER_ADDRESS${NC}"
echo -e "  Faucet:  ${CYAN}https://starknet-faucet.vercel.app/${NC}"
echo ""
cd /opt/obsqra.starknet/contracts

# Step 2: Build contracts
echo ""
echo -e "${YELLOW}Step 2: Building contracts...${NC}"
scarb build

if [ ! -f "target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json" ]; then
    echo -e "${RED}❌ Build failed! Contract not found.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"

# Step 3: Declare contract
echo ""
echo -e "${YELLOW}Step 3: Declaring StrategyRouterV2...${NC}"

# Check if already declared (class hash file)
CLASS_HASH_FILE="/opt/obsqra.starknet/deployments/v2_eth_class_hash.txt"

if [ -f "$CLASS_HASH_FILE" ]; then
    CLASS_HASH=$(cat $CLASS_HASH_FILE)
    echo -e "Using existing class hash: ${GREEN}$CLASS_HASH${NC}"
    echo -e "${YELLOW}⚠️  If contract code changed, delete this file to redeclare${NC}"
else
    # Declare using sncast (handles RPC compatibility)
    echo -e "Declaring contract (this may take a minute)..."
    
    DECLARE_OUTPUT=$(sncast --account $ACCOUNT_PROFILE declare \
        --contract-name StrategyRouterV2 \
        --network sepolia 2>&1)
    
    echo "$DECLARE_OUTPUT"
    
    # Extract class hash from output
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'class_hash:\s*\K0x[a-fA-F0-9]{64}' || \
                 echo "$DECLARE_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
    
    if [ -z "$CLASS_HASH" ]; then
        echo -e "${RED}❌ Failed to extract class hash. Check output above.${NC}"
        echo -e "${YELLOW}💡 If class already declared, you can manually extract the hash and save to:${NC}"
        echo -e "   ${CYAN}$CLASS_HASH_FILE${NC}"
        exit 1
    fi
    
    mkdir -p /opt/obsqra.starknet/deployments
    echo "$CLASS_HASH" > $CLASS_HASH_FILE
    echo -e "${GREEN}✅ Class hash saved: $CLASS_HASH${NC}"
fi

# Step 4: Deploy contract
echo ""
echo -e "${YELLOW}Step 4: Deploying StrategyRouterV2...${NC}"

# Constructor arguments (in order):
# 1. owner: ContractAddress
# 2. jediswap_router: ContractAddress (for swaps)
# 3. jediswap_nft_manager: ContractAddress (for liquidity)
# 4. ekubo_core: ContractAddress
# 5. risk_engine: ContractAddress
# 6. dao_manager: ContractAddress
# 7. asset_token: ContractAddress (ETH - NEW!)

echo -e "Constructor args:"
echo -e "  owner:            ${CYAN}$DEPLOYER_ADDRESS${NC}"
echo -e "  jediswap_router:  ${CYAN}$JEDISWAP_ROUTER${NC}"
echo -e "  jediswap_nft:     ${CYAN}$JEDISWAP_NFT_MANAGER${NC}"
echo -e "  ekubo_core:       ${CYAN}$EKUBO_CORE${NC}"
echo -e "  risk_engine:      ${CYAN}$RISK_ENGINE${NC}"
echo -e "  dao_manager:      ${CYAN}$DAO_MANAGER${NC}"
echo -e "  asset_token:      ${CYAN}$ETH_TOKEN${NC} ${GREEN}(ETH!)${NC}"
echo ""

DEPLOY_OUTPUT=$(sncast --account $ACCOUNT_PROFILE deploy \
    --class-hash $CLASS_HASH \
    --constructor-calldata \
        $DEPLOYER_ADDRESS \
        $JEDISWAP_ROUTER \
        $JEDISWAP_NFT_MANAGER \
        $EKUBO_CORE \
        $RISK_ENGINE \
        $DAO_MANAGER \
        $ETH_TOKEN \
    --network sepolia 2>&1)

echo "$DEPLOY_OUTPUT"

# Extract contract address
CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract_address:\s*\K0x[a-fA-F0-9]{64}' || \
                   echo "$DEPLOY_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | tail -1)

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo -e "${RED}❌ Failed to extract contract address. Check output above.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ StrategyRouterV2 Deployed Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Contract Address: ${CYAN}$CONTRACT_ADDRESS${NC}"
echo -e "Class Hash:       ${CYAN}$CLASS_HASH${NC}"
echo -e "Asset Token:      ${CYAN}$ETH_TOKEN${NC} ${GREEN}(ETH)${NC}"
echo ""

# Save deployment info
DEPLOY_JSON="/opt/obsqra.starknet/deployments/sepolia-v2-eth.json"
cat > $DEPLOY_JSON << EOF
{
  "network": "sepolia",
  "deployedAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "contracts": {
    "strategyRouterV2": "$CONTRACT_ADDRESS",
    "riskEngine": "$RISK_ENGINE",
    "daoConstraintManager": "$DAO_MANAGER"
  },
  "classHashes": {
    "strategyRouterV2": "$CLASS_HASH"
  },
  "configuration": {
    "owner": "$DEPLOYER_ADDRESS",
    "jediswapRouter": "$JEDISWAP_ROUTER",
    "jediswapNftManager": "$JEDISWAP_NFT_MANAGER",
    "ekuboCore": "$EKUBO_CORE",
    "riskEngine": "$RISK_ENGINE",
    "daoManager": "$DAO_MANAGER",
    "assetToken": "$ETH_TOKEN",
    "assetTokenName": "ETH"
  },
  "explorer": {
    "contract": "https://sepolia.starkscan.co/contract/$CONTRACT_ADDRESS",
    "class": "https://sepolia.starkscan.co/class/$CLASS_HASH"
  }
}
EOF

echo -e "Deployment info saved to: ${CYAN}$DEPLOY_JSON${NC}"
echo ""

# Update frontend .env.local
ENV_FILE="/opt/obsqra.starknet/frontend/.env.local"
echo -e "${YELLOW}Step 5: Updating frontend configuration...${NC}"

if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

# Update or add STRATEGY_ROUTER_ADDRESS
if grep -q "NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS" $ENV_FILE; then
    sed -i "s|NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=.*|NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$CONTRACT_ADDRESS|" $ENV_FILE
    echo -e "✅ Updated NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS in ${CYAN}$ENV_FILE${NC}"
else
    echo "NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$CONTRACT_ADDRESS" >> $ENV_FILE
    echo -e "✅ Added NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS to ${CYAN}$ENV_FILE${NC}"
fi

echo ""

# Summary
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo ""
echo -e "1. ${CYAN}Verify on Starkscan:${NC}"
echo -e "   https://sepolia.starkscan.co/contract/$CONTRACT_ADDRESS"
echo ""
echo -e "2. ${CYAN}Test deposit with ETH:${NC}"
echo -e "   - Contract now accepts ETH deposits"
echo -e "   - Will swap half ETH → STRK"
echo -e "   - Deploys to JediSwap + Ekubo"
echo ""
echo -e "3. ${CYAN}Check contract state:${NC}"
echo -e "   sncast --account $ACCOUNT_PROFILE --network sepolia call \\"
echo -e "     --contract-address $CONTRACT_ADDRESS \\"
echo -e "     --function get_allocation"
echo ""
echo -e "4. ${CYAN}Frontend:${NC}"
echo -e "   cd /opt/obsqra.starknet/frontend && npm run build"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"

