# Complete Integration Tutorial
## End-to-End Stone Prover Integration for Production

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Production-Validated  
**Category**: Implementation Guide

---

## Executive Summary

This tutorial provides a complete, step-by-step guide to integrating Stone Prover into a production application. It covers project setup, Stone Prover installation, Integrity setup, code integration, testing, deployment, and production best practices. Based on Obsqra Labs' production implementation.

**Time to Complete**: 2-4 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Python, basic Cairo knowledge, Linux/macOS

---

## Table of Contents

1. [Project Setup](#project-setup)
2. [Stone Prover Installation](#stone-prover-installation)
3. [Integrity Setup](#integrity-setup)
4. [Code Integration](#code-integration)
5. [Testing and Validation](#testing-and-validation)
6. [Deployment Considerations](#deployment-considerations)
7. [Production Best Practices](#production-best-practices)
8. [Complete Working Example](#complete-working-example)

---

## Project Setup

### Create Project Structure

```bash
mkdir my-stone-integration
cd my-stone-integration
mkdir -p {src,tests,config,traces,proofs}
```

### Initialize Python Project

```bash
python3 -m venv venv
source venv/bin/activate
pip install starknet-py asyncio pathlib
```

### Create Project Files

**File**: `requirements.txt`
```
starknet-py>=0.19.0
asyncio
pathlib
```

**File**: `config.py`
```python
import os
from pathlib import Path

# Stone Prover paths
STONE_BINARY = Path(os.getenv("STONE_BINARY", "/opt/stone-prover/.../cpu_air_prover"))
STONE_PARAMS = Path(os.getenv("STONE_PARAMS", "/opt/integrity/.../cpu_air_params.json"))

# Integrity paths
PROOF_SERIALIZER = Path(os.getenv("PROOF_SERIALIZER", "/opt/integrity/.../proof_serializer"))
FACT_REGISTRY = int(os.getenv("FACT_REGISTRY", "0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c"), 16)

# RPC
RPC_URL = os.getenv("RPC_URL", "https://starknet-sepolia.public.blastapi.io")
NETWORK = os.getenv("NETWORK", "sepolia")
```

---

## Stone Prover Installation

### Step 1: Clone and Build

```bash
# Clone Stone Prover
git clone https://github.com/starkware-libs/stone-prover.git
cd stone-prover
git checkout 1414a545e4fb38a85391289abe91dd4467d268e1

# Build
bazel build //src/starkware/main/cpu:cpu_air_prover

# Set path
export STONE_BINARY=$(pwd)/bazel-bin/src/starkware/main/cpu/cpu_air_prover
```

### Step 2: Verify Installation

```bash
$STONE_BINARY --help
```

**Expected**: Help message

---

## Integrity Setup

### Step 1: Clone and Build

```bash
# Clone Integrity
git clone https://github.com/HerodotusDev/integrity.git
cd integrity

# Build proof_serializer
cargo build --release --bin proof_serializer

# Set path
export PROOF_SERIALIZER=$(pwd)/target/release/proof_serializer
```

### Step 2: Get Parameters File

```bash
# Copy parameters file
cp examples/proofs/cpu_air_params.json /path/to/your/project/config/
```

---

## Code Integration

### Step 1: Create FRI Calculator

**File**: `src/fri_calculator.py`

```python
import math
from typing import List

def calculate_fri_step_list(n_steps: int, last_layer_degree_bound: int = 128) -> List[int]:
    """Calculate FRI step list dynamically"""
    if n_steps & (n_steps - 1) != 0 or n_steps < 512:
        raise ValueError(f"n_steps must be power of 2 and >= 512, got {n_steps}")
    
    log_n_steps = math.ceil(math.log2(n_steps))
    last_layer_log2 = math.ceil(math.log2(last_layer_degree_bound))
    target_sum = log_n_steps + 4
    sigma = target_sum - last_layer_log2
    
    if sigma < 0:
        raise ValueError(f"FRI equation impossible")
    
    q, r = divmod(sigma, 4)
    fri_steps = [0] + [4] * q + ([r] if r > 0 else [])
    
    # Verify
    equation_sum = sum(fri_steps)
    actual_sum = last_layer_log2 + equation_sum
    assert actual_sum == target_sum, "FRI equation mismatch"
    
    return fri_steps
```

### Step 2: Create Stone Service

**File**: `src/stone_service.py`

```python
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict
from fri_calculator import calculate_fri_step_list
from config import STONE_BINARY, STONE_PARAMS

class StoneProverService:
    def __init__(self):
        self.stone_binary = STONE_BINARY
        self.params_file = STONE_PARAMS
        
        if not self.stone_binary.exists():
            raise FileNotFoundError(f"Stone binary not found: {self.stone_binary}")
    
    def generate_proof(
        self,
        private_input_file: str,
        public_input_file: str,
        proof_output_file: Optional[str] = None
    ) -> Dict:
        """Generate STARK proof"""
        
        # Read public input
        with open(public_input_file) as f:
            public_input = json.load(f)
        
        n_steps = public_input.get("n_steps")
        if not n_steps:
            raise ValueError("n_steps not found")
        
        # Calculate FRI parameters
        with open(self.params_file) as f:
            params = json.load(f)
        
        last_layer = params["stark"]["fri"]["last_layer_degree_bound"]
        fri_steps = calculate_fri_step_list(n_steps, last_layer)
        params["stark"]["fri"]["fri_step_list"] = fri_steps
        
        # Create temp params file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_params = f.name
            json.dump(params, f)
        
        # Determine output
        if proof_output_file is None:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                proof_output_file = f.name
        
        # Build command
        cmd = [
            str(self.stone_binary),
            "--parameter_file", temp_params,
            "--private_input_file", private_input_file,
            "--public_input_file", public_input_file,
            "--out_file", proof_output_file,
            "--generate_annotations"
        ]
        
        # Run
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"Stone prover failed: {result.stderr}")
        
        # Read proof
        with open(proof_output_file) as f:
            proof_json = json.load(f)
        
        return {
            "success": True,
            "proof_file": proof_output_file,
            "proof_json": proof_json
        }
```

### Step 3: Create Integrity Service

**File**: `src/integrity_service.py`

```python
import subprocess
import struct
from pathlib import Path
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
from config import PROOF_SERIALIZER, FACT_REGISTRY, RPC_URL

def string_to_felt(value: str) -> int:
    """Encode string to felt"""
    return int.from_bytes(value.encode("ascii"), "big")

def serialize_proof(proof_json_path: str) -> list[int]:
    """Serialize proof to calldata"""
    result = subprocess.run(
        [str(PROOF_SERIALIZER), proof_json_path, "-"],
        capture_output=True,
        check=True
    )
    
    calldata = []
    for i in range(0, len(result.stdout), 32):
        felt_bytes = result.stdout[i:i+32]
        felt = int.from_bytes(felt_bytes, 'big')
        calldata.append(felt)
    
    return calldata

async def verify_proof(proof_json_path: str) -> bool:
    """Verify proof on-chain"""
    # Serialize proof
    proof_calldata = serialize_proof(proof_json_path)
    
    # Construct calldata
    calldata = [
        string_to_felt("recursive"),
        string_to_felt("keccak_160_lsb"),
        string_to_felt("stone6"),
        string_to_felt("strict"),
        *proof_calldata
    ]
    
    # Call Integrity
    client = FullNodeClient(node_url=RPC_URL)
    selector = get_selector_from_name("verify_proof_full_and_register_fact")
    
    call = {
        "to": FACT_REGISTRY,
        "selector": selector,
        "calldata": calldata
    }
    
    try:
        result = await client.call_contract(call, block_number="latest")
        return result is not None and len(result) > 0
    except Exception as e:
        print(f"Verification failed: {e}")
        return False
```

---

## Testing and Validation

### Step 1: Create Test Inputs

**File**: `tests/test_inputs.json`

```json
{
  "private_input": {
    "trace_path": "/path/to/trace.bin",
    "memory_path": "/path/to/memory.bin",
    "pedersen": [],
    "range_check": [],
    "ecdsa": []
  },
  "public_input": {
    "n_steps": 512,
    "layout": "recursive",
    "memory_segments": [...],
    "public_memory": []
  }
}
```

### Step 2: Create Test Script

**File**: `tests/test_integration.py`

```python
import asyncio
import json
from pathlib import Path
from src.stone_service import StoneProverService
from src.integrity_service import verify_proof

async def test_integration():
    # Load test inputs
    with open("tests/test_inputs.json") as f:
        test_data = json.load(f)
    
    # Initialize service
    stone_service = StoneProverService()
    
    # Write input files
    private_input_file = "tests/private_input.json"
    public_input_file = "tests/public_input.json"
    
    with open(private_input_file, 'w') as f:
        json.dump(test_data["private_input"], f)
    
    with open(public_input_file, 'w') as f:
        json.dump(test_data["public_input"], f)
    
    # Generate proof
    print("Generating proof...")
    result = stone_service.generate_proof(
        private_input_file,
        public_input_file,
        proof_output_file="proofs/test_proof.json"
    )
    
    if not result["success"]:
        print("❌ Proof generation failed")
        return False
    
    print("✅ Proof generated")
    
    # Verify proof
    print("Verifying proof...")
    verified = await verify_proof(result["proof_file"])
    
    if verified:
        print("✅ Proof verified on-chain")
        return True
    else:
        print("❌ Proof verification failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    exit(0 if success else 1)
```

### Step 3: Run Tests

```bash
python3 tests/test_integration.py
```

**Expected**: ✅ Proof generated and verified

---

## Deployment Considerations

### Production Configuration

**Environment Variables**:
```bash
export STONE_BINARY="/opt/stone-prover/.../cpu_air_prover"
export PROOF_SERIALIZER="/opt/integrity/.../proof_serializer"
export FACT_REGISTRY="0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c"
export RPC_URL="https://starknet-sepolia.public.blastapi.io"
```

### Monitoring

**Key Metrics**:
- Proof generation time
- Success rate
- Error rate
- Resource usage

**Tools**:
- Prometheus + Grafana
- Application logs
- Error tracking

### Scaling

**Horizontal Scaling**:
- Multiple instances
- Load balancing
- Queue system

**Vertical Scaling**:
- More CPU cores
- More RAM
- Faster storage

---

## Production Best Practices

### 1. Error Handling

```python
try:
    result = stone_service.generate_proof(...)
    if not result["success"]:
        logger.error(f"Proof generation failed: {result.get('error')}")
        # Handle error
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Handle unexpected error
```

### 2. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Generating proof for n_steps=%d", n_steps)
logger.info("FRI parameters: %s", fri_steps)
```

### 3. Monitoring

```python
import time

start_time = time.time()
result = stone_service.generate_proof(...)
elapsed = time.time() - start_time

logger.info(f"Proof generation: {elapsed:.2f}s")
metrics.record_proof_time(elapsed)
```

### 4. Retry Logic

```python
async def generate_proof_with_retry(inputs, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await stone_service.generate_proof(**inputs)
            if result["success"]:
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

---

## Complete Working Example

### Full Integration Example

**File**: `examples/complete_example.py`

```python
import asyncio
import json
from pathlib import Path
from src.stone_service import StoneProverService
from src.integrity_service import verify_proof, serialize_proof, string_to_felt
from config import FACT_REGISTRY, RPC_URL

async def complete_integration_example():
    """Complete integration example"""
    
    # Step 1: Prepare inputs
    metrics = {
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
    
    # Step 2: Generate Cairo trace (simplified - you'd use actual Cairo execution)
    # This is a placeholder - in reality you'd execute your Cairo program
    trace_file = "traces/example_trace.bin"
    memory_file = "traces/example_memory.bin"
    public_input = {
        "n_steps": 512,
        "layout": "recursive",
        "memory_segments": [{"begin_addr": 0, "stop_ptr": 100, "stop_ptr_offset": 0}],
        "public_memory": []
    }
    
    # Step 3: Create input files
    private_input = {
        "trace_path": str(Path(trace_file).absolute()),
        "memory_path": str(Path(memory_file).absolute()),
        "pedersen": [],
        "range_check": [],
        "ecdsa": []
    }
    
    with open("private_input.json", 'w') as f:
        json.dump(private_input, f)
    
    with open("public_input.json", 'w') as f:
        json.dump(public_input, f)
    
    # Step 4: Generate proof
    print("Step 4: Generating Stone proof...")
    stone_service = StoneProverService()
    result = stone_service.generate_proof(
        "private_input.json",
        "public_input.json",
        "proofs/example_proof.json"
    )
    
    if not result["success"]:
        print(f"❌ Proof generation failed: {result.get('error')}")
        return False
    
    print(f"✅ Proof generated: {result['proof_file']}")
    
    # Step 5: Verify proof
    print("Step 5: Verifying proof on-chain...")
    verified = await verify_proof(result["proof_file"])
    
    if verified:
        print("✅ Proof verified on-chain!")
        return True
    else:
        print("❌ Proof verification failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(complete_integration_example())
    exit(0 if success else 1)
```

---

## Conclusion

You now have a complete Stone Prover integration! Next steps:

1. ✅ Integration complete
2. → Test with your Cairo programs
3. → Optimize for your use case
4. → Deploy to production
5. → Monitor and optimize

**Time to Production**: With this foundation, 1-2 days to production-ready.

**Questions?** See `TROUBLESHOOTING_GUIDE.md` or `DEVELOPER_FAQ.md`

---

**This tutorial provides the foundation for production Stone Prover integration.**
