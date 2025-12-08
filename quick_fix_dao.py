"""
Quick fix: Update DAO constraints to 90% max
"""
import os
import sys

# Add backend to path
sys.path.insert(0, '/opt/obsqra.starknet/backend')

from dotenv import load_dotenv
load_dotenv('/opt/obsqra.starknet/backend/.env')

# Simple approach: Use starknet_py to invoke
import asyncio
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient  
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair

DAO_ADDRESS = 0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856

async def main():
    # Load credentials
    addr = int(os.getenv("BACKEND_WALLET_ADDRESS"), 16)
    pk = int(os.getenv("BACKEND_WALLET_PRIVATE_KEY"), 16)
    
    print(f"🔧 Updating DAO Constraints...")
    print(f"   Contract: {hex(DAO_ADDRESS)}")
    print(f"   New max_single: 9000 (90%)")
    
    # Setup
    client = FullNodeClient(node_url=os.getenv("STARKNET_RPC_URL"))
    account = Account(
        address=addr,
        client=client,
        key_pair=KeyPair.from_private_key(pk),
        chain=StarknetChainId.SEPOLIA,
    )
    
    # Execute call
    print("⏳ Sending transaction...")
    from starknet_py.net.client_models import Call
    from starknet_py.hash.selector import get_selector_from_name
    
    call = Call(
        to_addr=DAO_ADDRESS,
        selector=get_selector_from_name("set_constraints"),
        calldata=[9000, 2, 8000, 1]  # max_single, min_div, max_vol, min_liq
    )
    
    # Execute with auto fee estimation
    result = await account.execute_v3(
        calls=[call],
        auto_estimate=True
    )
    
    print(f"✅ TX: {hex(result.transaction_hash)}")
    print("⏳ Waiting for confirmation...")
    
    await account.client.wait_for_tx(result.transaction_hash)
    print("✅ DAO constraints updated to 90% max!")
    print("   Orchestration should now work")

if __name__ == "__main__":
    asyncio.run(main())

