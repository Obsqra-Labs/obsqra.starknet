#!/bin/bash
# Deploy zkde.fi frontend to Hostinger
# Run from zkdefi/ directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="zkdefi-frontend-${TIMESTAMP}.tar.gz"

echo "🚀 Deploying zkde.fi to Hostinger"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Error: frontend/ directory not found"
    echo "   Run this script from the zkdefi/ directory"
    exit 1
fi

# Create deployment archive
echo "📦 Creating deployment archive..."
cd "$FRONTEND_DIR"

# Exclude build artifacts and dependencies
tar --exclude='node_modules' \
    --exclude='.next' \
    --exclude='.git' \
    --exclude='.env.local' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    -czf "$ARCHIVE_NAME" \
    .

echo "✅ Archive created: $ARCHIVE_NAME"
echo "   Size: $(du -h "$ARCHIVE_NAME" | cut -f1)"
echo ""

# Move archive to zkdefi root for easy access
mv "$ARCHIVE_NAME" "$SCRIPT_DIR/"
ARCHIVE_PATH="$SCRIPT_DIR/$ARCHIVE_NAME"

echo "📍 Archive location: $ARCHIVE_PATH"
echo ""
echo "=================================="
echo "Manual deployment steps:"
echo "=================================="
echo ""
echo "Option A: Use Cursor with Hostinger MCP"
echo "  1. Open Cursor"
echo "  2. Ask: 'Deploy $ARCHIVE_PATH to zkde.fi using hosting_deployJsApplication'"
echo "  3. After deployment, set environment variables in Hostinger panel"
echo ""
echo "Option B: Use Hostinger control panel"
echo "  1. Login to Hostinger"
echo "  2. Go to Websites → zkde.fi"
echo "  3. Upload $ARCHIVE_NAME"
echo "  4. Hostinger will auto-detect Node.js and run 'npm install && npm run build'"
echo ""
echo "Environment variables to set after deployment:"
echo "  NEXT_PUBLIC_API_URL=https://starknet.obsqra.fi"
echo "  NEXT_PUBLIC_PROOF_GATED_AGENT_ADDRESS=<contract_address>"
echo "  NEXT_PUBLIC_SELECTIVE_DISCLOSURE_ADDRESS=<contract_address>"
echo "  NEXT_PUBLIC_CONFIDENTIAL_TRANSFER_ADDRESS=<contract_address>"
echo "  NEXT_PUBLIC_STARKNET_CHAIN_ID=0x534e5f5345504f4c4941"
echo ""
echo "✅ Archive ready for deployment!"
