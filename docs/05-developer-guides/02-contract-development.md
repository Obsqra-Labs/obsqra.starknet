# Contract Development Guide

This guide covers Cairo contract structure, compiling contracts, testing contracts, deployment process, and contract upgrade patterns.

## Cairo Contract Structure

### Basic Structure

```cairo
#[starknet::contract]
mod ContractName {
    use starknet::ContractAddress;
    
    #[storage]
    struct Storage {
        owner: ContractAddress,
        // ... other storage
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        // ... events
    }
    
    #[constructor]
    fn constructor(ref self: ContractState, owner: ContractAddress) {
        // ... initialization
    }
    
    #[abi(embed_v0)]
    impl ContractImpl of super::IContract<ContractState> {
        // ... functions
    }
}
```

### Key Components

**1. Storage:**
- State variables
- Maps for key-value storage
- Persistent on-chain data

**2. Events:**
- Emitted on state changes
- Indexed for querying
- Public audit trail

**3. Functions:**
- Public: Anyone can call
- View: Read-only queries
- External: Contract interactions

## Compiling Contracts

### Using Scarb

**Build:**
```bash
cd contracts
scarb build
```

**Output:**
- `target/dev/`: Development build
- `target/release/`: Release build
- Sierra JSON files
- CASM files

### Build Options

**Release Build:**
```bash
scarb build --release
```

**Check Only:**
```bash
scarb check
```

**Format:**
```bash
scarb fmt
```

## Testing Contracts

### Unit Tests

**Test Structure:**
```cairo
#[cfg(test)]
mod tests {
    use super::Contract;
    
    #[test]
    fn test_function() {
        // Test logic
    }
}
```

**Run Tests:**
```bash
scarb test
```

### Integration Tests

**Using starknet.py:**
```python
import pytest
from starknet_py.contract import Contract

@pytest.mark.asyncio
async def test_contract_function():
    contract = await Contract.from_address(...)
    result = await contract.functions["function_name"].call(...)
    assert result == expected
```

## Deployment Process

### Step 1: Declare

```bash
sncast declare \
  --contract-name ContractName \
  --network sepolia \
  --account <account>
```

### Step 2: Deploy

```bash
sncast deploy \
  --class-hash <class_hash> \
  --constructor-calldata <args> \
  --network sepolia \
  --account <account>
```

### Step 3: Verify

```bash
# Check on explorer
# Test functions
sncast call --contract-address <address> --function <function>
```

## Contract Upgrade Patterns

### Current Pattern

**No Upgrade Mechanism:**
- Contracts are immutable
- New versions require new deployment
- State migration needed

### Future Patterns

**Proxy Pattern (Planned):**
- Upgradeable logic
- Immutable storage
- Version management

**Migration Pattern:**
- Export state
- Deploy new contract
- Import state
- Update references

## Best Practices

### Security

1. **Access Control:**
   - Owner-only functions
   - Role-based access
   - Input validation

2. **Reentrancy:**
   - Use checks-effects-interactions
   - Avoid external calls in loops
   - Validate state changes

3. **Integer Overflow:**
   - Use safe math
   - Validate ranges
   - Check bounds

### Gas Optimization

1. **Storage:**
   - Minimize storage writes
   - Use packed structs
   - Cache reads

2. **Computation:**
   - Optimize loops
   - Cache calculations
   - Minimize external calls

### Code Quality

1. **Documentation:**
   - Comment complex logic
   - Document functions
   - Explain storage layout

2. **Testing:**
   - Unit tests for all functions
   - Integration tests
   - Edge case coverage

## Next Steps

- **[Backend Development](03-backend-development.md)** - Python service development
- **[Frontend Development](04-frontend-development.md)** - Next.js component development
- **[Integrating New Provers](05-integrating-new-provers.md)** - Prover integration

---

**Contract Development Summary:** Complete guide for Cairo contract development with testing, deployment, and best practices.
