#!/bin/bash
set -e

echo "========================================"
echo " DEPLOYING YOUR OWN FACTREGISTRY"
echo "========================================"
echo ""

OWNER="0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
CONTRACT_FILE="/opt/obsqra.starknet/integrity/target/dev/integrity_FactRegistry.contract_class.json"

cd /opt/obsqra.starknet/integrity

echo "📝 Building contract..."
scarb build > /dev/null 2>&1
echo "✅ Built"

cd /opt/obsqra.starknet/contracts

echo ""
echo "📝 Declaring FactRegistry..."
echo "   Contract file: $CONTRACT_FILE"

# Try declaring - use the contract file directly
DECLARE_OUTPUT=$(sncast --account deployer declare \
    --contract-name FactRegistry \
    --network sepolia 2>&1 || true)

# Check if it worked or if we need the file path
if echo "$DECLARE_OUTPUT" | grep -q "Failed to find\|not found"; then
    echo "⚠️  Contract not in package, trying with file..."
    # We'll need to add it to the package or use a different method
    echo "   Need to add FactRegistry to contracts package or use starkli"
else
    echo "$DECLARE_OUTPUT" | head -20
fi

# For now, provide manual instructions
echo ""
echo "========================================"
echo " MANUAL DEPLOYMENT STEPS"
echo "========================================"
echo ""
echo "The contract is built at:"
echo "  $CONTRACT_FILE"
echo ""
echo "To deploy manually:"
echo ""
echo "1. Option A: Use starkli (if installed):"
echo "   starkli declare $CONTRACT_FILE --network sepolia --account deployer"
echo "   starkli deploy <class_hash> --constructor-calldata $OWNER --network sepolia"
echo ""
echo "2. Option B: Add to contracts package:"
echo "   - Copy contract to contracts/src/"
echo "   - Add mod declaration"
echo "   - Declare from contracts directory"
echo ""
echo "3. Option C: Use existing contract (no credits needed!):"
echo "   Address: 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c"
echo "   Just use this address - it's public, just pay gas"
