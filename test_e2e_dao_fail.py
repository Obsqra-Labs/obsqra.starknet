#!/usr/bin/env python3
"""
E2E Test: DAO Constraints FAIL

Tests allocation execution with metrics that produce allocations
that VIOLATE DAO constraints.

DAO Constraints (from on-chain):
- max_single: 6000 (60%)
- min_diversification: 2 protocols  
- min per protocol: 1000 (10%)

Test cases:
1. Jedi high risk → ~9/91 allocation → Ekubo > 60% (FAIL)
2. Jedi ultra high risk → ~7/93 allocation → Ekubo > 60% (FAIL)
"""

import requests
import time
import sys

BACKEND_URL = "http://localhost:8001"

def test_case_1_ekubo_low_risk_30_70():
    """
    Ekubo with much lower risk → gets ~70% allocation.
    70% > 60% (max_single) → DAO constraint violated.
    Expected: FAIL (error contains "DAO constraints violated")
    """
    print("\n=== Test Case 1: Ekubo Low Risk → 30/70 Allocation (EXPECT FAIL) ===\n")
    
    # Ekubo: very low volatility → lower risk → higher allocation
    # JediSwap: high volatility → higher risk → lower allocation
    payload = {
        "jediswap_metrics": {
            "utilization": 700,
            "volatility": 4500,  # Very high volatility
            "liquidity": 30,
            "audit_score": 75,
            "age_days": 200
        },
        "ekubo_metrics": {
            "utilization": 300,
            "volatility": 800,   # Very low volatility
            "liquidity": 80,
            "audit_score": 95,
            "age_days": 500
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
    
    if response.status_code == 500:
        error_text = response.text
        print(f"✅ EXPECTED FAILURE")
        print(f"   Error: {error_text[:300]}")
        
        # Verify it's a DAO constraint violation, not other error
        if "DAO constraints violated" in error_text or "constraints violated" in error_text.lower():
            print(f"\n✅ Correct revert reason: DAO constraints violated")
            return True
        else:
            print(f"\n⚠️  Failed but not with expected reason")
            print(f"   Expected: 'DAO constraints violated'")
            print(f"   Got: {error_text[:200]}")
            return False
    elif response.status_code == 200:
        data = response.json()
        jedi_pct = data.get("jediswap_pct", 0)
        ekubo_pct = data.get("ekubo_pct", 0)
        print(f"❌ UNEXPECTED SUCCESS")
        print(f"   JediSwap: {jedi_pct/100:.1f}%")
        print(f"   Ekubo: {ekubo_pct/100:.1f}%")
        print(f"   Expected to fail with DAO constraint violation!")
        return False
    else:
        print(f"⚠️  Unexpected status code: {response.status_code}")
        print(f"   Error: {response.text[:300]}")
        return False


def test_case_2_jedi_ultra_high_risk_7_93():
    """
    Jedi with ultra extreme risk → Ekubo gets ~93% allocation.
    93% > 60% (max_single) → DAO constraint violated.
    Expected: FAIL (error contains "DAO constraints violated")
    """
    print("\n=== Test Case 2: Jedi Ultra High Risk → 7/93 Allocation (EXPECT FAIL) ===\n")
    
    # Extreme difference: Ekubo very safe, JediSwap very risky
    payload = {
        "jediswap_metrics": {
            "utilization": 900,
            "volatility": 6000,  # Extremely high volatility
            "liquidity": 0,  # Low liquidity category (valid: 0-3)
            "audit_score": 65,
            "age_days": 100
        },
        "ekubo_metrics": {
            "utilization": 200,
            "volatility": 500,   # Extremely low volatility
            "liquidity": 3,  # High liquidity category (valid: 0-3)
            "audit_score": 98,
            "age_days": 600
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
    
    if response.status_code == 500:
        error_text = response.text
        print(f"✅ EXPECTED FAILURE")
        print(f"   Error: {error_text[:300]}")
        
        # Verify it's a DAO constraint violation
        if "DAO constraints violated" in error_text or "constraints violated" in error_text.lower():
            print(f"\n✅ Correct revert reason: DAO constraints violated")
            return True
        else:
            print(f"\n⚠️  Failed but not with expected reason")
            print(f"   Expected: 'DAO constraints violated'")
            print(f"   Got: {error_text[:200]}")
            return False
    elif response.status_code == 200:
        data = response.json()
        jedi_pct = data.get("jediswap_pct", 0)
        ekubo_pct = data.get("ekubo_pct", 0)
        print(f"❌ UNEXPECTED SUCCESS")
        print(f"   JediSwap: {jedi_pct/100:.1f}%")
        print(f"   Ekubo: {ekubo_pct/100:.1f}%")
        print(f"   Expected to fail with DAO constraint violation!")
        return False
    else:
        print(f"⚠️  Unexpected status code: {response.status_code}")
        print(f"   Error: {response.text[:300]}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("E2E Test: DAO Constraints FAIL (Expected Reverts)")
    print("=" * 60)
    
    print("\nℹ️  These tests verify that allocations violating DAO limits")
    print("   correctly revert on-chain with 'DAO constraints violated'.")
    print("\nDAO Limits:")
    print("   - max_single: 6000 (60%)")
    print("   - min_diversification: 2 protocols")
    print("   - min per protocol: 1000 (10%)")
    
    results = []
    
    # Test Case 1
    result1 = test_case_1_jedi_high_risk_9_91()
    results.append(("9/91 Jedi Extreme Risk (>60%)", result1))
    
    if result1:
        print("\n⏸  Waiting 30s before next test (avoid nonce conflicts)...")
        time.sleep(30)
    
    # Test Case 2
    result2 = test_case_2_ekubo_very_low_risk_20_80()
    results.append(("20/80 Ekubo Very Low Risk (>60%)", result2))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_pass = all(r for _, r in results)
    
    if all_pass:
        print("\n🎉 All DAO constraint FAIL tests passed!")
        print("   Both allocations correctly reverted with 'DAO constraints violated'.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed - enforcement may not be working correctly.")
        sys.exit(1)
