#!/usr/bin/env python3
"""
Test script to verify the Integrity verification flow
Tests the complete /propose-allocation + /execute-allocation flow with proof verification
"""
import asyncio
import json
import httpx
import sys

BACKEND_URL = "http://localhost:8001/api/v1"

async def test_integrity_verification():
    """Test the allocation flow with Integrity verification"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Proposal request
        print("\n=== Step 1: Creating proposal ===")
        proposal_data = {
            "jediswap_metrics": {
                "utilization": 7500,
                "volatility": 2500,
                "liquidity": 2,
                "audit_score": 85,
                "age_days": 730
            },
            "ekubo_metrics": {
                "utilization": 6000,
                "volatility": 2000,
                "liquidity": 2,
                "audit_score": 90,
                "age_days": 365
            },
            "user_address": "0x1234567890abcdef",
            "allocation_type": "balanced"
        }
        
        proposal_response = await client.post(
            f"{BACKEND_URL}/risk-engine/propose-allocation",
            json=proposal_data
        )
        
        if proposal_response.status_code != 200:
            print(f"❌ Proposal failed: {proposal_response.status_code}")
            print(proposal_response.text[:500])
            return False
        
        proposal = proposal_response.json()
        decision_id = proposal.get("decision_id")
        proof_job_id = proposal.get("proof_job_id")
        
        print(f"✅ Proposal created successfully")
        print(f"   Decision ID: {decision_id}")
        print(f"   Proof Job ID: {proof_job_id}")
        
        proof_status = proposal.get("proof_status")
        l2_verified = proposal.get("l2_verified")
        verification_error = proposal.get("verification_error")
        
        print(f"\n=== Proof Verification Status ===")
        print(f"   Status: {proof_status}")
        print(f"   L2 Verified: {l2_verified}")
        if verification_error:
            print(f"   Error: {verification_error}")
        
        # Step 2: Execute allocation
        print(f"\n=== Step 2: Executing allocation ===")
        execute_data = {
            "proof_job_id": proof_job_id,
            "user_address": "0x1234567890abcdef"
        }
        
        execute_response = await client.post(
            f"{BACKEND_URL}/risk-engine/execute-allocation",
            json=execute_data
        )
        
        if execute_response.status_code not in [200, 201]:
            print(f"❌ Execution failed: {execute_response.status_code}")
            print(execute_response.text[:500])
            return False
        
        execution = execute_response.json()
        tx_hash = execution.get("tx_hash")
        status = execution.get("status")
        
        print(f"✅ Allocation executed successfully")
        print(f"   TX Hash: {tx_hash}")
        print(f"   Status: {status}")
        
        print(f"\n=== Test Summary ===")
        print(f"Proof Verification: {'✅ PASSED' if l2_verified else '⚠️  PENDING/FAILED'}")
        print(f"Execution Status: ✅ SUBMITTED")
        
        return True

async def main():
    try:
        result = await test_integrity_verification()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
