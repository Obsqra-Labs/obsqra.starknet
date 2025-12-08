"""
Update DAO Constraints to allow test allocations
"""
import asyncio
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
import os

# Contracts
DAO_CONSTRAINT_MANAGER = 0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856

# Backend wallet (deployer) - Load from .env
from dotenv import load_dotenv
load_dotenv("backend/.env")

BACKEND_ADDRESS_STR = os.getenv("BACKEND_WALLET_ADDRESS")
BACKEND_PRIVATE_KEY_STR = os.getenv("BACKEND_WALLET_PRIVATE_KEY")

if not BACKEND_ADDRESS_STR or not BACKEND_PRIVATE_KEY_STR:
    raise ValueError("Backend wallet credentials not found in backend/.env")

BACKEND_ADDRESS = int(BACKEND_ADDRESS_STR, 16)
BACKEND_PRIVATE_KEY = int(BACKEND_PRIVATE_KEY_STR, 16)

# New constraints (more permissive for testing)
MAX_SINGLE_PROTOCOL = 9000  # 90% (was 60%)
MIN_DIVERSIFICATION = 2     # Min 2 protocols (unchanged)
MAX_VOLATILITY = 8000       # 80% (increased)
MIN_LIQUIDITY = 1           # Tier 1 (unchanged)

async def main():
    print("🔧 Updating DAO Constraints...")
    print(f"   Max Single Protocol: {MAX_SINGLE_PROTOCOL / 100}%")
    print(f"   Min Diversification: {MIN_DIVERSIFICATION} protocols")
    print(f"   Max Volatility: {MAX_VOLATILITY / 100}%")
    print(f"   Min Liquidity Tier: {MIN_LIQUIDITY}")
    
    # Setup client and account (use Alchemy or public node)
    rpc_url = os.getenv("STARKNET_RPC_URL", "https://starknet-sepolia-rpc.publicnode.com")
    print(f"   RPC: {rpc_url}")
    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(BACKEND_PRIVATE_KEY)
    account = Account(
        address=BACKEND_ADDRESS,
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA,
    )
    
    # Load DAO Constraint Manager contract
    dao_contract = await Contract.from_address(
        address=DAO_CONSTRAINT_MANAGER,
        provider=account,
    )
    
    # Get current constraints
    print("\n📊 Current Constraints:")
    result = await dao_contract.functions["get_constraints"].call()
    print(f"   Max Single: {result[0]}")
    print(f"   Min Diversification: {result[1]}")
    print(f"   Max Volatility: {result[2]}")
    print(f"   Min Liquidity: {result[3]}")
    
    # Update constraints
    print("\n🔄 Updating constraints...")
    try:
        invocation = await dao_contract.functions["set_constraints"].invoke_v1(
            max_single=MAX_SINGLE_PROTOCOL,
            min_diversification=MIN_DIVERSIFICATION,
            max_volatility=MAX_VOLATILITY,
            min_liquidity=MIN_LIQUIDITY,
            max_fee=int(1e16),
        )
        
        print(f"✅ Transaction sent: {hex(invocation.transaction_hash)}")
        print("⏳ Waiting for confirmation...")
        
        await invocation.wait_for_acceptance()
        
        print("✅ Constraints updated successfully!")
        
        # Verify new constraints
        print("\n📊 New Constraints:")
        result = await dao_contract.functions["get_constraints"].call()
        print(f"   Max Single: {result[0]} ({result[0] / 100}%)")
        print(f"   Min Diversification: {result[1]}")
        print(f"   Max Volatility: {result[2]} ({result[2] / 100}%)")
        print(f"   Min Liquidity: {result[3]}")
        
        print("\n✅ Orchestration should now work with test allocations!")
        
    except Exception as e:
        print(f"❌ Failed to update constraints: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

