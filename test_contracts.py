#!/usr/bin/env python3
"""
Test deployed contracts on Starknet Sepolia
"""

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId

# Deployed contract addresses
RISK_ENGINE = 0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80
DAO_MANAGER = 0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856
STRATEGY_ROUTER = 0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a

# RPC
RPC_URL = "https://starknet-sepolia.public.blastapi.io"

async def test_contracts():
    print("=" * 70)
    print("🧪 TESTING OBSQRA CONTRACTS ON SEPOLIA")
    print("=" * 70)
    print()
    
    client = FullNodeClient(node_url=RPC_URL)
    
    # Test 1: Get class hash at address
    print("Test 1: Verify contracts are deployed")
    print("-" * 70)
    
    for name, addr in [
        ("RiskEngine", RISK_ENGINE),
        ("DAOConstraintManager", DAO_MANAGER),
        ("StrategyRouter", STRATEGY_ROUTER)
    ]:
        try:
            class_hash = await client.get_class_hash_at(addr)
            print(f"✅ {name}")
            print(f"   Address: {hex(addr)}")
            print(f"   Class Hash: {hex(class_hash)}")
            print()
        except Exception as e:
            print(f"❌ {name}")
            print(f"   Error: {e}")
            print()
    
    # Test 2: Get contract info
    print()
    print("Test 2: Get contract class info")
    print("-" * 70)
    
    try:
        class_hash = await client.get_class_hash_at(RISK_ENGINE)
        contract_class = await client.get_class(class_hash)
        print(f"✅ RiskEngine class retrieved")
        print(f"   Class Type: {type(contract_class).__name__}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    print("=" * 70)
    print("🎉 CONTRACT TESTS COMPLETE")
    print("=" * 70)
    print()
    print("💡 Next Steps:")
    print("  1. Install ArgentX or Braavos wallet extension")
    print("  2. Switch to Sepolia testnet")
    print("  3. Get testnet STRK from https://starknet-faucet.vercel.app")
    print("  4. Connect wallet at http://localhost:3003")
    print("  5. Interact with contracts through the dashboard")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_contracts())

