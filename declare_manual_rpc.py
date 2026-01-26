#!/usr/bin/env python3
"""
Declare StrategyRouterV2 contract directly via Starknet JSON-RPC 0.8.1
Uses Cairo-lang's hash computation to be compatible with Blake2s (Starknet v0.14.1+)
"""
import json
import hashlib
import requests
from pathlib import Path
from typing import Dict, Any

def compute_sierra_hash(sierra_class: Dict) -> str:
    """
    Compute Sierra class hash using the new Blake2s algorithm (Starknet v0.14.1+)
    This matches what the Alchemy RPC expects.
    """
    # Serialize in Starknet format
    # For now, use Cairo hash computation if available
    try:
        # Try importing cairo_lang if available
        from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
        return compute_sierra_class_hash(sierra_class)
    except ImportError:
        # Fallback: use hash of JSON representation
        # This is NOT correct for actual deployment but shows the approach
        sierra_str = json.dumps(sierra_class, separators=(',', ':'), sort_keys=True)
        hash_bytes = hashlib.blake2b(sierra_str.encode(), digest_size=32).digest()
        return "0x" + hash_bytes.hex()

def send_declare_transaction(rpc_url: str, sierra_class: Dict, casm_class: Dict, 
                           account_address: str, signature: list) -> Dict[str, Any]:
    """
    Send DECLARE transaction to Starknet RPC
    
    Starknet RPC 0.8.1 expects:
    {
      "type": "DECLARE",
      "sender_address": "0x...",
      "contract_class": {...},  # Sierra class
      "compiled_contract_class": {...},  # CASM class
      "version": "0x1" or "0x100000000000000000000000000000000",
      "max_fee": "0x...",
      "signature": ["0x...", "0x..."],
      "nonce": "0x...",
      "class_hash": "0x..."
    }
    """
    
    # Compute class hashes
    sierra_class_hash = compute_sierra_hash(sierra_class)
    # CASM hash should already be in the casm_class
    casm_class_hash = casm_class.get("casm_class_hash") or compute_sierra_hash(casm_class)
    
    print(f"[*] Sierra class hash: {sierra_class_hash}")
    print(f"[*] CASM class hash: {casm_class_hash}")
    
    # Build transaction
    tx = {
        "jsonrpc": "2.0",
        "method": "starknet_addDeclareTransaction",
        "params": {
            "declare_transaction": {
                "type": "DECLARE",
                "version": "0x2",  # V2 for Starknet v0.14.1+
                "max_fee": str(int(1e18)),  # 1 STRK
                "signature": signature,
                "nonce": "0x0",
                "class_hash": sierra_class_hash,
                "sender_address": account_address,
                "contract_class": sierra_class,
                "compiled_contract_class": casm_class,
            }
        },
        "id": 1
    }
    
    print(f"\n[*] Sending DECLARE transaction...")
    print(f"    RPC: {rpc_url}")
    print(f"    Sender: {account_address}")
    print(f"    Max fee: {tx['params']['declare_transaction']['max_fee']}")
    
    try:
        response = requests.post(
            rpc_url,
            json=tx,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            print(f"[!] RPC Error: {result['error']}")
            return result
        
        print(f"[✓] Transaction submitted!")
        print(f"[✓] Transaction hash: {result.get('result', {}).get('transaction_hash', 'unknown')}")
        return result
        
    except Exception as e:
        print(f"[!] Request failed: {e}")
        return {"error": str(e)}

def main():
    rpc_url = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
    account_address = "0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d"
    
    print("[*] Loading contract classes...")
    
    sierra_path = Path("/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json")
    casm_path = Path("/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json")
    
    with open(sierra_path) as f:
        sierra_class = json.load(f)
    
    with open(casm_path) as f:
        casm_class = json.load(f)
    
    print(f"[✓] Sierra class loaded")
    print(f"[✓] CASM class loaded")
    
    print(f"\n[!] NOTE:")
    print(f"[!] This approach requires:")
    print(f"[!] 1. Proper Sierra class hash computation (Blake2s for Starknet v0.14.1+)")
    print(f"[!] 2. ECDSA signature from account private key")
    print(f"[!] 3. Transaction fee calculation")
    print(f"[!] 4. Transaction nonce")
    print(f"\n[!] Cairo-lang provides these functions but requires complex setup")
    print(f"[!] starknet-py should handle this but has RPC version incompatibility")
    print(f"\n[!] RECOMMENDATION: Use a working starkli version or deploy via web UI")
    
    # Try to compute hash using starknet_py if available
    try:
        from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
        sierra_hash = compute_sierra_class_hash(sierra_class)
        print(f"\n[✓] Computed Sierra hash via starknet-py: {sierra_hash}")
        
        # Would need to sign transaction here
        # But signature requires account private key in proper format
        # And to get proper nonce
        
        print(f"\n[!] For full implementation, would need:")
        print(f"[!] - Account private key in proper Stark curve format")
        print(f"[!] - Transaction nonce from chain")
        print(f"[!] - ECDSA signing of transaction hash")
        print(f"[!] - Fee estimation and payment")
        
    except Exception as e:
        print(f"\n[!] Could not use starknet-py: {e}")
        print(f"[!] This is the RPC version incompatibility issue again")

if __name__ == "__main__":
    main()
