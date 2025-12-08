#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║    Step 3: Deploy Contracts to Local Devnet           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if devnet is running
if ! curl -s http://localhost:5050/is_alive > /dev/null 2>&1; then
    echo "❌ Devnet is not running on port 5050"
    echo "   Run: ./scripts/2-start-devnet.sh"
    exit 1
fi

echo "✅ Devnet is running"
echo ""

cd /opt/obsqra.starknet/contracts

# Check if contracts are compiled
if [ ! -f "target/dev/obsqra_contracts_RiskEngine.contract_class.json" ]; then
    echo "❌ Contracts not compiled"
    echo "   Run: ./scripts/1-compile-contracts.sh"
    exit 1
fi

echo "✅ Contracts compiled"
echo ""

echo " Deploying contracts..."
echo ""

# For now, we'll use sncast to declare and deploy
# This is a placeholder - actual deployment needs account setup

echo "📝 Note: This is a simplified deployment flow."
echo "   For full deployment, you'll need:"
echo "   1. Create a deployer account"
echo "   2. Fund it with devnet ETH"
echo "   3. Declare contract classes"
echo "   4. Deploy contract instances"
echo ""

# Create placeholder addresses for development
cat > /opt/obsqra.starknet/deployed-addresses.json <<EOF
{
  "network": "devnet",
  "rpc": "http://localhost:5050",
  "contracts": {
    "riskEngine": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
    "strategyRouter": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d",
    "daoConstraintManager": "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8"
  },
  "note": "These are placeholder addresses for local development",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "✅ Configuration saved to deployed-addresses.json"
echo ""
echo "🎯 Next step: ./scripts/4-configure-frontend.sh"
