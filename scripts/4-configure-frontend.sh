#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║    Step 4: Configure Frontend Environment             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Read deployed addresses
if [ ! -f "/opt/obsqra.starknet/deployed-addresses.json" ]; then
    echo "❌ deployed-addresses.json not found"
    echo "   Run: ./scripts/3-deploy-local.sh"
    exit 1
fi

echo "📝 Creating .env.local for frontend..."
echo ""

# Extract addresses (simplified - in production use jq)
RISK_ENGINE="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
STRATEGY_ROUTER="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
DAO_CONSTRAINT="0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8"

cat > /opt/obsqra.starknet/frontend/.env.local <<EOF
# Starknet Network Configuration
NEXT_PUBLIC_RPC_URL=http://localhost:5050
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA

# Deployed Contract Addresses
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=$RISK_ENGINE
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=$STRATEGY_ROUTER
NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=$DAO_CONSTRAINT

# MIST.cash Privacy Protocol (when available)
NEXT_PUBLIC_MIST_CHAMBER_ADDRESS=

# API Endpoints
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001

# Environment
NODE_ENV=development
EOF

echo "✅ Configuration created: frontend/.env.local"
echo ""
echo "📋 Settings:"
echo "  • RPC URL: http://localhost:5050"
echo "  • Risk Engine: $RISK_ENGINE"
echo "  • Strategy Router: $STRATEGY_ROUTER"
echo "  • DAO Constraints: $DAO_CONSTRAINT"
echo ""
echo "🔄 Restarting frontend to apply changes..."

# Kill and restart frontend
lsof -ti:3002 | xargs -r kill -9 2>/dev/null
sleep 2

cd /opt/obsqra.starknet/frontend
PORT=3002 nohup npm run dev > /tmp/starknet-frontend.log 2>&1 &

echo ""
echo "⏳ Waiting for frontend to start..."
sleep 5

if lsof -i:3002 -sTCP:LISTEN > /dev/null 2>&1; then
    echo "✅ Frontend running on http://localhost:3002"
else
    echo "⚠️  Frontend may still be starting..."
    echo "   Check logs: tail -f /tmp/starknet-frontend.log"
fi

echo ""
echo "🎯 Next: Open http://localhost:3002 and test wallet connection!"
