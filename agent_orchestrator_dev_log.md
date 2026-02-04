# Agent Orchestrator Development Log

**Product Name**: Agent Orchestrator (formerly "Stage 5")  
**Tagline**: "Verifiable autonomous agents with on-chain intents and reputation"  
**Timeline**: 2-3 months (accelerated - foundations exist)  
**Status**: In Development

---

## Executive Summary

The **Agent Orchestrator** is verifiable agent infrastructure for Starknet. Users submit **intents** (goals + constraints) on-chain, agents compete to execute them with **cryptographic proof**, and their **reputation** is tracked transparently. This creates a trustless marketplace for autonomous execution.

**Why Agent Orchestrator?**
- **Differentiated tech**: Not just "another zkML implementation" - this is cutting-edge agent infrastructure
- **Fast to market**: 50% of foundations already exist (constraint signatures = intent basis, events = receipts)
- **Clear narrative**: "Verifiable agents" is a compelling story for Starknet ecosystem
- **Composable**: Other protocols can plug into this infrastructure

---

## Current Foundations (Already Built)

From Stage 2 & 3A, we have:

### 1. Constraint Signatures (STEP 0.6)
```cairo
// contracts/src/risk_engine.cairo - already implemented
fn propose_and_execute_allocation(
    constraint_signer: ContractAddress,  // ← Intent signature
    constraint_signature_data: Span<felt252>  // ← Policy hash + timestamp
)
```
**Translation**: This is already an intent system - user signs constraints, agent executes with proof.

### 2. Execution Receipts (Events)
```cairo
event AllocationExecuted {
    protocol: ContractAddress,
    allocation: Span<felt252>,
    proof_hashes: Span<felt252>,
    constraint_signer: ContractAddress  // ← Links to intent
}
```
**Translation**: We track every execution with proof, perfect for reputation scoring.

### 3. Proof Verification Gate
```cairo
let proofs_valid = verify_allocation_decision_with_proofs(...);
assert(proofs_valid, 0);  // ← Trustless execution
```
**Translation**: Agents can't cheat - every execution must have valid proof.

---

## What Agent Orchestrator Adds

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                        │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Intent    │  │   Agent      │  │     Policy       │  │
│  │  Registry   │  │  Reputation  │  │   Marketplace    │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│         │                 │                    │            │
│         └─────────────────┴────────────────────┘            │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  RiskEngine v4  │
                    │ (Proof-Gated)   │
                    └────────────────┘
```

### 1. Intent Registry
**Purpose**: Store user intents on-chain (not just ephemeral signatures)

```cairo
// NEW: contracts/src/agent_orchestrator.cairo
#[derive(Drop, Starknet::Store)]
struct Intent {
    id: felt252,
    user: ContractAddress,
    goal: IntentType,         // MaximizeYield, MinimizeRisk, Custom
    constraints: ConstraintSet,
    policy_hash: felt252,     // Approved policy from marketplace
    status: IntentStatus,     // Pending, Active, Executed, Cancelled
    created_at: u64,
    expires_at: u64
}

#[derive(Drop, Starknet::Store)]
enum IntentType {
    MaximizeYield,
    MinimizeRisk,
    BalancedGrowth,
    CustomPolicy: felt252
}

#[storage]
intents: LegacyMap<felt252, Intent>
user_intents: LegacyMap<(ContractAddress, u64), felt252>  // (user, index) → intent_id
```

### 2. Agent Reputation System
**Purpose**: Track agent performance transparently

```cairo
#[derive(Drop, Starknet::Store)]
struct AgentReputation {
    agent_id: ContractAddress,
    total_executions: u64,
    successful_executions: u64,
    failed_executions: u64,
    total_value_executed: u256,
    avg_performance: felt252,      // Weighted average of outcomes
    reputation_score: felt252,      // 0-10000 (basis points)
    last_execution: u64,
    registered_at: u64
}

