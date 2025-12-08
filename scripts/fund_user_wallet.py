#!/usr/bin/env python3
"""
Fund user wallet with test ETH from Katana pre-funded account
"""

import asyncio
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
from starknet_py.net.client_models import Call

# Configuration
KATANA_RPC = "http://localhost:5050"
USER_ADDRESS = "0x07933ED0d1c5eD8976e18301921AAcbdd3abc48065c85c292B998f0e72a7F027"
AMOUNT = 10 * 10**18  # 10 ETH in wei

# Katana pre-funded account #0
KATANA_ACCOUNT_ADDRESS = "0x5b6b8189bb580f0df1e6d6bec509ff0d6c9be7365d10627e0cf222ec1b47a71"
KATANA_PRIVATE_KEY = "0x33003003001800009900180300d206308b0070db00121318d17b5e6262150b"

# ETH contract address (standard across Starknet networks)
ETH_CONTRACT_ADDRESS = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

async def main():
    print("=" * 60)
    print("💰 Funding Your Wallet with Test ETH")
    print("=" * 60)
    print()
    print(f"From:   {KATANA_ACCOUNT_ADDRESS}")
    print(f"To:     {USER_ADDRESS}")
    print(f"Amount: {AMOUNT / 10**18} ETH")
    print()
    
    try:
        # Connect to Katana
        print("🔗 Connecting to Katana...")
        client = FullNodeClient(node_url=KATANA_RPC)
        
        # Create account from Katana's pre-funded account
        print("🔑 Setting up sender account...")
        key_pair = KeyPair.from_private_key(int(KATANA_PRIVATE_KEY, 16))
        account = Account(
            client=client,
            address=KATANA_ACCOUNT_ADDRESS,
            key_pair=key_pair,
            chain=StarknetChainId.TESTNET,  # Katana uses testnet chain ID
        )
        
        # Prepare transfer call
        print("📝 Preparing ETH transfer...")
        
        # ETH transfer calldata
        call = Call(
            to_addr=int(ETH_CONTRACT_ADDRESS, 16),
            selector=int.from_bytes(b"transfer", "big"),  # transfer function
            calldata=[
                int(USER_ADDRESS, 16),  # recipient
                AMOUNT,  # amount low
                0,  # amount high (u256)
            ]
        )
        
        print("📤 Executing transfer...")
        # Execute the transaction
        result = await account.execute(call, max_fee=int(1e16))
        
        print(f"✅ Transaction sent!")
        print(f"   Transaction hash: {hex(result.transaction_hash)}")
        print()
        
        # Wait for transaction
        print("⏳ Waiting for confirmation...")
        await account.client.wait_for_tx(result.transaction_hash)
        
        print()
        print("=" * 60)
        print("🎉 SUCCESS! Your wallet has been funded!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Refresh your wallet")
        print("2. You should see 10 ETH!")
        print("3. Connect to http://localhost:3002")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Transfer Failed")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Possible solutions:")
        print("1. Make sure Katana is running:")
        print("   katana --dev --http.cors_origins \"*\"")
        print()
        print("2. Try the simpler approach:")
        print("   Just use the frontend with 0 ETH to test the UI!")
        print()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
