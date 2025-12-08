#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Deploy StrategyRouterV2 to Starknet Sepolia
# Prerequisites: Fund deployer with ~0.001 ETH from https://starknet-faucet.vercel.app/
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}       Deploy StrategyRouterV2 to Starknet Sepolia${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"

# Configuration
RPC_URL="https://starknet-sepolia-rpc.publicnode.com"
DEPLOYER_ADDRESS="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
ACCOUNTS_FILE="$HOME/.starknet_accounts/starknet_open_zeppelin_accounts.json"

# Contract addresses (existing deployments)
RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
DAO_MANAGER="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"

# Protocol addresses on Sepolia (placeholders - using deployer as stand-in)
JEDISWAP_ROUTER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"  # Placeholder
EKUBO_CORE="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"      # Placeholder

# STRK Token on Sepolia
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

echo ""
echo -e "${YELLOW}Step 1: Checking deployer balance...${NC}"
BALANCE=$(starkli balance --rpc $RPC_URL $DEPLOYER_ADDRESS 2>&1)
echo -e "Deployer: ${CYAN}$DEPLOYER_ADDRESS${NC}"
echo -e "Balance: ${GREEN}$BALANCE${NC}"

if [[ "$BALANCE" == "0.000000000000000000" ]]; then
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ERROR: Deployer has 0 balance!${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Please fund the deployer wallet:${NC}"
    echo -e "  Address: ${CYAN}$DEPLOYER_ADDRESS${NC}"
    echo -e "  Faucet:  ${CYAN}https://starknet-faucet.vercel.app/${NC}"
    echo ""
    echo -e "After funding, run this script again."
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Building contracts...${NC}"
cd /opt/obsqra.starknet/contracts
scarb build

echo ""
echo -e "${YELLOW}Step 3: Declaring StrategyRouterV2...${NC}"

# Check if already declared
CLASS_HASH_FILE="/opt/obsqra.starknet/deployments/v2_class_hash.txt"

if [ -f "$CLASS_HASH_FILE" ]; then
    CLASS_HASH=$(cat $CLASS_HASH_FILE)
    echo -e "Using existing class hash: ${GREEN}$CLASS_HASH${NC}"
else
    # Declare the contract
    DECLARE_OUTPUT=$(starkli declare \
        --rpc $RPC_URL \
        --account $ACCOUNTS_FILE \
        --watch \
        target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json 2>&1)
    
    echo "$DECLARE_OUTPUT"
    
    # Extract class hash
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
    
    if [ -z "$CLASS_HASH" ]; then
        echo -e "${RED}Failed to extract class hash from declare output${NC}"
        exit 1
    fi
    
    mkdir -p /opt/obsqra.starknet/deployments
    echo "$CLASS_HASH" > $CLASS_HASH_FILE
    echo -e "Class hash saved: ${GREEN}$CLASS_HASH${NC}"
fi

echo ""
echo -e "${YELLOW}Step 4: Deploying StrategyRouterV2...${NC}"

# Constructor arguments:
# owner: ContractAddress
# jediswap_router: ContractAddress
# ekubo_core: ContractAddress
# risk_engine: ContractAddress
# dao_manager: ContractAddress
# asset_token: ContractAddress (STRK)

DEPLOY_OUTPUT=$(starkli deploy \
    --rpc $RPC_URL \
    --account $ACCOUNTS_FILE \
    --watch \
    $CLASS_HASH \
    $DEPLOYER_ADDRESS \
    $JEDISWAP_ROUTER \
    $EKUBO_CORE \
    $RISK_ENGINE \
    $DAO_MANAGER \
    $STRK_TOKEN 2>&1)

echo "$DEPLOY_OUTPUT"

# Extract contract address
CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | tail -1)

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo -e "${RED}Failed to extract contract address from deploy output${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  StrategyRouterV2 Deployed Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Contract Address: ${CYAN}$CONTRACT_ADDRESS${NC}"
echo -e "Class Hash:       ${CYAN}$CLASS_HASH${NC}"
echo ""

# Save to deployments file
DEPLOY_JSON="/opt/obsqra.starknet/deployments/sepolia-v2.json"
cat > $DEPLOY_JSON << EOF
{
  "network": "sepolia",
  "rpc": "$RPC_URL",
  "contracts": {
    "strategyRouterV2": "$CONTRACT_ADDRESS",
    "riskEngine": "$RISK_ENGINE",
    "daoConstraintManager": "$DAO_MANAGER"
  },
  "classHashes": {
    "strategyRouterV2": "$CLASS_HASH"
  },
  "deployedAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo -e "Deployment info saved to: ${CYAN}$DEPLOY_JSON${NC}"
echo ""

# Update frontend .env.local
ENV_FILE="/opt/obsqra.starknet/frontend/.env.local"
echo ""
echo -e "${YELLOW}Step 5: Updating frontend configuration...${NC}"

# Update or add STRATEGY_ROUTER_ADDRESS
if grep -q "NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS" $ENV_FILE; then
    sed -i "s|NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=.*|NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$CONTRACT_ADDRESS|" $ENV_FILE
else
    echo "NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$CONTRACT_ADDRESS" >> $ENV_FILE
fi

echo -e "Updated ${CYAN}$ENV_FILE${NC}"
echo ""

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Next Steps:${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "1. Get MIST Chamber address for Sepolia from MIST team"
echo -e "2. Add to .env.local:"
echo -e "   ${CYAN}NEXT_PUBLIC_MIST_CHAMBER_ADDRESS=0x<chamber_address>${NC}"
echo ""
echo -e "3. Rebuild frontend:"
echo -e "   ${CYAN}cd /opt/obsqra.starknet/frontend && npm run build${NC}"
echo ""
echo -e "4. Restart frontend:"
echo -e "   ${CYAN}PORT=3003 npm run start${NC}"
echo ""
echo -e "5. View on Starkscan:"
echo -e "   ${CYAN}https://sepolia.starkscan.co/contract/$CONTRACT_ADDRESS${NC}"
echo ""
