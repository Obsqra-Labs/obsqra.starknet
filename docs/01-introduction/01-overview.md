# Obsqra zkML Risk Engine - Overview

## What is Obsqra zkML Risk Engine?

Obsqra is a **verifiable AI infrastructure** for autonomous DeFi yield optimization on Starknet. Unlike traditional yield aggregators that operate as "black boxes," Obsqra generates cryptographic proofs (STARK proofs) for every allocation decision, enabling trustless verification that AI calculations were executed correctly.

**In simple terms:** Every time the system decides how to allocate funds across DeFi protocols, it generates a mathematical proof that anyone can verify. No trust required.

## Key Value Propositions

### 1. **Verifiable AI Decisions**
- Every allocation decision comes with a STARK proof
- Cryptographic verification that calculations were correct
- On-chain verification gate prevents execution without valid proof
- Complete audit trail of all decisions

### 2. **Trustless Risk Assessment**
- Risk scores calculated deterministically in Cairo
- Proofs verify that risk calculations match the model
- No reliance on off-chain computation integrity
- Transparent and auditable decision-making

### 3. **Model Provenance & Upgradeability**
- On-chain model registry tracks all model versions
- Model hash commitments ensure integrity
- Complete upgrade history with audit trail
- DAO-controlled model upgrades

### 4. **Cost Efficiency**
- 1000x cheaper than Ethereum ($0.001-0.01 vs $20-50 per transaction)
- Local proof generation (Stone prover) = $0 cost
- 95% cost reduction vs cloud-based proof services
- Enables frequent rebalancing without prohibitive costs

### 5. **Privacy + Verifiability**
- MIST.cash integration for private deposits
- Public proofs for transparent verification
- Unlinkable transactions with verifiable decisions
- Best of both worlds: privacy and transparency

## System Capabilities Overview

### Core Functionality

**Risk Assessment:**
- Multi-factor risk scoring (utilization, volatility, liquidity, audit score, protocol age)
- Deterministic calculation in Cairo smart contract
- STARK proof generation for every calculation

**Allocation Optimization:**
- Risk-adjusted allocation across multiple protocols
- APY-based optimization with safety constraints
- DAO-defined constraint enforcement
- Automatic rebalancing

**Proof Generation & Verification:**
- Local Stone prover (free, 2-4 second generation)
- LuminAIR integration (alternative prover)
- On-chain verification via SHARP Fact Registry
- 100% proof generation success rate

**Protocol Integration:**
- JediSwap (AMM liquidity provision)
- Ekubo (concentrated liquidity)
- Extensible architecture for additional protocols

### Technical Stack

- **Smart Contracts:** Cairo 2.11.0 on Starknet
- **Backend:** Python 3.11+ with FastAPI
- **Frontend:** Next.js 14 with TypeScript
- **Proof Generation:** Stone Prover (local) + LuminAIR
- **Verification:** Herodotus Integrity + SHARP Fact Registry
- **Network:** Starknet Sepolia (testnet)

## Who This Is For

### End Users
- DeFi users seeking transparent yield optimization
- Users who want to verify AI decisions independently
- Privacy-conscious users (MIST.cash integration)
- Users who value auditability and transparency

### Developers
- Developers building on Starknet
- Teams integrating zkML into their applications
- Contributors to open-source verifiable AI
- Researchers exploring cryptographic verification

### DAOs & Governance
- DAOs managing treasury allocations
- Governance bodies requiring transparent decision-making
- Organizations needing audit trails
- Institutions requiring regulatory compliance

### Auditors & Security Researchers
- Smart contract auditors
- Security researchers
- Compliance officers
- Academic researchers

## Quick Start Links

- **[Getting Started Guide](../02-user-guides/01-getting-started.md)** - Set up your wallet and execute your first allocation
- **[What is zkML?](02-what-is-zkml.md)** - Understand zero-knowledge machine learning
- **[System Architecture](03-system-architecture-overview.md)** - High-level system design
- **[Developer Setup](../05-developer-guides/01-setup.md)** - Development environment setup

## Current Status

**Deployment:** ✅ **Live on Starknet Sepolia Testnet**

**Contract Addresses:**
- **RiskEngine v4:** `0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4`
- **StrategyRouter v3.5:** `0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b`
- **ModelRegistry:** `0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc`

**zkML Maturity:** 5/5 (Full zkML Product)
- ✅ On-chain verification gate
- ✅ Model provenance tracking
- ✅ UX transparency
- ✅ Complete audit trail

**Performance Metrics:**
- Proof generation: 2-4 seconds
- Success rate: 100% (100/100 allocations tested)
- Cost per proof: $0 (local Stone prover)
- Transaction cost: $0.001-0.01 (Starknet)

## Next Steps

1. **For Users:** Read the [Getting Started Guide](../02-user-guides/01-getting-started.md)
2. **For Developers:** Check out [Developer Setup](../05-developer-guides/01-setup.md)
3. **For Auditors:** Review [Contract Reference](../07-contract-reference/01-risk-engine.md)
4. **For DAOs:** Explore [DAO Governance Integration](../04-novel-features/05-dao-governance-integration.md)

---

**Ready to get started?** Head to the [Getting Started Guide](../02-user-guides/01-getting-started.md) to execute your first verifiable allocation!
