#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo " Starting Obsqra Frontend on Port 3003"
echo "════════════════════════════════════════════════════════════════"

# Kill any existing processes on ports 3000-3006
echo "🧹 Cleaning up old processes..."
for port in 3000 3001 3002 3003 3004 3005 3006; do
  lsof -ti:$port 2>/dev/null | xargs -r kill -9 2>/dev/null || true
done

sleep 2

# Navigate to frontend
echo "📂 Navigating to frontend directory..."
cd /opt/obsqra.starknet/frontend

# Verify we have dependencies
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Start Next.js on port 3003
echo ""
echo "▲ Starting Next.js 14..."
echo "📍 Access at: http://localhost:3003"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

PORT=3003 npm run dev

