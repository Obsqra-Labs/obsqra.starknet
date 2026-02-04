# On-Chain zkML Verification

This document explains what makes on-chain zkML verification novel, how the verification gate works, trustless risk assessment, and comparison to off-chain systems.

## What Makes This Novel

### The Innovation

Obsqra is one of the first production systems to enforce zkML verification **on-chain** at the contract level. This means:

1. **No Execution Without Proof:** Contracts verify proofs before executing
2. **Trustless Verification:** No reliance on backend or off-chain services
3. **Cryptographic Enforcement:** Mathematical guarantees, not promises
4. **Public Auditability:** Anyone can verify proofs independently

### Why This Matters

**Traditional Systems:**
- Off-chain AI calculations
- Backend verifies (trust required)
- No on-chain enforcement
- Opaque decision-making

**Obsqra:**
- On-chain proof verification
- Contract-level enforcement
- Trustless verification
- Transparent and verifiable

## On-Chain Proof Verification Gate

### How It Works

**Step 0 in RiskEngine:**
```cairo
// VERIFY PROOFS BEFORE EXECUTION
let proofs_valid = verify_allocation_decision_with_proofs(
    jediswap_metrics,
    ekubo_metrics,
    jediswap_proof_fact,
    ekubo_proof_fact,
    expected_jediswap_score,
    expected_ekubo_score,
    fact_registry_address
);

assert(proofs_valid, 0); // REVERT IF NOT VERIFIED
```

**What This Means:**
- Contract queries SHARP Fact Registry
- Verifies proof fact hash exists
- Validates risk scores match proof
- **Only then** proceeds with execution

### No Execution Without Valid Proof

**Enforcement:**
- Contract-level assertion
- Cannot be bypassed
- Reverts if proof invalid
- Cryptographic guarantee

**Benefits:**
- No trust in backend required
- No off-chain verification needed
- Public and verifiable
- Immutable enforcement

## Trustless Risk Assessment

### What is Trustless?

**Traditional:**
- Trust backend to calculate correctly
- Trust backend to verify proofs
- Trust backend to execute honestly
- No way to verify independently

**Obsqra:**
- Contract verifies on-chain
- Public Fact Registry
- Anyone can verify
- No trust required

### Risk Assessment Process

**1. Deterministic Calculation:**
- Risk formula in Cairo
- Same calculation on-chain and in proof
- Reproducible results
- Verifiable correctness

**2. Proof Generation:**
- STARK proof of calculation
- Cryptographic guarantee
- Public verification
- Immutable record

**3. On-Chain Verification:**
- Contract verifies proof
- Validates scores match
- Enforces correctness
- Trustless execution

## Comparison to Off-Chain Systems

### Off-Chain Systems

**Architecture:**
```
Backend calculates → Backend verifies → Backend executes
```

**Issues:**
- Trust in backend required
- No on-chain verification
- Opaque decision-making
- No cryptographic guarantees

**Examples:**
- Traditional yield optimizers
- Centralized AI systems
- Trust-based automation

### Obsqra (On-Chain Verification)

**Architecture:**
```
Backend generates proof → Fact Registry → Contract verifies → Contract executes
```

**Benefits:**
- No trust in backend
- On-chain verification
- Transparent decisions
- Cryptographic guarantees

**Enforcement:**
- Contract-level gate
- Cannot be bypassed
- Public verification
- Immutable records

## Technical Advantages

### 1. Cryptographic Guarantees

**STARK Proofs:**
- Mathematical proof of correctness
- Cannot be forged
- Publicly verifiable
- Permanent record

### 2. On-Chain Enforcement

**Contract Verification:**
- No execution without proof
- Cannot be bypassed
- Public and transparent
- Immutable

### 3. Trustless Operation

**No Trust Required:**
- Contract verifies
- Public Fact Registry
- Anyone can verify
- Independent validation

### 4. Complete Transparency

**Public Auditability:**
- All proofs public
- All decisions verifiable
- Complete audit trail
- Transparent process

## Use Cases Enabled

### 1. Institutional DeFi

**Requirements:**
- Regulatory compliance
- Audit trails
- Verifiable decisions
- Transparency

**Obsqra Provides:**
- Cryptographic proofs
- On-chain verification
- Complete audit trail
- Public transparency

### 2. DAO Treasury Management

**Requirements:**
- Transparent allocation
- Verifiable decisions
- Governance compliance
- Audit requirements

**Obsqra Provides:**
- On-chain verification
- Public proofs
- Governance integration
- Complete transparency

### 3. Regulatory Compliance

**Requirements:**
- Verifiable AI decisions
- Audit trails
- Transparency
- Accountability

**Obsqra Provides:**
- Cryptographic proofs
- On-chain records
- Public verification
- Immutable audit trail

## Comparison Table

| Feature | Off-Chain Systems | Obsqra (On-Chain) |
|---------|------------------|-------------------|
| **Verification** | Backend only | On-chain contract |
| **Trust Required** | Yes (backend) | No (trustless) |
| **Enforcement** | Backend policy | Contract assertion |
| **Auditability** | Limited | Complete |
| **Transparency** | Opaque | Public |
| **Guarantees** | Promises | Cryptographic |

## Next Steps

- **[Model Provenance](02-model-provenance.md)** - Version tracking
- **[Transparency Dashboard](03-transparency-dashboard.md)** - UX transparency
- **[Architecture: On-Chain Verification](../03-architecture/05-on-chain-verification.md)** - Technical details

---

**Key Takeaway:** On-chain zkML verification provides trustless, cryptographically enforced verification that cannot be bypassed, enabling institutional adoption and regulatory compliance.
