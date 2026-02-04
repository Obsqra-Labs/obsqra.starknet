# Stone Prover Integration Deep Dive
## Complete Technical Guide for Builders

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Production-Validated Implementation  
**Category**: Technical Deep Dive

---

## Executive Summary

This document provides a comprehensive technical guide to integrating Stone Prover for local STARK proof generation. Stone Prover is StarkWare's open-source CPU AIR prover that enables developers to generate cryptographic proofs locally without relying on cloud services. This guide is based on Obsqra Labs' production implementation that has achieved 100% success rate across 100+ proofs.

**Key Takeaways**:
- Stone Prover enables zero per-proof cost proof generation
- Dynamic FRI parameter calculation is critical for variable trace sizes
- Complete orchestration layer bridges Stone Prover with modern applications
- Production-ready patterns for error handling, logging, and validation

---

## Table of Contents

1. [Stone Prover Architecture Overview](#stone-prover-architecture-overview)
2. [Binary Setup and Compilation](#binary-setup-and-compilation)
3. [Input Format Requirements](#input-format-requirements)
4. [Output Format Parsing](#output-format-parsing)
5. [Dynamic FRI Parameter Calculation](#dynamic-fri-parameter-calculation)
6. [Error Handling and Debugging](#error-handling-and-debugging)
7. [Version Compatibility Matrix](#version-compatibility-matrix)
8. [Configuration Options](#configuration-options)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting Guide](#troubleshooting-guide)
11. [Code Examples](#code-examples)
12. [Performance Optimization](#performance-optimization)
13. [Production Best Practices](#production-best-practices)

---

## Stone Prover Architecture Overview

### What is Stone Prover?

Stone Prover (STARK One) is StarkWare's open-source STARK prover released under Apache 2.0 license in August 2023. It has been in production since June 2020 and is responsible for compressing transactions and generating cryptographic proofs to help scale Ethereum.

**Key Characteristics**:
- **Type**: CPU AIR (Algebraic Intermediate Representation) prover
- **Language**: C++ (with Python bindings available)
- **License**: Apache 2.0 (open source)
- **Production Status**: Battle-tested (proved $1 trillion in transaction volume)
- **Performance**: 2-4 seconds for typical proofs (512-65K steps)

### Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│                    Stone Prover Binary                  │
│              (cpu_air_prover executable)                │
├─────────────────────────────────────────────────────────┤
│  Input Processing                                       │
│  ├─ Private Input (trace paths, memory paths)          │
│  ├─ Public Input (n_steps, layout, memory_segments)   │
│  └─ Parameters (FRI config, security params)         │
├─────────────────────────────────────────────────────────┤
│  Proof Generation Engine                                │
│  ├─ Trace Loading                                       │
│  ├─ AIR Construction                                    │
│  ├─ FRI Protocol Execution                              │
│  ├─ Merkle Tree Construction                            │
│  └─ Proof Serialization                                 │
├─────────────────────────────────────────────────────────┤
│  Output Generation                                      │
│  ├─ STARK Proof JSON                                    │
│  ├─ Annotations (optional)                              │
│  └─ Metadata                                            │
└─────────────────────────────────────────────────────────┘
```

### How Stone Prover Works

1. **Trace Loading**: Reads execution trace and memory trace from binary files
2. **AIR Construction**: Builds Algebraic Intermediate Representation from trace
3. **FRI Protocol**: Executes Fast Reed-Solomon Interactive protocol for proof generation
4. **Merkle Tree**: Constructs Merkle trees for commitment layers
5. **Proof Generation**: Generates STARK proof with all necessary components
6. **Serialization**: Outputs proof as JSON format

### Why Use Stone Prover?

**Advantages**:
- ✅ **Zero per-proof cost** (runs locally)
- ✅ **Complete control** over proof generation
- ✅ **No API dependencies** (works offline)
- ✅ **Customizable parameters** (FRI, security levels)
- ✅ **Data privacy** (proofs never leave your infrastructure)
- ✅ **Production-proven** (battle-tested at scale)

**Disadvantages**:
- ❌ Requires infrastructure setup
- ❌ Need to maintain binary compatibility
- ❌ Operational overhead
- ❌ Limited to CPU AIR (not all proof types)

---

## Binary Setup and Compilation

### Prerequisites

**System Requirements**:
- Linux (Ubuntu 20.04+ recommended) or macOS
- 8GB+ RAM (16GB recommended for large proofs)
- Multi-core CPU (4+ cores recommended)
- 50GB+ disk space (for compilation and traces)

**Build Dependencies**:
```bash
# Ubuntu/Debian
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

# macOS
brew install bazel cmake python3
```

### Building Stone Prover

**Step 1: Clone Repository**
```bash
git clone https://github.com/starkware-libs/stone-prover.git
cd stone-prover
```

**Step 2: Checkout Stable Version**
```bash
# Recommended: Use a stable commit
# Stone v3 (Sept 2024): 1414a545e4fb38a85391289abe91dd4467d268e1
git checkout 1414a545e4fb38a85391289abe91dd4467d268e1
```

**Step 3: Build Binary**
```bash
# Build CPU AIR prover
bazel build //src/starkware/main/cpu:cpu_air_prover

# Binary will be at:
# bazel-bin/src/starkware/main/cpu/cpu_air_prover
```

**Step 4: Verify Build**
```bash
./bazel-bin/src/starkware/main/cpu/cpu_air_prover --help
```

### Binary Location and Paths

**Recommended Structure**:
```
/opt/stone-prover/
├── build/
│   └── bazelout/
│       └── k8-opt/
│           └── bin/
│               └── src/
│                   └── starkware/
│                       └── main/
│                           └── cpu/
│                               └── cpu_air_prover  # Binary here
├── src/  # Source code
└── examples/  # Example proofs
```

**In Production Code**:
```python
STONE_BINARY = Path("/opt/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover")
```

### Version Management

**Stone Prover Versions**:
- **Stone v2** (`7ac17c8b...`, March 2024): Earlier version, may match stone5 semantics
- **Stone v3** (`1414a545...`, Sept 2024): Current stable, matches stone6 semantics

**Important**: Stone Prover version must match Integrity verifier version:
- Stone v3 → Use `stone6` verifier setting
- Stone v2 → Use `stone5` verifier setting (hypothesis)

See `STONE_VERSION_COMPATIBILITY_MATRIX.md` for detailed version mapping.

---

## Input Format Requirements

### Private Input Format

**File**: `private_input.json`

**Structure**:
```json
{
  "trace_path": "/path/to/execution_trace.bin",
  "memory_path": "/path/to/memory_trace.bin",
  "pedersen": [],
  "range_check": [],
  "ecdsa": []
}
```

**Fields**:
- `trace_path`: Absolute path to execution trace binary file
- `memory_path`: Absolute path to memory trace binary file
- `pedersen`: List of Pedersen hash builtin segments (usually empty for CPU AIR)
- `range_check`: List of range check builtin segments (usually empty)
- `ecdsa`: List of ECDSA builtin segments (usually empty)

**Example**:
```json
{
  "trace_path": "/tmp/trace_12345.bin",
  "memory_path": "/tmp/memory_12345.bin",
  "pedersen": [],
  "range_check": [],
  "ecdsa": []
}
```

### Public Input Format

**File**: `public_input.json`

**Structure**:
```json
{
  "n_steps": 65536,
  "layout": "recursive",
  "memory_segments": [
    {
      "begin_addr": 0,
      "stop_ptr": 1000,
      "stop_ptr_offset": 0
    }
  ],
  "public_memory": [
    {
      "address": 0,
      "value": 12345
    }
  ]
}
```

**Required Fields**:
- `n_steps`: Number of execution steps (must be power of 2, >= 512)
- `layout`: Cairo layout type (`"recursive"`, `"dynamic"`, `"small"`, `"starknet"`)
- `memory_segments`: List of memory segment definitions
- `public_memory`: List of public memory values

**Layout Types**:
- `"recursive"`: Full recursive layout (recommended for production)
- `"dynamic"`: Dynamic layout (for complex programs)
- `"small"`: Small layout (for simple programs)
- `"starknet"`: Starknet-specific layout

**Memory Segments**:
```json
{
  "begin_addr": 0,        // Starting address
  "stop_ptr": 1000,       // Stop pointer value
  "stop_ptr_offset": 0    // Offset for stop pointer
}
```

**Public Memory**:
```json
{
  "address": 0,   // Memory address
  "value": 12345  // Value at address (felt252)
}
```

### Parameters File Format

**File**: `cpu_air_params.json`

**Structure**:
```json
{
  "stark": {
    "fri": {
      "fri_step_list": [0, 4, 4, 4, 1],
      "last_layer_degree_bound": 128,
      "n_queries": 10,
      "proof_of_work_bits": 30
    },
    "log_n_cosets": 2
  },
  "channel_hash": "poseidon3",
  "commitment_hash": "keccak256_masked160_lsb",
  "pow_hash": "keccak256",
  "n_verifier_friendly_commitment_layers": 9999,
  "verifier_friendly_channel_updates": true,
  "verifier_friendly_commitment_hash": "poseidon3"
}
```

**Critical Parameters**:
- `fri_step_list`: **MUST be calculated dynamically** based on `n_steps`
- `last_layer_degree_bound`: Fixed (typically 128)
- `n_queries`: Security parameter (10 for canonical)
- `proof_of_work_bits`: PoW difficulty (30 for canonical)
- `log_n_cosets`: FRI coset parameter (typically 2)

**FRI Step List Calculation**:
The `fri_step_list` MUST satisfy the FRI equation:
```
log2(last_layer_degree_bound) + Σ(fri_steps) = log2(n_steps) + 4
```

See `DYNAMIC_FRI_ALGORITHM_DETAILED.md` for complete algorithm.

### Prover Config File Format

**File**: `cpu_air_prover_config.json`

**Structure**:
```json
{
  "field": "PrimeField0",
  "air": {
    "constraints": []
  }
}
```

**Fields**:
- `field`: Field type (usually `"PrimeField0"` for Cairo)
- `air`: AIR configuration (usually minimal for CPU AIR)

---

## Output Format Parsing

### Proof JSON Structure

**File**: `proof.json` (generated by Stone Prover)

**Top-Level Structure**:
```json
{
  "version": "1.0.0",
  "proof_parameters": {
    "stark": {
      "fri": {
        "fri_step_list": [0, 4, 4, 4, 1],
        "last_layer_degree_bound": 128,
        "n_queries": 10,
        "proof_of_work_bits": 30
      },
      "log_n_cosets": 2
    },
    "channel_hash": "poseidon3",
    "commitment_hash": "keccak256_masked160_lsb",
    "pow_hash": "keccak256",
    "n_verifier_friendly_commitment_layers": 9999
  },
  "stark_proof": {
    "fri_proof": {
      "layers": [...],
      "final_poly_coefficients": [...]
    },
    "traces": [...],
    "ood_frame": {
      "columns": [...]
    }
  },
  "annotations": {
    "public_input": {...},
    "n_steps": 65536
  }
}
```

### Key Fields to Extract

**Proof Parameters** (for verification):
```python
proof_params = proof_json["proof_parameters"]
stark = proof_params["stark"]
fri = stark["fri"]

fri_step_list = fri["fri_step_list"]
n_queries = fri["n_queries"]
proof_of_work_bits = fri["proof_of_work_bits"]
last_layer_degree_bound = fri["last_layer_degree_bound"]
log_n_cosets = stark["log_n_cosets"]
```

**STARK Proof** (for serialization):
```python
stark_proof = proof_json["stark_proof"]
fri_proof = stark_proof["fri_proof"]
traces = stark_proof["traces"]
ood_frame = stark_proof["ood_frame"]
```

**Metadata**:
```python
n_steps = proof_json["annotations"]["n_steps"]
public_input = proof_json["annotations"]["public_input"]
```

### Proof Hash Calculation

**Method**: SHA-256 hash of proof JSON bytes

```python
import hashlib
import json

proof_bytes = json.dumps(proof_json, sort_keys=True).encode('utf-8')
proof_hash = hashlib.sha256(proof_bytes).hexdigest()
```

### Proof Size Analysis

**Typical Sizes**:
- **512 steps**: ~128-200 KB
- **16384 steps**: ~300-400 KB
- **65536 steps**: ~400-500 KB

**Size Components**:
- FRI proof layers: ~60-70% of total size
- Traces: ~20-30% of total size
- OOD frame: ~10-20% of total size

---

## Dynamic FRI Parameter Calculation

### The FRI Equation

**Critical Requirement**:
```
log2(last_layer_degree_bound) + Σ(fri_steps) = log2(n_steps) + 4
```

**Why This Matters**:
- Fixed FRI parameters only work for one trace size
- Variable trace sizes require dynamic calculation
- Incorrect parameters cause "Signal 6" crashes

### Algorithm Implementation

**Python Implementation**:
```python
import math

def calculate_fri_step_list(n_steps: int, last_layer_degree_bound: int) -> List[int]:
    """
    Calculate FRI step list based on trace size.
    
    FRI equation: log2(last_layer_degree_bound) + Σ(fri_steps) = log2(n_steps) + 4
    
    Args:
        n_steps: Number of execution steps (must be power of 2, >= 512)
        last_layer_degree_bound: Fixed last layer degree bound (typically 128)
    
    Returns:
        fri_step_list: List of FRI step values
    
    Raises:
        ValueError: If n_steps is not a power of 2 or equation is impossible
    """
    # Validate n_steps is power of 2
    if n_steps & (n_steps - 1) != 0 or n_steps < 512:
        raise ValueError(f"n_steps must be a power of 2 and >= 512, got {n_steps}")
    
    # Calculate logarithms
    log_n_steps = math.ceil(math.log2(n_steps))
    last_layer_log2 = math.ceil(math.log2(last_layer_degree_bound))
    
    # Calculate target sum
    target_sum = log_n_steps + 4
    
    # Calculate sigma (sum of FRI steps needed)
    sigma = target_sum - last_layer_log2
    
    if sigma < 0:
        raise ValueError(
            f"FRI equation impossible: log2(last_layer)={last_layer_log2} > target_sum={target_sum}"
        )
    
    # Calculate step list using quotient-remainder approach
    q, r = divmod(sigma, 4)
    fri_steps = [0] + [4] * q + ([r] if r > 0 else [])
    
    # Verify equation holds
    equation_sum = sum(fri_steps)
    actual_sum = last_layer_log2 + equation_sum
    
    if actual_sum != target_sum:
        raise ValueError(
            f"FRI equation mismatch: log2({last_layer_degree_bound})={last_layer_log2} + "
            f"{fri_steps}={equation_sum} = {actual_sum}, expected {target_sum}"
        )
    
    return fri_steps
```

### Example Calculations

**n_steps = 512**:
```
log2(512) = 9
log2(128) = 7
target_sum = 9 + 4 = 13
sigma = 13 - 7 = 6
q = 1, r = 2
fri_step_list = [0, 4, 2]
Verification: 7 + (0 + 4 + 2) = 13 ✓
```

**n_steps = 16384**:
```
log2(16384) = 14
log2(128) = 7
target_sum = 14 + 4 = 18
sigma = 18 - 7 = 11
q = 2, r = 3
fri_step_list = [0, 4, 4, 3]
Verification: 7 + (0 + 4 + 4 + 3) = 18 ✓
```

**n_steps = 65536**:
```
log2(65536) = 16
log2(128) = 7
target_sum = 16 + 4 = 20
sigma = 20 - 7 = 13
q = 3, r = 1
fri_step_list = [0, 4, 4, 4, 1]
Verification: 7 + (0 + 4 + 4 + 4 + 1) = 20 ✓
```

### Common Pitfalls

**Pitfall 1: Using Fixed FRI Parameters**
```python
# ❌ WRONG: Fixed parameters
fri_step_list = [0, 4, 4, 3]  # Only works for n_steps=16384

# ✅ CORRECT: Dynamic calculation
fri_step_list = calculate_fri_step_list(n_steps, last_layer_degree_bound)
```

**Pitfall 2: Not Validating Equation**
```python
# ❌ WRONG: No validation
fri_step_list = [0, 4, 4, 3]  # Might not satisfy equation

# ✅ CORRECT: Validate equation
actual_sum = last_layer_log2 + sum(fri_step_list)
assert actual_sum == target_sum, "FRI equation not satisfied"
```

**Pitfall 3: Non-Power-of-2 n_steps**
```python
# ❌ WRONG: n_steps not power of 2
n_steps = 1000  # Will cause errors

# ✅ CORRECT: Round to power of 2
n_steps_log = math.ceil(math.log2(n_steps))
n_steps = 2 ** n_steps_log  # Round up to next power of 2
```

---

## Error Handling and Debugging

### Common Error Types

**1. Signal 6 (SIGABRT)**
**Cause**: FRI parameter mismatch
**Solution**: Use dynamic FRI calculation
**Example**:
```
Error: Signal 6 (SIGABRT)
Cause: fri_step_list doesn't satisfy FRI equation
Fix: Recalculate fri_step_list based on n_steps
```

**2. File Not Found**
**Cause**: Incorrect file paths
**Solution**: Use absolute paths, verify files exist
**Example**:
```python
# ❌ WRONG: Relative path
trace_path = "trace.bin"

# ✅ CORRECT: Absolute path
trace_path = str(Path(trace_file).absolute())
```

**3. Invalid n_steps**
**Cause**: n_steps not power of 2 or < 512
**Solution**: Validate and round n_steps
**Example**:
```python
# Validate
if n_steps & (n_steps - 1) != 0:
    n_steps_log = math.ceil(math.log2(n_steps))
    n_steps = 2 ** n_steps_log
```

**4. Timeout**
**Cause**: Proof generation taking too long
**Solution**: Increase timeout or optimize trace size
**Example**:
```python
# Default timeout: 300 seconds
result = subprocess.run(cmd, timeout=600)  # Increase for large proofs
```

### Debugging Techniques

**1. Enable Verbose Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**2. Log Command and Parameters**
```python
logger.info(f"Stone command: {' '.join(cmd)}")
logger.info(f"FRI parameters: {fri_steps}")
logger.info(f"n_steps: {n_steps}")
```

**3. Capture stderr**
```python
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    logger.error(f"Stone stderr: {result.stderr}")
    logger.error(f"Stone stdout: {result.stdout}")
```

**4. Validate Input Files**
```python
# Check files exist
assert Path(trace_file).exists(), f"Trace file not found: {trace_file}"
assert Path(memory_file).exists(), f"Memory file not found: {memory_file}"

# Check file sizes
trace_size = Path(trace_file).stat().st_size
logger.info(f"Trace file size: {trace_size} bytes")
```

**5. Test with Minimal Input**
```python
# Start with small n_steps (512)
# Then scale up to target size
for test_n_steps in [512, 1024, 2048, 4096]:
    result = generate_proof(test_n_steps)
    if not result.success:
        logger.error(f"Failed at n_steps={test_n_steps}")
        break
```

---

## Version Compatibility Matrix

### Stone Prover Versions

| Version | Commit Hash | Date | Integrity Verifier | Notes |
|---------|-------------|------|-------------------|-------|
| Stone v2 | `7ac17c8b...` | March 2024 | `stone5` (hypothesis) | Earlier version |
| Stone v3 | `1414a545...` | Sept 2024 | `stone6` (confirmed) | Current stable |

### Integrity Verifier Versions

| Verifier Setting | Public Input Hash | n_verifier_friendly | Stone Version |
|------------------|-------------------|---------------------|---------------|
| `stone5` | Does NOT include | N/A | Stone v2 (hypothesis) |
| `stone6` | Includes | Included in hash | Stone v3 (confirmed) |

### Compatibility Rules

**Rule 1**: Stone version must match Integrity verifier setting
- Stone v3 → Use `stone6` verifier
- Stone v2 → Use `stone5` verifier (hypothesis)

**Rule 2**: Public input hash calculation differs
```cairo
// Integrity source: integrity/src/air/public_input.cairo
if *settings.stone_version == StoneVersion::Stone6 {
    hash_data.append(n_verifier_friendly_commitment_layers);
}
```

**Rule 3**: Mismatch causes OODS errors
- If Stone v3 proof verified as `stone5` → OODS failure
- If Stone v2 proof verified as `stone6` → OODS failure (hypothesis)

### Migration Guide

**From stone5 to stone6**:
1. Update Stone Prover to v3 (if not already)
2. Update config: `INTEGRITY_STONE_VERSION = "stone6"`
3. Regenerate proofs (or use existing if compatible)
4. Test verification

**From stone6 to stone5**:
1. Downgrade Stone Prover to v2
2. Update config: `INTEGRITY_STONE_VERSION = "stone5"`
3. Regenerate proofs
4. Test verification

---

## Configuration Options

### Base Parameters File

**Location**: `integrity/examples/proofs/cpu_air_params.json`

**Key Parameters**:
```json
{
  "stark": {
    "fri": {
      "fri_step_list": [0, 4, 4, 3],  // Template (recalculated dynamically)
      "last_layer_degree_bound": 128,  // Fixed
      "n_queries": 10,                 // Security parameter
      "proof_of_work_bits": 30         // PoW difficulty
    },
    "log_n_cosets": 2                  // FRI coset parameter
  },
  "channel_hash": "poseidon3",
  "commitment_hash": "keccak256_masked160_lsb",
  "pow_hash": "keccak256",
  "n_verifier_friendly_commitment_layers": 9999,
  "verifier_friendly_channel_updates": true,
  "verifier_friendly_commitment_hash": "poseidon3"
}
```

### Parameter Tuning

**Security vs Performance Trade-offs**:

| Parameter | Higher Value | Lower Value |
|-----------|--------------|-------------|
| `n_queries` | More secure, slower verification | Less secure, faster verification |
| `proof_of_work_bits` | More PoW work, slower generation | Less PoW work, faster generation |
| `last_layer_degree_bound` | Larger proofs, more security | Smaller proofs, less security |

**Recommended Settings** (canonical):
- `n_queries`: 10 (balance of security and performance)
- `proof_of_work_bits`: 30 (sufficient security)
- `last_layer_degree_bound`: 128 (standard)

### Prover Config File

**Location**: `integrity/examples/proofs/cpu_air_prover_config.json`

**Structure**:
```json
{
  "field": "PrimeField0",
  "air": {
    "constraints": []
  }
}
```

**Usually minimal** - default values work for most cases.

---

## Advanced Features

### Annotation Generation

**Enable annotations** for debugging:
```python
cmd = [
    stone_binary,
    "--generate_annotations",  # Add this flag
    # ... other args
]
```

**Annotations include**:
- Public input details
- n_steps information
- Memory segment information
- Trace metadata

### Custom FRI Parameters

**For advanced use cases**, you can customize FRI parameters:
```python
# Custom last_layer_degree_bound
last_layer = 256  # Instead of 128
fri_steps = calculate_fri_step_list(n_steps, last_layer)
```

**Trade-offs**:
- Larger `last_layer_degree_bound` → Larger proofs, more security
- Smaller `last_layer_degree_bound` → Smaller proofs, less security

### Parallel Proof Generation

**For multiple proofs**, generate in parallel:
```python
import asyncio

async def generate_proofs_parallel(inputs):
    tasks = [generate_proof(inp) for inp in inputs]
    return await asyncio.gather(*tasks)
```

**Considerations**:
- Memory usage (each proof needs ~500MB-1GB)
- CPU cores (one proof per core)
- I/O bandwidth (trace file access)

---

## Troubleshooting Guide

### Problem: "Signal 6" Error

**Symptoms**:
```
Error: Signal 6 (SIGABRT)
Stone prover crashed
```

**Root Cause**: FRI parameter mismatch

**Solution**:
1. Verify FRI equation holds
2. Use dynamic FRI calculation
3. Check n_steps is power of 2

**Debug Steps**:
```python
# Verify FRI equation
last_layer_log2 = math.ceil(math.log2(last_layer_degree_bound))
equation_sum = sum(fri_step_list)
target_sum = math.ceil(math.log2(n_steps)) + 4
actual_sum = last_layer_log2 + equation_sum

assert actual_sum == target_sum, f"FRI equation mismatch: {actual_sum} != {target_sum}"
```

### Problem: "File Not Found"

**Symptoms**:
```
Error: File not found: trace.bin
```

**Root Cause**: Incorrect file paths

**Solution**:
1. Use absolute paths
2. Verify files exist before calling Stone
3. Check file permissions

**Debug Steps**:
```python
# Use absolute paths
trace_path = str(Path(trace_file).absolute())
memory_path = str(Path(memory_file).absolute())

# Verify files exist
assert Path(trace_path).exists(), f"Trace file not found: {trace_path}"
assert Path(memory_path).exists(), f"Memory file not found: {memory_path}"
```

### Problem: "Invalid n_steps"

**Symptoms**:
```
Error: n_steps must be power of 2
```

**Root Cause**: n_steps not power of 2

**Solution**:
1. Round n_steps to next power of 2
2. Validate before calling Stone

**Debug Steps**:
```python
# Round to power of 2
if n_steps & (n_steps - 1) != 0:
    n_steps_log = math.ceil(math.log2(n_steps))
    n_steps = 2 ** n_steps_log
    logger.info(f"Rounded n_steps to {n_steps}")
```

### Problem: Timeout

**Symptoms**:
```
Error: Timeout after 300 seconds
```

**Root Cause**: Proof generation taking too long

**Solution**:
1. Increase timeout for large proofs
2. Optimize trace size
3. Check system resources

**Debug Steps**:
```python
# Increase timeout for large proofs
timeout = 300  # Default
if n_steps > 32768:
    timeout = 600  # 10 minutes for very large proofs

result = subprocess.run(cmd, timeout=timeout)
```

### Problem: OODS Verification Failure

**Symptoms**:
```
Error: Invalid OODS
On-chain verification fails
```

**Root Cause**: Stone version mismatch with Integrity verifier

**Solution**:
1. Check Stone version
2. Check Integrity verifier setting
3. Ensure compatibility (Stone v3 → stone6)

**Debug Steps**:
```python
# Check Stone version
stone_version = get_stone_version()  # e.g., "1414a545..."

# Check Integrity setting
integrity_version = settings.INTEGRITY_STONE_VERSION  # e.g., "stone6"

# Verify compatibility
if stone_version.startswith("1414a545"):  # Stone v3
    assert integrity_version == "stone6", "Stone v3 requires stone6 verifier"
```

---

## Code Examples

### Basic Proof Generation

```python
from pathlib import Path
import asyncio
from stone_prover_service import StoneProverService

async def generate_basic_proof():
    # Initialize service
    stone_service = StoneProverService()
    
    # Prepare input files
    private_input = {
        "trace_path": "/tmp/trace.bin",
        "memory_path": "/tmp/memory.bin",
        "pedersen": [],
        "range_check": [],
        "ecdsa": []
    }
    
    public_input = {
        "n_steps": 512,
        "layout": "recursive",
        "memory_segments": [...],
        "public_memory": [...]
    }
    
    # Write input files
    private_input_file = "/tmp/private_input.json"
    public_input_file = "/tmp/public_input.json"
    
    with open(private_input_file, 'w') as f:
        json.dump(private_input, f)
    
    with open(public_input_file, 'w') as f:
        json.dump(public_input, f)
    
    # Generate proof
    result = await stone_service.generate_proof(
        private_input_file,
        public_input_file,
        proof_output_file="/tmp/proof.json"
    )
    
    if result.success:
        print(f"Proof generated: {result.proof_hash}")
        print(f"Size: {result.proof_size_kb} KB")
        print(f"Time: {result.generation_time_ms} ms")
    else:
        print(f"Error: {result.error}")

# Run
asyncio.run(generate_basic_proof())
```

### Complete Integration Example

```python
import asyncio
import json
import tempfile
from pathlib import Path
from stone_prover_service import StoneProverService
from integrity_service import IntegrityService

async def generate_and_verify_proof(metrics):
    # Step 1: Generate Cairo trace
    trace_file, memory_file, public_input_file = await generate_cairo_trace(metrics)
    
    # Step 2: Initialize Stone service
    stone_service = StoneProverService()
    
    # Step 3: Generate proof
    proof_result = await stone_service.generate_proof_from_trace_files(
        trace_file,
        memory_file,
        public_input_file
    )
    
    if not proof_result.success:
        raise Exception(f"Proof generation failed: {proof_result.error}")
    
    # Step 4: Serialize proof for Integrity
    calldata = serialize_proof_for_integrity(proof_result.proof_json)
    
    # Step 5: Verify with Integrity
    integrity_service = IntegrityService(rpc_url, network="sepolia")
    verified = await integrity_service.verify_with_calldata(calldata)
    
    if verified:
        print("✅ Proof verified on-chain")
        return proof_result.proof_hash
    else:
        raise Exception("Proof verification failed")

# Usage
metrics = {
    "jediswap_metrics": {...},
    "ekubo_metrics": {...}
}

proof_hash = asyncio.run(generate_and_verify_proof(metrics))
```

### Error Handling Example

```python
async def generate_proof_with_retry(inputs, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await stone_service.generate_proof(**inputs)
            
            if result.success:
                return result
            
            # Check if error is retryable
            if "Signal 6" in result.error:
                # FRI parameter issue - recalculate
                n_steps = inputs["public_input"]["n_steps"]
                fri_steps = recalculate_fri_steps(n_steps)
                inputs["fri_steps"] = fri_steps
                continue
            
            if "timeout" in result.error.lower():
                # Increase timeout
                inputs["timeout_seconds"] = inputs.get("timeout_seconds", 300) * 2
                continue
            
            # Non-retryable error
            raise Exception(f"Proof generation failed: {result.error}")
        
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    raise Exception("Max retries exceeded")
```

---

## Performance Optimization

### Trace Size Optimization

**Minimize n_steps**:
- Use smallest trace size that fits computation
- Round up to next power of 2 (don't over-allocate)
- Consider batching multiple computations

**Example**:
```python
# Calculate actual steps needed
actual_steps = calculate_required_steps(computation)

# Round to next power of 2
n_steps_log = math.ceil(math.log2(actual_steps))
n_steps = 2 ** n_steps_log

# Don't over-allocate
if n_steps > actual_steps * 2:
    n_steps = n_steps // 2  # Use smaller size if possible
```

### Parallel Processing

**Generate multiple proofs in parallel**:
```python
async def generate_proofs_batch(inputs_list):
    # Limit concurrency to avoid memory issues
    semaphore = asyncio.Semaphore(4)  # Max 4 concurrent proofs
    
    async def generate_with_limit(inputs):
        async with semaphore:
            return await stone_service.generate_proof(**inputs)
    
    tasks = [generate_with_limit(inp) for inp in inputs_list]
    return await asyncio.gather(*tasks)
```

### Caching Strategies

**Cache FRI parameters**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_fri_steps(n_steps: int, last_layer: int) -> tuple:
    """Cache FRI step list calculations"""
    return tuple(calculate_fri_step_list(n_steps, last_layer))
```

**Cache proof results** (if inputs are deterministic):
```python
proof_cache = {}

def get_proof_cache_key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()

async def generate_proof_cached(inputs):
    cache_key = get_proof_cache_key(inputs)
    
    if cache_key in proof_cache:
        return proof_cache[cache_key]
    
    result = await stone_service.generate_proof(**inputs)
    proof_cache[cache_key] = result
    return result
```

---

## Production Best Practices

### 1. Always Use Dynamic FRI Calculation

```python
# ❌ WRONG: Fixed parameters
fri_steps = [0, 4, 4, 3]

# ✅ CORRECT: Dynamic calculation
fri_steps = calculate_fri_step_list(n_steps, last_layer_degree_bound)
```

### 2. Validate Inputs Before Calling Stone

```python
# Validate n_steps
assert n_steps & (n_steps - 1) == 0, "n_steps must be power of 2"
assert n_steps >= 512, "n_steps must be >= 512"

# Validate files exist
assert Path(trace_file).exists(), "Trace file not found"
assert Path(memory_file).exists(), "Memory file not found"
```

### 3. Implement Proper Error Handling

```python
try:
    result = await stone_service.generate_proof(...)
    if not result.success:
        logger.error(f"Proof generation failed: {result.error}")
        # Handle error appropriately
except subprocess.TimeoutExpired:
    logger.error("Proof generation timeout")
    # Retry with longer timeout or smaller trace
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Handle unexpected errors
```

### 4. Log All Parameters

```python
logger.info("=" * 80)
logger.info("STONE PROVER PARAMETERS")
logger.info("=" * 80)
logger.info(f"n_steps: {n_steps}")
logger.info(f"FRI step_list: {fri_steps}")
logger.info(f"FRI last_layer: {last_layer_degree_bound}")
logger.info(f"FRI n_queries: {n_queries}")
logger.info("=" * 80)
```

### 5. Monitor Performance

```python
import time

start_time = time.time()
result = await stone_service.generate_proof(...)
elapsed = time.time() - start_time

logger.info(f"Proof generation: {elapsed:.2f}s")
logger.info(f"Proof size: {result.proof_size_kb:.1f} KB")

# Track metrics
metrics.record_proof_generation_time(elapsed)
metrics.record_proof_size(result.proof_size_kb)
```

### 6. Use Absolute Paths

```python
# ❌ WRONG: Relative paths
trace_path = "trace.bin"

# ✅ CORRECT: Absolute paths
trace_path = str(Path(trace_file).absolute())
```

### 7. Clean Up Temporary Files

```python
import tempfile
import atexit

temp_files = []

def cleanup_temp_files():
    for f in temp_files:
        try:
            Path(f).unlink()
        except:
            pass

atexit.register(cleanup_temp_files)

# Create temp file
with tempfile.NamedTemporaryFile(delete=False) as f:
    temp_file = f.name
    temp_files.append(temp_file)
```

---

## Conclusion

Stone Prover integration enables zero per-proof cost proof generation with complete control over the proving process. The key to successful integration is:

1. **Dynamic FRI parameter calculation** - Critical for variable trace sizes
2. **Proper input validation** - Prevents common errors
3. **Version compatibility** - Match Stone version with Integrity verifier
4. **Error handling** - Robust error handling and retry logic
5. **Performance monitoring** - Track metrics for optimization

This guide provides the foundation for integrating Stone Prover into production systems. For additional resources, see:
- `DYNAMIC_FRI_ALGORITHM_DETAILED.md` - Complete FRI algorithm documentation
- `INTEGRITY_FACTREGISTRY_INTEGRATION_GUIDE.md` - Integrity integration guide
- `TROUBLESHOOTING_GUIDE.md` - Comprehensive troubleshooting
- `STONE_PROVER_PERFORMANCE_BENCHMARKS.md` - Performance benchmarks

---

**Next Steps**:
1. Set up Stone Prover binary
2. Implement dynamic FRI calculation
3. Integrate with your application
4. Test with small traces first
5. Scale up to production workloads

**Questions?** See `DEVELOPER_FAQ.md` or open an issue in the repository.
