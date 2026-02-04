#!/usr/bin/env python3
"""
Test script for OODS debugging improvements

Tests:
1. Hard logging at proof generation
2. Enhanced layout mismatch guard
3. Canonical Integrity pipeline

Run with:
    python test_oods_debugging.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.api.routes.risk_engine import _canonical_integrity_pipeline, _stone_integrity_fact_for_metrics
from app.config import get_settings

settings = get_settings()


async def test_canonical_pipeline():
    """Test the canonical Integrity pipeline"""
    
    print("=" * 80)
    print("🔬 TESTING CANONICAL INTEGRITY PIPELINE")
    print("=" * 80)
    print()
    print(f"Configuration:")
    print(f"  Layout: {settings.INTEGRITY_LAYOUT}")
    print(f"  Stone Version: {settings.INTEGRITY_STONE_VERSION}")
    print(f"  Hasher: {settings.INTEGRITY_HASHER}")
    print(f"  Memory Verification: {settings.INTEGRITY_MEMORY_VERIFICATION}")
    print()
    
    # Sample metrics
    jediswap_metrics = {
        "utilization": 7500,  # 75%
        "volatility": 3000,   # 30%
        "liquidity": 1,       # Medium
        "audit_score": 85,
        "age_days": 365,
    }
    
    ekubo_metrics = {
        "utilization": 6000,  # 60%
        "volatility": 2500,   # 25%
        "liquidity": 0,       # High
        "audit_score": 90,
        "age_days": 500,
    }
    
    print("Test Metrics:")
    print(f"  JediSwap: {json.dumps(jediswap_metrics, indent=2)}")
    print(f"  Ekubo: {json.dumps(ekubo_metrics, indent=2)}")
    print()
    print("Starting canonical pipeline...")
    print("(This follows Integrity's generate.py approach exactly)")
    print()
    
    try:
        import time
        start_time = time.time()
        
        fact_hash, proof_path, output_dir, proof_hash = await _canonical_integrity_pipeline(
            jediswap_metrics,
            ekubo_metrics,
        )
        
        elapsed = time.time() - start_time
        
        print("=" * 80)
        print("✅ CANONICAL PIPELINE COMPLETE")
        print("=" * 80)
        print()
        print(f"Fact Hash: {hex(fact_hash) if fact_hash else 'None'}")
        print(f"Proof Path: {proof_path}")
        print(f"Output Dir: {output_dir}")
        print(f"Proof Hash: {proof_hash}")
        print(f"Time Elapsed: {elapsed:.2f}s")
        print()
        
        if fact_hash:
            print("✅ Integrity verification: SUCCESS")
            print(f"   Fact registered on-chain: {hex(fact_hash)}")
            print()
            print("🎯 DIAGNOSIS: Canonical pipeline verifies successfully.")
            print("   → Issue is likely in Obsqra pipeline, not AIR/version/stone mismatch")
        else:
            print("⚠️  Integrity verification: FAILED")
            print("   Fact hash is None - proof may not have been verified")
            print()
            print("🎯 DIAGNOSIS: Canonical pipeline fails.")
            print("   → Issue is likely AIR/version/stone mismatch")
            print("   → Check Stone binary version matches verifier setting")
            print("   → Compare proof parameters with canonical example")
        
        return {
            "success": True,
            "fact_hash": fact_hash,
            "proof_path": proof_path,
            "output_dir": output_dir,
            "proof_hash": proof_hash,
            "elapsed_seconds": elapsed,
            "verified": fact_hash is not None,
        }
        
    except Exception as e:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        print("=" * 80)
        print("❌ CANONICAL PIPELINE FAILED")
        print("=" * 80)
        print()
        print(f"Error: {type(e).__name__}: {str(e)}")
        print(f"Time Elapsed: {elapsed:.2f}s")
        print()
        
        import traceback
        print("Traceback:")
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "elapsed_seconds": elapsed,
        }


async def test_regular_pipeline_with_logging():
    """Test regular pipeline with new logging enabled"""
    
    print("=" * 80)
    print("🔍 TESTING REGULAR PIPELINE WITH HARD LOGGING")
    print("=" * 80)
    print()
    print("This will generate a proof using the regular Obsqra pipeline")
    print("and show all the new diagnostic logging.")
    print()
    
    jediswap_metrics = {
        "utilization": 7500,
        "volatility": 3000,
        "liquidity": 1,
        "audit_score": 85,
        "age_days": 365,
    }
    
    ekubo_metrics = {
        "utilization": 6000,
        "volatility": 2500,
        "liquidity": 0,
        "audit_score": 90,
        "age_days": 500,
    }
    
    try:
        import time
        start_time = time.time()
        
        fact_hash, proof_path, output_dir, proof_hash = await _stone_integrity_fact_for_metrics(
            jediswap_metrics,
            ekubo_metrics,
        )
        
        elapsed = time.time() - start_time
        
        print("=" * 80)
        print("✅ REGULAR PIPELINE COMPLETE")
        print("=" * 80)
        print()
        print(f"Fact Hash: {hex(fact_hash) if fact_hash else 'None'}")
        print(f"Proof Path: {proof_path}")
        print(f"Output Dir: {output_dir}")
        print(f"Proof Hash: {proof_hash}")
        print(f"Time Elapsed: {elapsed:.2f}s")
        print()
        print("📋 Check logs above for:")
        print("   - Active settings dump")
        print("   - Stone prover parameters")
        print("   - Proof parameters after generation")
        print("   - Verifier config validation")
        
        return {
            "success": True,
            "fact_hash": fact_hash,
            "proof_path": proof_path,
            "output_dir": output_dir,
            "proof_hash": proof_hash,
            "elapsed_seconds": elapsed,
            "verified": fact_hash is not None,
        }
        
    except Exception as e:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        print("=" * 80)
        print("❌ REGULAR PIPELINE FAILED")
        print("=" * 80)
        print()
        print(f"Error: {type(e).__name__}: {str(e)}")
        print(f"Time Elapsed: {elapsed:.2f}s")
        print()
        
        import traceback
        print("Traceback:")
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "elapsed_seconds": elapsed,
        }


async def main():
    """Run all tests"""
    
    print("=" * 80)
    print("OODS DEBUGGING IMPROVEMENTS - TEST SUITE")
    print("=" * 80)
    print()
    print("This script tests the three improvements:")
    print("1. Hard logging at proof generation")
    print("2. Enhanced layout mismatch guard")
    print("3. Canonical Integrity pipeline")
    print()
    print("Choose test:")
    print("1. Test canonical pipeline (recommended for OODS diagnosis)")
    print("2. Test regular pipeline with logging")
    print("3. Run both")
    print()
    
    choice = input("Enter choice (1/2/3) [default: 1]: ").strip() or "1"
    
    results = {}
    
    if choice in ["1", "3"]:
        print()
        results["canonical"] = await test_canonical_pipeline()
        print()
    
    if choice in ["2", "3"]:
        print()
        results["regular"] = await test_regular_pipeline_with_logging()
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    if "canonical" in results:
        r = results["canonical"]
        status = "✅ SUCCESS" if r.get("success") and r.get("verified") else "❌ FAILED"
        print(f"Canonical Pipeline: {status}")
        if r.get("fact_hash"):
            print(f"  Fact Hash: {hex(r['fact_hash'])}")
        if r.get("error"):
            print(f"  Error: {r['error']}")
        print()
    
    if "regular" in results:
        r = results["regular"]
        status = "✅ SUCCESS" if r.get("success") and r.get("verified") else "❌ FAILED"
        print(f"Regular Pipeline: {status}")
        if r.get("fact_hash"):
            print(f"  Fact Hash: {hex(r['fact_hash'])}")
        if r.get("error"):
            print(f"  Error: {r['error']}")
        print()
    
    print("=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print()
    print("1. Review the logs above for parameter mismatches")
    print("2. Compare proof parameters with canonical Integrity example")
    print("3. If canonical pipeline verifies but regular fails:")
    print("   → Issue is in Obsqra pipeline (check FRI calculation, params)")
    print("4. If both fail:")
    print("   → Issue is AIR/version/stone mismatch")
    print("   → Check Stone binary version matches verifier setting")
    print("   → Verify backend was restarted with new settings")
    print()


if __name__ == "__main__":
    asyncio.run(main())
