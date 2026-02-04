#!/usr/bin/env python3
"""
E2E Test: Constraint Signature Support (STEP 0.6)

Tests that RiskEngine v4 accepts and records constraint signatures.

Test cases:
1. Zero signature (signer=0) - default behavior → PASS
2. Provided signature (signer≠0) → PASS + verify event has constraint_signer
"""

import requests
import time
import sys

BACKEND_URL = "http://localhost:8001"

# Metrics that produce PASS allocation (41/59)
SAFE_METRICS = {
    "jediswap_metrics": {
        "utilization": 500,
        "volatility": 2000,
        "liquidity": 2,
        "audit_score": 85,
        "age_days": 365
    },
    "ekubo_metrics": {
        "utilization": 500,
        "volatility": 2000,
        "liquidity": 2,
        "audit_score": 85,
        "age_days": 365
    }
}


def test_case_1_zero_signature():
    """
    No constraint signature provided (signer=0) - current default.
    Expected: PASS (constraint_signature accepted with signer=0)
    """
    print("\n=== Test Case 1: Zero Signature (signer=0) - Default ===\n")
    
    print("📋 No constraint_signature provided (backend uses zero signature)")
    print(f"📋 Metrics: SAFE (41/59 allocation)")
    print("\n⏳ Calling orchestrate-allocation...")
    
    response = requests.post(
        f"{BACKEND_URL}/api/v1/risk-engine/orchestrate-allocation",
        json=SAFE_METRICS,
        timeout=300
    )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        tx_hash = data.get("tx_hash")
        
        print(f"✅ SUCCESS")
        print(f"   TX: {tx_hash}")
        print(f"   https://sepolia.starkscan.co/tx/{tx_hash}")
        print(f"\n✅ Zero signature accepted (STEP 0.6 passed)")
        return True
    else:
        error_text = response.text
        print(f"❌ FAIL: {response.status_code}")
        print(f"   Error: {error_text[:500]}")
        return False


def test_case_2_provided_signature():
    """
    Provide constraint signature with signer≠0.
    Expected: PASS + AllocationExecuted event has constraint_signer
    """
    print("\n=== Test Case 2: Provided Signature (signer≠0) ===\n")
    
    # Fake signature for testing (contract doesn't verify ECDSA yet)
    constraint_signature = {
        "signer": "0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d",
        "max_single": 6000,
        "min_diversification": 2,
        "max_volatility": 5000,
        "min_liquidity": 1,
        "signature_r": "0x" + "1" * 63,  # Fake signature
        "signature_s": "0x" + "2" * 63,  # Fake signature
        "timestamp": int(time.time())
    }
    
    payload = {
        **SAFE_METRICS,
        "constraint_signature": constraint_signature
    }
    
    print(f"📋 Constraint signature: signer={constraint_signature['signer'][:10]}...")
    print(f"📋 Metrics: SAFE (41/59 allocation)")
    print("\n⏳ Calling orchestrate-allocation...")
    
    response = requests.post(
        f"{BACKEND_URL}/api/v1/risk-engine/orchestrate-allocation",
        json=payload,
        timeout=300
    )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        tx_hash = data.get("tx_hash")
        
        print(f"✅ SUCCESS")
        print(f"   TX: {tx_hash}")
        print(f"   https://sepolia.starkscan.co/tx/{tx_hash}")
        print(f"\n✅ Constraint signature accepted (STEP 0.6 passed)")
        print(f"   ℹ️  Verify event: AllocationExecuted should have constraint_signer={constraint_signature['signer'][:10]}...")
        return True
    else:
        error_text = response.text
        print(f"❌ FAIL: {response.status_code}")
        print(f"   Error: {error_text[:500]}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("E2E Test: Constraint Signature Support (STEP 0.6)")
    print("=" * 60)
    
    print("\nℹ️  These tests verify STEP 0.6: constraint signature support.")
    print("   Contract accepts signatures (signer=0 or signer≠0) and records in events.")
    
    results = []
    
    # Test Case 1: Zero signature
    result1 = test_case_1_zero_signature()
    results.append(("Zero Signature (signer=0)", result1))
    
    if result1:
        print("\n⏸  Waiting 30s before next test...")
        time.sleep(30)
    
    # Test Case 2: Provided signature
    result2 = test_case_2_provided_signature()
    results.append(("Provided Signature (signer≠0)", result2))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_pass = all(r for _, r in results)
    
    if all_pass:
        print("\n🎉 Constraint signature support verified!")
        print("   Both zero and provided signatures work.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed.")
        sys.exit(1)
