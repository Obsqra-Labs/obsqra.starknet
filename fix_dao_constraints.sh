#!/bin/bash
# Quick fix: Update DAO constraints to allow test allocations
# Max single protocol: 6000 (60%) → 9000 (90%)

set -e

cd /opt/obsqra.starknet
source backend/.env

echo "🔧 Updating DAO Constraints on Starknet..."
echo "   Contract: 0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
echo "   New max_single: 9000 (90%)"
echo ""

# Use sncast to call set_constraints
sncast \
  --account deployer \
  --url https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  invoke \
  --contract-address 0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856 \
  --function set_constraints \
  --calldata 9000 2 8000 1 \
  --max-fee 0.01

echo ""
echo "✅ DAO constraints updated!"
echo "   Orchestration should now work"

