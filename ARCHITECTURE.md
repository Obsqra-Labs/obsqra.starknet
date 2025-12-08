# System Architecture

## Overview

Obsqura implements a three-layer architecture for autonomous yield optimization with verifiable AI decision-making on Starknet.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend Layer                        │
│  ┌─────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Governance │  │   Dashboard    │  │ Audit Trail  │  │
│  │     UI      │  │   Components   │  │    Viewer    │  │
│  └─────────────┘  └────────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    Backend Layer (FastAPI)                │
│  ┌────────────────────────────────────────────────────┐  │
│  │          Orchestration Service                     │  │
│  │  - Protocol metrics aggregation                    │  │
│  │  - Autonomous transaction signing                  │  │
│  │  - Decision execution coordination                 │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│              Smart Contract Layer (Starknet)              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  RiskEngine  │  │  Strategy    │  │      DAO      │  │
│  │   Contract   │──│   RouterV2   │  │  Constraints  │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│         │                  │                             │
│         └──────────────────┴─────────────────────────────┤
│                           ▼                               │
│                   Protocol Integrations                   │
│              (JediSwap, Ekubo, Future...)                │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Smart Contract Layer

#### RiskEngine Contract

**Purpose**: Core risk assessment and allocation decision engine

**Key Functions**:
- `calculate_risk_score(metrics: ProtocolMetrics) -> felt252`
  - Computes risk score (5-95 scale) based on protocol metrics
  - Factors: utilization, volatility, liquidity, audit score, protocol age

- `calculate_allocation(risks, apys) -> (felt252, felt252, felt252)`
  - Determines optimal allocation percentages across protocols
  - Risk-adjusted optimization considering APY and safety

- `propose_and_execute_allocation(jediswap_metrics, ekubo_metrics) -> AllocationDecision`
  - Full orchestration flow
  - Validates against DAO constraints
  - Executes allocation via StrategyRouter
  - Emits comprehensive audit trail

**Storage**:
- Decision counter and history
- Latest allocation decision
- Performance snapshots
- Protocol APY cache

#### StrategyRouterV2 Contract

**Purpose**: Fund management and rebalancing execution

**Key Functions**:
- `deposit(amount: felt252)`
  - User deposits STRK tokens
  - Allocates to protocols based on current strategy

- `withdraw(amount: felt252)`
  - User withdraws funds plus accrued yield
  - Proportional withdrawal from all protocols

- `update_allocation(jediswap_pct, ekubo_pct)`
  - Restricted to RiskEngine contract only
  - Rebalances funds across protocols
  - Links to decision ID for audit trail

**Storage**:
- Total deposited amount
- Current allocation percentages
- User deposit tracking
- Performance metrics per decision

#### DAOConstraintManager Contract

**Purpose**: Governance parameter storage and validation

**Constraints**:
- Allocation bounds (min/max per protocol)
- Risk score limits
- Volatility difference thresholds
- Liquidity requirements

**Access Control**:
- Owner can update constraints
- RiskEngine reads for validation
- Transparent parameter history

### 2. Backend Service Layer

#### Orchestration API

**Technology**: Python 3.11+ with FastAPI framework

**Core Responsibilities**:
1. **Protocol Metrics Aggregation**
   - Fetches real-time data from DeFi protocols
   - Computes utilization, volatility, liquidity metrics
   - Maintains protocol audit score database

2. **Transaction Signing**
   - Autonomous signing using backend wallet
   - Implements account abstraction via starknet.py
   - Secure private key management

3. **Decision Coordination**
   - Receives allocation requests from frontend
   - Validates input parameters
   - Submits transactions to RiskEngine
   - Returns decision data with proof hashes

**API Endpoints**:

```
POST /api/v1/risk-engine/calculate-risk
POST /api/v1/risk-engine/calculate-allocation
POST /api/v1/risk-engine/orchestrate-allocation
```

**Security**:
- Environment-based configuration
- Rate limiting (planned)
- Request validation via Pydantic
- CORS policy enforcement

### 3. Frontend Application

#### Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Starknet Integration**: @starknet-react/core

#### Key Components

