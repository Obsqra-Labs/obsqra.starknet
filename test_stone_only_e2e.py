#!/usr/bin/env python3
"""
End-to-End Test: Stone-Only Proof Pipeline (Strict Mode)

Tests the complete Stone-only proof pipeline:
1. Generate Stone proof
2. Register with Integrity FactRegistry
3. Verify on-chain
4. Execute via RiskEngine (if verified)

This test validates the strict mode behavior - no mocks, no fallbacks.
"""
import asyncio
import requests
import json
import time
from typing import Dict, Any, Optional

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

BASE_URL = "http://localhost:8001/api/v1"
FACT_REGISTRY = "0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c"
RISK_ENGINE = "0x00b844ac8c4f9bfc8675e29db75808b5e2ac59100e1e71967a76878522fb5f81"

def fetch_live_metrics() -> Dict[str, Any]:
    resp = requests.get(f"{BASE_URL}/market/metrics", timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return {
        "jediswap_metrics": data.get("jediswap", {}),
        "ekubo_metrics": data.get("ekubo", {}),
    }

def print_test(name: str):
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"  {name}")
    print(f"{'='*70}{Colors.RESET}\n")

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"📝 {msg}")

results = {}

async def test_backend_health():
    """Test 1: Backend Health"""
    print_test("TEST 1: Backend Health Check")
    try:
        resp = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if resp.status_code == 200:
            print_success("Backend is healthy")
            results["backend_health"] = True
            return True
        else:
            print_error(f"Backend returned {resp.status_code}")
            results["backend_health"] = False
            return False
    except Exception as e:
        print_error(f"Backend not accessible: {e}")
        results["backend_health"] = False
        return False

async def test_stone_proof_generation():
    """Test 2: Stone Proof Generation via /proofs/generate"""
    print_test("TEST 2: Stone Proof Generation (Strict Mode)")
    
    test_metrics = {
        "jediswap_metrics": {
            "utilization": 6500,  # 65%
            "volatility": 3500,   # 35%
            "liquidity": 1,
            "audit_score": 98,
            "age_days": 800
        },
        "ekubo_metrics": {
            "utilization": 5000,  # 50%
            "volatility": 2500,   # 25%
            "liquidity": 2,
            "audit_score": 95,
            "age_days": 600
        }
    }
    
    try:
        print_info("Requesting Stone proof generation...")
        print_info(f"Jediswap: util={test_metrics['jediswap_metrics']['utilization']}, vol={test_metrics['jediswap_metrics']['volatility']}")
        print_info(f"Ekubo: util={test_metrics['ekubo_metrics']['utilization']}, vol={test_metrics['ekubo_metrics']['volatility']}")
        
        start_time = time.time()
        resp = requests.post(
            f"{BASE_URL}/proofs/generate",
            json=test_metrics,
            timeout=120  # Stone proof generation can take 2-4 seconds
        )
        generation_time = time.time() - start_time
        
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"Proof generated in {generation_time:.2f}s")
            print_info(f"Proof hash: {data.get('proof_hash', 'N/A')[:32]}...")
            fact_hash = data.get('fact_hash')
            if fact_hash:
                print_info(f"Fact hash: {fact_hash[:20]}...")
            else:
                print_warning("⚠️  Fact hash is MISSING - Integrity registration may have failed")
            print_info(f"Jediswap score: {data.get('jediswap_score')}")
            print_info(f"Ekubo score: {data.get('ekubo_score')}")
            verified = data.get('verified', False)
            print_info(f"Verified: {verified}")
            print_info(f"Status: {data.get('status')}")
            
            # Check if this is the old response format (missing fact_hash/verified)
            if 'fact_hash' not in data or 'verified' not in data:
                print_error("❌ Response missing fact_hash or verified field - server may be running old code")
                print_error("   Expected fields: fact_hash, verified")
                print_error("   Got fields: " + ", ".join(data.keys()))
                results["stone_proof_generation"] = False
                return False, data
            
            if verified and fact_hash:
                print_success("✅ Proof verified on-chain in FactRegistry")
                results["stone_proof_generation"] = True
                return True, data
            else:
                print_error("❌ Proof generated but NOT verified on-chain")
                print_error("   This should not happen in strict mode")
                if not fact_hash:
                    print_error("   Root cause: No fact_hash returned - Integrity registration failed")
                    print_error("   This usually means VERIFIER_NOT_FOUND or contract call failed")
                results["stone_proof_generation"] = False
                return False, data
        else:
            error_detail = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
            print_error(f"Proof generation failed: {resp.status_code}")
            print_error(f"Error: {error_detail}")
            results["stone_proof_generation"] = False
            return False, None
    except requests.exceptions.Timeout:
        print_error("Proof generation timed out (>120s)")
        results["stone_proof_generation"] = False
        return False, None
    except Exception as e:
        print_error(f"Proof generation exception: {e}")
        results["stone_proof_generation"] = False
        return False, None