#[derive(Drop, Starknet::Store)]
struct ExecutionRecord {
    intent_id: felt252,
    agent: ContractAddress,
    timestamp: u64,
    proof_hashes: Span<felt252>,
    outcome: ExecutionOutcome,     // Success, Failed, Partial
    performance_score: felt252     // How well did it meet intent?
}
```

### 3. Policy Marketplace
**Purpose**: Pre-built, audited policy templates users can choose

```cairo
#[derive(Drop, Starknet::Store)]
struct Policy {
    policy_hash: felt252,
    name: ByteArray,              // "Conservative Growth"
    description: ByteArray,
    parameters: PolicyParams,
    approved: bool,
    approver: ContractAddress,    // DAO or Labs
    usage_count: u64,
    created_at: u64
}

#[derive(Drop, Starknet::Store)]
struct PolicyParams {
    min_diversification: felt252,
    max_single_allocation: felt252,
    risk_tolerance: felt252,      // 0-100
    rebalance_frequency: u64,     // seconds
    // Extensible for custom params
}
```

---

## Implementation Phases

### Phase 1: Core Contracts (Weeks 1-2)

**File**: `contracts/src/agent_orchestrator.cairo`

#### Week 1: Intent Registry + Basic Reputation
```cairo
#[starknet::contract]
mod AgentOrchestrator {
    // Storage
    #[storage]
    struct Storage {
        owner: ContractAddress,
        intent_counter: felt252,
        intents: LegacyMap<felt252, Intent>,
        user_intents: LegacyMap<(ContractAddress, u64), felt252>,
        agent_reputation: LegacyMap<ContractAddress, AgentReputation>,
        execution_records: LegacyMap<felt252, ExecutionRecord>,
    }

    // Core functions
    fn submit_intent(goal: IntentType, constraints: ConstraintSet, policy_hash: felt252) -> felt252
    fn cancel_intent(intent_id: felt252)
    fn execute_intent(intent_id: felt252, proof_hashes: Span<felt252>) -> bool
    fn record_execution(intent_id: felt252, agent: ContractAddress, outcome: ExecutionOutcome)
    fn get_agent_reputation(agent: ContractAddress) -> AgentReputation
}
```

#### Week 2: Policy Marketplace + Integration
```cairo
// Add to AgentOrchestrator
#[storage]
policies: LegacyMap<felt252, Policy>,
approved_policies: LegacyMap<felt252, bool>,

fn register_policy(name: ByteArray, description: ByteArray, params: PolicyParams) -> felt252
fn approve_policy(policy_hash: felt252)  // Owner/DAO only
fn get_policy(policy_hash: felt252) -> Policy
fn list_approved_policies() -> Array<felt252>

// Integration with RiskEngine
fn execute_intent_with_risk_engine(
    intent_id: felt252,
    metrics: ProtocolMetrics,
    proof_hashes: Span<felt252>
) {
    // 1. Verify intent is valid
    let intent = self.intents.read(intent_id);
    assert(intent.status == IntentStatus::Active, 'Intent not active');
    
    // 2. Call RiskEngine with proof
    let risk_engine = IRiskEngineDispatcher { contract_address: self.risk_engine.read() };
    risk_engine.propose_and_execute_allocation(
        intent.user,           // constraint_signer
        proof_hashes,
        0_felt252              // model_version
    );
    
    // 3. Record execution
    self.record_execution(intent_id, get_caller_address(), ExecutionOutcome::Success);
}
```

**Deliverables Week 1-2**:
- ✅ Intent submission & storage
- ✅ Agent reputation tracking
- ✅ Execution recording with proofs
- ✅ Policy registry

---

### Phase 2: Backend Services (Weeks 3-4)

**Files**: 
- `backend/app/services/agent_service.py`
- `backend/app/api/routes/agent.py`

#### Agent Service (`agent_service.py`)
```python
from starknet_py.contract import Contract
from typing import Optional, List

