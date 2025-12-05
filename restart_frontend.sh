#!/bin/bash
echo "Stopping all Next.js processes..."
pkill -9 -f "next dev"
sleep 2

echo "Starting frontend on port 3001..."
cd /opt/obsqra.starknet/frontend
PORT=3001 npm run dev &

sleep 5
echo ""
echo "✓ Frontend should be running on http://localhost:3001"
echo ""
echo "To check: curl http://localhost:3001"

