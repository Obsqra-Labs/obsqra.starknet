# Giza Integration Setup Guide

## Overview

Giza Actions enables Cairo programs to generate zero-knowledge proofs that can be verified on Starknet via SHARP.

## Architecture

```
Cairo Risk Model → Giza Transpiler → Provable Format → Stone Prover → SHARP → On-chain Verification
```

## Prerequisites

- Python 3.11+
- Cairo 2.0 compiled contract
- Giza Actions account
- SHARP testnet access

## Installation

### 1. Install Giza CLI

```bash
pip install giza-cli
```

### 2. Initialize Giza Account

```bash
giza users create
giza users login
```

### 3. Verify Installation

```bash
giza --version
giza users me
```

## Project Setup

### 1. Initialize Giza Workspace

```bash
cd /opt/obsqra.starknet
giza workspaces create --name obsqra-risk-model
```

### 2. Transpile Cairo Model

```bash
# Convert Cairo contract to Giza format
giza transpile \
  --input contracts/src/ml/risk_model.cairo \
  --output giza/risk_model.json \
  --entry-point calculate_risk_score
```

### 3. Configure Proof Parameters

Create `giza/config.yaml`:

```yaml
model:
  name: risk_scoring_model
  version: v1
  entry_point: calculate_risk_score
  
proof:
  layout: recursive  # or 'small' for faster proofs
  max_steps: 1000000
  
verification:
  network: starknet-sepolia
  verifier: sharp
```

## Proof Generation Workflow

### Local Testing

```bash
# 1. Compile Cairo model
cd contracts
scarb build

# 2. Generate proof for test case
giza prove \
  --model risk_scoring_model \
  --version v1 \
  --input ../tests/risk_model_test_cases.json \
  --output proofs/test_proof.json

# 3. Verify proof locally
giza verify \
  --proof proofs/test_proof.json \
  --model risk_scoring_model
```

### SHARP Submission

```bash
# Submit proof to SHARP
giza sharp submit \
  --proof proofs/test_proof.json \
  --network starknet-sepolia

# Monitor verification status
giza sharp status \
  --job-id <JOB_ID>

# Get proof fact (for on-chain verification)
giza sharp fact \
  --job-id <JOB_ID>
```

## Python Integration

### Automated Proof Generation

```python
# backend/app/services/proof_service.py

from giza_actions import GizaClient
import json

class ProofService:
    def __init__(self):
        self.client = GizaClient(
            api_key=os.getenv('GIZA_API_KEY'),
            workspace='obsqra-risk-model'
        )
    
    async def generate_risk_proof(
        self, 
        metrics: dict
    ) -> dict:
        """Generate ZK proof for risk calculation"""
        
        # 1. Prepare input
        proof_input = {
            "utilization": metrics["utilization"],
            "volatility": metrics["volatility"],
            "liquidity": metrics["liquidity"],
            "audit_score": metrics["audit_score"],
            "age_days": metrics["age_days"]
        }
        
        # 2. Generate proof
        job = await self.client.prove(
            model="risk_scoring_model",
            version="v1",
            input_data=proof_input
        )
        
        # 3. Wait for completion
        result = await job.wait()
        
        return {
            "proof_hash": result.proof_hash,
            "job_id": result.job_id,
            "output": result.output
        }
    
    async def submit_to_sharp(
        self, 
        proof_hash: str
    ) -> str:
        """Submit proof to SHARP for on-chain verification"""
        
        submission = await self.client.sharp.submit(
            proof_hash=proof_hash,
            network="starknet-sepolia"
        )
        
        return submission.fact_hash
    
    async def check_sharp_status(
        self, 
        fact_hash: str
    ) -> dict:
        """Check if proof has been verified by SHARP"""
        
        status = await self.client.sharp.status(
            fact_hash=fact_hash
        )
        
        return {
            "verified": status.verified,
            "block_number": status.block_number,
            "transaction_hash": status.transaction_hash
        }
```

## Backend API Integration

### Updated Orchestration Endpoint

