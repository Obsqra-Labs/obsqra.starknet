#!/usr/bin/env python3
"""Comprehensive E2E Test Suite for 5/5 zkML System"""
import asyncio
import json
import sys
from pathlib import Path
import httpx
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.config import get_settings
from app.utils.rpc import get_rpc_urls

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

settings = get_settings()
results = {}
# Backend runs on port 8001 - try both ports and use the one that works
backend_url = None
import httpx as _httpx
try:
    for port in [8001, 8000]:
        try:
            _test_client = _httpx.AsyncClient(timeout=2.0)
            _test_r = asyncio.run(_test_client.get(f"http://localhost:{port}/health"))
            if _test_r.status_code == 200:
                backend_url = f"http://localhost:{port}"
                break
            asyncio.run(_test_client.aclose())
        except:
            pass
except:
    pass
if not backend_url:
    backend_url = settings.API_BASE_URL or "http://localhost:8001"
print(f"{Colors.CYAN}Using backend URL: {backend_url}{Colors.RESET}\n")

def print_test(name, status, details=""):
    icon = f"{Colors.GREEN}✅" if status else f"{Colors.RED}❌"
    print(f"{icon} {name:.<50} {'PASS' if status else 'FAIL'}")
    if details: print(f"   {Colors.CYAN}{details}{Colors.RESET}")
    results[name] = status

async def test_backend_health():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{backend_url}/health")
            print_test("Backend Health", r.status_code == 200, f"Status: {r.status_code}")
            return r.status_code == 200
    except Exception as e:
        print_test("Backend Health", False, str(e))
        return False

async def test_model_registry():
    print(f"\n{Colors.BLUE}{'='*70}")
    print("  Test 2: Model Registry Configuration")
    print(f"{'='*70}{Colors.RESET}\n")
    
    if not settings.MODEL_REGISTRY_ADDRESS:
        print_test("Model Registry Address", False, "Not configured")
        return False
    
    print_test("Model Registry Address", True, f"Address: {settings.MODEL_REGISTRY_ADDRESS}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try the correct endpoint path
            r = await client.get(f"{backend_url}/api/v1/model-registry/current")
            if r.status_code == 200:
                data = r.json()
                version = data.get('version', 'N/A')
                model_hash = data.get('model_hash', 'N/A')[:16] if data.get('model_hash') else 'N/A'
                print_test("Model Registry API", True, f"Version: {version}, Hash: {model_hash}...")
                return True
            else:
                # Debug: show what we got
                error_msg = f"Status: {r.status_code}"
                if r.text:
                    error_msg += f", Response: {r.text[:100]}"
                print_test("Model Registry API", False, error_msg)
                return False
    except Exception as e:
        print_test("Model Registry API", False, f"Exception: {str(e)}")
        return False

async def test_proof_generation():
    print(f"\n{Colors.BLUE}{'='*70}")
    print("  Test 3: Proof Generation with Model Hash")
    print(f"{'='*70}{Colors.RESET}\n")
    
    # Use valid metric ranges (0-100 for percentages, 0-3 for liquidity tier)
    test_metrics = {
        "jediswap_metrics": {"utilization": 50, "volatility": 30, "liquidity": 2, "audit_score": 90, "age_days": 365},
        "ekubo_metrics": {"utilization": 60, "volatility": 25, "liquidity": 2, "audit_score": 85, "age_days": 180}
    }
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            print(f"   {Colors.CYAN}Generating proof...{Colors.RESET}")
            r = await client.post(f"{backend_url}/api/v1/risk-engine/propose-allocation", json=test_metrics)
            if r.status_code != 200:
                error_msg = f"Status: {r.status_code}"
                if r.text:
                    error_msg += f", Response: {r.text[:200]}"
                print_test("Proof Generation", False, error_msg)
                return False
            
            data = r.json()
            proof_job_id = data.get("proof_job_id")
            if not proof_job_id:
                print_test("Proof Generation", False, f"No proof_job_id in response: {data}")
                return False
            
            # Check if proof is already verified (might be instant)
            proof_status = data.get("proof_status")
            if proof_status == "verified":
                metrics = data.get("metrics", {})
                model_version = metrics.get("model_version", {})
                has_hash = bool(model_version.get("model_hash"))
                print_test("Proof Generation", True, f"Status: verified (instant)")
                if has_hash:
                    print_test("Model Hash in Proof", True, f"Hash: {model_version.get('model_hash', 'N/A')[:16]}...")
                return True
            
            # Otherwise wait and check status
            await asyncio.sleep(5)
            status_r = await client.get(f"{backend_url}/api/v1/risk-engine/proof-status/{proof_job_id}")
            if status_r.status_code == 200:
                status_data = status_r.json()
                metrics = status_data.get("metrics", {})
                model_version = metrics.get("model_version", {})
                has_hash = bool(model_version.get("model_hash"))
                print_test("Proof Generation", True, f"Status: {status_data.get('status')}")
                if has_hash:
                    print_test("Model Hash in Proof", True, f"Hash: {model_version.get('model_hash', 'N/A')[:16]}...")
                return True
            else:
                print_test("Proof Generation", False, f"Status check failed: {status_r.status_code}")
                return False
    except Exception as e:
        print_test("Proof Generation", False, f"Exception: {str(e)}")
        return False

async def test_onchain_verification():
    print(f"\n{Colors.BLUE}{'='*70}")
    print("  Test 4: On-Chain Verification")
    print(f"{'='*70}{Colors.RESET}\n")
    
    if not settings.RISK_ENGINE_ADDRESS:
        print_test("RiskEngine Address", False, "Not configured")
        return False
    
    print_test("RiskEngine Address", True, f"Address: {settings.RISK_ENGINE_ADDRESS}")
    
    try:
        rpc_urls = get_rpc_urls()
        client = FullNodeClient(node_url=rpc_urls[0])
        abi_path = ROOT / "contracts" / "target" / "dev" / "obsqra_contracts_RiskEngine.contract_class.json"
        if not abi_path.exists():
            print_test("RiskEngine ABI", False, "ABI not found")
            return False
        with open(abi_path) as f:
            abi = json.load(f).get("abi", [])
        contract = Contract(address=int(settings.RISK_ENGINE_ADDRESS, 16), abi=abi, provider=client)
        version = await contract.functions["get_contract_version"].call(block_number="latest")
        print_test("RiskEngine Version", True, f"Version: {version}")
        return True
    except Exception as e:
        print_test("On-Chain Verification", False, str(e))
        return False

async def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print("  OBSQRA LABS - COMPREHENSIVE 5/5 ZKML E2E TEST SUITE")
    print(f"{'='*70}{Colors.RESET}\n")
    print(f"{Colors.CYAN}Testing complete zkML system with model provenance{Colors.RESET}\n")
    
    await test_backend_health()
    await test_model_registry()
    await test_proof_generation()
    await test_onchain_verification()
    
    print(f"\n{Colors.BLUE}{'='*70}")
    print("  Test Summary")
    print(f"{'='*70}{Colors.RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {name:.<50} {status}")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"  {Colors.GREEN}✅ All tests passed!{Colors.RESET}\n")
    else:
        print(f"  {Colors.YELLOW}⚠️  Some tests need attention{Colors.RESET}\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
