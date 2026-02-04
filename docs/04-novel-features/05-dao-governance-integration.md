# DAO Governance Integration

This document explains DAO constraint enforcement, on-chain governance parameters, constraint validation, and governance upgrade path.

## DAO Constraint Enforcement

### Overview

DAO constraints are governance parameters that define limits and rules for allocation decisions. These constraints are:

- **Stored On-Chain:** In DAOConstraintManager contract
- **Enforced On-Chain:** In RiskEngine contract
- **Verifiable:** Part of proof generation
- **Upgradeable:** DAO can update via governance

### Constraint Types

**1. Allocation Limits:**
- `max_single_protocol`: Maximum allocation per protocol (e.g., 70%)
- `min_diversification`: Minimum spread requirement (e.g., 30%)

**2. Risk Limits:**
- `max_volatility`: Maximum volatility threshold
- `min_liquidity`: Minimum liquidity requirement

**3. Protocol Constraints:**
- Minimum audit score
- Maximum utilization
- Age requirements

### Enforcement

**In RiskEngine:**
```cairo
// Verify constraints before execution
let constraints_valid = verify_constraints(
    jediswap_pct,
    ekubo_pct,
    max_single,
    min_diversification
);

assert(constraints_valid, 3); // Revert if violated
```

## On-Chain Governance Parameters

### DAOConstraintManager Contract

**Purpose:** Store and manage governance parameters on-chain.

**Key Functions:**
- `get_max_single() -> felt252`
- `get_min_diversification() -> felt252`
- `get_max_volatility() -> felt252`
- `get_min_liquidity() -> felt252`
- `update_constraints(...)` (owner only)

### Parameter Storage

**On-Chain Storage:**
```cairo
struct Storage {
    owner: ContractAddress,
    max_single: felt252,           // e.g., 7000 (70%)
    min_diversification: felt252,  // e.g., 3000 (30%)
    max_volatility: felt252,       // e.g., 5000 (50%)
    min_liquidity: felt252,        // e.g., 1
}
```

### Parameter Access

**Public Queries:**
- Anyone can read constraints
- Transparent governance
- Verifiable parameters
- No hidden rules

**Updates:**
- Owner-only (can be DAO)
- Transparent changes
- Event emission
- Audit trail

## Constraint Validation

### Validation Process

**Step 1: Read Constraints**
```cairo
let dao_manager = IDAOConstraintManagerDispatcher {
    contract_address: self.dao_manager.read()
};

let max_single = dao_manager.get_max_single();
let min_diversification = dao_manager.get_min_diversification();
```

**Step 2: Validate Allocation**
```cairo
// Check max single protocol
assert(jediswap_pct <= max_single, 1);
assert(ekubo_pct <= max_single, 2);

// Check min diversification
let total = jediswap_pct + ekubo_pct;
assert(total == 10000, 3); // Must sum to 100%
// Diversification is implicit if both are below max_single
```

**Step 3: Validate Risk Metrics**
```cairo
// Check volatility limits
assert(jediswap_metrics.volatility <= max_volatility, 4);
assert(ekubo_metrics.volatility <= max_volatility, 5);

// Check liquidity requirements
assert(jediswap_metrics.liquidity >= min_liquidity, 6);
assert(ekubo_metrics.liquidity >= min_liquidity, 7);
```

### Validation in Proofs

**Proof Generation:**
- Constraints are public inputs
- Proof verifies constraint compliance
- Cryptographic guarantee
- Immutable record

**On-Chain Verification:**
- Contract validates constraints
- Must match proof
- Double verification
- Trustless enforcement

## Governance Upgrade Path

### Current Governance

**Owner-Controlled:**
- Single owner address
- Direct parameter updates
- Immediate effect
- Simple but centralized

### DAO Governance (Future)

**Multi-Signature:**
- DAO multisig wallet
- Governance proposals
- Voting mechanism
- Timelock for changes

**Upgrade Process:**
1. **Proposal:**
   - DAO member proposes constraint change
   - Community discussion
   - Formal proposal

2. **Voting:**
   - DAO members vote
   - Quorum requirement
   - Majority approval

3. **Execution:**
   - Timelock period
   - Automatic execution
   - Parameter update
   - Event emission

### Governance Contracts

**Future Integration:**
- DAO governance contract
- Voting mechanism
- Proposal system
- Timelock execution

## Constraint Examples

### Conservative Strategy

**Constraints:**
- `max_single_protocol`: 60% (diversified)
- `min_diversification`: 40% (spread)
- `max_volatility`: 40% (low risk)
- `min_liquidity`: 2 (high liquidity)

**Result:**
- Balanced allocations
- Lower risk exposure
- Higher liquidity requirements

### Aggressive Strategy

**Constraints:**
- `max_single_protocol`: 80% (concentrated)
- `min_diversification`: 20% (focused)
- `max_volatility`: 60% (higher risk)
- `min_liquidity`: 1 (standard)

**Result:**
- Concentrated allocations
- Higher risk tolerance
- Standard liquidity

## Integration Points

### RiskEngine Integration

**Constraint Reading:**
- Queries DAOConstraintManager
- Reads current constraints
- Validates allocations
- Enforces rules

### Proof Generation

**Constraint Inclusion:**
- Constraints in public inputs
- Proof verifies compliance
- Cryptographic guarantee
- Immutable record

### Frontend Integration

**Constraint Display:**
- Show current constraints
- Display constraint limits
- Visual indicators
- Update notifications

## Security Considerations

### Constraint Validation

**On-Chain Enforcement:**
- Contract validates
- Cannot be bypassed
- Public verification
- Immutable rules

### Upgrade Security

**Access Control:**
- Owner-only updates
- Can be DAO-controlled
- Transparent process
- Audit trail

### Attack Prevention

**Invalid Constraints:**
- Validation on update
- Range checks
- Logic verification
- Event emission

## Best Practices

### Constraint Design

1. **Clear Limits:**
   - Well-defined ranges
   - Reasonable defaults
   - Documented rationale

2. **Gradual Changes:**
   - Incremental updates
   - Community input
   - Testing period
   - Monitoring

3. **Transparency:**
   - Public parameters
   - Change notifications
   - Governance records
   - Audit trail

## Next Steps

- **[Smart Contracts: DAOConstraintManager](../03-architecture/02-smart-contracts.md)** - Contract details
- **[Contract Reference: DAO Constraint Manager](../07-contract-reference/04-dao-constraint-manager.md)** - Interface reference
- **[User Guide: DAO Governance](../02-user-guides/02-executing-allocations.md)** - User instructions

---

**DAO Governance Integration Summary:** On-chain constraint storage and enforcement with transparent governance parameters, upgradeable via DAO, and cryptographically verified in proofs.
