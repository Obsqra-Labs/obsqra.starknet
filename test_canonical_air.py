#!/usr/bin/env python3
"""
Test script for canonical AIR regeneration
Tests proof generation with recursive layout + stone5 (canonical Integrity settings)
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.api.routes.risk_engine import _stone_integrity_fact_for_metrics
from app.config import get_settings

settings = get_settings()


async def test_canonical_air():
    """Test canonical AIR regeneration with sample metrics"""
    
    print("=" * 80)
    print("CANONICAL AIR REGENERATION TEST")
    print("=" * 80)
    print()
    print(f"Configuration:")
    print(f"  Layout: {settings.INTEGRITY_LAYOUT}")
    print(f"  Stone Version: {settings.INTEGRITY_STONE_VERSION}")
    print(f"  Hasher: {settings.INTEGRITY_HASHER}")
    print(f"  Memory Verification: {settings.INTEGRITY_MEMORY_VERIFICATION}")
    print(f"  Timeout: {getattr(settings, 'INTEGRITY_CAIRO_TIMEOUT', 300)}s")
    print()
    
    # Sample metrics (from E2E test)
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
    print("Starting proof generation...")
    print("(This may take up to 5 minutes with recursive layout)")
    print()
    
    try:
        import time
        start_time = time.time()
        
        fact_hash, proof_path, output_dir, proof_hash = await _stone_integrity_fact_for_metrics(
            jediswap_metrics,
            ekubo_metrics,
        )
        
        elapsed = time.time() - start_time
        
        print("=" * 80)
        print("✅ PROOF GENERATION SUCCESSFUL")
        print("=" * 80)
        print()
        print(f"Fact Hash: {fact_hash}")
        print(f"Proof Path: {proof_path}")
        print(f"Output Dir: {output_dir}")
        print(f"Proof Hash: {proof_hash}")
        print(f"Time Elapsed: {elapsed:.2f}s")
        print()
        
        if fact_hash:
            print("✅ Integrity verification: SUCCESS")
            print(f"   Fact registered on-chain: {hex(fact_hash)}")
        else:
            print("⚠️  Integrity verification: FAILED")
            print("   Fact hash is None - proof may not have been verified")
        
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
        print("❌ PROOF GENERATION FAILED")
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


if __name__ == "__main__":
    result = asyncio.run(test_canonical_air())
    
    print("=" * 80)
    print("TEST RESULT SUMMARY")
    print("=" * 80)
    print(json.dumps(result, indent=2))
    print()
    
    sys.exit(0 if result.get("success") and result.get("verified") else 1)
