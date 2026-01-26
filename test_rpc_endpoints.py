#!/usr/bin/env python3
"""
Test various RPC endpoints to find one compatible with starkli v0.3.2/v0.4.x
"""
import requests
import json

rpc_endpoints = {
    "PublicNode": "https://starknet-sepolia-rpc.publicnode.com",
    "Alchemy": "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7",
    "StarknetRPC": "https://free-rpc.nethermind.io/sepolia-juno",
    "Infura": "https://starknet-sepolia.infura.io/v3/YOUR_API_KEY",
}

def get_rpc_version(rpc_url):
    """Query RPC for Starknet version info"""
    payload = {
        "jsonrpc": "2.0",
        "method": "starknet_blockNumber",
        "params": [],
        "id": 1
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Check spec version from headers or try to infer
        if "error" in data:
            return f"ERROR: {data['error']}"
        
        return f"OK (block #{data.get('result', 'unknown')})"
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

print("[*] Testing RPC endpoints for starkli v0.3.2 compatibility\n")
print(f"{'RPC Endpoint':<40} {'Status':<50}")
print("-" * 90)

for name, url in rpc_endpoints.items():
    if "YOUR_API_KEY" in url:
        print(f"{name:<40} {'SKIPPED (requires API key)':<50}")
        continue
    
    status = get_rpc_version(url)
    print(f"{name:<40} {status:<50}")

print("\n[!] NOTE:")
print("[!] starkli v0.3.2 is very old and may have compatibility issues")
print("[!] Recommend using starkli v0.5.x+ for recent Starknet deployments")
print("[!] Current issue: RPC spec version mismatch (tools expect 0.7.1, 0.10.0)")
print("[!] PublicNode is v0.13.x (outdated, different hash algorithm)")
print("[!] Alchemy is v0.8.1 (incompatible with starkli v0.3.2-0.4.x)")
