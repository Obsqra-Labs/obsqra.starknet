#!/usr/bin/env python3
"""
Integration test for Obsqra.starknet deployment
Tests that frontend config, AI service, and contracts are all integrated
"""

import asyncio
import json
import requests
from starknet_py.net.full_node_client import FullNodeClient

# Configuration from frontend .env.local
RISK_ENGINE = "0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80"
DAO_MANAGER = "0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856"
STRATEGY_ROUTER = "0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a"

RPC_URL = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
AI_SERVICE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3003"

async def test_rpc_connectivity():
    """Test 1: RPC Connection"""
    print("\n" + "="*70)
    print("TEST 1: RPC CONNECTIVITY")
    print("="*70)
    
    try:
        client = FullNodeClient(node_url=RPC_URL)
        block = await client.get_block_number()
        print(f"✅ RPC Connected")
        print(f"   Current block: {block}")
        return True
    except Exception as e:
        print(f"❌ RPC Connection Failed: {e}")
        return False

async def test_contract_deployment():
    """Test 2: Contract Deployment Status"""
    print("\n" + "="*70)
    print("TEST 2: CONTRACT DEPLOYMENT STATUS")
    print("="*70)
    
    client = FullNodeClient(node_url=RPC_URL)
    
    contracts = {
        "RiskEngine": RISK_ENGINE,
        "DAOConstraintManager": DAO_MANAGER,
        "StrategyRouter": STRATEGY_ROUTER,
    }
    
    all_deployed = True
    for name, addr in contracts.items():
        try:
            class_hash = await client.get_class_hash_at(addr)
            storage = await client.get_storage_at(addr, 0)
            print(f"✅ {name}")
            print(f"   Address: {addr}")
            print(f"   Class Hash: {hex(class_hash)}")
            print(f"   Storage[0]: {storage}")
        except Exception as e:
            print(f"❌ {name}: {str(e)[:80]}")
            all_deployed = False
    
    return all_deployed

def test_ai_service():
    """Test 3: AI Service Health"""
    print("\n" + "="*70)
    print("TEST 3: AI SERVICE HEALTH")
    print("="*70)
    
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Service Healthy")
            print(f"   URL: {AI_SERVICE_URL}")
            print(f"   Status: {data.get('status')}")
            print(f"   Services: {json.dumps(data.get('services', {}), indent=6)}")
            return True
        else:
            print(f"❌ AI Service returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI Service Error: {e}")
        return False

def test_frontend():
    """Test 4: Frontend Accessibility"""
    print("\n" + "="*70)
    print("TEST 4: FRONTEND ACCESSIBILITY")
    print("="*70)
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend Running")
            print(f"   URL: {FRONTEND_URL}")
            print(f"   Port: 3003")
            
            # Check for key content
            if 'Obsqra' in response.text:
                print(f"   Status: Loaded successfully")
                return True
            else:
                print(f"   ⚠️  Page loaded but content not verified")
                return True  # Still running even if content is unexpected
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
        return False

def test_env_config():
    """Test 5: Environment Configuration"""
    print("\n" + "="*70)
    print("TEST 5: ENVIRONMENT CONFIGURATION")
    print("="*70)
    
    try:
        with open('/opt/obsqra.starknet/frontend/.env.local', 'r') as f:
            env_content = f.read()
        
        required_vars = [
            'NEXT_PUBLIC_RISK_ENGINE_ADDRESS',
            'NEXT_PUBLIC_DAO_MANAGER_ADDRESS',
            'NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS',
            'NEXT_PUBLIC_RPC_URL',
            'NEXT_PUBLIC_AI_SERVICE_URL',
        ]
        
        all_present = True
        for var in required_vars:
            if var in env_content:
                value = [line.split('=')[1].strip() for line in env_content.split('\n') if line.startswith(var)][0]
                print(f"✅ {var}")
                print(f"   Value: {value[:50]}...")
            else:
                print(f"❌ {var} missing")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"❌ Config Error: {e}")
        return False

async def main():
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  OBSQRA.STARKNET - INTEGRATION TEST SUITE".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    results = {
        "RPC Connectivity": await test_rpc_connectivity(),
        "Contract Deployment": await test_contract_deployment(),
        "AI Service": test_ai_service(),
        "Frontend": test_frontend(),
        "Environment Config": test_env_config(),
    }
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n📝 Next Steps:")
        print("   1. Install wallet extension (Argent X or Braavos)")
        print("   2. Switch to Starknet Sepolia network")
        print("   3. Get testnet STRK from faucet")
        print("   4. Connect wallet at http://localhost:3003")
        print("   5. Interact with contracts through the dashboard")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - check output above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

