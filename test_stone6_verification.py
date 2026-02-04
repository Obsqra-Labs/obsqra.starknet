#!/usr/bin/env python3
"""
Test Stone Version Mismatch Hypothesis

Tests if verifying with stone6 instead of stone5 fixes the OODS issue.
"""
import asyncio
import sys
sys.path.insert(0, '/opt/obsqra.starknet/backend')

from app.services.integrity_service import get_integrity_service
from app.services.proof_loader import serialize_stone_proof
from pathlib import Path

async def test_stone6_verification():
    """Test verifying with stone6 instead of stone5"""
    print("=== Testing Stone6 Verification ===")
    print()
    
    # Use actual failing proof
    proof_file = Path("/tmp/risk_stone_nttstalm/risk_proof.json")
    serializer_bin = Path("/opt/obsqra.starknet/integrity/target/release/proof_serializer")
    
    if not proof_file.exists():
        print(f"❌ Proof not found: {proof_file}")
        return
    
    print(f"Proof: {proof_file}")
    print(f"Serializer: {serializer_bin}")
    print()
    
    # Serialize proof
    calldata_body = serialize_stone_proof(proof_file, serializer_bin)
    
    # Helper to encode string to felt
    def _string_to_felt(value: str) -> int:
        return int.from_bytes(value.encode("ascii"), "big")
    
    # Test with stone6
    print("Testing with stone6...")
    calldata_stone6 = [
        _string_to_felt("recursive"),
        _string_to_felt("keccak_160_lsb"),
        _string_to_felt("stone6"),  # Changed from stone5
        _string_to_felt("strict"),
        *calldata_body,
    ]
    
    integrity = get_integrity_service()
    
    try:
        fact_hash_int, fact_hash_hex, block_number = await integrity.register_calldata_and_get_fact(calldata_stone6)
        if fact_hash_int:
            print(f"✅ Stone6 verification: SUCCESS!")
            print(f"   Fact hash: {fact_hash_hex}")
            print(f"   Block: {block_number}")
            print()
            print("This confirms stone version mismatch was the issue!")
        else:
            print("❌ Stone6 verification: FAILED")
            print("   Stone version mismatch is NOT the issue")
    except Exception as e:
        print(f"❌ Stone6 verification error: {e}")
        print("   Check error details above")
    
    print()
    print("=== Comparison ===")
    print("If stone6 passes but stone5 fails → stone version mismatch confirmed")
    print("If both fail → different issue")

if __name__ == "__main__":
    asyncio.run(test_stone6_verification())
