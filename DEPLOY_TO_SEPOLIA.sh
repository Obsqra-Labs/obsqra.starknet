#!/bin/bash

echo "════════════════════════════════════════════════════════"
echo "🚀 Deploy Obsqra Contracts to Sepolia Testnet"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Your Wallet: 0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027"
echo ""

# Step 1: Check tools
echo "🔍 Step 1: Checking required tools..."
echo ""

if ! command -v scarb &> /dev/null; then
    echo "📦 Installing Scarb..."
    curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v starkli &> /dev/null; then
    echo "📦 Installing Starkli..."
    curl https://get.starkli.sh | sh
    starkliup
    export PATH="$HOME/.starkli/bin:$PATH"
fi

echo "✅ Tools ready"
echo ""

# Step 2: Compile contracts
echo "🔨 Step 2: Compiling Cairo contracts..."
cd /opt/obsqra.starknet/contracts
scarb build

if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi

echo "✅ Contracts compiled"
echo ""

# Step 3: List compiled contracts
echo "📋 Compiled contracts:"
ls -lh target/dev/*.contract_class.json 2>/dev/null | awk '{print "   " $9}'
echo ""

echo "════════════════════════════════════════════════════════"
echo "📝 Next Steps - Manual Deployment"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Since you need to provide your private key, please run"
echo "these commands manually:"
echo ""
echo "1️⃣  Setup your account:"
echo ""
echo "mkdir -p ~/.starkli-wallets/deployer"
echo ""
echo "starkli account fetch \\"
echo "  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \\"
echo "  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \\"
echo "  --output ~/.starkli-wallets/deployer/account.json"
echo ""
echo "starkli signer keystore from-key ~/.starkli-wallets/deployer/keystore.json"
echo "# Enter your private key from Argent X when prompted"
echo ""
echo ""
echo "2️⃣  Declare RiskEngine:"
echo ""
echo "starkli declare \\"
echo "  /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json \\"
echo "  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \\"
echo "  --account ~/.starkli-wallets/deployer/account.json \\"
echo "  --keystore ~/.starkli-wallets/deployer/keystore.json"
echo ""
echo "# Save the CLASS_HASH that's returned!"
echo ""
echo ""
echo "3️⃣  Deploy RiskEngine:"
echo ""
echo "starkli deploy \\"
echo "  <CLASS_HASH_FROM_ABOVE> \\"
echo "  0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027 \\"
echo "  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \\"
echo "  --account ~/.starkli-wallets/deployer/account.json \\"
echo "  --keystore ~/.starkli-wallets/deployer/keystore.json"
echo ""
echo "# Save the CONTRACT_ADDRESS!"
echo ""
echo ""
echo "4️⃣  Repeat for other contracts:"
echo ""
echo "# StrategyRouter"
echo "starkli declare target/dev/obsqra_contracts_StrategyRouter.contract_class.json ..."
echo "starkli deploy <CLASS_HASH> 0x07933... ..."
echo ""
echo "# DAOConstraintManager"
echo "starkli declare target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json ..."
echo "starkli deploy <CLASS_HASH> 0x07933... ..."
echo ""
echo ""
echo "5️⃣  Update frontend .env.local with deployed addresses:"
echo ""
echo "cd /opt/obsqra.starknet/frontend"
echo "nano .env.local  # or vi, code, etc."
echo ""
echo "# Update these lines with your deployed addresses:"
echo "# NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x..."
echo "# NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x..."
echo "# NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS=0x..."
echo ""
echo ""
echo "6️⃣  Restart frontend:"
echo ""
echo "pkill -f 'PORT=3002'"
echo "PORT=3002 npm run dev"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""
