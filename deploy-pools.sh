#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Deploy Obsqra Multi-Pool System to Starknet Sepolia
# - PoolFactory (creates and manages pools)
# - 3 Pools: Conservative (70/30), Balanced (50/50), Aggressive (30/70)
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}       Deploy Obsqra Multi-Pool System to Starknet Sepolia${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"

# Configuration
RPC_URL="https://starknet-sepolia-rpc.publicnode.com"
DEPLOYER_ADDRESS="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
ACCOUNT="$HOME/.starkli-wallets/deployer/account_fetched.json"
PRIVATE_KEY=$(cat $HOME/.starkli-wallets/deployer_key.txt)

# Existing contract addresses
RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
DAO_MANAGER="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"

# Protocol addresses (placeholders)
JEDISWAP_ROUTER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
EKUBO_CORE="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"

# STRK Token on Sepolia
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

# Pool caps ($100K in STRK, assuming STRK ~= $1, 18 decimals)
# 100,000 STRK = 100000 * 10^18 = 100000000000000000000000
POOL_CAP_LOW="0x56bc75e2d63100000"  # Low part of u256
POOL_CAP_HIGH="0x0"                  # High part of u256

echo ""
echo -e "${YELLOW}Step 1: Building contracts...${NC}"
cd /opt/obsqra.starknet/contracts
scarb build

echo ""
echo -e "${YELLOW}Step 2: Declaring Pool contract...${NC}"
POOL_DECLARE=$(starkli declare \
    --rpc $RPC_URL \
    --private-key $PRIVATE_KEY \
    --account $ACCOUNT \
    --watch \
    target/dev/obsqra_contracts_Pool.contract_class.json 2>&1)

echo "$POOL_DECLARE"
POOL_CLASS_HASH=$(echo "$POOL_DECLARE" | grep -oP '0x[a-fA-F0-9]{64}' | tail -1)

if [ -z "$POOL_CLASS_HASH" ]; then
    echo -e "${RED}Failed to extract Pool class hash${NC}"
    exit 1
fi

echo -e "Pool class hash: ${GREEN}$POOL_CLASS_HASH${NC}"

echo ""
echo -e "${YELLOW}Step 3: Declaring PoolFactory contract...${NC}"
FACTORY_DECLARE=$(starkli declare \
    --rpc $RPC_URL \
    --private-key $PRIVATE_KEY \
    --account $ACCOUNT \
    --watch \
    target/dev/obsqra_contracts_PoolFactory.contract_class.json 2>&1)

echo "$FACTORY_DECLARE"
FACTORY_CLASS_HASH=$(echo "$FACTORY_DECLARE" | grep -oP '0x[a-fA-F0-9]{64}' | tail -1)

if [ -z "$FACTORY_CLASS_HASH" ]; then
    echo -e "${RED}Failed to extract PoolFactory class hash${NC}"
    exit 1
fi

echo -e "PoolFactory class hash: ${GREEN}$FACTORY_CLASS_HASH${NC}"

echo ""
echo -e "${YELLOW}Step 4: Deploying PoolFactory...${NC}"
FACTORY_DEPLOY=$(starkli deploy \
    --rpc $RPC_URL \
    --private-key $PRIVATE_KEY \
    --account $ACCOUNT \
    --watch \
    $FACTORY_CLASS_HASH \
    $DEPLOYER_ADDRESS \
    $POOL_CLASS_HASH \
    $JEDISWAP_ROUTER \
    $EKUBO_CORE \
    $RISK_ENGINE \
    $DAO_MANAGER \
    $STRK_TOKEN 2>&1)

echo "$FACTORY_DEPLOY"
FACTORY_ADDRESS=$(echo "$FACTORY_DEPLOY" | grep -oP '0x[a-fA-F0-9]{64}' | tail -1)

if [ -z "$FACTORY_ADDRESS" ]; then
    echo -e "${RED}Failed to extract PoolFactory address${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  PoolFactory Deployed Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "PoolFactory Address: ${CYAN}$FACTORY_ADDRESS${NC}"
echo ""

# Save deployment info
DEPLOY_JSON="/opt/obsqra.starknet/deployments/sepolia-pools.json"
cat > $DEPLOY_JSON << EOF
{
  "network": "sepolia",
  "poolFactory": "$FACTORY_ADDRESS",
  "poolClassHash": "$POOL_CLASS_HASH",
  "factoryClassHash": "$FACTORY_CLASS_HASH",
  "pools": {},
  "deployedAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "deployer": "$DEPLOYER_ADDRESS"
}
EOF

echo ""
echo -e "${YELLOW}Step 5: Creating Conservative Pool (70% Jedi, 30% Ekubo)...${NC}"
echo -e "${CYAN}Note: This requires manual invocation via starkli invoke${NC}"
echo ""
echo -e "${CYAN}Run this command:${NC}"
echo ""
echo -e "starkli invoke \\"
echo -e "  --rpc $RPC_URL \\"
echo -e "  --private-key <PRIVATE_KEY> \\"
echo -e "  --account $ACCOUNT \\"
echo -e "  --watch \\"
echo -e "  $FACTORY_ADDRESS \\"
echo -e "  create_pool \\"
echo -e "  str:'Conservative' \\"  # name
echo -e "  $POOL_CAP_LOW $POOL_CAP_HIGH \\"  # cap (u256)
echo -e "  7000 \\"  # jediswap_pct (70%)
echo -e "  3000"     # ekubo_pct (30%)
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "Next steps:"
echo -e "1. Create 3 pools using the factory (commands above)"
echo -e "2. Update frontend with PoolFactory address"
echo -e "3. Build multi-pool UI"
echo ""

