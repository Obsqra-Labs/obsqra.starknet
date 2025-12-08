#!/usr/bin/env python3
"""
Generate Zero-Knowledge Proof for Risk Model

Uses Giza Actions SDK to create verifiable proofs of risk calculations
"""

import json
import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.proof_service import get_proof_service, ProofService


async def generate_single_proof(metrics: dict, output_file: str):
    """Generate proof for a single test case"""
    
    print(f"\n{'='*60}")
    print("Generating Zero-Knowledge Proof")
    print(f"{'='*60}\n")
    
    print("Input Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\nGenerating proof...")
    
    proof_service = get_proof_service()
    
    try:
        result = await proof_service.generate_risk_proof(metrics)
        
        print("\n✓ Proof generated successfully!")
        print(f"\nProof Details:")
        print(f"  Proof Hash: {result.proof_hash}")
        print(f"  Job ID: {result.job_id}")
        print(f"  Status: {result.status}")
        
        print(f"\nOutput Score:")
        print(f"  Total Risk: {result.output_score}")
        print(f"  Components:")
        for component, value in result.output_components.items():
            print(f"    {component}: {value}")
        
        # Save proof
        proof_data = {
            "proof_hash": result.proof_hash,
            "job_id": result.job_id,
            "input": metrics,
            "output": {
                "total_score": result.output_score,
                **result.output_components
            },
            "status": result.status
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(proof_data, f, indent=2)
        
        print(f"\n✓ Proof saved to: {output_path}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Proof generation failed: {e}")
        raise


async def generate_batch_proofs(test_cases_file: str, output_dir: str):
    """Generate proofs for all test cases"""
    
    print(f"\n{'='*60}")
    print("Batch Proof Generation")
    print(f"{'='*60}\n")
    
    # Load test cases
    with open(test_cases_file, 'r') as f:
        test_cases = json.load(f)
    
    print(f"Loaded {len(test_cases)} test cases")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    proof_service = get_proof_service()
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        name = test_case["name"]
        metrics = test_case["input"]
        
        print(f"\n[{i}/{len(test_cases)}] Generating proof for: {name}")
        
        try:
            result = await proof_service.generate_risk_proof(metrics)
            
            proof_file = output_path / f"{name}_proof.json"
            with open(proof_file, 'w') as f:
                json.dump({
                    "name": name,
                    "proof_hash": result.proof_hash,
                    "job_id": result.job_id,
                    "input": metrics,
                    "output": {
                        "total_score": result.output_score,
                        **result.output_components
                    },
                    "expected": test_case["expected_output"],
                    "status": result.status
                }, f, indent=2)
            
            # Verify output matches expected
            if result.output_score == test_case["expected_output"]["total_score"]:
                print(f"  ✓ Score matches: {result.output_score}")
            else:
                print(f"  ✗ Score mismatch: {result.output_score} vs {test_case['expected_output']['total_score']}")
            
            results.append(result)
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    print(f"\n{'='*60}")
    print(f"Batch Complete: {len(results)}/{len(test_cases)} proofs generated")
    print(f"{'='*60}\n")
    
    return results


async def submit_proof_to_sharp(proof_file: str):
    """Submit a proof to SHARP for verification"""
    
    print(f"\n{'='*60}")
    print("Submitting Proof to SHARP")
    print(f"{'='*60}\n")
    
    # Load proof
    with open(proof_file, 'r') as f:
        proof_data = json.load(f)
    
    print(f"Proof Hash: {proof_data['proof_hash']}")
    print(f"Job ID: {proof_data['job_id']}")
    
    print("\nSubmitting to SHARP...")
    
    proof_service = get_proof_service()
    
    try:
        submission = await proof_service.submit_to_sharp(
            proof_data['proof_hash']
        )
        
        print("\n✓ Submitted to SHARP!")
        print(f"\nSubmission Details:")
        print(f"  Fact Hash: {submission.fact_hash}")
        print(f"  SHARP Job ID: {submission.job_id}")
        print(f"  Status: {submission.status}")
        
        # Save submission data
        submission_file = Path(proof_file).parent / f"{Path(proof_file).stem}_sharp.json"
        with open(submission_file, 'w') as f:
            json.dump({
                "proof_hash": proof_data['proof_hash'],
                "fact_hash": submission.fact_hash,
                "sharp_job_id": submission.job_id,
                "status": submission.status,
                "submitted_at": str(asyncio.get_event_loop().time())
            }, f, indent=2)
        
        print(f"\n✓ Submission data saved to: {submission_file}")
        
        if submission.status != "verified":
            print(f"\n⏳ SHARP verification in progress...")
            print(f"   This can take 10-60 minutes")
            print(f"   Monitor status with: python3 scripts/monitor_sharp.py {submission.fact_hash}")
        
        return submission
        
    except Exception as e:
        print(f"\n✗ SHARP submission failed: {e}")
        raise


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate ZK proofs for risk model")
    parser.add_argument("--mode", choices=["single", "batch", "sharp"], default="single",
                       help="Proof generation mode")
    parser.add_argument("--input", type=str, help="Input file (JSON)")
    parser.add_argument("--output", type=str, help="Output file/directory")
    parser.add_argument("--test-cases", type=str, default="tests/risk_model_test_cases.json",
                       help="Test cases file for batch mode")
    
    args = parser.parse_args()
    
    # Check if API key is set
    if not os.getenv('GIZA_API_KEY'):
        print("\n✗ ERROR: GIZA_API_KEY not set")
        print("   Real proof generation required.")
        print("\n   Setup: python3 scripts/giza_setup_sdk.py")
        print("   Or see: docs/GIZA_API_KEY_SETUP.md\n")
        sys.exit(1)
    
    if args.mode == "single":
        # Single proof generation
        if not args.input:
            # Use default JediSwap-like metrics
            metrics = {
                "utilization": 6500,
                "volatility": 3500,
                "liquidity": 1,
                "audit_score": 98,
                "age_days": 800
            }
        else:
            with open(args.input, 'r') as f:
                metrics = json.load(f)
        
        output_file = args.output or "giza/proofs/test_proof.json"
        asyncio.run(generate_single_proof(metrics, output_file))
    
    elif args.mode == "batch":
        # Batch proof generation
        output_dir = args.output or "giza/proofs"
        asyncio.run(generate_batch_proofs(args.test_cases, output_dir))
    
    elif args.mode == "sharp":
        # SHARP submission
        if not args.input:
            print("Error: --input required for SHARP mode")
            sys.exit(1)
        asyncio.run(submit_proof_to_sharp(args.input))


if __name__ == "__main__":
    main()

