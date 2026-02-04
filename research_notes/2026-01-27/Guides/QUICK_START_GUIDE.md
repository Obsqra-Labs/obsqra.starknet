# Quick Start Guide - Stone Prover Integration
## Get Up and Running in 30 Minutes

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Production-Validated  
**Category**: Implementation Guide

---

## Executive Summary

This guide will get you generating STARK proofs with Stone Prover in 30 minutes. It covers installation, basic setup, and your first proof generation. Based on Obsqra Labs' production implementation.

**Time to First Proof**: ~30 minutes  
**Prerequisites**: Linux/macOS, basic Python knowledge  
**Difficulty**: Intermediate

---

## Prerequisites

### System Requirements

**Operating System**:
- Linux (Ubuntu 20.04+ recommended)
- macOS (10.15+)
- Windows (WSL2 recommended)

**Hardware**:
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 50GB+ free space

**Software**:
- Python 3.11+
- Git
- Bazel (for building Stone Prover)
- Basic build tools

### Install Dependencies

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    bazel \
    python3 \
    python3-pip \
    git \
    libssl-dev \
    libgmp-dev
```

**macOS**:
```bash
brew install bazel cmake python3 git
```

**Verify Installation**:
```bash
python3 --version  # Should be 3.11+
bazel --version    # Should be 4.0+
git --version      # Any recent version
```

---

## Step 1: Build Stone Prover (15 minutes)

### Clone Repository

```bash
git clone https://github.com/starkware-libs/stone-prover.git
cd stone-prover
```

### Checkout Stable Version

```bash
# Use Stone v3 (Sept 2024) - matches stone6 verifier
git checkout 1414a545e4fb38a85391289abe91dd4467d268e1
```

### Build Binary

```bash
# Build CPU AIR prover (this takes 10-15 minutes)
bazel build //src/starkware/main/cpu:cpu_air_prover
```

**Expected Output**:
```
INFO: Build completed successfully
Target //src/starkware/main/cpu:cpu_air_prover up-to-date
```

### Verify Build

```bash
# Binary location
./bazel-bin/src/starkware/main/cpu/cpu_air_prover --help
```

**Expected**: Help message showing available options

### Set Binary Path

```bash
# Make binary accessible
export STONE_BINARY=$(pwd)/bazel-bin/src/starkware/main/cpu/cpu_air_prover
echo "export STONE_BINARY=$STONE_BINARY" >> ~/.bashrc
```

---

## Step 2: Install Integrity (5 minutes)

### Clone Integrity Repository

```bash
cd ..
git clone https://github.com/HerodotusDev/integrity.git
cd integrity
```

### Build proof_serializer

```bash
# Build proof serializer (required for Integrity integration)
cargo build --release --bin proof_serializer
```

**Binary Location**: `target/release/proof_serializer`

### Set Serializer Path

```bash
export PROOF_SERIALIZER=$(pwd)/target/release/proof_serializer
echo "export PROOF_SERIALIZER=$PROOF_SERIALIZER" >> ~/.bashrc
```

---

## Step 3: Install Python Dependencies (2 minutes)

### Create Virtual Environment

```bash
cd ..
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Required Packages

```bash
pip install \
    starknet-py \
    asyncio \
    pathlib
```

---

## Step 4: Create Basic Integration (5 minutes)

### Create Project Structure

```bash
mkdir stone-prover-integration
cd stone-prover-integration
mkdir -p {traces,proofs,config}
```

### Create FRI Calculation Module

**File**: `fri_calculator.py`

```python
import math
from typing import List

def calculate_fri_step_list(n_steps: int, last_layer_degree_bound: int = 128) -> List[int]:
    """
    Calculate FRI step list dynamically based on trace size.
    
    FRI equation: log2(last_layer_degree_bound) + Σ(fri_steps) = log2(n_steps) + 4
    """
    # Validate n_steps is power of 2
    if n_steps & (n_steps - 1) != 0 or n_steps < 512:
        raise ValueError(f"n_steps must be power of 2 and >= 512, got {n_steps}")
    
    # Calculate logarithms
    log_n_steps = math.ceil(math.log2(n_steps))
    last_layer_log2 = math.ceil(math.log2(last_layer_degree_bound))
    
    # Calculate target sum
    target_sum = log_n_steps + 4
    sigma = target_sum - last_layer_log2
    
    if sigma < 0:
        raise ValueError(f"FRI equation impossible for n_steps={n_steps}")
    
    # Calculate step list
    q, r = divmod(sigma, 4)
    fri_steps = [0] + [4] * q + ([r] if r > 0 else [])
    
    # Verify equation
    equation_sum = sum(fri_steps)
    actual_sum = last_layer_log2 + equation_sum
    
    if actual_sum != target_sum:
        raise ValueError(f"FRI equation mismatch: {actual_sum} != {target_sum}")
    
    return fri_steps
```

### Create Stone Prover Service

**File**: `stone_service.py`

