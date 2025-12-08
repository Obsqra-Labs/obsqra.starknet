#!/usr/bin/env python3
"""
Transfer STRK from deployer wallet to recipient
Using starknet_py 0.21.0
"""
import subprocess
import sys
import time
import json

def run_sncast_transfer():
    """Use sncast to transfer STRK"""
    
    deployer_addr = "0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
    deployer_key = "0xf4506f978f613c4f3d8934b4bf5c3459fba3a16fbc479d5f7dee8e3832404aab"
    recipient = "0x0348914Bed4FDC65399d347C4498D778B75d5835D9276027a4357FE78B4a7eb3"
    strk_token = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1"
    
    print("=" * 70)
    print(" Transferring STRK from Deployer Wallet")
    print("=" * 70)
    print(f"From:      {deployer_addr}")
    print(f"To:        {recipient}")
    print(f"Amount:    5 STRK")
    print()
    
    # Build sncast command
    cmd = [
        "sncast",
        "invoke",
        "--private-key", deployer_key,
        "--account-address", deployer_addr,
        "--network", "sepolia",
        strk_token,
        "transfer",
        recipient,
        "5000000000000000000",  # 5 STRK in wei
        "0"
    ]
    
    print(f"📤 Running: {' '.join(cmd[:7])} ...")
    print()
    
    try:
        # Run with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Transaction submitted successfully!")
            print("🎉 Check your wallet - 5 STRK is on the way!")
            return True
        else:
            print(f"\n⚠️ Command exited with code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 90 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = run_sncast_transfer()
    sys.exit(0 if success else 1)

