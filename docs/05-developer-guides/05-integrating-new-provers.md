# Integrating New Provers

This guide covers the prover service interface, adding LuminAIR integration, adding Stone integration, proof format requirements, and testing new provers.

## Prover Service Interface

### Interface Definition

**Base Interface:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class ProverInterface(ABC):
    """Base interface for proof generators"""
    
    @abstractmethod
    async def generate_proof(
        self,
        trace: Dict[str, Any],
        memory: Dict[str, Any],
        public_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate STARK proof"""
        pass
    
    @abstractmethod
    async def verify_proof(
        self,
        proof: Dict[str, Any],
        public_inputs: Dict[str, Any]
    ) -> bool:
        """Verify STARK proof"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if prover is available"""
        pass
```

## Adding LuminAIR Integration

### Service Implementation

**File:** `backend/app/services/luminair_service.py`

**Key Methods:**
```python
class LuminAIRService(ProverInterface):
    def __init__(self, config: dict):
        self.binary_path = config.get("luminair_binary")
        self.enabled = config.get("luminair_enabled", True)
    
    async def generate_proof(self, trace, memory, public_inputs):
        # LuminAIR proof generation
        # Call Rust binary
        # Parse proof JSON
        # Return proof result
        pass
    
    def is_available(self) -> bool:
        return self.enabled and os.path.exists(self.binary_path)
```

### Integration Points

**1. Orchestrator:**
- Add to prover selection
- Configure as fallback
- Test integration

**2. Configuration:**
```python
LUMINAIR_ENABLED=true
LUMINAIR_BINARY_PATH=/path/to/luminair
```

## Adding Stone Integration

### Service Implementation

**File:** `backend/app/services/stone_prover_service.py`

**Key Methods:**
```python
class StoneProverService(ProverInterface):
    def __init__(self, config: dict):
        self.binary_path = config.get("stone_binary", "cpu_air_prover")
        self.enabled = config.get("stone_enabled", True)
    
    async def generate_proof_sync(self, trace, memory, public_inputs):
        # Calculate FRI parameters
        fri_params = self.calculate_fri_parameters(trace_size)
        
        # Generate proof
        proof = self.run_prover(trace, memory, public_inputs, fri_params)
        
        # Return proof result
        return proof
    
    def calculate_fri_parameters(self, trace_size: int) -> Dict:
        # Dynamic FRI calculation
        # Formula: log2(last_layer) + Σ(fri_steps) = log2(n_steps) + 4
        pass
```

## Proof Format Requirements

### Required Format

**Proof Structure:**
```json
{
  "proof": [...],
  "public_inputs": [...],
  "fact_hash": "0x...",
  "verifier_config": {...}
}
```

### Public Inputs

**Required Fields:**
- Protocol metrics
- Risk scores
- Allocation percentages
- Constraint parameters

### Fact Hash

**Calculation:**
- Pedersen hash of public inputs
- Felt252 format
- SHARP registry key

## Testing New Provers

### Unit Tests

```python
import pytest
from app.services.new_prover_service import NewProverService

def test_prover_available():
    prover = NewProverService({})
    assert prover.is_available() == True

def test_proof_generation():
    prover = NewProverService({})
    proof = await prover.generate_proof(trace, memory, public_inputs)
    assert proof is not None
    assert "fact_hash" in proof
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_end_to_end_proof():
    # Generate proof
    # Verify proof
    # Register in Fact Registry
    # Execute on-chain
    pass
```

## Prover Selection

### Orchestrator Logic

```python
class AllocationProofOrchestrator:
    def select_prover(self) -> ProverType:
        # Priority: Stone > LuminAIR > Error
        if stone_prover.is_available():
            return ProverType.STONE
        elif luminair_prover.is_available():
            return ProverType.LUMINAIR
        else:
            raise ProverUnavailableError()
```

## Next Steps

- **[Backend Development](03-backend-development.md)** - Service development
- **[Proof Generation Pipeline](../03-architecture/04-proof-generation.md)** - Architecture details
- **[Multi-Prover Support](../04-novel-features/04-multi-prover-support.md)** - Feature overview

---

**Prover Integration Summary:** Complete guide for integrating new STARK provers with interface, testing, and orchestration.
