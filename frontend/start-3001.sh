#!/bin/bash

echo "Stopping all processes on port 3001..."

# Try multiple methods to kill the process
PID=$(lsof -ti:3001 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "Found PID $PID on port 3001, killing it..."
    kill -9 $PID 2>/dev/null
fi

# Also try fuser
fuser -k 3001/tcp 2>/dev/null

# Try PM2 if it exists
if command -v pm2 &> /dev/null; then
    echo "Stopping PM2 processes..."
    pm2 stop obsqra-frontend 2>/dev/null || true
    pm2 delete obsqra-frontend 2>/dev/null || true
fi

# Wait a moment
sleep 2

echo "Starting server on port 3001..."
cd /opt/obsqra.starknet/frontend
PORT=3001 npm run dev