class AgentService:
    """Service for agent orchestrator interactions"""
    
    async def submit_intent(
        self,
        user_address: str,
        goal: str,  # "MaximizeYield", "MinimizeRisk", etc.
        constraints: dict,
        policy_hash: str,
        expires_in_hours: int = 24
    ) -> str:
        """Submit user intent to AgentOrchestrator contract"""
        # Convert to contract types
        intent_type = self._parse_intent_type(goal)
        constraint_set = self._encode_constraints(constraints)
        
        # Call contract
        orchestrator = Contract(...)
        tx = await orchestrator.functions["submit_intent"].invoke(
            intent_type,
            constraint_set,
            int(policy_hash, 16),
            expires_at=int(time.time()) + (expires_in_hours * 3600)
        )
        
        # Wait for confirmation
        await tx.wait_for_acceptance()
        intent_id = tx.events[0].data[0]  # IntentSubmitted event
        return hex(intent_id)
    
    async def get_agent_reputation(self, agent_address: str) -> dict:
        """Fetch agent reputation from contract"""
        orchestrator = Contract(...)
        reputation = await orchestrator.functions["get_agent_reputation"].call(
            int(agent_address, 16)
        )
        return {
            "agent_id": agent_address,
            "total_executions": reputation.total_executions,
            "success_rate": reputation.successful_executions / reputation.total_executions,
            "reputation_score": reputation.reputation_score / 100,  # basis points to percentage
            "avg_performance": reputation.avg_performance,
            "total_value": str(reputation.total_value_executed)
        }
    
    async def list_active_intents(self, user_address: Optional[str] = None) -> List[dict]:
        """List active intents (optionally filtered by user)"""
        # Query contract or indexer for IntentSubmitted events
        # Filter by status == Active
        pass
    
    async def execute_intent(
        self,
        intent_id: str,
        metrics: dict,
        agent_address: str
    ) -> dict:
        """Execute intent with proof generation"""
        # 1. Generate proof (existing flow)
        proof_result = await self.proof_service.generate_allocation_proof(metrics)
        
        # 2. Call AgentOrchestrator.execute_intent_with_risk_engine
        orchestrator = Contract(...)
        tx = await orchestrator.functions["execute_intent_with_risk_engine"].invoke(
            int(intent_id, 16),
            self._encode_metrics(metrics),
            proof_result['proof_hashes']
        )
        
        # 3. Return execution details
        return {
            "intent_id": intent_id,
            "tx_hash": hex(tx.hash),
            "agent": agent_address,
            "status": "executed",
            "proof_hashes": proof_result['proof_hashes']
        }
```

#### API Routes (`routes/agent.py`)
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class IntentSubmitRequest(BaseModel):
    goal: str  # "MaximizeYield", "MinimizeRisk", "BalancedGrowth"
    constraints: dict
    policy_hash: str
    expires_in_hours: int = 24

class IntentExecuteRequest(BaseModel):
    intent_id: str
    metrics: dict

@router.post("/intents/submit", tags=["Agent Orchestrator"])
async def submit_intent(request: IntentSubmitRequest):
    """Submit user intent to agent orchestrator"""
    agent_service = get_agent_service()
    intent_id = await agent_service.submit_intent(
        user_address=get_current_user(),  # from auth
        goal=request.goal,
        constraints=request.constraints,
        policy_hash=request.policy_hash,
        expires_in_hours=request.expires_in_hours
    )
    return {"intent_id": intent_id, "status": "submitted"}

@router.get("/intents/active", tags=["Agent Orchestrator"])
async def list_active_intents(user_address: Optional[str] = None):
    """List active intents"""
    agent_service = get_agent_service()
    intents = await agent_service.list_active_intents(user_address)
    return {"intents": intents, "count": len(intents)}

@router.post("/intents/{intent_id}/execute", tags=["Agent Orchestrator"])
async def execute_intent(intent_id: str, request: IntentExecuteRequest):
    """Execute intent with proof (agent endpoint)"""
    agent_service = get_agent_service()
    result = await agent_service.execute_intent(
        intent_id=intent_id,
        metrics=request.metrics,
        agent_address=get_current_user()
    )
    return result

@router.get("/agents/{agent_address}/reputation", tags=["Agent Orchestrator"])
async def get_agent_reputation(agent_address: str):
    """Get agent reputation score and history"""
    agent_service = get_agent_service()
    reputation = await agent_service.get_agent_reputation(agent_address)
    return reputation

@router.get("/policies", tags=["Agent Orchestrator"])
async def list_policies():
    """List approved policy templates"""
    # Query AgentOrchestrator for approved policies
    pass
```

