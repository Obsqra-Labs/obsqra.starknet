# Test Existing FactRegistry First

## Quick Test

The existing FactRegistry contract **DOES verify proofs** - it calls the verifier first, then registers.

**Let's test it**:

```python
# In your backend
from app.services.integrity_service import IntegrityService
from app.services.luminair_service import LuminAIRService

# 1. Generate proof (you already do this)
luminair = LuminAIRService()
proof = await luminair.generate_risk_proof({
    "utilization": 6500,
    "volatility": 3500,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800
})

# 2. Submit to existing FactRegistry (just gas, no credits!)
integrity = IntegrityService(rpc_url="...", network="sepolia")
result = await integrity.verify_proof_full_and_register_fact(
    verifier_config=proof.verifier_config,
    stark_proof=proof.stark_proof
)

if result:
    print("✅ Works! No deployment needed!")
    fact_hash = proof.fact_hash
    # Use this in your contract call
else:
    print("❌ Need to deploy your own")
```

---

## If You Still Want Your Own

The Integrity contract needs to be declared from the integrity directory. The issue is the snfoundry.toml has a different RPC.

**Option**: Use the existing contract for now, deploy your own later if needed.

**Or**: Fix the integrity/snfoundry.toml RPC URL to match your setup.
