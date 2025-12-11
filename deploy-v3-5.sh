#!/bin/bash
# Deploy StrategyRouterV3.5 with all v3 functions, fixed user balances, and MIST integration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Deploy StrategyRouterV3.5 (Unified + MIST) to Starknet Sepolia${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"

# Configuration
DEPLOYER_ADDRESS="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
ACCOUNT_PROFILE="deployer"

# Contract addresses
RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
DAO_MANAGER="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"

# Protocol addresses
JEDISWAP_ROUTER="0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21"
JEDISWAP_NFT_MANAGER="0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399"
JEDISWAP_FACTORY="0x050d3df81b920d3e608c4f7aeb67945a830413f618a1cf486bdcce66a395109c"  # V2 Factory (Sepolia)
EKUBO_CORE="0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384"
EKUBO_POSITIONS="0x06a2aee84bb0ed5dded4384ddd0e40e9c1372b818668375ab8e3ec08807417e5"

# Tokens
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
ETH_TOKEN="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

# MIST Chamber (mainnet address - Sepolia not available, use 0x0 for now, can be set later)
MIST_CHAMBER="0x063eab2f19523fc8578c66a3ddf248d72094c65154b6dd7680b6e05a64845277"

echo ""
echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
echo -e "  Owner:           ${CYAN}$DEPLOYER_ADDRESS${NC}"
echo -e "  JediSwap Router: ${CYAN}$JEDISWAP_ROUTER${NC}"
echo -e "  JediSwap NFT:    ${CYAN}$JEDISWAP_NFT_MANAGER${NC}"
echo -e "  JediSwap Factory: ${CYAN}$JEDISWAP_FACTORY${NC}"
echo -e "  Ekubo Core:      ${CYAN}$EKUBO_CORE${NC}"
echo -e "  Ekubo Positions: ${CYAN}$EKUBO_POSITIONS${NC}"
echo -e "  Risk Engine:     ${CYAN}$RISK_ENGINE${NC}"
echo -e "  DAO Manager:     ${CYAN}$DAO_MANAGER${NC}"
echo -e "  Asset Token:     ${CYAN}$STRK_TOKEN${NC} ${GREEN}(STRK)${NC}"
echo -e "  MIST Chamber:    ${CYAN}$MIST_CHAMBER${NC} ${YELLOW}(mainnet - Sepolia not available)${NC}"
echo -e "  Default Allocation: ${GREEN}50% JediSwap, 50% Ekubo${NC}"
echo ""

cd /opt/obsqra.starknet/contracts

# Build
echo -e "${YELLOW}Building contracts...${NC}"
scarb build

if [ ! -f "target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json" ]; then
    echo -e "${RED}❌ Build failed! Contract class not found.${NC}"
    echo -e "${YELLOW}Expected: target/dev/obsqra_contracts_StrategyRouterV35.contract_class.json${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"

# Declare
echo ""
echo -e "${YELLOW}Declaring contract...${NC}"

CLASS_HASH_FILE="/opt/obsqra.starknet/deployments/v3_5_class_hash.txt"

if [ -f "$CLASS_HASH_FILE" ]; then
    CLASS_HASH=$(cat $CLASS_HASH_FILE)
    echo -e "Using existing class hash: ${GREEN}$CLASS_HASH${NC}"
    echo -e "${YELLOW}⚠️  To redeclare, delete: $CLASS_HASH_FILE${NC}"