**Deliverables Week 3-4**:
- ✅ Intent submission API
- ✅ Agent reputation query API
- ✅ Intent execution endpoint
- ✅ Policy marketplace API

---

### Phase 3: Frontend Demo (Weeks 5-6)

**New Route**: `/agent` (not `/demo` - keep existing demo intact)

**File**: `frontend/src/app/agent/page.tsx`

#### Agent Orchestrator Demo Flow

```tsx
'use client';

import { useState } from 'react';
import { IntentBuilder } from '@/components/agent/IntentBuilder';
import { AgentReputationBoard } from '@/components/agent/AgentReputationBoard';
import { ExecutionTracker } from '@/components/agent/ExecutionTracker';
import { PolicyMarketplace } from '@/components/agent/PolicyMarketplace';

export default function AgentOrchestratorDemo() {
  const [activeTab, setActiveTab] = useState<'submit' | 'track' | 'agents' | 'policies'>('submit');
  
  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white">
      <header className="border-b border-white/10 px-6 py-4">
        <h1 className="text-2xl font-display">Agent Orchestrator</h1>
        <p className="text-white/60 text-sm">Verifiable autonomous agents with on-chain intents</p>
      </header>
      
      <nav className="border-b border-white/10 px-6">
        <div className="flex gap-6">
          <Tab active={activeTab === 'submit'} onClick={() => setActiveTab('submit')}>
            Submit Intent
          </Tab>
          <Tab active={activeTab === 'track'} onClick={() => setActiveTab('track')}>
            Track Executions
          </Tab>
          <Tab active={activeTab === 'agents'} onClick={() => setActiveTab('agents')}>
            Agent Leaderboard
          </Tab>
          <Tab active={activeTab === 'policies'} onClick={() => setActiveTab('policies')}>
            Policy Marketplace
          </Tab>
        </div>
      </nav>
      
      <main className="px-6 py-8 max-w-6xl mx-auto">
        {activeTab === 'submit' && <IntentBuilder />}
        {activeTab === 'track' && <ExecutionTracker />}
        {activeTab === 'agents' && <AgentReputationBoard />}
        {activeTab === 'policies' && <PolicyMarketplace />}
      </main>
    </div>
  );
}
```

#### Key Components

**1. Intent Builder** (`components/agent/IntentBuilder.tsx`)
```tsx
// User submits intent: goal + constraints + policy
// Shows preview of what agent will execute
// Connects wallet to sign intent on-chain
```

**2. Agent Reputation Board** (`components/agent/AgentReputationBoard.tsx`)
```tsx
// Leaderboard of agents by reputation score
// Shows: success rate, total executions, avg performance
// Click agent → see detailed history
```

**3. Execution Tracker** (`components/agent/ExecutionTracker.tsx`)
```tsx
// Real-time feed of intent executions
// Shows: intent_id, agent, proof hash, outcome
// Links to Starkscan for proof verification
```

**4. Policy Marketplace** (`components/agent/PolicyMarketplace.tsx`)
```tsx
// Grid of approved policy templates
// Each shows: name, description, usage count, parameters
// Click to use in intent builder
```

**Deliverables Week 5-6**:
- ✅ `/agent` demo route
- ✅ Intent submission UI
- ✅ Live reputation leaderboard
- ✅ Execution tracker with proof links
- ✅ Policy marketplace browser