```python
@router.post("/orchestrate-with-proof")
async def orchestrate_with_proof(
    request: OrchestrationRequest,
    proof_service: ProofService = Depends()
):
    """Execute allocation with ZK proof"""
    
    # 1. Generate proof for JediSwap risk
    jediswap_proof = await proof_service.generate_risk_proof(
        request.jediswap_metrics.dict()
    )
    
    # 2. Generate proof for Ekubo risk  
    ekubo_proof = await proof_service.generate_risk_proof(
        request.ekubo_metrics.dict()
    )
    
    # 3. Submit proofs to SHARP
    jediswap_fact = await proof_service.submit_to_sharp(
        jediswap_proof["proof_hash"]
    )
    ekubo_fact = await proof_service.submit_to_sharp(
        ekubo_proof["proof_hash"]
    )
    
    # 4. Wait for SHARP verification (async job)
    # This can take 10-60 minutes, so we need job tracking
    
    # 5. Once verified, execute on-chain with proof facts
    result = await execute_allocation_with_proofs(
        jediswap_pct=jediswap_proof["output"]["total_score"],
        ekubo_pct=ekubo_proof["output"]["total_score"],
        jediswap_proof_fact=jediswap_fact,
        ekubo_proof_fact=ekubo_fact
    )
    
    return {
        "decision": result,
        "proofs": {
            "jediswap": jediswap_fact,
            "ekubo": ekubo_fact
        }
    }
```

## Contract Integration

### SHARP Fact Registry

```cairo
use starknet::ContractAddress;

#[starknet::interface]
trait IFactRegistry<TContractState> {
    fn is_valid(self: @TContractState, fact: felt252) -> bool;
}

// SHARP Fact Registry on Sepolia
const SHARP_FACT_REGISTRY: ContractAddress = 
    0x...; // Updated with actual address

fn verify_risk_proof(
    ref self: ContractState,
    metrics: ProtocolMetrics,
    expected_score: felt252,
    proof_fact: felt252
) -> bool {
    // 1. Check proof exists in SHARP registry
    let registry = IFactRegistryDispatcher { 
        contract_address: SHARP_FACT_REGISTRY 
    };
    
    let is_verified = registry.is_valid(proof_fact);
    assert(is_verified, 'Proof not verified by SHARP');
    
    // 2. Calculate risk score locally
    let calculated = calculate_risk_score(metrics);
    
    // 3. Verify proof output matches
    assert(calculated.total_score == expected_score, 'Score mismatch');
    
    true
}
```

## Testing

### End-to-End Test

```bash
# 1. Start from Python test case
python tests/test_cairo_python_parity.py

# 2. Generate proof for one case
giza prove \
  --model risk_scoring_model \
  --input '{"utilization":6500,"volatility":3500,"liquidity":1,"audit_score":98,"age_days":800}' \
  --output proofs/jediswap_proof.json

# 3. Submit to SHARP testnet
giza sharp submit \
  --proof proofs/jediswap_proof.json \
  --network starknet-sepolia

# 4. Monitor status (poll every 60s)
giza sharp status --job-id <JOB_ID>

# 5. Once verified, get fact hash
FACT_HASH=$(giza sharp fact --job-id <JOB_ID>)

# 6. Verify on-chain
sncast call \
  --contract-address $SHARP_REGISTRY \
  --function is_valid \
  --calldata $FACT_HASH
```

## Performance Expectations

- **Proof Generation**: 30-120 seconds (depends on layout)
- **SHARP Verification**: 10-60 minutes
- **Proof Size**: ~100KB
- **Gas Cost**: ~500K gas for verification

## Troubleshooting

### Proof Generation Fails

```bash
# Check Cairo compilation
cd contracts && scarb build

# Verify model structure
giza models list

# Check proof parameters
giza config show
```

### SHARP Submission Fails

```bash
# Verify network connection
giza sharp health --network starknet-sepolia

# Check account balance
sncast account fetch

# Retry with different parameters
giza sharp submit --proof proof.json --retry-count 3
```

### Verification Takes Too Long

- SHARP processes proofs in batches
- Testnet can be slower than mainnet
- Consider using 'small' layout for faster proofs
- Monitor SHARP dashboard for queue status

## Cost Analysis

### Testnet (Sepolia)
- Proof generation: Free
- SHARP submission: ~0.01 ETH gas
- Fact registry query: ~50K gas

### Mainnet (Future)
- Proof generation: $0.10-1.00 per proof
- SHARP verification: Amortized across batch
- Expected cost: $0.50-2.00 per decision

## Resources

- [Giza Docs](https://docs.giza.tech)
- [SHARP Documentation](https://starkware.co/sharp/)
- [Cairo Proof Tutorial](https://cairo-lang.org/docs/proving.html)
- [Starknet Fact Registry](https://sepolia.starkscan.co/contract/...)

## Next Steps

1. Create Giza account
2. Transpile risk model
3. Generate test proofs
4. Submit to SHARP testnet
5. Update contracts with proof verification
6. Integrate into backend API

---

**Status**: Ready for implementation once Giza account is created