async def test_error_handling_invalid_metrics():
    """Test 3: Error Handling - Invalid Metrics"""
    print_test("TEST 3: Error Handling (Invalid Metrics)")
    
    invalid_metrics = {
        "jediswap_metrics": {
            "utilization": -100,  # Invalid: negative
            "volatility": 3500,
            "liquidity": 1,
            "audit_score": 98,
            "age_days": 800
        },
        "ekubo_metrics": {
            "utilization": 5000,
            "volatility": 2500,
            "liquidity": 2,
            "audit_score": 95,
            "age_days": 600
        }
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/proofs/generate",
            json=invalid_metrics,
            timeout=30
        )
        
        if resp.status_code >= 400:
            error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
            print_success("Error correctly returned for invalid metrics")
            print_info(f"Status: {resp.status_code}")
            print_info(f"Error structure: {json.dumps(error_data, indent=2)[:200]}...")
            
            # Check if error has strict_mode flag
            if isinstance(error_data, dict) and error_data.get('strict_mode'):
                print_success("Error includes 'strict_mode' flag")
            else:
                print_warning("Error missing 'strict_mode' flag")
            
            results["error_handling"] = True
            return True
        else:
            print_error(f"Expected error but got {resp.status_code}")
            results["error_handling"] = False
            return False
    except Exception as e:
        print_error(f"Error handling test exception: {e}")
        results["error_handling"] = False
        return False

async def test_orchestration_flow():
    """Test 4: Full Orchestration Flow"""
    print_test("TEST 4: Full Orchestration Flow (Stone → Integrity → RiskEngine)")
    
    test_metrics = {
        "jediswap_metrics": {
            "utilization": 6500,
            "volatility": 3500,
            "liquidity": 1,
            "audit_score": 98,
            "age_days": 800
        },
        "ekubo_metrics": {
            "utilization": 5000,
            "volatility": 2500,
            "liquidity": 2,
            "audit_score": 95,
            "age_days": 600
        }
    }
    
    try:
        print_info("Starting orchestration (Stone proof → Integrity → RiskEngine)...")
        start_time = time.time()
        
        resp = requests.post(
            f"{BASE_URL}/risk-engine/orchestrate-allocation",
            json=test_metrics,
            timeout=180  # Full flow can take longer
        )
        
        orchestration_time = time.time() - start_time
        
        if resp.status_code == 200:
            data = resp.json()
            print_success(f"Orchestration completed in {orchestration_time:.2f}s")
            print_info(f"Proposal ID: {data.get('proposal_id', 'N/A')}")
            print_info(f"Proof hash: {data.get('proof_hash', 'N/A')[:32]}...")
            print_info(f"Fact hash: {data.get('fact_hash', 'N/A')[:20]}...")
            print_info(f"Verified: {data.get('verified', False)}")
            
            if data.get('verified'):
                print_success("✅ Full flow: Stone → Integrity → RiskEngine (verified)")
                results["orchestration_flow"] = True
                return True
            else:
                print_warning("Orchestration completed but proof not verified")
                results["orchestration_flow"] = False
                return False
        else:
            error_data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
            print_error(f"Orchestration failed: {resp.status_code}")
            print_error(f"Error: {json.dumps(error_data, indent=2)[:300]}...")
            results["orchestration_flow"] = False
            return False
    except Exception as e:
        print_error(f"Orchestration exception: {e}")
        results["orchestration_flow"] = False
        return False

