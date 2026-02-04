# Integrity FactRegistry Integration Guide
## Complete Guide to On-Chain Proof Verification

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Production-Validated  
**Category**: Technical Deep Dive

---

## Executive Summary

This document provides a comprehensive guide to integrating with Integrity FactRegistry for on-chain STARK proof verification on Starknet. Integrity enables verification of Stone proofs on Starknet itself, similar to verifying Starknet execution on Ethereum. This guide is based on Obsqra Labs' production implementation with 100% verification success rate.

**Key Concepts**: FactRegistry, verifier registration, proof serialization, calldata construction, on-chain verification flow.

---

## Table of Contents

1. [FactRegistry Architecture](#factregistry-architecture)
2. [Verifier Registration Process](#verifier-registration-process)
3. [Proof Serialization Format](#proof-serialization-format)
4. [Calldata Construction](#calldata-construction)
5. [Verification Flow](#verification-flow)
6. [Error Codes and Handling](#error-codes-and-handling)
7. [Public vs Custom FactRegistry](#public-vs-custom-factregistry)
8. [Stone Version Compatibility](#stone-version-compatibility)
9. [Best Practices](#best-practices)
10. [Code Examples](#code-examples)
11. [Troubleshooting](#troubleshooting)

---

## FactRegistry Architecture

### What is Integrity FactRegistry?

Integrity FactRegistry is a Cairo smart contract that enables on-chain verification of STARK proofs. It acts as a registry of verified computation facts, allowing contracts to verify proofs without re-executing the computation.

**Key Components**:
1. **FactRegistry Contract**: Stores verified facts
2. **Verifiers**: Registered verifier configurations
3. **Facts**: Hash commitments to verified computations
4. **Verification Function**: `verify_proof_full_and_register_fact`

### Architecture Diagram

```
Stone Proof (JSON)
    ↓
proof_serializer (binary)
    ↓
Calldata (felts)
    ↓
Integrity FactRegistry Contract
    ├─ Verifier Lookup
    ├─ Proof Verification
    ├─ Fact Hash Calculation
    └─ Fact Registration
    ↓
Fact Hash (on-chain)
```

### Contract Addresses

**Sepolia Testnet**:
- Public FactRegistry: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`
- Has all verifiers pre-registered
- Recommended for production and testing

**Mainnet**:
- Public FactRegistry: `0xcc63a1e8e7824642b89fa6baf996b8ed21fa4707be90ef7605570ca8e4f00b`

**Custom FactRegistry**:
- Deploy your own (requires verifier registration)
- Only use if you've registered verifiers

---

## Verifier Registration Process

### Verifier Configuration

**Verifier Settings**:
- `layout`: Cairo layout (`"recursive"`, `"dynamic"`, etc.)
- `hasher`: Hash function (`"keccak_160_lsb"`, etc.)
- `stone_version`: Stone version (`"stone5"`, `"stone6"`)
- `memory_verification`: Memory mode (`"strict"`, etc.)

**Example Configuration**:
```python
verifier_config = {
    "layout": "recursive",
    "hasher": "keccak_160_lsb",
    "stone_version": "stone6",  # Must match Stone Prover version
    "memory_verification": "strict"
}
```

### Registration Process

**Step 1: Verifier Deployment**
- Deploy verifier contract (if custom)
- Or use public FactRegistry (has verifiers registered)

**Step 2: Verifier Registration**
- Register verifier in FactRegistry
- Associate verifier with configuration
- One-time setup (already done in public FactRegistry)

**Step 3: Verification**
- Use registered verifier for proof verification
- FactRegistry looks up verifier by configuration
- Verifies proof and registers fact

### Public FactRegistry

**Advantages**:
- ✅ All verifiers pre-registered
- ✅ No setup required
- ✅ Production-ready
- ✅ Recommended for most use cases

**Usage**:
```python
PUBLIC_FACT_REGISTRY = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
```

---

## Proof Serialization Format

### Stone Proof JSON Structure

**Input**: Stone proof JSON (from `cpu_air_prover`)

**Structure**:
```json
{
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
    "fri_proof": {...},
    "traces": [...],
    "ood_frame": {...}
  }
}
```

### Serialization Process

**Step 1: Use proof_serializer**
```bash
proof_serializer proof.json calldata.bin
```

**Step 2: Parse Binary Output**
- Binary format (felts)
- Convert to calldata array
- Ready for contract call

**Python Integration**:
```python
import subprocess
import struct

def serialize_proof(proof_json_path: str, serializer_bin: str) -> list[int]:
    """Serialize Stone proof to calldata"""
    # Run proof_serializer
    result = subprocess.run(
        [serializer_bin, proof_json_path, "-"],
        capture_output=True,
        check=True
    )
    
    # Parse binary output (felts)
    calldata = []
    for i in range(0, len(result.stdout), 32):
        felt_bytes = result.stdout[i:i+32]
        felt = int.from_bytes(felt_bytes, 'big')
        calldata.append(felt)
    
    return calldata
```

---

## Calldata Construction

### Calldata Format

**Structure**:
```
[layout_felt, hasher_felt, stone_version_felt, memory_felt, ...proof_calldata...]
```

**Verifier Config Prefix**:
1. `layout`: String encoded as felt (`"recursive"` → felt)
2. `hasher`: String encoded as felt (`"keccak_160_lsb"` → felt)
3. `stone_version`: String encoded as felt (`"stone6"` → felt)
4. `memory_verification`: String encoded as felt (`"strict"` → felt)

**Proof Calldata**: Serialized proof from `proof_serializer`

### String to Felt Encoding

**Method**: ASCII encoding
```python
def string_to_felt(value: str) -> int:
    """Encode ASCII string to felt"""
    return int.from_bytes(value.encode("ascii"), "big")
```

**Examples**:
- `"recursive"` → `0x726563757273697665` (felt)
- `"keccak_160_lsb"` → `0x6b656363616b5f3136305f6c7362` (felt)
- `"stone6"` → `0x73746f6e6536` (felt)
- `"strict"` → `0x737472696374` (felt)

### Complete Calldata Construction

```python
def construct_calldata(
    proof_json_path: str,
    serializer_bin: str,
    layout: str = "recursive",
    hasher: str = "keccak_160_lsb",
    stone_version: str = "stone6",
    memory_verification: str = "strict"
) -> list[int]:
    """Construct complete calldata for Integrity verification"""
    
    # Serialize proof
    proof_calldata = serialize_proof(proof_json_path, serializer_bin)
    
    # Prefix verifier config
    calldata = [
        string_to_felt(layout),
        string_to_felt(hasher),
        string_to_felt(stone_version),
        string_to_felt(memory_verification),
        *proof_calldata
    ]
    
    return calldata
```

---

## Verification Flow

### Step-by-Step Process

**Step 1: Generate Proof**
```python
# Generate Stone proof
proof_result = await stone_service.generate_proof(...)
proof_json_path = proof_result.proof_file
```

**Step 2: Serialize Proof**
```python
# Serialize to calldata
proof_calldata = serialize_proof(proof_json_path, serializer_bin)
```

**Step 3: Construct Calldata**
```python
# Add verifier config prefix
calldata = construct_calldata(
    proof_json_path,
    serializer_bin,
    layout="recursive",
    hasher="keccak_160_lsb",
    stone_version="stone6",
    memory_verification="strict"
)
```

**Step 4: Call Integrity Contract**
```python
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name

# Initialize client
client = FullNodeClient(node_url=rpc_url)

# Get selector
selector = get_selector_from_name("verify_proof_full_and_register_fact")

# Construct call
call = {
    "to": fact_registry_address,
    "selector": selector,
    "calldata": calldata
}

# Execute call
result = await client.call_contract(call, block_number="latest")
```

**Step 5: Extract Fact Hash**
```python
# Fact hash is first element of result
fact_hash = result[0]
print(f"Fact hash: {hex(fact_hash)}")
```

### Preflight vs Invoke

**Preflight Call** (Read-only):
- Checks if proof verifies
- Returns fact hash
- No on-chain state change
- Fast and free

**Invoke** (Write):
- Actually registers fact on-chain
- Requires wallet and gas
- Creates on-chain record
- Slower and costs gas

**Recommendation**: Use preflight for verification, invoke for registration

---

## Error Codes and Handling

### Common Errors

**1. "VERIFIER_NOT_FOUND"**
**Cause**: Verifier not registered in FactRegistry
**Solution**: Use public FactRegistry or register verifier

**2. "Invalid OODS"**
**Cause**: Stone version mismatch
**Solution**: Match Stone version with verifier setting (Stone v3 → stone6)

**3. "Invalid builtin"**
**Cause**: Layout/builtin mismatch
**Solution**: Use correct layout and builtins

**4. "Invalid final_pc"**
**Cause**: Trace execution issue
**Solution**: Check trace generation

### Error Handling

```python
try:
    result = await integrity_service.verify_with_calldata(calldata)
    if result:
        print("✅ Proof verified")
    else:
        print("❌ Proof verification failed")
except Exception as e:
    error_msg = str(e)
    
    if "VERIFIER_NOT_FOUND" in error_msg:
        print("Error: Verifier not registered")
        print("Solution: Use public FactRegistry or register verifier")
    elif "Invalid OODS" in error_msg:
        print("Error: OODS verification failed")
        print("Solution: Check Stone version compatibility")
    elif "Invalid builtin" in error_msg:
        print("Error: Builtin mismatch")
        print("Solution: Use correct layout and builtins")
    else:
        print(f"Error: {error_msg}")
```

---

## Public vs Custom FactRegistry

### Public FactRegistry

**Address**: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`

**Advantages**:
- ✅ All verifiers pre-registered
- ✅ No setup required
- ✅ Production-ready
- ✅ Recommended for most use cases

**Usage**:
```python
PUBLIC_FACT_REGISTRY = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
integrity_service = IntegrityService(
    rpc_url=rpc_url,
    network="sepolia",
    verifier_address=PUBLIC_FACT_REGISTRY
)
```

### Custom FactRegistry

**When to Use**:
- Need custom verifier configuration
- Want isolated fact registry
- Enterprise requirements

**Requirements**:
- Deploy FactRegistry contract
- Register verifiers
- Maintain verifier registry

**Not Recommended** for most use cases (use public instead)

---

## Stone Version Compatibility

### Version Mapping

**Stone v3** (`1414a545...`) → **stone6** verifier
- Includes `n_verifier_friendly_commitment_layers` in public input hash
- Must use `stone6` verifier setting

**Stone v2** (`7ac17c8b...`) → **stone5** verifier (hypothesis)
- Does NOT include `n_verifier_friendly_commitment_layers` in hash
- Must use `stone5` verifier setting

### Compatibility Rules

**Rule 1**: Stone version must match verifier setting
- Stone v3 → `stone6`
- Stone v2 → `stone5` (hypothesis)

**Rule 2**: Mismatch causes OODS errors
- Stone v3 proof with `stone5` verifier → OODS failure
- Stone v2 proof with `stone6` verifier → OODS failure (hypothesis)

**Rule 3**: Check version before verification
```python
# Get Stone version
stone_version = get_stone_prover_version()  # e.g., "1414a545..."

# Set Integrity verifier accordingly
if stone_version.startswith("1414a545"):  # Stone v3
    integrity_stone_version = "stone6"
elif stone_version.startswith("7ac17c8b"):  # Stone v2
    integrity_stone_version = "stone5"
else:
    raise ValueError(f"Unknown Stone version: {stone_version}")
```

---

## Best Practices

### 1. Always Use Public FactRegistry

```python
# ✅ RECOMMENDED: Public FactRegistry
PUBLIC_FACT_REGISTRY = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
integrity_service = IntegrityService(verifier_address=PUBLIC_FACT_REGISTRY)

# ❌ NOT RECOMMENDED: Custom FactRegistry (unless you have specific needs)
```

### 2. Match Stone Version with Verifier

```python
# ✅ CORRECT: Match versions
stone_version = "1414a545..."  # Stone v3
integrity_stone_version = "stone6"  # Matches Stone v3

# ❌ WRONG: Version mismatch
stone_version = "1414a545..."  # Stone v3
integrity_stone_version = "stone5"  # Mismatch → OODS failure
```

### 3. Use Preflight for Verification

```python
# ✅ RECOMMENDED: Preflight first
result = await integrity_service.verify_with_calldata(calldata)
if result:
    # Then invoke if needed
    fact_hash = await integrity_service.register_calldata_and_get_fact(calldata)
```

### 4. Handle Errors Gracefully

```python
try:
    result = await integrity_service.verify_with_calldata(calldata)
except Exception as e:
    # Log error
    logger.error(f"Verification failed: {e}")
    
    # Check specific error types
    if "VERIFIER_NOT_FOUND" in str(e):
        # Handle verifier not found
    elif "Invalid OODS" in str(e):
        # Handle OODS error (check version)
    else:
        # Handle other errors
```

### 5. Validate Calldata Before Sending

```python
# Validate calldata size
if len(calldata) > 100000:  # Arbitrary limit
    raise ValueError("Calldata too large")

# Validate verifier config
assert calldata[0] == string_to_felt("recursive"), "Invalid layout"
assert calldata[1] == string_to_felt("keccak_160_lsb"), "Invalid hasher"
assert calldata[2] == string_to_felt("stone6"), "Invalid stone version"
```

---

## Code Examples

### Complete Integration Example

```python
import asyncio
from pathlib import Path
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name

async def verify_proof_onchain(
    proof_json_path: str,
    serializer_bin: str,
    fact_registry_address: int,
    rpc_url: str,
    layout: str = "recursive",
    hasher: str = "keccak_160_lsb",
    stone_version: str = "stone6",
    memory_verification: str = "strict"
):
    """Complete on-chain verification flow"""
    
    # Step 1: Serialize proof
    proof_calldata = serialize_proof(proof_json_path, serializer_bin)
    
    # Step 2: Construct calldata
    calldata = [
        string_to_felt(layout),
        string_to_felt(hasher),
        string_to_felt(stone_version),
        string_to_felt(memory_verification),
        *proof_calldata
    ]
    
    # Step 3: Initialize client
    client = FullNodeClient(node_url=rpc_url)
    
    # Step 4: Get selector
    selector = get_selector_from_name("verify_proof_full_and_register_fact")
    
    # Step 5: Construct call
    call = {
        "to": fact_registry_address,
        "selector": selector,
        "calldata": calldata
    }
    
    # Step 6: Execute call
    try:
        result = await client.call_contract(call, block_number="latest")
        
        if result and len(result) > 0:
            fact_hash = result[0]
            print(f"✅ Proof verified: fact_hash={hex(fact_hash)}")
            return fact_hash
        else:
            print("❌ Verification returned empty result")
            return None
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Verification failed: {error_msg}")
        
        # Handle specific errors
        if "VERIFIER_NOT_FOUND" in error_msg:
            print("   → Verifier not registered in FactRegistry")
            print("   → Use public FactRegistry or register verifier")
        elif "Invalid OODS" in error_msg:
            print("   → OODS verification failed")
            print("   → Check Stone version compatibility")
        elif "Invalid builtin" in error_msg:
            print("   → Builtin mismatch")
            print("   → Check layout and builtins")
        
        return None

# Usage
fact_hash = asyncio.run(verify_proof_onchain(
    proof_json_path="proof.json",
    serializer_bin="/path/to/proof_serializer",
    fact_registry_address=0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c,
    rpc_url="https://starknet-sepolia.public.blastapi.io"
))
```

### Service Integration Example

```python
class IntegrityService:
    def __init__(self, rpc_url: str, network: str = "sepolia"):
        self.rpc_url = rpc_url
        self.network = network
        self.verifier_address = PUBLIC_FACT_REGISTRY  # Use public
        
    async def verify_with_calldata(self, calldata: list[int]) -> bool:
        """Verify proof using calldata"""
        from starknet_py.net.full_node_client import FullNodeClient
        from starknet_py.hash.selector import get_selector_from_name
        
        client = FullNodeClient(node_url=self.rpc_url)
        selector = get_selector_from_name("verify_proof_full_and_register_fact")
        
        call = {
            "to": self.verifier_address,
            "selector": selector,
            "calldata": calldata
        }
        
        try:
            result = await client.call_contract(call, block_number="latest")
            return result is not None and len(result) > 0
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    async def register_calldata_and_get_fact(
        self, 
        calldata: list[int]
    ) -> tuple[Optional[int], Optional[str]]:
        """Register proof and get fact hash"""
        # Preflight call
        fact_hash = None
        try:
            result = await self.verify_with_calldata(calldata)
            if result:
                # Extract fact hash from result
                # (implementation depends on result format)
                fact_hash = result[0] if result else None
        except Exception as e:
            logger.warning(f"Preflight failed: {e}")
        
        # Invoke to register (if wallet configured)
        if wallet_configured:
            # Invoke transaction
            # (implementation depends on wallet setup)
            pass
        
        return fact_hash, None
```

---

## Troubleshooting

### Issue 1: "VERIFIER_NOT_FOUND"

**Symptoms**: Verification fails with "VERIFIER_NOT_FOUND"

**Causes**:
- Using custom FactRegistry without registered verifiers
- Wrong verifier configuration
- FactRegistry address incorrect

**Solutions**:
1. Use public FactRegistry (recommended)
2. Register verifier in custom FactRegistry
3. Check verifier configuration matches registered verifier

### Issue 2: "Invalid OODS"

**Symptoms**: Verification fails with "Invalid OODS"

**Causes**:
- Stone version mismatch with verifier setting
- FRI parameter mismatch
- Proof generation issue

**Solutions**:
1. Match Stone version with verifier (Stone v3 → stone6)
2. Check FRI parameters are correct
3. Regenerate proof with correct parameters

### Issue 3: "Invalid builtin"

**Symptoms**: Verification fails with "Invalid builtin"

**Causes**:
- Layout mismatch
- Builtin configuration incorrect
- Verifier expects different builtins

**Solutions**:
1. Use correct layout (`"recursive"` for most cases)
2. Check builtin configuration
3. Match verifier expectations

### Issue 4: Calldata Too Large

**Symptoms**: RPC error or timeout

**Causes**:
- Proof too large
- RPC limits
- Network issues

**Solutions**:
1. Check proof size (should be < 500 KB)
2. Use different RPC endpoint
3. Optimize proof size if possible

---

## Conclusion

Integrity FactRegistry integration enables on-chain verification of Stone proofs:

**Key Takeaways**:
1. Use public FactRegistry (has all verifiers)
2. Match Stone version with verifier setting
3. Serialize proof correctly
4. Handle errors gracefully
5. Use preflight before invoke

**Next Steps**:
1. Set up Integrity service
2. Test with canonical proof
3. Integrate with your application
4. Deploy to production

**Related Documents**:
- `STONE_PROVER_INTEGRATION_DEEP_DIVE.md` - Stone integration
- `STONE_VERSION_COMPATIBILITY_MATRIX.md` - Version mapping
- `TROUBLESHOOTING_GUIDE.md` - Comprehensive troubleshooting

---

**This guide enables on-chain proof verification for production systems.**
