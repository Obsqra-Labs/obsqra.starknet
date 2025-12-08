#!/bin/bash
# Giza Setup Script
# 
# Note: Giza CLI has compatibility issues with current Typer version
# Alternative: Use Giza Actions Python SDK directly

set -e

echo "========================================="
echo "Giza Proof Infrastructure Setup"
echo "========================================="
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p /opt/obsqra.starknet/giza/{models,proofs,jobs}
mkdir -p /opt/obsqra.starknet/sharp/{submissions,verifications}

echo "✓ Directories created"
echo ""

# Check for Python SDK alternative
echo "Checking for Giza Actions SDK..."
if python3 -c "import giza_actions" 2>/dev/null; then
    echo "✓ Giza Actions SDK installed"
else
    echo "Installing Giza Actions SDK (alternative to CLI)..."
    pip3 install giza-actions --quiet
    echo "✓ Giza Actions SDK installed"
fi

echo ""
echo "========================================="
echo "Setup Complete"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Create Giza account at https://app.giza.tech"
echo "2. Get API key from dashboard"
echo "3. Set environment variable: export GIZA_API_KEY='your_key'"
echo "4. Run: python3 scripts/generate_proof.py"
echo ""
echo "Alternative: Use mock mode (no account needed)"
echo "Backend will auto-detect missing GIZA_API_KEY and use mock proofs"
echo ""

