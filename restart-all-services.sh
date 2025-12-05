#!/bin/bash

echo "======================================"
echo "Restarting All Obsqra Starknet Services"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Stop any existing Starknet frontend on port 3001
echo -e "${YELLOW}[1/6] Stopping existing Starknet frontend...${NC}"
lsof -ti:3001 | xargs -r kill -9 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓ Port 3001 cleared${NC}"
echo ""

# 2. Stop any existing AI service on port 8001
echo -e "${YELLOW}[2/6] Stopping existing Starknet AI service...${NC}"
lsof -ti:8001 | xargs -r kill -9 2>/dev/null || true
pkill -f "obsqra.starknet/ai-service" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓ AI service stopped${NC}"
echo ""

# 3. Restart Starknet devnet/katana if running
echo -e "${YELLOW}[3/6] Checking for Starknet devnet...${NC}"
if pgrep -f "katana\|starknet-devnet" > /dev/null; then
    echo "Found running Starknet devnet, restarting..."
    pkill -f "katana\|starknet-devnet"
    sleep 2
    # Start it in background if there's a start script
    if [ -f "/opt/obsqra.starknet/scripts/start-devnet.sh" ]; then
        nohup /opt/obsqra.starknet/scripts/start-devnet.sh > /opt/obsqra.starknet/logs/devnet.log 2>&1 &
        echo -e "${GREEN}✓ Starknet devnet restarted${NC}"
    else
        echo -e "${YELLOW}⚠ No devnet start script found, skipping${NC}"
    fi
else
    echo -e "${YELLOW}⚠ No Starknet devnet running${NC}"
fi
echo ""

# 4. Start Starknet AI Service
echo -e "${YELLOW}[4/6] Starting Starknet AI service...${NC}"
cd /opt/obsqra.starknet/ai-service
if [ -f "requirements.txt" ] && [ -d "venv" ]; then
    nohup ./venv/bin/python main.py > /opt/obsqra.starknet/logs/ai-service.log 2>&1 &
    AI_PID=$!
    sleep 3
    if ps -p $AI_PID > /dev/null; then
        echo -e "${GREEN}✓ AI service started (PID: $AI_PID)${NC}"
    else
        echo -e "${RED}✗ AI service failed to start${NC}"
    fi
else
    echo -e "${YELLOW}⚠ AI service not set up yet, skipping${NC}"
fi
echo ""

# 5. Start Starknet Frontend
echo -e "${YELLOW}[5/6] Starting Starknet frontend on port 3001...${NC}"
cd /opt/obsqra.starknet/frontend
if [ -f "package.json" ] && [ -d "node_modules" ]; then
    nohup npm run dev -- --port 3001 > /opt/obsqra.starknet/logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    sleep 5
    if ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
        echo -e "${GREEN}  → http://localhost:3001${NC}"
    else
        echo -e "${RED}✗ Frontend failed to start${NC}"
        echo "Check logs: /opt/obsqra.starknet/logs/frontend.log"
    fi
else
    echo -e "${RED}✗ Frontend not set up (missing node_modules)${NC}"
    echo "Run: cd /opt/obsqra.starknet/frontend && npm install"
fi
echo ""

# 6. Check main obsqra.fi services (PM2)
echo -e "${YELLOW}[6/6] Checking main obsqra.fi services...${NC}"
if command -v pm2 > /dev/null; then
    cd /opt/obsqra.fi
    pm2 restart all --update-env
    echo -e "${GREEN}✓ PM2 services restarted${NC}"
    echo ""
    pm2 list
else
    echo -e "${YELLOW}⚠ PM2 not found, skipping main services${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}Service Restart Complete!${NC}"
echo "======================================"
echo ""
echo "Service URLs:"
echo "  • Starknet Frontend: http://localhost:3001"
echo "  • Starknet AI API:   http://localhost:8001"
echo "  • Main Frontend:     http://localhost:3000 (PM2)"
echo "  • Main AI Service:   http://localhost:8000 (PM2)"
echo ""
echo "Check logs:"
echo "  • Starknet: /opt/obsqra.starknet/logs/"
echo "  • Main: /opt/obsqra.fi/logs/"
echo ""
