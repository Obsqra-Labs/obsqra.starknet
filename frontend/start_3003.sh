#!/bin/bash
# Start Next.js frontend on port 3003

echo "🔥 Starting Obsqra Frontend on Port 3003..."

# Kill any existing processes on port 3003 (use fuser/ss for portability)
if command -v fuser >/dev/null 2>&1; then
  fuser -k 3003/tcp 2>/dev/null || true
else
  pids=$(ss -tlnp 2>/dev/null | awk '/:3003 / {print $NF}' | sed 's/.*pid=//;s/,.*//')
  if [ -n "$pids" ]; then
    echo "$pids" | xargs kill -9 2>/dev/null || true
  fi
fi
sleep 1

# Navigate to frontend directory
cd /opt/obsqra.starknet/frontend

# Start Next.js production server on port 3003
npm run start:3003
