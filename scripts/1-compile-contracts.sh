#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║    Step 1: Compile Obsqra Starknet Contracts          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

cd /opt/obsqra.starknet/contracts

echo "📦 Compiling Cairo contracts with Scarb..."
scarb build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Compilation successful!"
    echo ""
    echo "📁 Compiled artifacts:"
    ls -lh target/dev/*.json | awk '{print "  •", $9, "(" $5 ")"}'
    echo ""
    echo "🎯 Next step: Run ./scripts/2-start-devnet.sh"
else
    echo ""
    echo "❌ Compilation failed. Check errors above."
    exit 1
fi
