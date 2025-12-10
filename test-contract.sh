#!/bin/bash
# Test StrategyRouterV2 contract functions

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
CONTRACT_ADDRESS="0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e"
ACCOUNT_PROFILE="deployer"
STRK_TOKEN="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

# Test amount: 0.1 STRK (100000000000000000 wei)
TEST_AMOUNT="100000000000000000"
TEST_AMOUNT_LOW="100000000000000000"
TEST_AMOUNT_HIGH="0"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Testing StrategyRouterV2 Contract${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Contract: ${CYAN}$CONTRACT_ADDRESS${NC}"
echo -e "Network:  ${CYAN}Starknet Sepolia${NC}"
echo ""

cd /opt/obsqra.starknet/contracts

# Test 1: Check allocation
echo -e "${YELLOW}📊 Test 1: Check current allocation${NC}"
sncast --profile $ACCOUNT_PROFILE call \
    --contract-address $CONTRACT_ADDRESS \
    --function get_allocation \
    2>&1 | grep -E "(jediswap|ekubo|error)" || echo "  Allocation check complete"
echo ""

# Test 2: Check position counts (should be 0 initially)
echo -e "${YELLOW}📊 Test 2: Check position counts${NC}"
echo -e "  JediSwap positions:"
sncast --profile $ACCOUNT_PROFILE call \
    --contract-address $CONTRACT_ADDRESS \
    --function get_jediswap_position_count \
    2>&1 | tail -3 || true
echo ""
echo -e "  Ekubo positions:"
sncast --profile $ACCOUNT_PROFILE call \
    --contract-address $CONTRACT_ADDRESS \
    --function get_ekubo_position_count \
    2>&1 | tail -3 || true
echo ""

# Test 3: Approve STRK for deposit
echo -e "${YELLOW}💰 Test 3: Approve STRK token for deposit${NC}"
echo -e "  Approving $TEST_AMOUNT wei (0.1 STRK)..."
sncast --profile $ACCOUNT_PROFILE invoke \
    --contract-address $STRK_TOKEN \
    --function approve \
    --calldata $CONTRACT_ADDRESS $TEST_AMOUNT_LOW $TEST_AMOUNT_HIGH \
    2>&1 | grep -E "(command:|transaction_hash|error)" || true
echo ""

# Wait a moment for approval
sleep 3

# Test 4: Deposit STRK
echo -e "${YELLOW}💰 Test 4: Deposit STRK to contract${NC}"
echo -e "  Depositing $TEST_AMOUNT wei (0.1 STRK)..."
DEPOSIT_TX=$(sncast --profile $ACCOUNT_PROFILE invoke \
    --contract-address $CONTRACT_ADDRESS \
    --function deposit \
    --calldata $TEST_AMOUNT_LOW $TEST_AMOUNT_HIGH \
    2>&1)

if echo "$DEPOSIT_TX" | grep -q "transaction_hash"; then
    TX_HASH=$(echo "$DEPOSIT_TX" | grep "transaction_hash" | awk '{print $2}')
    echo -e "  ${GREEN}✅ Deposit transaction: $TX_HASH${NC}"
    echo -e "  View on Starkscan: https://sepolia.starkscan.co/tx/$TX_HASH"
else
    echo -e "  ${RED}❌ Deposit failed${NC}"
    echo "$DEPOSIT_TX"
fi
echo ""

# Wait for transaction to be included
echo -e "${YELLOW}⏳ Waiting for transaction to be included...${NC}"
sleep 10

# Test 5: Check user balance
echo -e "${YELLOW}📊 Test 5: Check user balance after deposit${NC}"
DEPLOYER_ADDRESS="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
sncast --profile $ACCOUNT_PROFILE call \
    --contract-address $CONTRACT_ADDRESS \
    --function get_user_balance \
    --calldata $DEPLOYER_ADDRESS \
    2>&1 | tail -5 || true
echo ""

# Test 6: Deploy to protocols (if deposit succeeded)
echo -e "${YELLOW}🚀 Test 6: Deploy to protocols${NC}"
echo -e "  This will swap STRK to ETH and add liquidity to both JediSwap and Ekubo..."
echo -e "  ${YELLOW}Note: This requires sufficient STRK balance and may take a while${NC}"
read -p "  Continue with deploy_to_protocols? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    DEPLOY_TX=$(sncast --profile $ACCOUNT_PROFILE invoke \
        --contract-address $CONTRACT_ADDRESS \
        --function deploy_to_protocols \
        2>&1)
    
    if echo "$DEPLOY_TX" | grep -q "transaction_hash"; then
        TX_HASH=$(echo "$DEPLOY_TX" | grep "transaction_hash" | awk '{print $2}')
        echo -e "  ${GREEN}✅ Deploy transaction: $TX_HASH${NC}"
        echo -e "  View on Starkscan: https://sepolia.starkscan.co/tx/$TX_HASH"
        echo -e "  ${YELLOW}⏳ This may take 30-60 seconds to complete...${NC}"
    else
        echo -e "  ${RED}❌ Deploy failed${NC}"
        echo "$DEPLOY_TX"
    fi
else
    echo -e "  ${YELLOW}Skipped deploy_to_protocols${NC}"
fi
echo ""

# Test 7: Check positions after deployment (if deployed)
echo -e "${YELLOW}📊 Test 7: Check positions after deployment${NC}"
echo -e "  JediSwap positions:"
sncast --profile $ACCOUNT_PROFILE call \
    --contract-address $CONTRACT_ADDRESS \
    --function get_jediswap_position_count \
    2>&1 | tail -3 || true
echo ""
echo -e "  Ekubo positions:"
sncast --profile $ACCOUNT_PROFILE call \
    --contract-address $CONTRACT_ADDRESS \
    --function get_ekubo_position_count \
    2>&1 | tail -3 || true
echo ""

# Test 8: Test accrue_yields (if positions exist)
echo -e "${YELLOW}💰 Test 8: Test accrue_yields (fee collection)${NC}"
echo -e "  ${YELLOW}Note: This will collect fees from all positions${NC}"
read -p "  Continue with accrue_yields? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    YIELD_TX=$(sncast --profile $ACCOUNT_PROFILE invoke \
        --contract-address $CONTRACT_ADDRESS \
        --function accrue_yields \
        2>&1)
    
    if echo "$YIELD_TX" | grep -q "transaction_hash"; then
        TX_HASH=$(echo "$YIELD_TX" | grep "transaction_hash" | awk '{print $2}')
        echo -e "  ${GREEN}✅ Accrue yields transaction: $TX_HASH${NC}"
        echo -e "  View on Starkscan: https://sepolia.starkscan.co/tx/$TX_HASH"
    else
        echo -e "  ${RED}❌ Accrue yields failed${NC}"
        echo "$YIELD_TX"
    fi
else
    echo -e "  ${YELLOW}Skipped accrue_yields${NC}"
fi
echo ""

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Testing Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Contract Explorer: ${CYAN}https://sepolia.starkscan.co/contract/$CONTRACT_ADDRESS${NC}"