**ConstraintBuilder**
- DAO governance interface
- Slider-based constraint configuration
- Real-time validation
- On-chain submission (via backend)

**AIProposalDisplay**
- Visualization of AI allocation reasoning
- Expected performance metrics
- Cryptographic proof display
- Execution trigger interface

**AIDecisionAuditTrail**
- Historical decision browser
- On-chain data fetching
- Decision detail modal
- Performance tracking linkage

**Dashboard**
- Portfolio overview
- Deposit/withdraw interface
- Real-time APY display
- Transaction history

## Data Flow

### Allocation Decision Flow

1. **Trigger**: User clicks "Orchestrate Allocation" in frontend
2. **Request**: Frontend sends protocol metrics to backend API
3. **Validation**: Backend validates metrics via Pydantic
4. **Serialization**: Backend converts Python dicts to Cairo calldata
5. **Signing**: Backend signs transaction with orchestrator wallet
6. **Execution**: Transaction submitted to Starknet
7. **Contract Logic**:
   - RiskEngine calculates risk scores
   - Computes optimal allocation
   - Validates against DAO constraints
   - Calls StrategyRouter.update_allocation
   - Emits audit events
8. **Response**: Backend fetches resulting decision from contract
9. **Display**: Frontend shows decision details and proof

### User Deposit Flow

1. **User Action**: Enters amount and approves STRK token
2. **Frontend**: Calls StrategyRouterV2.deposit
3. **Contract**: Receives STRK, updates user balance
4. **Allocation**: Deposits to protocols based on current allocation
5. **Confirmation**: User receives shares representing deposit

### Withdrawal Flow

1. **User Action**: Requests withdrawal amount
2. **Frontend**: Calls StrategyRouterV2.withdraw
3. **Contract**: Calculates proportional amounts from each protocol
4. **Execution**: Withdraws from JediSwap and Ekubo
5. **Transfer**: Returns STRK + yield to user

## Security Architecture

### Access Control

**Contract Level**:
- RiskEngine owner: Can update strategy router reference
- StrategyRouter owner: Can update protocol addresses
- DAOConstraintManager owner: Can update constraints
- Only RiskEngine can call StrategyRouter.update_allocation

**Backend Level**:
- Orchestrator wallet: Authorized to call RiskEngine
- Environment-based secrets management
- No direct user fund access

### Validation Layers

1. **Frontend**: Input validation, user authorization
2. **Backend**: Pydantic models, business logic validation
3. **Contract**: DAO constraint enforcement, access control

### Audit Trail

All decisions recorded on-chain with:
- Decision ID (sequential)
- Block number and timestamp
- Input metrics and calculated risks
- Allocation percentages and APYs
- Rationale hash (future: zkML proof)
- Strategy router transaction hash

## Scalability Considerations

### Current Limitations

- Two protocol support (JediSwap, Ekubo)
- Sepolia testnet deployment
- Centralized backend orchestration

### Planned Improvements

1. **Multi-Protocol Support**
   - Generic protocol adapter interface
   - Dynamic protocol addition via governance
   - Cross-protocol arbitrage strategies

2. **Decentralized Orchestration**
   - Keeper network for autonomous execution
   - Multi-signature authorization
   - Decentralized metric aggregation

3. **zkML Integration**
   - On-chain ML model inference
   - Cairo-based computation proofs
   - SHARP-verified decisions

## Monitoring and Observability

### Contract Events

```cairo
AllocationProposed
AllocationExecuted
ConstraintsValidated
PerformanceRecorded
DecisionRationale
```

### Backend Metrics

- Request count and latency
- Transaction success rate
- RPC endpoint health
- Wallet balance monitoring

### Frontend Analytics

- User engagement metrics
- Transaction completion rates
- Error tracking
- Performance monitoring

## Disaster Recovery

### Contract Upgrade Path

- Proxy pattern implementation (planned)
- Migration scripts for state transfer
- Backward compatibility considerations

### Backend Redundancy

- Multiple RPC endpoints
- Automatic failover
- Health check monitoring
- State backup procedures

### Frontend Deployment

- Static asset CDN
- Multiple region deployment
- Rollback capability
- Feature flags for gradual rollouts

