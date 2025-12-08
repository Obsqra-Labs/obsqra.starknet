#!/bin/bash
# Start Next.js frontend on port 3003

echo "🔥 Starting Obsqra Frontend on Port 3003..."

# Kill any existing processes on port 3003
lsof -ti:3003 | xargs kill -9 2>/dev/null || true
sleep 2

# Navigate to frontend directory
cd /opt/obsqra.starknet/frontend

# Start Next.js with port 3003
PORT=3003 npm run dev