async def test_verification_status_endpoint():
    """Test 5: Verification Status Endpoint"""
    print_test("TEST 5: Verification Status Endpoint")
    
    # First generate a proof to get a proof_job_id
    test_metrics = {
        "jediswap_metrics": {
            "utilization": 6500,
            "volatility": 3500,
            "liquidity": 1,
            "audit_score": 98,
            "age_days": 800
        },
        "ekubo_metrics": {
            "utilization": 5000,
            "volatility": 2500,
            "liquidity": 2,
            "audit_score": 95,
            "age_days": 600
        }
    }
    
    try:
        # Generate proof first
        resp = requests.post(
            f"{BASE_URL}/risk-engine/orchestrate-allocation",
            json=test_metrics,
            timeout=180
        )
        
        if resp.status_code != 200:
            print_warning("Could not generate proof for verification test")
            results["verification_status"] = None
            return None
        
        data = resp.json()
        proof_job_id = data.get('proposal_id')  # Same as proof_job_id
        
        if not proof_job_id:
            print_warning("No proof_job_id returned")
            results["verification_status"] = None
            return None
        
        # Check verification status
        print_info(f"Checking verification status for proof_job_id: {proof_job_id}")
        status_resp = requests.get(
            f"{BASE_URL}/verification/verification-status/{proof_job_id}",
            timeout=30
        )
        
        if status_resp.status_code == 200:
            status_data = status_resp.json()
            print_success("Verification status retrieved")
            print_info(f"Fact hash: {status_data.get('fact_hash', 'N/A')[:20]}...")
            print_info(f"Verified: {status_data.get('verified', False)}")
            print_info(f"Fact Registry: {status_data.get('fact_registry_address', 'N/A')[:20]}...")
            
            if status_data.get('verified'):
                print_success("✅ Verification status confirms on-chain verification")
                results["verification_status"] = True
                return True
            else:
                print_warning("Verification status shows not verified")
                results["verification_status"] = False
                return False
        else:
            print_error(f"Verification status check failed: {status_resp.status_code}")
            results["verification_status"] = False
            return False
    except Exception as e:
        print_error(f"Verification status test exception: {e}")
        results["verification_status"] = False
        return False

async def main():
    """Run all Stone-only E2E tests"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print("  STONE-ONLY E2E TEST SUITE (Strict Mode)")
    print("  Testing: Stone → Integrity → RiskEngine")
    print(f"{'='*70}{Colors.RESET}\n")
    
    # Test 1: Backend Health
    if not await test_backend_health():
        print_error("Backend is not healthy. Stopping tests.")
        return 1
    
    # Test 2: Stone Proof Generation
    success, proof_data = await test_stone_proof_generation()
    if not success:
        print_error("Stone proof generation failed. This is critical.")
        return 1
    
    # Test 3: Error Handling
    await test_error_handling_invalid_metrics()
    
    # Test 4: Full Orchestration
    await test_orchestration_flow()
    
    # Test 5: Verification Status
    await test_verification_status_endpoint()
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*70}")
    print("  TEST SUMMARY")
    print(f"{'='*70}{Colors.RESET}\n")
    
    passed = sum(1 for v in results.values() if v is True)
    total = len([v for v in results.values() if v is not None])
    
    for test_name, result in results.items():
        if result is True:
            status = f"{Colors.GREEN}PASS{Colors.RESET}"
        elif result is False:
            status = f"{Colors.RED}FAIL{Colors.RESET}"
        else:
            status = f"{Colors.YELLOW}SKIP{Colors.RESET}"
        print(f"  {test_name:.<50} {status}")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"  {Colors.GREEN}✅ All tests passed! Stone-only pipeline is working.{Colors.RESET}\n")
        return 0
    else:
        print(f"  {Colors.YELLOW}⚠️  Some tests need attention{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
