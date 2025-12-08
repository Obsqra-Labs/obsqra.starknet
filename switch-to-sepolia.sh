#!/bin/bash

echo "════════════════════════════════════════════════════════"
echo "🔄 Switching Frontend to Sepolia Testnet"
echo "════════════════════════════════════════════════════════"
echo ""

cd /opt/obsqra.starknet/frontend

# Update .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io/rpc/v0_7
NEXT_PUBLIC_CHAIN_ID=SN_SEPOLIA
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8001
EOF

echo "✅ Updated .env.local for Sepolia"
echo ""

# Kill old frontend process
echo "🛑 Stopping old frontend..."
pkill -f "PORT=3002" 2>/dev/null || echo "No old process found"
sleep 2

echo ""
echo " Starting frontend on Sepolia..."
PORT=3002 npm run dev > /tmp/frontend-sepolia.log 2>&1 &

sleep 5

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Frontend Updated & Restarted!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📝 Configuration:"
echo "   Network: Sepolia Testnet"
echo "   RPC: https://starknet-sepolia.public.blastapi.io/rpc/v0_7"
echo ""
echo "🌐 Open in browser:"
echo "   http://localhost:3002"
echo ""
echo "👛 Make sure your wallet is on Sepolia network!"
echo ""
echo "📊 Frontend logs:"
echo "   tail -f /tmp/frontend-sepolia.log"
echo ""
