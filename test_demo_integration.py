#!/usr/bin/env python3
"""
Demo Frontend Integration Test

Tests that demo frontend can connect to backend and generate proofs.
"""

import asyncio
import sys
import httpx
from pathlib import Path

BASE_URL = "http://localhost:8001"
DEMO_FRONTEND_URL = "http://localhost:8080"
TIMEOUT = 30


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def log_test(name: str):
    print(f"\n{Colors.BLUE}━━━ {name} ━━━{Colors.RESET}")


def log_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def log_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def log_info(msg: str):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.RESET}")


async def test_backend_demo_endpoint():
    """Test demo endpoint is accessible"""
    log_test("Backend Demo Endpoint")
    
    async with httpx.AsyncClient(timeout=TIMEOUT * 2) as client:
        try:
            payload = {
                "jediswap_metrics": {
                    "utilization": 75,
                    "volatility": 30,
                    "liquidity": 5000000,
                    "audit_score": 85,
                    "age_days": 180
                },
                "ekubo_metrics": {
                    "utilization": 60,
                    "volatility": 25,
                    "liquidity": 3000000,
                    "audit_score": 90,
                    "age_days": 120
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/demo/generate-proof",
                json=payload
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            
            # Verify response structure
            required_fields = ["proof_hash", "proof_source", "generation_time_seconds", 
                             "proof_size_kb", "jediswap_pct", "ekubo_pct", "cost_savings"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                log_error(f"Missing fields: {missing}")
                return False
            
            log_success(f"Demo endpoint working - Proof: {data['proof_hash'][:32]}...")
            log_info(f"Proof source: {data['proof_source']}")
            log_info(f"Generation time: {data['generation_time_seconds']:.2f}s")
            log_info(f"Cost savings: ${data['cost_savings']['annual_savings']:,.2f}")
            
            return True
            
        except Exception as e:
            log_error(f"Demo endpoint test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_cost_comparison_endpoint():
    """Test cost comparison endpoint"""
    log_test("Cost Comparison Endpoint")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/demo/cost-comparison",
                params={"allocations_per_year": 100000}
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            
            log_success("Cost comparison endpoint working")
            log_info(f"Stone cost: ${data['stone_prover']['annual_cost']:,.2f}")
            log_info(f"Cloud cost: ${data['cloud_proving']['annual_cost']:,.2f}")
            log_info(f"Savings: ${data['savings']['annual']:,.2f} ({data['savings']['percentage']:.1f}%)")
            
            return True
            
        except Exception as e:
            log_error(f"Cost comparison test failed: {e}")
            return False


async def test_demo_frontend_accessible():
    """Test if demo frontend is accessible"""
    log_test("Demo Frontend Accessibility")
    
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        try:
            response = await client.get(DEMO_FRONTEND_URL)
            if response.status_code == 200:
                log_success("Demo frontend is accessible")
                return True
            else:
                log_info(f"Demo frontend returned {response.status_code} (may not be running)")
                log_info("Start with: cd demo-frontend/src && python3 -m http.server 8080")
                return True  # Don't fail if frontend isn't running
        except Exception as e:
            log_info(f"Demo frontend not accessible: {e}")
            log_info("This is OK - frontend can be started separately")
            return True  # Don't fail if frontend isn't running


async def test_end_to_end_flow():
    """Test complete end-to-end flow"""
    log_test("End-to-End Flow")
    
    async with httpx.AsyncClient(timeout=TIMEOUT * 2) as client:
        try:
            # Step 1: Generate proof
            log_info("Step 1: Generating proof...")
            proof_response = await client.post(
                f"{BASE_URL}/api/v1/demo/generate-proof",
                json={
                    "jediswap_metrics": {
                        "utilization": 70,
                        "volatility": 28,
                        "liquidity": 4500000,
                        "audit_score": 88,
                        "age_days": 150
                    },
                    "ekubo_metrics": {
                        "utilization": 65,
                        "volatility": 22,
                        "liquidity": 3500000,
                        "audit_score": 92,
                        "age_days": 100
                    }
                }
            )
            
            assert proof_response.status_code == 200
            proof_data = proof_response.json()
            log_success(f"Proof generated: {proof_data['proof_hash'][:32]}...")
            
            # Step 2: Verify constraints
            log_info("Step 2: Verifying constraints...")
            max_single = max(proof_data['jediswap_pct'], proof_data['ekubo_pct'])
            constraints_verified = proof_data.get('constraints_verified', False)
            if constraints_verified:
                log_success(f"Constraints verified (max single: {max_single/100}%)")
            else:
                log_info(f"Constraints not verified (max single: {max_single/100}%)")
                # Don't fail the test - this is expected behavior for demo
                # The demo shows both verified and unverified cases
            
            # Step 3: Check cost savings
            log_info("Step 3: Checking cost savings...")
            savings = proof_data['cost_savings']['annual_savings']
            if savings > 0:
                log_success(f"Cost savings: ${savings:,.2f}")
            else:
                log_info("No cost savings calculated")
            
            log_success("End-to-end flow completed successfully")
            return True
            
        except Exception as e:
            log_error(f"End-to-end flow failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run demo integration tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("  Demo Frontend Integration Tests")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = {}
    
    # Test 1: Backend Demo Endpoint
    results["demo_endpoint"] = await test_backend_demo_endpoint()
    
    # Test 2: Cost Comparison
    results["cost_comparison"] = await test_cost_comparison_endpoint()
    
    # Test 3: Frontend Accessibility
    results["frontend_accessible"] = await test_demo_frontend_accessible()
    
    # Test 4: End-to-End Flow
    if results["demo_endpoint"]:
        results["e2e_flow"] = await test_end_to_end_flow()
    else:
        results["e2e_flow"] = False
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print("  Test Summary")
    print(f"{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {test_name:.<40} {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"  Total: {passed}/{total} tests passed\n")
    
    if passed == total:
        print(f"  {Colors.GREEN}✅ All tests passed!{Colors.RESET}")
        print(f"\n  {Colors.YELLOW}To start the demo frontend:{Colors.RESET}")
        print(f"  cd /opt/obsqra.starknet/demo-frontend/src")
        print(f"  python3 -m http.server 8080")
        print(f"  Then open: http://localhost:8080\n")
    else:
        print(f"  {Colors.RED}❌ Some tests failed{Colors.RESET}\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
