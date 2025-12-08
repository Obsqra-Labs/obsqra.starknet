#!/bin/bash
# Production deployment script for Obsqra.starknet contracts
# Uses sncast (Starknet Foundry) for reliable deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════════"
echo "  Obsqra.starknet - Contract Deployment Script"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if sncast is installed
if ! command -v sncast &> /dev/null; then
    echo -e "${RED}Error: sncast not found${NC}"
    echo "Install Starknet Foundry: https://foundry-rs.github.io/starknet-foundry/"
    exit 1
fi

# Check if in correct directory
if [ ! -d "contracts" ]; then
    echo -e "${RED}Error: Must run from project root${NC}"
    exit 1
fi

# Parse arguments
NETWORK="${1:-sepolia}"
ACCOUNT="${2:-deployer}"

echo -e "${YELLOW}Configuration:${NC}"
echo "  Network: $NETWORK"
echo "  Account: $ACCOUNT"
echo ""

# Navigate to contracts directory
cd contracts

# Build contracts
echo -e "${YELLOW}[1/4] Building contracts...${NC}"
scarb build
echo -e "${GREEN}✓ Build complete${NC}"
echo ""

# Declare contracts
echo -e "${YELLOW}[2/4] Declaring contracts...${NC}"

echo "  → RiskEngine"
RISK_ENGINE_CLASS=$(sncast --account $ACCOUNT declare \
    --contract-name RiskEngine \
    --network $NETWORK 2>&1 | grep "class_hash" | awk '{print $2}')

echo "  → DAOConstraintManager"
DAO_MANAGER_CLASS=$(sncast --account $ACCOUNT declare \
    --contract-name DAOConstraintManager \
    --network $NETWORK 2>&1 | grep "class_hash" | awk '{print $2}')

echo "  → StrategyRouter"
STRATEGY_ROUTER_CLASS=$(sncast --account $ACCOUNT declare \
    --contract-name StrategyRouter \
    --network $NETWORK 2>&1 | grep "class_hash" | awk '{print $2}')

echo -e "${GREEN}✓ All contracts declared${NC}"
echo ""

# Deploy contracts
echo -e "${YELLOW}[3/4] Deploying contracts...${NC}"

# Deploy RiskEngine
echo "  → RiskEngine"
RISK_ENGINE_RESULT=$(sncast --account $ACCOUNT deploy \
    --class-hash $RISK_ENGINE_CLASS \
    --network $NETWORK)
RISK_ENGINE_ADDR=$(echo "$RISK_ENGINE_RESULT" | grep "contract_address" | awk '{print $2}')

# Deploy DAOConstraintManager
echo "  → DAOConstraintManager"
DAO_MANAGER_RESULT=$(sncast --account $ACCOUNT deploy \
    --class-hash $DAO_MANAGER_CLASS \
    --constructor-calldata 6000 2 3000 1000000000000000000 \
    --network $NETWORK)
DAO_MANAGER_ADDR=$(echo "$DAO_MANAGER_RESULT" | grep "contract_address" | awk '{print $2}')

# Deploy StrategyRouter
echo "  → StrategyRouter"
STRATEGY_ROUTER_RESULT=$(sncast --account $ACCOUNT deploy \
    --class-hash $STRATEGY_ROUTER_CLASS \
    --constructor-calldata \
        $RISK_ENGINE_ADDR \
        $DAO_MANAGER_ADDR \
        0x123 0x456 0x789 \
        3333 3333 3334 \
    --network $NETWORK)
STRATEGY_ROUTER_ADDR=$(echo "$STRATEGY_ROUTER_RESULT" | grep "contract_address" | awk '{print $2}')

echo -e "${GREEN}✓ All contracts deployed${NC}"
echo ""

# Save deployment info
echo -e "${YELLOW}[4/4] Saving deployment info...${NC}"

DEPLOYMENT_FILE="../deployments/${NETWORK}.json"
cat > $DEPLOYMENT_FILE <<EOF
{
  "network": "$NETWORK",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "RiskEngine": {
    "address": "$RISK_ENGINE_ADDR",
    "class_hash": "$RISK_ENGINE_CLASS"
  },
  "DAOConstraintManager": {
    "address": "$DAO_MANAGER_ADDR",
    "class_hash": "$DAO_MANAGER_CLASS"
  },
  "StrategyRouter": {
    "address": "$STRATEGY_ROUTER_ADDR",
    "class_hash": "$STRATEGY_ROUTER_CLASS"
  }
}
EOF

echo -e "${GREEN}✓ Deployment info saved to $DEPLOYMENT_FILE${NC}"
echo ""

# Summary
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Contract Addresses:"
echo "  RiskEngine:           $RISK_ENGINE_ADDR"
echo "  DAOConstraintManager: $DAO_MANAGER_ADDR"
echo "  StrategyRouter:       $STRATEGY_ROUTER_ADDR"
echo ""
echo "View on Voyager:"
echo "  https://sepolia.voyager.online/contract/$STRATEGY_ROUTER_ADDR"
echo ""
echo "Update frontend .env.local with these addresses!"
echo "════════════════════════════════════════════════════════════════"
