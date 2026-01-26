#!/usr/bin/env python3
"""
Declare StrategyRouterV2 contract using starknet-py with account signer
"""
import asyncio
import json
from pathlib import Path
from typing import List

async def main():
    # Import after suppressing warnings
    import warnings
    warnings.filterwarnings("ignore")
    
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.net.account.account import Account
    from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
    from starknet_py.net.signer.key_pair import KeyPair
    
    # Configuration
    rpc_url = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
    account_address = "0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
    # Private key extracted from keystore (Starknet format, not Ethereum)
    # The address we got from web3.py decryption was Ethereum format, but the keystore
    # contains a Starknet private key
    
    print("[*] Loading contract class files...")
    
    sierra_path = Path("/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json")
    casm_path = Path("/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json")
    
    with open(sierra_path) as f:
        sierra_class = json.load(f)
    
    with open(casm_path) as f:
        casm_class = json.load(f)
    
    print(f"[✓] Sierra class loaded (size: {len(json.dumps(sierra_class))} bytes)")
    print(f"[✓] CASM class loaded (size: {len(json.dumps(casm_class))} bytes)")
    
    # Create RPC client
    print(f"\n[*] Connecting to RPC: {rpc_url}")
    client = FullNodeClient(node_url=rpc_url)
    
    try:
        # Get block number to verify connectivity
        block_num = await client.get_block_number()
        print(f"[✓] RPC connected, current block: {block_num}")
    except Exception as e:
        print(f"❌ RPC connection failed: {e}")
        return 1
    
    print(f"\n[!] NOTE: Full starknet-py declaration requires Account setup with proper private key")
    print(f"[!] The private key extracted is from Ethereum keystore format")
    print(f"[!] Need to verify it matches the Starknet account private key")
    print(f"\n[*] Account address: {account_address}")
    print(f"[*] Account status: Check if deployed on chain")
    
    # Verify account is deployed
    try:
        class_hash_on_chain = await client.get_class_by_hash("0x5b4b537eaa2399e3aa99c4e2e0208ebd6c71bc1467938cd52c798c601e43564")
        print(f"[✓] Account contract class exists on chain (OpenZeppelin)")
    except Exception as e:
        print(f"⚠️  Account class check failed: {e}")
    
    print(f"\n[!] To proceed with declaration, need:")
    print(f"    1. Starknet-format private key (not Ethereum format)")
    print(f"    2. starknet-py version compatible with Alchemy RPC 0.8.1")
    print(f"    3. Proper Account initialization with signer")
    print(f"\n[!] Current starknet-py appears to expect RPC 0.10.0")
    print(f"[!] Alchemy Sepolia provides RPC 0.8.1")
    print(f"\n[*] Alternative: Install starkli v0.5.x which supports newer RPC versions")
    
    return 1

if __name__ == "__main__":
    asyncio.run(main())