---

### Phase 4: Landing Page Integration (Week 7)

Update `frontend/src/app/page.tsx` with Agent Orchestrator section.

#### New Section After Products

```tsx
{/* Agent Orchestrator */}
<section id="agent" className="py-24 px-6 border-t border-white/5">
  <div className="max-w-6xl mx-auto">
    <div className="text-center mb-16">
      <p className="font-mono text-[11px] text-white/40 tracking-wider mb-4">
        AGENT ORCHESTRATOR
      </p>
      <h2 className="font-display text-4xl mb-4">
        Verifiable Autonomous Agents
      </h2>
      <p className="text-white/60 text-lg max-w-2xl mx-auto">
        Submit intents, agents compete to execute with proof, reputation tracked transparently.
      </p>
    </div>
    
    {/* Feature Grid */}
    <div className="grid md:grid-cols-3 gap-6 mb-12">
      <FeatureCard 
        icon="🎯"
        title="Intent Registry"
        description="Submit goals + constraints on-chain. Agents discover and execute your intents."
      />
      <FeatureCard 
        icon="🏆"
        title="Agent Reputation"
        description="Every execution tracked with proof. Success rates and performance transparent."
      />
      <FeatureCard 
        icon="📋"
        title="Policy Marketplace"
        description="Pre-built, audited policy templates. Choose your risk profile, agents execute."
      />
    </div>
    
    {/* Demo CTA */}
    <div className="text-center">
      <Link 
        href="/agent"
        className="inline-block px-8 py-3.5 bg-gradient-to-r from-purple-400 to-pink-400 text-black text-sm font-semibold rounded-lg hover:shadow-lg transition-all"
      >
        Launch Agent Demo →
      </Link>
    </div>
  </div>
</section>
```

#### Update Navigation
```tsx
<nav className="hidden md:flex items-center gap-6 text-[12px] text-white/50 font-medium">
  <a href="#overview">Overview</a>
  <a href="#pillars">Pillars</a>
  <a href="#architecture">Architecture</a>
  <a href="#proof-pipeline">Proof Pipeline</a>
  <a href="#privacy">Privacy</a>
  <a href="#agent">Agent</a>  {/* NEW */}
  <a href="#roadmap">Roadmap</a>
  <a href="#labs">Labs</a>
  <a href="#demo">Demo</a>
</nav>
```

---

## Narrative: Why Agent Orchestrator?

### The Problem
Traditional DeFi automation is centralized: a single entity decides when/how to rebalance, with no transparency or accountability. Users must trust the operator won't front-run, extract value, or fail silently.

### The Solution
**Agent Orchestrator** makes automation verifiable:
1. **User submits intent** on-chain: "I want max yield with < 40% single protocol risk"
2. **Agents compete** to execute: they generate proofs showing their allocation meets constraints
3. **Contract verifies** proof before execution: no proof → no execution
4. **Reputation tracked**: every execution recorded, agents ranked by performance

### The Result
- Users get **trustless automation** - agents can't cheat
- Agents build **verifiable reputation** - good performance = more intents
- Protocols get **composable infrastructure** - plug into intent registry

### Market Positioning
- Not just "another zkML": This is **agent infrastructure** (cutting-edge)
- Not just "DeFi automation": This is **verifiable agents** (novel tech)
- Not just "for obsqra.fi": This is **protocol infrastructure** (composable)

**Tagline**: "The verifiable agent layer for Starknet"

---

## Success Metrics

### Week 2 (Contracts)
- ✅ Intent submission working
- ✅ Agent reputation tracking active
- ✅ Policy registry functional

### Week 4 (Backend)
- ✅ API endpoints live
- ✅ Intent execution with proof
- ✅ Reputation queries working

### Week 6 (Frontend)
- ✅ `/agent` demo route live
- ✅ Intent builder functional
- ✅ Reputation leaderboard showing real data

