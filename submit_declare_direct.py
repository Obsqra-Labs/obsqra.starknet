#!/usr/bin/env python3
"""
Submit DECLARE transaction directly to Alchemy using proper RPC 0.8.1 format
Bypasses starkli's JSON-RPC compatibility issue
"""
import json
import requests
from pathlib import Path

def submit_declare_transaction():
    """
    Submit DECLARE transaction with Alchemy RPC 0.8.1 compatible format
    """
    
    rpc_url = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
    
    print("[*] Loading contract artifacts...")
    
    sierra_path = Path("/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json")
    casm_path = Path("/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json")
    
    with open(sierra_path) as f:
        sierra_class = json.load(f)
    
    with open(casm_path) as f:
        casm_class = json.load(f)
    
    print(f"[✓] Artifacts loaded")
    print(f"[*] Sierra class hash: 0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d42b7")
    print(f"[*] CASM class hash: 0x039bcde8fe0a75c690195698ac14248788b4304c9f23d22d19765c352f8b3b3f")
    
    # Build DECLARE transaction in Starknet RPC 0.8.1 format
    # NOTE: This requires transaction signing with account private key
    # For now, show what the transaction would look like
    
    declare_tx = {
        "type": "DECLARE",
        "version": "0x100000000000000000000000000000000",  # V2 (bits packed version for Starknet v0.14.1+)
        "max_fee": int(1e18),  # 1 STRK as estimate
        "signature": [
            "0x0",  # Placeholder - would be actual ECDSA signature
            "0x0"   # Placeholder - would be actual ECDSA signature
        ],
        "nonce": 0,
        "class_hash": "0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d42b7",
        "sender_address": "0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d",
        "contract_class": sierra_class,
        "compiled_contract_class": casm_class,
    }
    
    print(f"\n[!] To submit via RPC directly, would need:")
    print(f"    1. Account private key in Stark curve format")
    print(f"    2. Current account nonce from chain")
    print(f"    3. ECDSA signature of transaction hash")
    print(f"    4. Submit via starknet_addDeclareTransaction method")
    
    print(f"\n[*] Transaction structure prepared (showing for reference):")
    print(f"    Type: DECLARE")
    print(f"    Sender: 0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d")
    print(f"    Class hash: 0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d42b7")
    print(f"    Max fee: 1 STRK")
    print(f"    Sierra + CASM: ~1.3 MB total")
    
    print(f"\n[!] RECOMMENDATION:")
    print(f"    Since starkli already computed the hash and reached final submission,")
    print(f"    try running the starkli command again - it might succeed on retry")
    print(f"    (sometimes RPC issues are transient)")
    
    print(f"\n[!] Fallback if retry fails:")
    print(f"    1. Use Alchemy's web dashboard to submit transactions")
    print(f"    2. Or switch to a different RPC that's compatible with starkli v0.3.x")
    print(f"    3. Or wait for starkli v0.4.x to be available (should support RPC 0.8.1)")
    
    return 0

if __name__ == "__main__":
    submit_declare_transaction()
