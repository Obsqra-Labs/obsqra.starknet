#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║    Step 2: Start Local Starknet Devnet                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if devnet is already running
if lsof -i:5050 -sTCP:LISTEN > /dev/null 2>&1; then
    echo "⚠️  Port 5050 is already in use!"
    echo ""
    echo "Options:"
    echo "  1. Stop existing devnet: lsof -ti:5050 | xargs kill -9"
    echo "  2. Use existing devnet and continue to next step"
    echo ""
    exit 1
fi

echo "🚀 Starting Katana (Starknet devnet)..."
echo ""
echo "Configuration:"
echo "  • Port: 5050"
echo "  • Accounts: 10 pre-funded"
echo "  • Seed: 0"
echo ""

# Check if katana is available
if command -v katana > /dev/null 2>&1; then
    echo "Starting Katana..."
    katana --accounts 10 --seed 0 --port 5050
elif command -v starknet-devnet > /dev/null 2>&1; then
    echo "Starting starknet-devnet..."
    starknet-devnet --seed 42 --port 5050 --accounts 10
else
    echo "❌ No devnet found!"
    echo ""
    echo "Install options:"
    echo "  • Katana: curl -L https://install.dojoengine.org | bash"
    echo "  • starknet-devnet: pip install starknet-devnet"
    echo ""
    exit 1
fi