else
    # Use sncast for declaration
    echo -e "Declaring contract (this may take a minute)..."
    DECLARE_OUTPUT=$(sncast --account $ACCOUNT_PROFILE declare \
        --contract-name StrategyRouterV35 \
        --network sepolia 2>&1)
    
    echo "$DECLARE_OUTPUT"
    
    CLASS_HASH=$(echo "$DECLARE_OUTPUT" | grep -oP 'class_hash:\s*\K0x[a-fA-F0-9]{64}' || \
                 echo "$DECLARE_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | head -1)
    
    if [ -z "$CLASS_HASH" ]; then
        echo -e "${RED}❌ Failed to extract class hash${NC}"
        exit 1
    fi
    
    mkdir -p /opt/obsqra.starknet/deployments
    echo "$CLASS_HASH" > $CLASS_HASH_FILE
    echo -e "${GREEN}✅ Class hash saved: $CLASS_HASH${NC}"
fi

# Deploy
echo ""
echo -e "${YELLOW}Deploying StrategyRouterV3.5...${NC}"

DEPLOY_OUTPUT=$(sncast --account $ACCOUNT_PROFILE deploy \
    --class-hash $CLASS_HASH \
    --constructor-calldata \
        $DEPLOYER_ADDRESS \
        $JEDISWAP_ROUTER \
        $JEDISWAP_NFT_MANAGER \
        $JEDISWAP_FACTORY \
        $EKUBO_CORE \
        $EKUBO_POSITIONS \
        $RISK_ENGINE \
        $DAO_MANAGER \
        $STRK_TOKEN \
        5000 \
        5000 \
        $MIST_CHAMBER \
    --network sepolia 2>&1)

echo "$DEPLOY_OUTPUT"

CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep -oP 'contract_address:\s*\K0x[a-fA-F0-9]{64}' || \
                   echo "$DEPLOY_OUTPUT" | grep -oP '0x[a-fA-F0-9]{64}' | tail -1)

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo -e "${RED}❌ Failed to extract contract address${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ StrategyRouterV3.5 Deployed!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Contract Address: ${CYAN}$CONTRACT_ADDRESS${NC}"
echo -e "Class Hash:       ${CYAN}$CLASS_HASH${NC}"
echo -e "Asset Token:      ${CYAN}$STRK_TOKEN${NC} ${GREEN}(STRK)${NC}"
echo -e "MIST Chamber:     ${CYAN}$MIST_CHAMBER${NC}"
echo ""

# Save deployment
DEPLOY_JSON="/opt/obsqra.starknet/deployments/sepolia-v3-5.json"
cat > $DEPLOY_JSON << EOF
{
  "network": "sepolia",
  "version": "v3.5",
  "deployedAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "contracts": {
    "strategyRouterV35": "$CONTRACT_ADDRESS",
    "riskEngine": "$RISK_ENGINE",
    "daoConstraintManager": "$DAO_MANAGER",
    "mistChamber": "$MIST_CHAMBER"
  },
  "classHashes": {
    "strategyRouterV35": "$CLASS_HASH"
  },
  "configuration": {
    "owner": "$DEPLOYER_ADDRESS",
    "jediswapRouter": "$JEDISWAP_ROUTER",
    "jediswapNftManager": "$JEDISWAP_NFT_MANAGER",
    "jediswapFactory": "$JEDISWAP_FACTORY",
    "ekuboCore": "$EKUBO_CORE",
    "ekuboPositions": "$EKUBO_POSITIONS",
    "riskEngine": "$RISK_ENGINE",
    "daoManager": "$DAO_MANAGER",
    "assetToken": "$STRK_TOKEN",
    "assetTokenName": "STRK",
    "mistChamber": "$MIST_CHAMBER",
    "defaultAllocation": {
      "jediswapBps": 5000,
      "ekuboBps": 5000
    },
    "defaultSlippage": {
      "swapBps": 100,
      "liquidityBps": 50
    }
  },
  "features": {
    "userBalanceTracking": true,
    "fixedWithdrawLogic": true,
    "allV3Functions": true,
    "mistIntegration": true,
    "slippageProtection": true,
    "individualYieldAccrual": true
  },
  "explorer": {
    "contract": "https://sepolia.starkscan.co/contract/$CONTRACT_ADDRESS",
    "class": "https://sepolia.starkscan.co/class/$CLASS_HASH"
  }
}
EOF

echo -e "${GREEN}✅ Deployment saved to: $DEPLOY_JSON${NC}"
echo ""
echo -e "${YELLOW}📋 V3.5 Features:${NC}"
echo -e "  ✅ Fixed user balance tracking (per-user balances)"
echo -e "  ✅ Fixed withdraw logic (checks user balance)"
echo -e "  ✅ All v3 functions (TVL, yield accrual, slippage)"
echo -e "  ✅ MIST.cash privacy integration (hash commitment pattern)"
echo -e "  ✅ Backward compatible (supports v2 and v3 TVL patterns)"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo -e "  1. Update frontend .env.local:"
echo -e "     ${CYAN}NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$CONTRACT_ADDRESS${NC}"
echo -e "  2. Update backend config.py:"
echo -e "     ${CYAN}STRATEGY_ROUTER_ADDRESS=$CONTRACT_ADDRESS${NC}"
echo -e "  3. Test integration tests panel (MIST functions)"
echo -e "  4. Test deposit/withdraw with fixed user balances"
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

