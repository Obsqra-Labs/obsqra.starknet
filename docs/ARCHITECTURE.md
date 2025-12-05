# Obsqra.starknet Architecture

**Version:** 1.0  
**Date:** December 2025

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  • Simplified dashboard                                  │
│  • MIST.cash integration                                 │
│  • Contract interactions                                 │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              MIST.cash Privacy Layer                    │
│  • Deposit/Withdraw with ZK proofs                      │
│  • Amount correlation mitigation                        │
│  • Privacy pool contracts                               │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          Cairo Contracts (On-Chain AI)                  │
│  • RiskEngine.cairo (risk scoring)                      │
│  • StrategyRouter.cairo (allocation routing)            │
│  • DAOConstraintManager.cairo (governance)              │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              SHARP (Automatic Proving)                   │
│  • Proves all Cairo computations                        │
│  • Batches transactions                                 │
│  • Cost amortized                                       │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│         Off-Chain Service (Python)                      │
│  • Monitors protocols                                    │
│  • Fetches data                                         │
│  • Triggers rebalances                                  │
└─────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Frontend (Next.js)

- **Purpose:** User interface for interacting with the protocol
- **Technologies:** Next.js 14, React 18, TypeScript
- **Key Features:**
  - Dashboard showing pool state
  - Deposit/withdraw flows
  - AI decision history
  - Allocation visualization

### MIST.cash Privacy Layer

- **Purpose:** Provide privacy for deposits and withdrawals
- **Integration:** MIST.cash SDK
- **Key Features:**
  - Deposit with ZK commitments
  - Withdraw to fresh addresses
  - Amount correlation mitigation
  - Unlinkable transactions

### Cairo Contracts

#### RiskEngine.cairo

- **Purpose:** On-chain risk scoring and allocation calculation
- **Key Functions:**
  - `calculate_risk_score()` - Multi-factor risk calculation
  - `calculate_allocation()` - Risk-adjusted allocation
  - `verify_constraints()` - Constraint compliance

#### StrategyRouter.cairo

- **Purpose:** Multi-protocol routing and rebalancing
- **Key Functions:**
  - `update_allocation()` - Update protocol allocations
  - `get_allocation()` - Get current allocations
  - `accrue_yields()` - Track yields

#### DAOConstraintManager.cairo

- **Purpose:** Governance constraints and validation
- **Key Functions:**
  - `set_constraints()` - Set governance rules
  - `validate_allocation()` - Validate allocations
  - `get_constraints()` - Get current constraints

### SHARP (Shared Prover)

- **Purpose:** Automatic proving of Cairo computations
- **Key Features:**
  - Batches transactions
  - Amortizes proving costs
  - No validator network needed
  - Cost: <$0.01 per computation

### Off-Chain Service (Python)

- **Purpose:** Monitor protocols and trigger rebalances
- **Technologies:** FastAPI, Web3.py
- **Key Features:**
  - Protocol monitoring
  - Data fetching
  - Rebalance triggers
  - Health checks

## Data Flow

1. User deposits via MIST.cash (private)
2. Off-chain service monitors protocols
3. Service calls Cairo contract with data
4. Cairo contract computes:
   - Risk scores (on-chain)
   - Allocation (on-chain)
   - Constraint verification (on-chain)
5. SHARP automatically proves computations
6. If constraints met: Execute allocation
7. User withdraws via MIST.cash (unlinkable)

## Integration Points

- **MIST.cash SDK:** Privacy layer integration
- **Starknet DeFi Protocols:** Ekubo, zkLend, Nostra
- **SHARP:** Automatic proving (no action needed)
- **Starknet RPC:** Network connectivity

## Security Considerations

- All AI logic in Cairo contracts (auditable)
- SHARP proves correctness (cryptographic guarantee)
- MIST.cash handles privacy (battle-tested)
- Constraints on-chain (governance enforced)

