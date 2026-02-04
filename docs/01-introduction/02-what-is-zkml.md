# What is Zero-Knowledge Machine Learning (zkML)?

## Introduction

Zero-Knowledge Machine Learning (zkML) is the application of zero-knowledge proofs to machine learning computations, enabling cryptographic verification that ML model inferences were executed correctly without revealing the model's internal weights or the computation process.

## Why zkML for DeFi Risk Management?

### The Problem: Black-Box AI

Traditional DeFi yield optimizers face a fundamental trust problem:

1. **Off-Chain Computation**: AI models run on centralized servers
2. **No Verification**: Users cannot verify that calculations were correct
3. **Trust Required**: Users must trust the operator's honesty
4. **No Audit Trail**: Decisions are opaque and unverifiable

**Example Scenario:**
- A yield optimizer claims to allocate 60% to Protocol A and 40% to Protocol B
- The user has no way to verify this actually happened
- If funds are lost, there's no cryptographic proof of what went wrong

### The Solution: Verifiable AI

zkML solves this by:

1. **Cryptographic Proofs**: Every calculation generates a STARK proof
2. **Public Verification**: Anyone can verify proofs independently
3. **On-Chain Enforcement**: Contracts verify proofs before execution
4. **Complete Transparency**: All decisions are cryptographically auditable

**With zkML:**
- The system generates a STARK proof that risk scores were calculated correctly
- The proof is verified on-chain before any allocation executes
- Users can independently verify proofs using public tools
- Complete audit trail is cryptographically secured

## Trust and Transparency Benefits

### 1. **Trustless Verification**

Traditional systems require trust in:
- The operator's honesty
- The server's integrity
- The code's correctness (without verification)

zkML eliminates trust by:
- Cryptographic proofs that anyone can verify
- On-chain verification that cannot be bypassed
- Public audit trail of all decisions

### 2. **Regulatory Compliance**

For institutions and DAOs:
- **Audit Trail**: Every decision has a cryptographic proof
- **Transparency**: All calculations are verifiable
- **Compliance**: Meets regulatory requirements for transparency
- **Accountability**: Decisions are cryptographically bound to inputs

### 3. **Security**

- **Tamper-Proof**: Proofs cannot be forged
- **Immutable**: Once verified, proofs are permanent
- **Verifiable**: Anyone can check proof validity
- **Transparent**: All inputs and outputs are public

## Proof Generation and Verification Overview

### STARK Proofs

**What are STARK Proofs?**
- Scalable Transparent Arguments of Knowledge
- Cryptographic proofs that computation was executed correctly
- No trusted setup required
- Fast verification (milliseconds)

**Key Properties:**
- **Completeness**: Valid proofs always verify
- **Soundness**: Invalid proofs cannot verify
- **Zero-Knowledge**: Proofs don't reveal computation details (optional)
- **Transparency**: No trusted setup

### Proof Generation Process

```
1. Input Data (Protocol Metrics)
        ↓
2. Model Execution (Risk Calculation)
        ↓
3. Trace Generation (Cairo Execution Trace)
        ↓
4. Proof Generation (Stone Prover / LuminAIR)
        ↓
5. STARK Proof (Cryptographic Proof)
        ↓
6. Verification (On-Chain / Off-Chain)
```

### Verification Process

**On-Chain Verification:**
1. Contract receives proof fact hash
2. Queries SHARP Fact Registry
3. Verifies proof exists and is valid
4. Only then executes allocation

**Off-Chain Verification:**
1. Download proof from API
2. Use verifier tool (local or online)
3. Verify proof against public inputs
4. Confirm calculation correctness

### Fact Registry (SHARP)

**What is SHARP?**
- Shared Prover for Starknet
- Public registry of verified computations
- On-chain fact registry contract
- Immutable proof records

**How It Works:**
1. Proof is submitted to SHARP
2. SHARP verifies the proof
3. Fact hash is registered on-chain
4. Contracts can query fact registry
5. Execution only proceeds if fact exists

## Obsqra's zkML Implementation

### Current Status: 4/5 zkML Maturity (On-Chain Verification Gate Complete)

**✅ Level 1: Proof Generation**
- Stone prover integration (local, free)
- LuminAIR integration (alternative)
- 100% success rate (100/100 allocations)

**✅ Level 2: Deterministic Model**
- Risk scoring model in Cairo
- Deterministic calculations
- Reproducible results

**✅ Level 3: Backend Orchestration**
- Proof job tracking
- Verification status management
- Database integration

**✅ Level 4: On-Chain Verification Gate** ✅ **COMPLETE**
- Contract-level proof verification (RiskEngine v4 STEP 0)
- Integrity FactRegistry integration
- No execution without valid proof
- Cryptographic enforcement at contract level
- StrategyRouter authorization complete

**⏳ Level 5: Model Provenance & UX** (In Progress)
- Model registry infrastructure exists
- Version tracking (partial)
- Transparency dashboard (partial)
- Complete audit trail (partial)
- **Note**: Model upgradeability and full provenance tracking still needed for 5/5

### Proof Generation Pipeline

**Stone Prover (Primary):**
- Local proof generation
- 2-4 second generation time
- $0 cost (local execution)
- 100% success rate

**LuminAIR (Alternative):**
- Rust-based prover
- Similar performance
- Fallback option

### Verification Architecture

**Backend Verification:**
- Integrity service (Herodotus)
- Fact hash registration
- Status tracking

**On-Chain Verification:**
- RiskEngine contract verifies proofs
- FactRegistry query
- Assertion before execution

## Comparison: Traditional vs zkML

| Aspect | Traditional | zkML (Obsqra) |
|--------|------------|---------------|
| **Verification** | Trust-based | Cryptographic proof |
| **Transparency** | Opaque | Fully transparent |
| **Audit Trail** | Logs (can be modified) | Immutable proofs |
| **User Trust** | Required | Not required |
| **Compliance** | Difficult | Built-in |
| **Security** | Server-dependent | Cryptographically secure |

## Use Cases

### 1. **Institutional DeFi**
- Treasury management with verifiable decisions
- Regulatory compliance
- Audit requirements

### 2. **DAO Governance**
- Transparent allocation decisions
- Verifiable constraint enforcement
- Complete audit trail

### 3. **Individual Users**
- Trustless yield optimization
- Verifiable AI decisions
- Privacy + transparency

### 4. **Developers**
- Building on verifiable AI infrastructure
- Integrating zkML into applications
- Research and development

## Next Steps

- **[System Architecture Overview](03-system-architecture-overview.md)** - See how zkML is integrated
- **[On-Chain Verification](../04-novel-features/01-on-chain-zkml-verification.md)** - Deep dive into verification
- **[Getting Started](../02-user-guides/01-getting-started.md)** - Try it yourself

---

**Key Takeaway:** zkML transforms "trust me" into "verify it yourself" - enabling trustless, transparent, and verifiable AI in DeFi.
