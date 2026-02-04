#!/usr/bin/env python3
"""
E2E Test: DAO Constraints PASS

Tests allocation execution with metrics that produce allocations
that PASS DAO constraints.

DAO Constraints (from on-chain):
- max_single: 6000 (60%)
- min_diversification: 2 protocols
- min per protocol: 1000 (10%)

Test cases:
1. Equal metrics → 50/50 allocation (PASS)
2. Jedi higher risk → 40/60 allocation (PASS)
"""

import requests
import time
import sys

BACKEND_URL = "http://localhost:8001"

def test_case_1_equal_metrics_50_50():
    """
    Equal metrics for both protocols should produce ~50/50 allocation.
    Both 50% are <= 60% (max_single) and >= 10% (diversification).
    Expected: PASS (tx_hash returned)
    """
    print("\n=== Test Case 1: Equal Metrics → 50/50 Allocation ===\n")
    
    # Equal metrics for both protocols
    payload = {
        "jediswap_metrics": {
            "utilization": 500,
            "volatility": 2000,
            "liquidity": 2,  # Valid range: 0-3
            "audit_score": 85,
            "age_days": 365
        },
        "ekubo_metrics": {
            "utilization": 500,
            "volatility": 2000,
            "liquidity": 2,  # Valid range: 0-3
            "audit_score": 85,
            "age_days": 365
        }
    }
    
    print("📋 Metrics:")
    print(f"   JediSwap: {payload['jediswap_metrics']}")
    print(f"   Ekubo: {payload['ekubo_metrics']}")
    print("\n⏳ Calling orchestrate-allocation (this will take ~2-3 minutes for proof generation)...")
    
    response = requests.post(
        f"{BACKEND_URL}/api/v1/risk-engine/orchestrate-allocation",
        json=payload,
        timeout=300
    )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        jedi_pct = data.get("jediswap_pct", 0)
        ekubo_pct = data.get("ekubo_pct", 0)
        tx_hash = data.get("tx_hash")
        
        print(f"✅ SUCCESS")
        print(f"   JediSwap: {jedi_pct/100:.1f}%")
        print(f"   Ekubo: {ekubo_pct/100:.1f}%")
        print(f"   TX: {tx_hash}")
        print(f"   Starkscan: https://sepolia.starkscan.co/tx/{tx_hash}")
        
        # Verify allocation is within DAO limits
        assert jedi_pct <= 6000, f"JediSwap {jedi_pct} > 6000 (max_single)"
        assert ekubo_pct <= 6000, f"Ekubo {ekubo_pct} > 6000 (max_single)"
        assert jedi_pct >= 1000, f"JediSwap {jedi_pct} < 1000 (min diversification)"
        assert ekubo_pct >= 1000, f"Ekubo {ekubo_pct} < 1000 (min diversification)"
        print(f"\n✅ Allocation passes all DAO constraints")
        
        return True
    else:
        print(f"❌ FAIL: {response.status_code}")
        print(f"   Error: {response.text[:500]}")
        return False


def test_case_2_slight_variation_42_58():
    """
    Slight variation from test 1 to verify consistent behavior.
    Expected allocation: ~42/58 (within 60% limit).
    Expected: PASS (tx_hash returned)
    """
    print("\n=== Test Case 2: Slight Variation → ~42/58 Allocation ===\n")
    
    # Slight variation: slightly different audit scores
    payload = {
        "jediswap_metrics": {
            "utilization": 500,
            "volatility": 2000,
            "liquidity": 2,
            "audit_score": 82,  # Slightly lower audit
            "age_days": 365
        },
        "ekubo_metrics": {
            "utilization": 500,
            "volatility": 2000,
            "liquidity": 2,
            "audit_score": 88,  # Slightly higher audit
            "age_days": 365
        }
    }
    
    print("📋 Metrics:")
    print(f"   JediSwap: {payload['jediswap_metrics']}")
    print(f"   Ekubo: {payload['ekubo_metrics']}")
    print("\n⏳ Calling orchestrate-allocation (this will take ~2-3 minutes for proof generation)...")
    
    response = requests.post(
        f"{BACKEND_URL}/api/v1/risk-engine/orchestrate-allocation",
        json=payload,
        timeout=300
    )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        jedi_pct = data.get("jediswap_pct", 0)
        ekubo_pct = data.get("ekubo_pct", 0)
        tx_hash = data.get("tx_hash")
        
        print(f"✅ SUCCESS")
        print(f"   JediSwap: {jedi_pct/100:.1f}%")
        print(f"   Ekubo: {ekubo_pct/100:.1f}%")
        print(f"   TX: {tx_hash}")
        print(f"   Starkscan: https://sepolia.starkscan.co/tx/{tx_hash}")
        
        # Verify allocation is within DAO limits
        assert jedi_pct <= 6000, f"JediSwap {jedi_pct} > 6000 (max_single)"
        assert ekubo_pct <= 6000, f"Ekubo {ekubo_pct} > 6000 (max_single)"
        assert jedi_pct >= 1000, f"JediSwap {jedi_pct} < 1000 (min diversification)"
        assert ekubo_pct >= 1000, f"Ekubo {ekubo_pct} < 1000 (min diversification)"
        print(f"\n✅ Allocation passes all DAO constraints")
        
        return True
    else:
        print(f"❌ FAIL: {response.status_code}")
        print(f"   Error: {response.text[:500]}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("E2E Test: DAO Constraints PASS")
    print("=" * 60)
    
    print("\nℹ️  These tests verify that allocations within DAO limits")
    print("   successfully execute on-chain.")
    print("\nDAO Limits:")
    print("   - max_single: 6000 (60%)")
    print("   - min_diversification: 2 protocols")
    print("   - min per protocol: 1000 (10%)")
    
    results = []
    
    # Test Case 1
    result1 = test_case_1_equal_metrics_50_50()
    results.append(("50/50 Equal Metrics", result1))
    
    if result1:
        print("\n⏸  Waiting 30s before next test (avoid nonce conflicts)...")
        time.sleep(30)
    
    # Test Case 2
    result2 = test_case_2_slight_variation_42_58()
    results.append(("42/58 Slight Variation", result2))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_pass = all(r for _, r in results)
    
    if all_pass:
        print("\n🎉 All DAO constraint PASS tests completed successfully!")
        print("   Both allocations executed on-chain without revert.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed - see details above.")
        sys.exit(1)
