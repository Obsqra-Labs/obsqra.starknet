#!/usr/bin/env python3
"""
SHARP Verification Monitor

Monitors the status of SHARP proof verification jobs
"""

import json
import os
import sys
import asyncio
import time
from pathlib import Path
from typing import Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.proof_service import get_proof_service


async def monitor_fact(fact_hash: str, poll_interval: int = 60, max_wait: int = 3600):
    """
    Monitor SHARP verification status for a fact hash
    
    Args:
        fact_hash: SHARP fact hash to monitor
        poll_interval: Seconds between status checks
        max_wait: Maximum seconds to wait
    """
    
    print(f"\n{'='*60}")
    print("SHARP Verification Monitor")
    print(f"{'='*60}\n")
    
    print(f"Fact Hash: {fact_hash}")
    print(f"Poll Interval: {poll_interval}s")
    print(f"Max Wait: {max_wait}s ({max_wait//60} minutes)")
    print("")
    
    proof_service = get_proof_service()
    
    start_time = time.time()
    attempt = 0
    
    while True:
        attempt += 1
        elapsed = int(time.time() - start_time)
        
        print(f"[{elapsed}s] Attempt {attempt}: Checking status...")
        
        try:
            status = await proof_service.check_sharp_status(fact_hash)
            
            print(f"  Status: {status.status}")
            
            if status.status == "verified":
                print(f"\n{'='*60}")
                print("✓ PROOF VERIFIED!")
                print(f"{'='*60}\n")
                
                print("Verification Details:")
                print(f"  Fact Hash: {status.fact_hash}")
                print(f"  Block Number: {status.block_number}")
                print(f"  Transaction Hash: {status.transaction_hash}")
                print(f"  Total Time: {elapsed}s ({elapsed//60}m {elapsed%60}s)")
                print("")
                
                # Save verification data
                verification_file = Path("sharp/verifications") / f"{fact_hash}_verified.json"
                verification_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(verification_file, 'w') as f:
                    json.dump({
                        "fact_hash": status.fact_hash,
                        "status": status.status,
                        "block_number": status.block_number,
                        "transaction_hash": status.transaction_hash,
                        "verification_time_seconds": elapsed
                    }, f, indent=2)
                
                print(f"✓ Verification data saved to: {verification_file}\n")
                
                return status
            
            elif status.status == "failed":
                print(f"\n{'='*60}")
                print("✗ VERIFICATION FAILED")
                print(f"{'='*60}\n")
                return None
            
            else:
                # Still pending/verifying
                remaining = max_wait - elapsed
                print(f"  ⏳ Still {status.status}... ({remaining}s remaining)")
                
                if elapsed >= max_wait:
                    print(f"\n{'='*60}")
                    print("⏱️  TIMEOUT: Maximum wait time exceeded")
                    print(f"{'='*60}\n")
                    print("Verification may still complete. Check status later with:")
                    print(f"  python3 scripts/monitor_sharp.py {fact_hash}")
                    print("")
                    return None
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            if elapsed >= max_wait:
                return None
            await asyncio.sleep(poll_interval)


async def check_fact_on_chain(fact_hash: str):
    """
    Check if a fact is registered on-chain in SHARP fact registry
    
    Note: This requires RPC access and the SHARP fact registry address
    """
    
    print(f"\n{'='*60}")
    print("On-Chain Fact Verification")
    print(f"{'='*60}\n")
    
    print(f"Fact Hash: {fact_hash}")
    print("")
    
    print("Checking SHARP fact registry...")
    
    try:
        from starknet_py.contract import Contract
        from starknet_py.net.full_node_client import FullNodeClient
        
        # SHARP Fact Registry address (Sepolia testnet)
        # Note: Update with actual address
        SHARP_REGISTRY = "0x0" # TODO: Get actual address
        
        rpc_url = os.getenv('STARKNET_RPC_URL', 'https://starknet-sepolia-rpc.publicnode.com')
        client = FullNodeClient(node_url=rpc_url)
        
        # Minimal ABI for is_valid function
        abi = [{
            "type": "function",
            "name": "is_valid",
            "inputs": [{"name": "fact", "type": "felt"}],
            "outputs": [{"type": "felt"}],
            "state_mutability": "view"
        }]
        
        contract = Contract(
            address=int(SHARP_REGISTRY, 16),
            abi=abi,
            provider=client
        )
        
        # Check if fact is valid
        result = await contract.functions["is_valid"].call(int(fact_hash, 16))
        
        is_valid = bool(result[0])
        
        if is_valid:
            print("✓ Fact is VALID on-chain")
            print(f"  Registry: {SHARP_REGISTRY}")
            print("")
        else:
            print("✗ Fact is NOT valid on-chain")
            print("  Fact may still be verifying, or verification failed")
            print("")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ On-chain check failed: {e}")
        print("")
        return None


async def list_pending_submissions():
    """List all pending SHARP submissions"""
    
    print(f"\n{'='*60}")
    print("Pending SHARP Submissions")
    print(f"{'='*60}\n")
    
    submissions_dir = Path("sharp/submissions")
    
    if not submissions_dir.exists():
        print("No submissions directory found")
        return
    
    submission_files = list(submissions_dir.glob("*_sharp.json"))
    
    if not submission_files:
        print("No pending submissions")
        return
    
    print(f"Found {len(submission_files)} submission(s):\n")
    
    for sub_file in submission_files:
        with open(sub_file, 'r') as f:
            data = json.load(f)
        
        print(f"  File: {sub_file.name}")
        print(f"  Fact Hash: {data['fact_hash']}")
        print(f"  Status: {data['status']}")
        print("")


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor SHARP proof verification")
    parser.add_argument("fact_hash", nargs="?", help="SHARP fact hash to monitor")
    parser.add_argument("--poll-interval", type=int, default=60,
                       help="Seconds between status checks (default: 60)")
    parser.add_argument("--max-wait", type=int, default=3600,
                       help="Maximum seconds to wait (default: 3600 = 1 hour)")
    parser.add_argument("--check-on-chain", action="store_true",
                       help="Check fact validity on-chain")
    parser.add_argument("--list-pending", action="store_true",
                       help="List all pending submissions")
    
    args = parser.parse_args()
    
    # Check if API key is set
    if not os.getenv('GIZA_API_KEY'):
        print("\n✗ ERROR: GIZA_API_KEY not set")
        print("   Real proof generation required.")
        print("\n   Setup: python3 scripts/giza_setup_sdk.py\n")
        sys.exit(1)
    
    if args.list_pending:
        asyncio.run(list_pending_submissions())
    
    elif args.check_on_chain:
        if not args.fact_hash:
            print("Error: fact_hash required for --check-on-chain")
            sys.exit(1)
        asyncio.run(check_fact_on_chain(args.fact_hash))
    
    elif args.fact_hash:
        asyncio.run(monitor_fact(
            args.fact_hash,
            poll_interval=args.poll_interval,
            max_wait=args.max_wait
        ))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

