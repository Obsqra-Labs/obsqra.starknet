#!/usr/bin/env python3
"""
Manual contract declaration via raw JSON-RPC calls
Bypasses tool version incompatibilities
"""
import json
import requests
import sys
from pathlib import Path
from Crypto.Hash import keccak
import hashlib

def send_rpc_call(url, method, params):
    """Send a JSON-RPC call and return result"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            raise Exception(f"RPC Error: {data['error']}")
        
        return data.get("result")
    except Exception as e:
        print(f"RPC Call failed ({method}): {e}", file=sys.stderr)
        raise

def main():
    rpc_url = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
    account_address = "0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
    
    # Load contract classes
    sierra_path = Path("/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json")
    casm_path = Path("/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json")
    
    with open(sierra_path) as f:
        sierra_class = json.load(f)
    
    with open(casm_path) as f:
        casm_class = json.load(f)
    
    sierra_class_hash = sierra_class.get("sierra_program", {})
    if not sierra_class_hash:
        print("ERROR: Could not extract sierra_program from class file")
        return 1
    
    print("[*] Loading contract classes...")
    print(f"[*] Sierra file size: {sierra_path.stat().st_size} bytes")
    print(f"[*] CASM file size: {casm_path.stat().st_size} bytes")
    
    # Query account nonce
    print(f"\n[*] Querying account nonce at {account_address}...")
    try:
        nonce_hex = send_rpc_call(
            rpc_url,
            "starknet_getNonce",
            {
                "block_id": "pending",
                "contract_address": account_address
            }
        )
        print(f"[✓] Account nonce: {nonce_hex}")
    except Exception as e:
        print(f"[!] Could not fetch nonce (proceeding with assumption): {e}")
        nonce_hex = "0x0"
    
    # Query block number
    print(f"\n[*] Querying chain info...")
    try:
        block_num = send_rpc_call(rpc_url, "starknet_blockNumber", [])
        print(f"[✓] Current block: {block_num}")
    except Exception as e:
        print(f"[!] Could not fetch block number: {e}")
    
    # Check if class already exists
    print(f"\n[*] Checking if class already declared...")
    sierra_class_hash_from_file = sierra_class.get("sierra_program")
    
    # This would require computing the class hash - complex operation
    # For now, proceed with declaration
    
    print(f"\n[!] NOTE: Full declaration via raw JSON-RPC requires:")
    print(f"    1. Computing exact sierra class hash (complex hash algorithm)")
    print(f"    2. Signing transaction with account private key")
    print(f"    3. Constructing complete DECLARE transaction")
    print(f"\n    This approach is too complex without proper Starknet SDK support.")
    print(f"    starkli/sncast incompatibility is the core issue.")
    
    print(f"\n[*] Alternative approach needed:")
    print(f"    - Use Starkli v0.5.x+ (supports Alchemy RPC 0.8.1)")
    print(f"    - Or downgrade Alchemy to older RPC version")
    print(f"    - Or use Python async/await with starknet_py upgrade")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
