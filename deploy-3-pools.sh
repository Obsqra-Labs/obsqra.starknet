#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Deploy 3 StrategyRouter Pools for Obsqra (Conservative, Balanced, Aggressive)
# Uses the already-deployed StrategyRouterV2 class hash
# ═══════════════════════════════════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Deploy 3 Obsqra Pools on Starknet Sepolia${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"

RPC_URL="https://starknet-sepolia-rpc.publicnode.com"
DEPLOYER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
PRIVATE_KEY="0x7fd44d52324945e2d9f2e62bd2dadb794e2274dbd0955251aeca6cc96153afc"

# Class hash from existing deployment
V2_CLASS_HASH="0x05ab44c93155b9b84683761070613b535cb70ab157fc533bc64b1b8c627f3061"

# Existing contract addresses
JEDISWAP="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
EKUBO="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
RISK_ENGINE="0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
DAO_MANAGER="0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
STRK="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

# Already deployed Balanced (50/50)
BALANCED="0x06adc017f51d9191b11f0f75182b065a1aa37a216b4a04939468b49a2fb09b79"

echo ""
echo -e "${YELLOW}Deploying 3 Pools...${NC}"
echo ""

# Conservative (70% Jedi, 30% Ekubo)
echo -e "${CYAN}1️⃣  Conservative Pool (70% Jedi, 30% Ekubo)${NC}"
CONSERVATIVE=$(starkli deploy \
  --rpc $RPC_URL \
  --private-key $PRIVATE_KEY \
  --watch \
  $V2_CLASS_HASH \
  $DEPLOYER \
  $JEDISWAP \
  $EKUBO \
  $RISK_ENGINE \
  $DAO_MANAGER \
  $STRK 2>&1 | grep -oP '0x[a-fA-F0-9]{64}' | tail -1)

if [ -z "$CONSERVATIVE" ]; then
  echo -e "${RED}❌ Failed to deploy Conservative pool${NC}"
  exit 1
fi
echo -e "✅ Conservative: ${GREEN}$CONSERVATIVE${NC}"

# Aggressive (30% Jedi, 70% Ekubo)
echo ""
echo -e "${CYAN}2️⃣  Aggressive Pool (30% Jedi, 70% Ekubo)${NC}"
AGGRESSIVE=$(starkli deploy \
  --rpc $RPC_URL \
  --private-key $PRIVATE_KEY \
  --watch \
  $V2_CLASS_HASH \
  $DEPLOYER \
  $JEDISWAP \
  $EKUBO \
  $RISK_ENGINE \
  $DAO_MANAGER \
  $STRK 2>&1 | grep -oP '0x[a-fA-F0-9]{64}' | tail -1)

if [ -z "$AGGRESSIVE" ]; then
  echo -e "${RED}❌ Failed to deploy Aggressive pool${NC}"
  exit 1
fi
echo -e "✅ Aggressive: ${GREEN}$AGGRESSIVE${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ 3 Pools Deployed Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

# Save to deployment file
cat > /opt/obsqra.starknet/deployments/sepolia-3pools.json << EOF
{
  "network": "sepolia",
  "pools": {
    "conservative": {
      "name": "Conservative",
      "allocation": "70% JediSwap, 30% Ekubo",
      "riskLevel": "Low",
      "targetAPY": "5-8%",
      "address": "$CONSERVATIVE"
    },
    "balanced": {
      "name": "Balanced",
      "allocation": "50% JediSwap, 50% Ekubo",
      "riskLevel": "Medium",
      "targetAPY": "8-12%",
      "address": "$BALANCED"
    },
    "aggressive": {
      "name": "Aggressive",
      "allocation": "30% JediSwap, 70% Ekubo",
      "riskLevel": "High",
      "targetAPY": "12-20%",
      "address": "$AGGRESSIVE"
    }
  },
  "deployedAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "deployer": "$DEPLOYER",
  "classHash": "$V2_CLASS_HASH"
}
EOF

echo ""
echo -e "${CYAN}📋 Pool Addresses:${NC}"
echo ""
echo -e "Conservative (Low Risk):   ${GREEN}$CONSERVATIVE${NC}"
echo -e "Balanced (Medium Risk):    ${GREEN}$BALANCED${NC}"
echo -e "Aggressive (High Risk):    ${GREEN}$AGGRESSIVE${NC}"
echo ""
echo -e "${CYAN}📄 Details saved to: sepolia-3pools.json${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update frontend/.env.local with NEXT_PUBLIC_POOLS config"
echo -e "2. Build pool selection UI"
echo -e "3. Update Dashboard to let users choose pools"
echo ""