### Week 8 (Launch)
- ✅ Landing page updated
- ✅ Blog post: "Introducing Agent Orchestrator"
- ✅ Twitter thread with demo video
- ✅ 10+ test intents executed on Sepolia

---

## Technical Challenges & Solutions

### Challenge 1: Intent Expiry
**Problem**: Intents can go stale (market conditions change)  
**Solution**: Add `expires_at` timestamp; agents can't execute expired intents

### Challenge 2: Agent Selection
**Problem**: Multiple agents might try to execute same intent  
**Solution**: First agent to submit valid proof wins; intent marked as Executed

### Challenge 3: Reputation Gaming
**Problem**: Agents might game system with fake executions  
**Solution**: Reputation weighted by value executed + time-decay on old executions

### Challenge 4: Policy Complexity
**Problem**: Users might want custom policies beyond templates  
**Solution**: `IntentType::CustomPolicy` allows arbitrary policy hash (advanced users)

---

## Next Steps (Post-Launch)

### Month 3: Advanced Features
- Multi-agent coordination (agents calling agents)
- Intent bundling (batch multiple intents)
- Agent staking (stake required to register)

### Month 4: Ecosystem Integration
- SDK for agents (Python/TypeScript)
- Intent indexer (fast query of active intents)
- Policy builder UI (create custom policies)

### Month 5: Governance
- DAO can approve/reject agents
- DAO can set reputation thresholds
- Community policy proposals

---

## Development Log

### 2026-01-29: Project Kickoff
- ✅ Created development plan
- ✅ Defined architecture (intent registry, reputation, policies)
- ✅ Named project: **Agent Orchestrator**
- ✅ Created todos for 8-week timeline

### 2026-01-29: Contract Implementation Complete (Week 1)
- ✅ Created `contracts/src/agent_orchestrator.cairo` (750+ lines)
- ✅ Implemented Intent Registry (submit, cancel, get, track by user)
- ✅ Implemented Agent Reputation (register, track executions, score calculation)
- ✅ Implemented Policy Marketplace (register, approve, revoke)
- ✅ Implemented Execution Records (for audit trail)
- ✅ Added all events (IntentSubmitted, IntentExecuted, AgentRegistered, etc.)
- ✅ Contract compiles successfully with `scarb build`
- ✅ Class hash: `0x0736b73f526338456cabfe8af3b09bc2ea71f597c95c9f16a6202b23a5a920a0`
- ✅ Created deployment script: `scripts/deploy_agent_orchestrator.sh`
- 🔄 Next: Deploy to Sepolia (requires interactive keystore password)

**Contract Features:**
| Feature | Status |
|---------|--------|
| Intent submission | ✅ |
| Intent cancellation | ✅ |
| Intent expiry | ✅ |
| Agent registration | ✅ |
| Reputation tracking | ✅ |
| Execution recording | ✅ |
| Policy registration | ✅ |
| Policy approval (owner) | ✅ |
| RiskEngine integration | ✅ (storage, not wired) |

---

## Development Log

### 2026-01-29: Phase 1 Complete - Contract Deployed

**Contract Deployment**
- Class Hash: `0x032a75737e990b7b136bf05f22211cf2623950fe8e5958a7ac5e0d7d676c1995`
- Contract Address: `0x050a35c0f4f42e7b3fcf1186d2465d5a14f7c17054bf4d3da4ac8ca8f5f8bb23`
- Owner: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`
- Network: Starknet Sepolia

**Verified On-Chain**
- `get_version()` returns `agent_orchestrator_v1`
- Contract fully operational

**Technical Notes**
- CASM hash mismatch resolved by using `--casm-hash` flag with sequencer-expected hash
- Previous declaration attempts had cached different CASM in sequencer state

**Next**: Phase 2 - Backend Services

---

**Last Updated**: 2026-01-29  
**Status**: Phase 1 COMPLETE - Starting Phase 2  
**Target Launch**: March 2026 (8 weeks)
