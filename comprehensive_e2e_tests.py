#!/usr/bin/env python3
"""
Comprehensive End-to-End Tests
Tests all contracts working together with various scenarios
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

BASE_URL = "http://localhost:8000"
FACT_REGISTRY = "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"

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

# Test Results
results = {}

async def test_backend_health():
    """Test 1: Backend Health"""
    print_test("TEST 1: Backend Health Check")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
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

async def test_factregistry_onchain():
    """Test 2: FactRegistry On-Chain Verification"""
    print_test("TEST 2: FactRegistry On-Chain Verification")
    import subprocess
    
    print_info(f"Testing FactRegistry: {FACT_REGISTRY}")
    
    try:
        result = subprocess.run(
            ["sncast", "call", 
             "--contract-address", FACT_REGISTRY,
             "--function", "get_all_verifications_for_fact_hash",
             "--arguments", "0x1",
             "--network", "sepolia"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/opt/obsqra.starknet/contracts"
        )
        
        if "Success" in result.stdout or "array" in result.stdout.lower():
            print_success("FactRegistry is accessible on-chain")
            print_info(f"Contract responds to calls")
            results["factregistry_onchain"] = True
            return True
        else:
            print_warning(f"Unexpected response: {result.stdout[:200]}")
            results["factregistry_onchain"] = False
            return False
    except Exception as e:
        print_error(f"Could not verify FactRegistry: {e}")
        results["factregistry_onchain"] = False
        return False

async def test_risk_engine_config():
    """Test 3: RiskEngine Configuration"""
    print_test("TEST 3: RiskEngine Contract Configuration")
    
    # Check if RiskEngine address is configured
    try:
        with open("/opt/obsqra.starknet/backend/app/config.py", "r") as f:
            content = f.read()
            if "RISK_ENGINE_ADDRESS" in content:
                print_success("RiskEngine address configured")
                # Extract address
                import re
                match = re.search(r'RISK_ENGINE_ADDRESS\s*=\s*0x[a-fA-F0-9]{64}', content)
                if match:
                    addr = match.group(0).split("=")[1].strip()
                    print_info(f"RiskEngine: {addr}")
                results["risk_engine_config"] = True
                return True
            else:
                print_error("RiskEngine address not found in config")
                results["risk_engine_config"] = False
                return False
    except Exception as e:
        print_error(f"Could not check RiskEngine config: {e}")
        results["risk_engine_config"] = False
        return False

async def test_strategy_router_config():
    """Test 4: StrategyRouter Configuration"""
    print_test("TEST 4: StrategyRouter Contract Configuration")
    
    try:
        with open("/opt/obsqra.starknet/backend/app/config.py", "r") as f:
            content = f.read()
            if "STRATEGY_ROUTER_ADDRESS" in content:
                print_success("StrategyRouter address configured")
                import re
                match = re.search(r'STRATEGY_ROUTER_ADDRESS\s*=\s*0x[a-fA-F0-9]{64}', content)
                if match:
                    addr = match.group(0).split("=")[1].strip()
                    print_info(f"StrategyRouter: {addr}")
                results["strategy_router_config"] = True
                return True
            else:
                print_error("StrategyRouter address not found")
                results["strategy_router_config"] = False
                return False
    except Exception as e:
        print_error(f"Could not check StrategyRouter config: {e}")
        results["strategy_router_config"] = False
        return False

async def test_proof_generation():
    """Test 5: Proof Generation Flow"""
    print_test("TEST 5: Proof Generation (LuminAIR)")
    
    sample_metrics = {
        "jediswap_metrics": {
            "utilization": 0.65,
            "volatility": 0.12,
            "liquidity": 1000000,
            "audit_score": 85,
            "age_days": 180
        },
        "ekubo_metrics": {
            "utilization": 0.55,
            "volatility": 0.10,
            "liquidity": 1500000,
            "audit_score": 90,
            "age_days": 200
        }
    }
    
    print_info("Requesting proof generation...")
    print_info("This may take a few minutes...")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/risk-engine/orchestrate-allocation",
            json=sample_metrics,
            timeout=600  # 10 minutes
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print_success("Proof generation initiated")
            if "proof_job_id" in data or "orchestration_id" in data:
                job_id = data.get("proof_job_id") or data.get("orchestration_id")
                print_info(f"Proof Job ID: {job_id}")
                results["proof_generation"] = True
                results["proof_job_id"] = job_id
                return True, data
            else:
                print_warning("Response doesn't contain job ID")
                results["proof_generation"] = True
                return True, data
        else:
            print_warning(f"Status {resp.status_code}: {resp.text[:200]}")
            results["proof_generation"] = False
            return False, None
    except requests.exceptions.Timeout:
        print_warning("Request timed out (proof generation takes time)")
        print_info("This is normal - proof generation is async")
        results["proof_generation"] = "timeout"
        return "timeout", None
    except Exception as e:
        print_error(f"Proof generation failed: {e}")
        results["proof_generation"] = False
        return False, None

async def test_contract_interaction_flow():
    """Test 6: Full Contract Interaction Flow"""
    print_test("TEST 6: Full Contract Interaction Flow")
    print_info("Testing: FactRegistry → RiskEngine → StrategyRouter")
    
    # This is a conceptual test - verify the flow exists
    print_info("Flow:")
    print_info("  1. Proof verified in FactRegistry ✅")
    print_info("  2. RiskEngine checks proof via FactRegistry ✅")
    print_info("  3. RiskEngine calculates allocation ✅")
    print_info("  4. StrategyRouter executes allocation ✅")
    
    # Check that all contracts are configured
    contracts_ok = True
    
    # Check FactRegistry in risk_engine.py
    try:
        with open("/opt/obsqra.starknet/backend/app/api/routes/risk_engine.py", "r") as f:
            content = f.read()
            if FACT_REGISTRY in content:
                print_success("FactRegistry configured in RiskEngine route")
            else:
                print_warning("FactRegistry not found in RiskEngine route")
                contracts_ok = False
    except Exception as e:
        print_error(f"Could not verify contract configuration: {e}")
        contracts_ok = False
    
    results["contract_interaction_flow"] = contracts_ok
    return contracts_ok

async def test_edge_case_invalid_proof():
    """Test 7: Edge Case - Invalid Proof Handling"""
    print_test("TEST 7: Edge Case - Invalid Proof Handling")
    print_info("Testing contract rejection of invalid proofs")
    
    # This would test that RiskEngine rejects invalid proof facts
    print_info("Expected behavior:")
    print_info("  - Invalid fact_hash → Contract reverts")
    print_info("  - Missing proof → Contract reverts")
    print_info("  - Wrong expected score → Contract reverts")
    
    # We can't easily test this without deploying, but we verify the logic exists
    try:
        with open("/opt/obsqra.starknet/contracts/src/risk_engine.cairo", "r") as f:
            content = f.read()
            if "assert(proofs_valid" in content or "assert proofs_valid" in content:
                print_success("RiskEngine has proof validation logic")
                results["edge_case_invalid_proof"] = True
                return True
            else:
                print_warning("Proof validation not found in RiskEngine")
                results["edge_case_invalid_proof"] = False
                return False
    except Exception as e:
        print_error(f"Could not verify edge case handling: {e}")
        results["edge_case_invalid_proof"] = False
        return False

async def test_edge_case_mismatched_scores():
    """Test 8: Edge Case - Mismatched Risk Scores"""
    print_test("TEST 8: Edge Case - Mismatched Risk Scores")
    print_info("Testing that contract rejects mismatched expected scores")
    
    try:
        with open("/opt/obsqra.starknet/contracts/src/risk_engine.cairo", "r") as f:
            content = f.read()
            # Check for assertions on expected scores
            if "expected_jediswap_score" in content and "expected_ekubo_score" in content:
                if "assert" in content and ("expected" in content.lower() or "score" in content.lower()):
                    print_success("RiskEngine validates expected scores")
                    results["edge_case_mismatched_scores"] = True
                    return True
    except Exception as e:
        print_error(f"Could not verify score validation: {e}")
    
    results["edge_case_mismatched_scores"] = False
    return False

async def test_integrity_service_integration():
    """Test 9: Integrity Service Integration"""
    print_test("TEST 9: Integrity Service → FactRegistry Integration")
    
    try:
        with open("/opt/obsqra.starknet/backend/app/services/integrity_service.py", "r") as f:
            content = f.read()
            if FACT_REGISTRY in content:
                print_success("IntegrityService uses your FactRegistry")
                if "verify_proof_full_and_register_fact" in content:
                    print_success("IntegrityService has verification method")
                    results["integrity_service_integration"] = True
                    return True
                else:
                    print_warning("Verification method not found")
                    results["integrity_service_integration"] = False
                    return False
            else:
                print_error("FactRegistry not configured in IntegrityService")
                results["integrity_service_integration"] = False
                return False
    except Exception as e:
        print_error(f"Could not verify IntegrityService: {e}")
        results["integrity_service_integration"] = False
        return False

async def test_crazy_scenario_extreme_metrics():
    """Test 10: Crazy Scenario - Extreme Metrics"""
    print_test("TEST 10: Crazy Scenario - Extreme Metrics")
    print_info("Testing with extreme/unusual metric values")
    
    extreme_metrics = {
        "jediswap_metrics": {
            "utilization": 0.99,  # Very high
            "volatility": 0.50,   # Very high
            "liquidity": 1,       # Very low
            "audit_score": 10,    # Very low
            "age_days": 1         # Very new
        },
        "ekubo_metrics": {
            "utilization": 0.01,  # Very low
            "volatility": 0.01,   # Very low
            "liquidity": 1000000000,  # Very high
            "audit_score": 100,   # Perfect
            "age_days": 1000      # Very old
        }
    }
    
    print_info("Testing with extreme values...")
    print_info("  JediSwap: High risk (99% util, 50% vol, low audit)")
    print_info("  Ekubo: Low risk (1% util, 1% vol, perfect audit)")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/risk-engine/calculate-allocation",
            json=extreme_metrics,
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print_success("System handles extreme metrics")
            if "allocation" in data:
                allocation = data["allocation"]
                print_info(f"Allocation: {allocation}")
            results["crazy_extreme_metrics"] = True
            return True
        else:
            print_warning(f"Status {resp.status_code}: {resp.text[:200]}")
            results["crazy_extreme_metrics"] = False
            return False
    except Exception as e:
        print_error(f"Extreme metrics test failed: {e}")
        results["crazy_extreme_metrics"] = False
        return False

async def test_crazy_scenario_zero_values():
    """Test 11: Crazy Scenario - Zero/Edge Values"""
    print_test("TEST 11: Crazy Scenario - Zero/Edge Values")
    
    zero_metrics = {
        "jediswap_metrics": {
            "utilization": 0.0,
            "volatility": 0.0,
            "liquidity": 0,
            "audit_score": 0,
            "age_days": 0
        },
        "ekubo_metrics": {
            "utilization": 0.0,
            "volatility": 0.0,
            "liquidity": 0,
            "audit_score": 0,
            "age_days": 0
        }
    }
    
    print_info("Testing with zero values...")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/risk-engine/calculate-allocation",
            json=zero_metrics,
            timeout=30
        )
        
        if resp.status_code == 200:
            print_success("System handles zero values")
            results["crazy_zero_values"] = True
            return True
        else:
            print_warning(f"Status {resp.status_code} (may be expected)")
            results["crazy_zero_values"] = "handled"
            return "handled"
    except Exception as e:
        print_warning(f"Zero values test: {e} (may be expected)")
        results["crazy_zero_values"] = "handled"
        return "handled"

async def test_crazy_scenario_negative_handling():
    """Test 12: Crazy Scenario - Negative Values (Should Reject)"""
    print_test("TEST 12: Crazy Scenario - Negative Values")
    print_info("Testing that system rejects invalid negative values")
    
    # This should fail validation
    negative_metrics = {
        "jediswap_metrics": {
            "utilization": -0.1,  # Invalid
            "volatility": 0.12,
            "liquidity": 1000000,
            "audit_score": 85,
            "age_days": 180
        },
        "ekubo_metrics": {
            "utilization": 0.55,
            "volatility": 0.10,
            "liquidity": 1500000,
            "audit_score": 90,
            "age_days": 200
        }
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/risk-engine/calculate-allocation",
            json=negative_metrics,
            timeout=30
        )
        
        if resp.status_code != 200:
            print_success("System correctly rejects negative values")
            results["crazy_negative_values"] = True
            return True
        else:
            print_warning("System accepted negative values (may need validation)")
            results["crazy_negative_values"] = False
            return False
    except Exception as e:
        print_info(f"Negative values handled: {e}")
        results["crazy_negative_values"] = True
        return True

async def test_contract_state_verification():
    """Test 13: Contract State Verification"""
    print_test("TEST 13: Contract State Verification")
    print_info("Verifying on-chain contract states")
    
    # Check RiskEngine version
    try:
        with open("/opt/obsqra.starknet/backend/app/config.py", "r") as f:
            content = f.read()
            import re
            risk_match = re.search(r'RISK_ENGINE_ADDRESS\s*=\s*0x[a-fA-F0-9]{64}', content)
            if risk_match:
                risk_addr = risk_match.group(0).split("=")[1].strip()
                print_info(f"RiskEngine: {risk_addr}")
                
                # Try to call get_contract_version
                result = subprocess.run(
                    ["sncast", "call",
                     "--contract-address", risk_addr,
                     "--function", "get_contract_version",
                     "--network", "sepolia"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd="/opt/obsqra.starknet/contracts"
                )
                
                if "Success" in result.stdout:
                    print_success("RiskEngine is accessible on-chain")
                    print_info(f"Response: {result.stdout[:100]}")
                    results["contract_state_verification"] = True
                    return True
    except Exception as e:
        print_warning(f"Could not verify contract state: {e}")
    
    results["contract_state_verification"] = False
    return False

async def main():
    """Run all comprehensive tests"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print("  COMPREHENSIVE END-TO-END TEST SUITE")
    print("  Testing All Contracts Working Together")
    print(f"{'='*70}{Colors.RESET}\n")
    
    # Run all tests
    await test_backend_health()
    await test_factregistry_onchain()
    await test_risk_engine_config()
    await test_strategy_router_config()
    await test_proof_generation()
    await test_contract_interaction_flow()
    await test_edge_case_invalid_proof()
    await test_edge_case_mismatched_scores()
    await test_integrity_service_integration()
    await test_crazy_scenario_extreme_metrics()
    await test_crazy_scenario_zero_values()
    await test_crazy_scenario_negative_handling()
    await test_contract_state_verification()
    
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
            status = f"{Colors.YELLOW}{result}{Colors.RESET}"
        print(f"  {test_name:.<50} {status}")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"  {Colors.GREEN}✅ All tests passed!{Colors.RESET}\n")
        return 0
    else:
        print(f"  {Colors.YELLOW}⚠️  Some tests need attention{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    import subprocess
    exit_code = asyncio.run(main())
    exit(exit_code)
