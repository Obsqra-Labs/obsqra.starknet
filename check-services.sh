#!/bin/bash

echo "======================================"
echo "Obsqra Services Status Check"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check ports
echo "Port Status:"
echo "============"

check_port() {
    local port=$1
    local name=$2
    if lsof -i:$port -sTCP:LISTEN > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name (port $port) - RUNNING"
        lsof -i:$port -sTCP:LISTEN | grep LISTEN | awk '{print "  Process:", $1, "PID:", $2}'
    else
        echo -e "${RED}✗${NC} $name (port $port) - NOT RUNNING"
    fi
}

check_port 3000 "Main Frontend (obsqra.fi)"
check_port 3001 "Starknet Frontend"
check_port 8000 "Main AI Service"
check_port 8001 "Starknet AI Service"
check_port 8545 "Anvil (Ethereum)"
check_port 5050 "Starknet Devnet"

echo ""
echo "PM2 Services:"
echo "============="
if command -v pm2 > /dev/null; then
    pm2 list
else
    echo -e "${YELLOW}⚠ PM2 not installed${NC}"
fi

echo ""
echo "Blockchain Nodes:"
echo "================="
if pgrep -f anvil > /dev/null; then
    echo -e "${GREEN}✓${NC} Anvil (Ethereum) is running"
else
    echo -e "${RED}✗${NC} Anvil is not running"
fi

if pgrep -f "katana\|starknet-devnet" > /dev/null; then
    echo -e "${GREEN}✓${NC} Starknet devnet is running"
else
    echo -e "${RED}✗${NC} Starknet devnet is not running"
fi

echo ""
echo "Recent Logs:"
echo "============"
if [ -d "/opt/obsqra.starknet/logs" ]; then
    echo "Starknet logs:"
    for log in /opt/obsqra.starknet/logs/*.log; do
        if [ -f "$log" ]; then
            echo "  - $(basename $log)"
        fi
    done
else
    echo -e "${YELLOW}⚠ No Starknet logs directory${NC}"
fi

echo ""
