#!/usr/bin/env python3
"""
Decrypt starkli keystore (EIP-2386 format) to extract private key
"""
import json
import hashlib
import hmac
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt as crypto_scrypt

def decrypt_keystore(keystore_path, password):
    """Decrypt EIP-2386 encrypted keystore"""
    with open(keystore_path) as f:
        keystore = json.load(f)
    
    # Extract crypto params
    crypto = keystore['crypto']
    cipherparams = crypto['cipherparams']
    kdfparams = crypto['kdfparams']
    
    # Derive decryption key using scrypt
    kdf_salt = bytes.fromhex(kdfparams['salt'])
    dklen = kdfparams['dklen']
    n = kdfparams['n']
    r = kdfparams['r']
    p = kdfparams['p']
    
    print(f"[*] Deriving key from password using scrypt...")
    print(f"    salt: {kdfparams['salt'][:16]}...")
    print(f"    n={n}, r={r}, p={p}, dklen={dklen}")
    
    derived_key = crypto_scrypt(
        password.encode('utf-8'),
        kdf_salt,
        dklen,
        n=n,
        r=r,
        p=p
    )
    
    print(f"[✓] Key derived successfully")
    
    # Verify MAC
    mac_message = derived_key[16:32] + bytes.fromhex(crypto['ciphertext'])
    mac_hash = hashlib.sha256(mac_message).digest()
    expected_mac = bytes.fromhex(crypto['mac'])
    
    print(f"[*] Verifying MAC...")
    if mac_hash != expected_mac:
        print(f"❌ MAC verification failed!")
        print(f"    Expected: {expected_mac.hex()}")
        print(f"    Got: {mac_hash.hex()}")
        return None
    
    print(f"[✓] MAC verification passed")
    
    # Decrypt
    cipher = crypto['cipher']  # aes-128-ctr
    iv = bytes.fromhex(cipherparams['iv'])
    ciphertext = bytes.fromhex(crypto['ciphertext'])
    encryption_key = derived_key[:16]
    
    print(f"[*] Decrypting with {cipher}...")
    aes = AES.new(encryption_key, AES.MODE_CTR, nonce=iv[:8], initial_value=iv[8:])
    plaintext = aes.decrypt(ciphertext)
    
    print(f"[✓] Decryption successful")
    
    # Parse plaintext as JSON (should be the private key or account data)
    try:
        result = json.loads(plaintext)
        return result
    except:
        # Might be raw hex private key
        return plaintext.hex()

def main():
    keystore_path = Path("/root/.starkli/keystore.json")
    password = "L!nux123"
    
    print(f"[*] Attempting to decrypt keystore: {keystore_path}")
    
    try:
        decrypted = decrypt_keystore(keystore_path, password)
        
        if decrypted:
            print(f"\n[✓] Decrypted successfully!")
            if isinstance(decrypted, dict):
                print(f"[*] Content (JSON):")
                print(json.dumps(decrypted, indent=2))
            else:
                print(f"[*] Content (hex):")
                print(decrypted)
                
                # If it's a hex string, might be private key
                if len(decrypted) == 64:  # 256-bit private key
                    print(f"\n[*] This appears to be a 256-bit private key")
                    print(f"[*] Private key: 0x{decrypted}")
        else:
            print("❌ Decryption failed")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
