#!/usr/bin/env python3
"""
Direct starkli invocation with proper input/output handling
"""
import subprocess
import os
import sys

def main():
    rpc_url = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
    account_path = "/root/.starkli-wallets/deployer/account.json"
    keystore_path = "/root/.starkli/keystore.json"
    password = "L!nux123"
    
    # Build command
    cmd = [
        "starkli", "declare",
        "/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json",
        "--casm-file", "/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json",
        "--rpc", rpc_url,
        "--account", account_path,
        "--keystore", keystore_path,
    ]
    
    print(f"[*] Declaring StrategyRouterV2 on Alchemy Sepolia")
    print(f"[*] RPC: {rpc_url}")
    print(f"[*] Account: {account_path}")
    print(f"[*] Keystore: {keystore_path}")
    print()
    
    # Set environment variable for password
    env = os.environ.copy()
    env['STARKLI_KEYSTORE_PASSWORD'] = password
    
    try:
        # Run with stdin providing password as backup
        result = subprocess.run(
            cmd,
            input=password + "\n",
            capture_output=True,
            text=True,
            env=env,
            timeout=120
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            print("\n✅ Declaration successful!")
        else:
            print(f"\n❌ Declaration failed with code {result.returncode}")
        
        return result.returncode
    
    except subprocess.TimeoutExpired:
        print("❌ Declaration timed out after 120 seconds")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