```python
import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict

class StoneProverService:
    def __init__(self, stone_binary: Optional[str] = None):
        self.stone_binary = Path(stone_binary or os.getenv("STONE_BINARY"))
        if not self.stone_binary.exists():
            raise FileNotFoundError(f"Stone binary not found: {self.stone_binary}")
    
    def generate_proof(
        self,
        private_input_file: str,
        public_input_file: str,
        proof_output_file: Optional[str] = None,
        params_file: Optional[str] = None
    ) -> Dict:
        """Generate STARK proof using Stone Prover"""
        
        # Read public input to get n_steps
        with open(public_input_file) as f:
            public_input = json.load(f)
        
        n_steps = public_input.get("n_steps")
        if not n_steps:
            raise ValueError("n_steps not found in public input")
        
        # Calculate FRI parameters
        from fri_calculator import calculate_fri_step_list
        fri_steps = calculate_fri_step_list(n_steps, last_layer_degree_bound=128)
        
        # Load base parameters
        if params_file is None:
            # Create default params
            params = {
                "stark": {
                    "fri": {
                        "fri_step_list": fri_steps,
                        "last_layer_degree_bound": 128,
                        "n_queries": 10,
                        "proof_of_work_bits": 30
                    },
                    "log_n_cosets": 2
                },
                "channel_hash": "poseidon3",
                "commitment_hash": "keccak256_masked160_lsb",
                "pow_hash": "keccak256"
            }
        else:
            with open(params_file) as f:
                params = json.load(f)
            params["stark"]["fri"]["fri_step_list"] = fri_steps
        
        # Create temp params file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_params_file = f.name
            json.dump(params, f)
        
        # Determine output file
        if proof_output_file is None:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                proof_output_file = f.name
        
        # Build command
        cmd = [
            str(self.stone_binary),
            "--parameter_file", temp_params_file,
            "--private_input_file", private_input_file,
            "--public_input_file", public_input_file,
            "--out_file", proof_output_file,
            "--generate_annotations"
        ]
        
        # Run prover
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
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

---

## Step 5: Generate Your First Proof (3 minutes)

### Create Test Input Files

**File**: `test_private_input.json`

```json
{
  "trace_path": "/path/to/your/trace.bin",
  "memory_path": "/path/to/your/memory.bin",
  "pedersen": [],
  "range_check": [],
  "ecdsa": []
}
```

**File**: `test_public_input.json`

```json
{
  "n_steps": 512,
  "layout": "recursive",
  "memory_segments": [
    {
      "begin_addr": 0,
      "stop_ptr": 100,
      "stop_ptr_offset": 0
    }
  ],
  "public_memory": []
}
```

### Generate Proof

**File**: `test_proof.py`

```python
from stone_service import StoneProverService
import os

# Initialize service
stone_service = StoneProverService()

# Generate proof
result = stone_service.generate_proof(
    private_input_file="test_private_input.json",
    public_input_file="test_public_input.json",
    proof_output_file="proof.json"
)

if result["success"]:
    print("✅ Proof generated successfully!")
    print(f"Proof file: {result['proof_file']}")
    print(f"Proof size: {os.path.getsize(result['proof_file']) / 1024:.1f} KB")
else:
    print(f"❌ Proof generation failed: {result.get('error')}")
```

### Run Test

```bash
python3 test_proof.py
```

**Expected Output**:
```
✅ Proof generated successfully!
Proof file: proof.json
Proof size: 128.5 KB
```

---

## Common Issues and Solutions

### Issue 1: "Stone binary not found"

**Solution**:
```bash
# Check binary exists
ls -la $STONE_BINARY

# If not found, rebuild
cd stone-prover
bazel build //src/starkware/main/cpu:cpu_air_prover
```

### Issue 2: "Signal 6" Error

**Cause**: FRI parameter mismatch

**Solution**: Ensure using dynamic FRI calculation:
```python
# ✅ CORRECT: Dynamic calculation
fri_steps = calculate_fri_step_list(n_steps, 128)

# ❌ WRONG: Fixed parameters
fri_steps = [0, 4, 4, 3]  # Only works for one size
```

### Issue 3: "n_steps must be power of 2"

**Solution**: Round to next power of 2:
```python
import math

actual_steps = 1000  # Your actual steps
n_steps_log = math.ceil(math.log2(actual_steps))
n_steps = 2 ** n_steps_log  # = 1024
```

### Issue 4: "File not found"

**Solution**: Use absolute paths:
```python
from pathlib import Path

trace_path = str(Path("trace.bin").absolute())
memory_path = str(Path("memory.bin").absolute())
```

---

## Next Steps

### 1. Integrate with Your Application

- Add Stone service to your codebase
- Integrate with your trace generation
- Add error handling

### 2. Test with Real Traces

- Generate traces from your Cairo programs
- Test with different trace sizes
- Validate proof correctness

### 3. Integrate with Integrity

- Set up Integrity FactRegistry
- Serialize proofs for on-chain verification
- Test on-chain verification

### 4. Production Deployment

- Set up monitoring
- Implement retry logic
- Add performance tracking

---

## Additional Resources

**Documentation**:
- `STONE_PROVER_INTEGRATION_DEEP_DIVE.md` - Complete integration guide
- `DYNAMIC_FRI_ALGORITHM_DETAILED.md` - FRI algorithm details
- `TROUBLESHOOTING_GUIDE.md` - Comprehensive troubleshooting

**Examples**:
- `COMPLETE_INTEGRATION_TUTORIAL.md` - Full integration example
- `EXAMPLE_PROJECTS.md` - Working code examples

**Support**:
- GitHub Issues: [Your repo]
- Documentation: [Your docs]
- Community: [Your community]

---

## Conclusion

You now have Stone Prover set up and generating proofs! This is just the beginning. Next steps:

1. ✅ Stone Prover built and working
2. ✅ Basic integration complete
3. → Integrate with your application
4. → Test with real traces
5. → Deploy to production

**Time to Production**: With this foundation, you can be production-ready in 1-2 days.

**Questions?** See `DEVELOPER_FAQ.md` or check troubleshooting guides.
