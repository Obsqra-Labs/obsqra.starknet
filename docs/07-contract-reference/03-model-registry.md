# ModelRegistry Contract Reference

Complete reference for the ModelRegistry contract, including address, interface, model registration, version querying, and events.

## Contract Address

**Sepolia Testnet:**
```
0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc
```

**Explorer:**
- Starkscan: https://sepolia.starkscan.co/contract/0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc

## Interface Definition

```cairo
#[starknet::interface]
trait IModelRegistry<TContractState> {
    fn register_model_version(
        ref self: TContractState,
        version: felt252,
        model_hash: felt252,
        description: ByteArray
    ) -> ModelVersion;
    
    fn get_current_model(self: @TContractState) -> ModelVersion;
    fn get_model_version(self: @TContractState, version: felt252) -> Option<ModelVersion>;
    fn get_model_history(self: @TContractState) -> Span<felt252>;
}
```

## Key Functions

### register_model_version

Registers a new model version (owner only).

**Parameters:**
- `version`: Version number as felt252 (semantic version encoded)
- `model_hash`: SHA-256 hash of model code (as felt252)
- `description`: Human-readable description

**Returns:**
- `ModelVersion`: Registered model version

**Access Control:** Owner only

**Process:**
1. Verify caller is owner
2. Store model version
3. Update current version
4. Add to version history
5. Emit `ModelRegistered` event

### get_current_model

Retrieves the current active model version.

**Returns:**
- `ModelVersion`: Current model or empty if none registered

**Public Query:** Anyone can call

### get_model_version

Retrieves a specific model version.

**Parameters:**
- `version`: Version number as felt252

**Returns:**
- `Option<ModelVersion>`: Model version or None if not found

**Public Query:** Anyone can call

### get_model_history

Retrieves all version numbers in chronological order.

**Returns:**
- `Span<felt252>`: Array of version numbers

**Public Query:** Anyone can call

## ModelVersion Structure

```cairo
struct ModelVersion {
    version: felt252,        // Semantic version as felt252
    model_hash: felt252,      // SHA-256 hash of model code
    deployed_at: u64,        // Block timestamp
    description: ByteArray,   // Human-readable description
    is_active: bool,         // Current active version
}
```

## Events

### ModelRegistered

Emitted when a new model version is registered.

```cairo
event ModelRegistered {
    version: felt252,
    model_hash: felt252
}
```

## Storage Layout

```cairo
struct Storage {
    owner: ContractAddress,
    current_version: felt252,
    model_versions: Map<felt252, ModelVersion>,
    version_count: felt252,
    versions_by_index: Map<felt252, felt252>,  // index -> version
}
```

## Version Encoding

### Semantic Version to Felt252

**Format:** `MAJOR.MINOR.PATCH`

**Encoding:**
```
(major << 16) + (minor << 8) + patch
```

**Examples:**
- `1.0.0` → `0x010000` (65536)
- `1.1.0` → `0x010100` (65792)
- `2.0.0` → `0x020000` (131072)

## Usage Examples

### Register Model Version

```python
from starknet_py.contract import Contract

contract = await Contract.from_address(
    address=model_registry_address,
    provider=provider
)

# Version 1.0.0 = 0x010000
version = 0x010000
model_hash = 0x06ab2595...  # SHA-256 hash as felt252
description = "Initial risk scoring model"

result = await contract.functions["register_model_version"].invoke(
    version=version,
    model_hash=model_hash,
    description=description,
    max_fee=max_fee
)
```

### Get Current Model

```python
current_model = await contract.functions["get_current_model"].call()
print(f"Version: {current_model.version}")
print(f"Hash: {hex(current_model.model_hash)}")
```

### Get Model History

```python
history = await contract.functions["get_model_history"].call()
for version in history:
    model = await contract.functions["get_model_version"].call(version)
    print(f"Version {version}: {model.description}")
```

## Access Control

**Owner Functions:**
- `register_model_version()`: Only owner can register

**Public Functions:**
- `get_current_model()`: Public query
- `get_model_version()`: Public query
- `get_model_history()`: Public query

## Next Steps

- **[DAO Constraint Manager](04-dao-constraint-manager.md)** - Governance contract
- **[Fact Registry](05-fact-registry.md)** - Proof verification contract
- **[Architecture: Smart Contracts](../03-architecture/02-smart-contracts.md)** - Contract architecture

---

**ModelRegistry Summary:** On-chain model provenance tracking with version management, hash commitments, and complete upgrade history.
