#!/bin/bash

set -e

echo "================================"
echo "Obsqra Local Deployment Setup"
echo "================================"
echo ""

# Step 1: Check Python
echo "[1/4] Checking Python..."
python3 --version

# Step 2: Install dependencies
echo ""
echo "[2/4] Installing starknet-py..."
pip install --quiet starknet-py
echo "✓ starknet-py installed"

# Step 3: Check Katana
echo ""
echo "[3/4] Checking for Katana..."
if command -v katana &> /dev/null; then
    echo "✓ Katana found:"
    katana --version
else
    echo "! Katana not found. To install:"
    echo "  curl -L https://install.dojoengine.org | bash"
    echo "  dojoup"
fi

# Step 4: Build contracts
echo ""
echo "[4/4] Building contracts..."
cd /opt/obsqra.starknet/contracts
scarb build
echo "✓ Contracts built"

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Start Katana (Terminal 1):"
echo "   katana --host 0.0.0.0"
echo ""
echo "2. Deploy contracts (Terminal 2):"
echo "   cd /opt/obsqra.starknet"
echo "   python3 scripts/deploy_local.py"
echo ""
echo "3. Start frontend (Terminal 3):"
echo "   cd /opt/obsqra.starknet/frontend"
echo "   npm run dev"
echo ""

