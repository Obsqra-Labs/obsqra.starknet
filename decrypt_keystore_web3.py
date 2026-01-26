#!/usr/bin/env python3
"""
Decrypt starkli keystore using web3.py's Account functionality
"""
import json
from pathlib import Path

def decrypt_keystore_v3(keystore_path, password):
    """Decrypt EIP-2386 (v3) keystore file using web3.py"""
    try:
        from web3 import Account
    except ImportError:
        print("ERROR: web3 not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip3", "install", "-q", "web3"])
        from web3 import Account
    
    with open(keystore_path) as f:
        keystore_json = f.read()
    
    try:
        # web3.py's Account can decrypt v3 keystores
        account = Account.from_key(Account.decrypt(keystore_json, password))
        return account
    except Exception as e:
        raise Exception(f"Decryption failed: {e}")

def main():
    keystore_path = Path("/root/.starkli/keystore.json")
    password = "L!nux123"
    
    print(f"[*] Attempting to decrypt keystore using web3.py...")
    
    try:
        account = decrypt_keystore_v3(keystore_path, password)
        
        print(f"\n[✓] Decryption successful!")
        print(f"[*] Account address: {account.address}")
        print(f"[*] Private key: {account.key.hex()}")
        
        return 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
