#!/usr/bin/env python3
"""
Direct contract declaration using starknet-py
Bypasses starkli limitations with RPC version compatibility
"""
import asyncio
import json
import os
from pathlib import Path
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chain import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.models import transaction
from starknet_py.contract import ContractFunction
from eth_keys import keys as eth_keys
import base64

async def main():
    # Configuration
    rpc_url = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
    account_address = 0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d
    
    # Load account config
    account_config_path = Path("/root/.starkli-wallets/deployer/account.json")
    with open(account_config_path) as f:
        account_config = json.load(f)
    
    public_key = int(account_config['variant']['public_key'], 16)
    
    # Load keystore and decrypt with password
    keystore_path = Path("/root/.starkli/keystore.json")
    with open(keystore_path) as f:
        keystore_data = json.load(f)
    
    password = "L!nux123"
    
    # Try to extract private key from keystore
    # This is a simplified approach - actual starkli format may vary
    print(f"[*] Account address: {hex(account_address)}")
    print(f"[*] Public key: {hex(public_key)}")
    print(f"[*] RPC URL: {rpc_url}")
    
    # For now, let's use starkli's built-in signing via subprocess
    print("\n[!] Using subprocess to invoke starkli with proper TTY handling")
    
    import subprocess
    import sys
    
    cmd = [
        "starkli", "declare",
        "/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json",
        "--casm-file", "/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json",
        "--rpc", rpc_url,
        "--account", str(account_config_path),
        "--keystore", str(keystore_path),
    ]
    
    env = os.environ.copy()
    env['STARKLI_KEYSTORE_PASSWORD'] = password
    
    print(f"[*] Running: {' '.join(cmd[:3])} ... --rpc <alchemy> --account <deployer> --keystore <keystore>")
    print(f"[*] Setting STARKLI_KEYSTORE_PASSWORD environment variable")
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            input=password + "\n"  # Also provide via stdin
        )
        print("\n" + "="*60)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        print(f"\nReturn code: {result.returncode}")
        print("="*60)
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out after 60 seconds")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
