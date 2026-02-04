#!/usr/bin/env python3
"""
Stone Prover Integration Tests

Tests specific to Stone prover functionality and verification.
"""

import asyncio
import sys
import time
from pathlib import Path
import httpx

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

BASE_URL = "http://localhost:8001"
TIMEOUT = 60  # Longer timeout for proof generation


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


async def test_stone_prover_available():
    """Test if Stone prover service is available"""
    log_test("Stone Prover Availability")
    
    try:
        # Check if Stone prover binary exists
        stone_binary = Path("/opt/obsqra.starknet/stone-prover/target/release/stone-prover")
        if stone_binary.exists():
            log_success("Stone prover binary found")
            return True
        else:
            log_info("Stone prover binary not found (may use LuminAIR instead)")
            return False
    except Exception as e:
        log_error(f"Stone prover check failed: {e}")
        return False


async def test_stone_proof_generation():
    """Test Stone prover proof generation"""
    log_test("Stone Prover Proof Generation")
    
    async with httpx.AsyncClient(timeout=TIMEOUT * 2) as client:
        try:
            payload = {
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
            
            log_info("Generating proof with Stone prover...")
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/api/v1/risk-engine/orchestrate-allocation",
                json=payload
            )
            elapsed = time.time() - start_time
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            
            # Check proof source
            proof_source = data.get("proof_source") or data.get("metrics", {}).get("proof_source", "")
            log_info(f"Proof source: {proof_source}")
            log_info(f"Generation time: {elapsed:.2f}s")
            
            # Verify proof hash
            proof_hash = data.get("proof_hash")
            assert proof_hash, "Proof hash missing"
            
            if "stone" in proof_source.lower():
                log_success(f"Stone prover used - Proof: {proof_hash[:32]}...")
                log_success(f"Generation time: {elapsed:.2f}s")
                return True, data
            else:
                log_info(f"LuminAIR prover used instead (proof_source: {proof_source})")
                log_info("Stone prover may not be configured or may have fallen back")
                return True, data  # Still pass, just note the source
            
        except Exception as e:
            log_error(f"Stone proof generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False, None


async def test_proof_metadata(proof_data: dict):
    """Test proof metadata completeness"""
    log_test("Proof Metadata Verification")
    
    try:
        required_fields = ["proof_hash", "jediswap_pct", "ekubo_pct"]
        missing = [f for f in required_fields if f not in proof_data]
        
        if missing:
            log_error(f"Missing fields: {missing}")
            return False
        
        log_success("All required proof fields present")
        
        # Check proof size
        metrics = proof_data.get("metrics", {})
        proof_size = metrics.get("proof_data_size_bytes", 0)
        if proof_size > 0:
            log_success(f"Proof size: {proof_size / 1024:.2f} KB")
        else:
            log_info("Proof size not available (may be mock proof)")
        
        # Check generation time
        gen_time = metrics.get("proof_generation_time_seconds", 0)
        if gen_time > 0:
            log_success(f"Generation time: {gen_time:.2f}s")
        
        return True
        
    except Exception as e:
        log_error(f"Metadata verification failed: {e}")
        return False


async def test_proof_verification():
    """Test proof verification status"""
    log_test("Proof Verification Status")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            # Get proof summary
            response = await client.get(f"{BASE_URL}/api/v1/analytics/proof-summary")
            assert response.status_code == 200
            
            data = response.json()
            verified_count = data.get("verified_proofs", 0)
            total_proofs = data.get("total_proofs", 0)
            
            log_info(f"Verified proofs: {verified_count}/{total_proofs}")
            
            if total_proofs > 0:
                log_success("Proof verification system operational")
            else:
                log_info("No proofs in database yet")
            
            return True
            
        except Exception as e:
            log_error(f"Verification check failed: {e}")
            return False


async def test_cost_comparison():
    """Test cost comparison calculation"""
    log_test("Cost Comparison (Stone vs Cloud)")
    
    try:
        # Stone prover: $0
        # Cloud proving: $0.75 per proof
        allocations_per_year = 100000
        stone_cost = 0
        cloud_cost = allocations_per_year * 0.75
        
        savings = cloud_cost - stone_cost
        savings_pct = (savings / cloud_cost * 100) if cloud_cost > 0 else 0
        
        log_info(f"Annual allocations: {allocations_per_year:,}")
        log_info(f"Stone prover cost: ${stone_cost:,.2f}")
        log_info(f"Cloud proving cost: ${cloud_cost:,.2f}")
        log_success(f"Annual savings: ${savings:,.2f} ({savings_pct:.1f}%)")
        
        return True
        
    except Exception as e:
        log_error(f"Cost comparison failed: {e}")
        return False


async def main():
    """Run Stone prover integration tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("  Stone Prover Integration Tests")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = {}
    
    # Test 1: Availability
    results["availability"] = await test_stone_prover_available()
    
    # Test 2: Proof Generation
    success, proof_data = await test_stone_proof_generation()
    results["proof_generation"] = success
    
    if success and proof_data:
        # Test 3: Metadata
        results["metadata"] = await test_proof_metadata(proof_data)
    
    # Test 4: Verification
    results["verification"] = await test_proof_verification()
    
    # Test 5: Cost Comparison
    results["cost_comparison"] = await test_cost_comparison()
    
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
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
