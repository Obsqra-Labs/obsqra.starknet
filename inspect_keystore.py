#!/usr/bin/env python3
"""
Decrypt starkli keystore and extract private key
"""
import json
import sys
from pathlib import Path

def main():
    keystore_path = Path("/root/.starkli/keystore.json")
    password = "L!nux123"
    
    try:
        with open(keystore_path) as f:
            keystore_data = json.load(f)
        
        print(json.dumps(keystore_data, indent=2))
        
        # Check keystore format
        if "ciphertext" in keystore_data:
            print("\n[*] Keystore is encrypted with ciphertext")
            print(f"[*] Cipher: {keystore_data.get('cipher', 'unknown')}")
            print(f"[*] KDF: {keystore_data.get('kdf', 'unknown')}")
            
            # This is likely EIP-2386 or similar format
            # Would need proper library to decrypt
            print("\n[!] This is an encrypted keystore.")
            print("[!] Decryption requires the Starkli keystore library (eth_keystore or web3.py)")
            print("[!] Current approach cannot decrypt automatically.")
            
            return 1
        else:
            print("\n[*] Keystore appears to be unencrypted or different format")
            print("[*] Available keys:", list(keystore_data.keys()))
            
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
