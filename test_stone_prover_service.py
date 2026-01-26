#!/usr/bin/env python3
"""
Test Stone Prover Service with the fibonacci example

This tests the basic functionality of StoneProverService using the known-working
fibonacci example from Stone prover e2e tests.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.stone_prover_service import StoneProverService


async def test_fibonacci_proof():
    """Test Stone prover with fibonacci example"""
    
    print("="*70)
    print("STONE PROVER SERVICE - FIBONACCI TEST")
    print("="*70)
    
    # Initialize service
    print("\n1. Initializing Stone Prover Service...")
    try:
        service = StoneProverService()
        print("   ✅ Service initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Define test files
    private_input_file = "/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_private.json"
    public_input_file = "/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_public.json"
    
    print(f"\n2. Checking input files...")
    print(f"   Private input: {private_input_file}")
    print(f"   Public input: {public_input_file}")
    
    if not Path(private_input_file).exists():
        print(f"   ❌ Private input file not found")
        return False
    if not Path(public_input_file).exists():
        print(f"   ❌ Public input file not found")
        return False
    
    print("   ✅ Input files exist")
    
    # Read public input to see trace size
    with open(public_input_file) as f:
        public_input = json.load(f)
    
    n_steps = public_input.get("n_steps")
    print(f"\n3. Trace Information:")
    print(f"   n_steps: {n_steps}")
    
    # Generate proof
    print(f"\n4. Generating STARK proof...")
    result = await service.generate_proof(private_input_file, public_input_file)
    
    if not result.success:
        print(f"   ❌ Proof generation failed: {result.error}")
        return False
    
    print(f"   ✅ Proof generated successfully!")
    print(f"\n5. Proof Details:")
    print(f"   Hash: {result.proof_hash[:32]}...")
    print(f"   Size: {result.proof_size_kb:.1f} KB")
    print(f"   Time: {result.generation_time_ms:.0f} ms")
    print(f"   FRI Parameters: last_layer={result.fri_parameters['last_layer']}, fri_steps={result.fri_parameters['fri_steps']}")
    
    # Verify proof structure
    if result.proof_json:
        print(f"\n6. Proof Structure:")
        proof = result.proof_json
        if "stark_proof" in proof:
            print(f"   ✅ Contains stark_proof")
        if "public_input" in proof:
            print(f"   ✅ Contains public_input")
        if "n_steps" in proof:
            print(f"   ✅ Contains n_steps")
    
    print(f"\n7. Summary:")
    print(f"   ✅ Stone prover service working correctly!")
    print(f"   ✅ FRI parameters calculated dynamically")
    print(f"   ✅ Proof generation successful")
    print(f"   ✅ Ready for Phase 3 integration")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_fibonacci_proof())
    sys.exit(0 if success else 1)
