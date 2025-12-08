#!/usr/bin/env python3
"""
Send STRK from deployer wallet to user's ArgentX wallet
"""
import asyncio
import sys
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.account.account import Account
from starknet_py.signers.stark_curve_signer import StarkCurveSigner
from starknet_py.net.models import StarknetChainId

async def main():
    # Configuration
    DEPLOYER_ADDR = 0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b
    DEPLOYER_KEY = 0xf4506f978f613c4f3d8934b4bf5c3459fba3a16fbc479d5f7dee8e3832404aab
    RECIPIENT = 0x0348914Bed4FDC65399d347C4498D778B75d5835D9276027a4357FE78B4a7eb3
    STRK_TOKEN = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1
    RPC_URL = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
    AMOUNT_STRK = 5  # Send 5 STRK
    
    print("=" * 70)
    print(" STRK Transfer from Deployer")
    print("=" * 70)
    print()
    
    client = FullNodeClient(node_url=RPC_URL)
    signer = StarkCurveSigner(account_address=DEPLOYER_ADDR, private_key=DEPLOYER_KEY)
    account = Account(
        client=client,
        address=DEPLOYER_ADDR,
        signer=signer,
        chain=StarknetChainId.SEPOLIA
    )
    
    print(f"From:      {hex(DEPLOYER_ADDR)}")
    print(f"To:        {hex(RECIPIENT)}")
    print(f"Amount:    {AMOUNT_STRK} STRK")
    print()
    
    try:
        print("📤 Sending transaction...")
        amount_wei = int(AMOUNT_STRK * 1e18)
        
        tx_hash = await account.execute_v1(
            calls=[{
                "to_address": STRK_TOKEN,
                "function_name": "transfer",
                "calldata": [RECIPIENT, amount_wei, 0]
            }],
            max_fee=int(1e16)
        )
        
        print(f"✅ Transaction submitted!")
        print(f"   TX Hash: {hex(tx_hash)}")
        print()
        print("⏳ Waiting for confirmation (this may take 30-60 seconds)...")
        
        receipt = await client.wait_for_tx(tx_hash, check_interval=3)
        
        print(f"✅ Transaction confirmed!")
        print(f"   Status: {receipt.status}")
        print()
        print(f"🎉 Success! {AMOUNT_STRK} STRK sent to your wallet")
        print(f"   Check your ArgentX wallet in a few moments")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

