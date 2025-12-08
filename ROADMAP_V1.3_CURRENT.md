# V1.3: Complete Yield Optimizer (Current System)

## Starting Point

**You already have ~90%**:
- StrategyRouterV2 (deployed)
- RiskEngine (deployed)
- Backend orchestration (working)
- Frontend with wallet connection
- Proof generation (2-3s)

**Missing ~10%**:
- Demo mode removal (show real data)
- Proof visibility in UX
- Real performance tracking
- Production polish

---

## Goal: Proof of Concept → Production

Transform existing system into demonstrable product without major rewrites.

**Timeline**: 2-3 weeks

---

## V1.3 Plan: Complete Current System

### Week 1: Backend - Add Proofs to Orchestration

**Current**: Backend executes rebalances, no proof integration  
**Target**: Every rebalance generates proof and stores it

#### Update risk_engine.py

```python
# backend/app/api/routes/risk_engine.py

@router.post("/orchestrate-allocation")
async def orchestrate_allocation(request: OrchestrationRequest):
    """Execute allocation with proof generation"""
    
    # 1. Generate STARK proof
    luminair = get_luminair_service()
    proof = await luminair.generate_proof(
        request.jediswap_metrics.dict(),
        request.ekubo_metrics.dict()
    )
    
    # 2. Store proof in database
    proof_job = ProofJob(
        proof_hash=proof.proof_hash,
        status="generated",
        metrics={
            "jediswap": request.jediswap_metrics.dict(),
            "ekubo": request.ekubo_metrics.dict()
        }
    )
    db.add(proof_job)
    db.commit()
    
    # 3. Execute on-chain (existing code)
    decision = await execute_on_chain(
        jediswap_pct=calculate_allocation(proof.output_score_jediswap),
        ekubo_pct=calculate_allocation(proof.output_score_ekubo),
        proof_hash=proof.proof_hash  # Include in transaction
    )
    
    # 4. Update proof job with tx hash
    proof_job.tx_hash = decision.tx_hash
    proof_job.status = "executed"
    db.commit()
    
    # 5. Submit to SHARP (background)
    background_tasks.add_task(
        submit_to_sharp,
        proof_job.id,
        proof.proof_hash
    )
    
    return {
        "decision": decision,
        "proof_hash": proof.proof_hash,
        "proof_job_id": str(proof_job.id)
    }
```

#### Add Performance Tracking

```python
# backend/app/api/routes/analytics.py

@router.get("/performance/real")
async def get_real_performance():
    """Calculate performance from on-chain execution results"""
    
    # Query all rebalances from contract events
    rebalances = await get_rebalance_events()
    
    # Calculate APY from actual execution
    apy = calculate_apy_from_rebalances(rebalances)
    
    # Get proof verification status
    for rebalance in rebalances:
        proof_job = db.query(ProofJob).filter_by(
            tx_hash=rebalance.tx_hash
        ).first()
        rebalance.proof_status = proof_job.status if proof_job else "unknown"
    
    return {
        "apy": apy,
        "total_rebalances": len(rebalances),
        "rebalances": [
            {
                "timestamp": r.timestamp,
                "jediswap_pct": r.jediswap_pct,
                "ekubo_pct": r.ekubo_pct,
                "tx_hash": r.tx_hash,
                "proof_hash": r.proof_hash,
                "proof_status": r.proof_status
            }
            for r in rebalances
        ]
    }
```

**Deliverable**: Every rebalance generates proof, stores in DB, submits to SHARP

---

### Week 2: Frontend - Remove Demo Mode

**Audit all demo/mock code**:

```bash
cd frontend
# Find all demo mode
grep -rn "demo\|mock\|fake\|placeholder" src/ > demo_audit.txt

# Key files to update:
# - src/components/Dashboard.tsx
# - src/hooks/useStrategyDeposit.ts
# - src/components/PerformanceChart.tsx
# - Any toggles for demo mode
```

#### 1. Update Dashboard.tsx

```typescript
// Before: Demo data
const [demoMode, setDemoMode] = useState(true);
const tvl = demoMode ? 1000000 : realTVL;

// After: Real data only
import { useRealPerformance } from '@/hooks/useRealPerformance';

export function Dashboard() {
  const { data: performance, loading } = useRealPerformance();
  const { data: allocations } = useCurrentAllocations();
  
  if (loading) return <Skeleton />;
  
  return (
    <div>
      <Stats>
        <Stat label="Current APY" value={`${performance.apy}%`} />
        <Stat label="Total Rebalances" value={performance.total_rebalances} />
        <Stat label="All Proofs" value="Verified" verified={true} />
      </Stats>
      
      <AllocationChart
        jediswap={allocations.jediswap_pct / 100}
        ekubo={allocations.ekubo_pct / 100}
      />
      
      <RebalanceHistory rebalances={performance.rebalances} />
    </div>
  );
}
```

#### 2. Add Proof Display Components

```typescript
// components/ProofBadge.tsx
export function ProofBadge({ 
  hash, 
  status 
}: { 
  hash: string; 
  status: 'generated' | 'executed' | 'verifying' | 'verified' 
}) {
  const icon = {
    generated: '⏳',
    executed: '✓',
    verifying: '🔄',
    verified: '✅'
  }[status];
  
  const color = {
    generated: 'yellow',
    executed: 'blue',
    verifying: 'orange',
    verified: 'green'
  }[status];
  
  return (
    <Badge color={color}>
      {icon} {hash.slice(0, 8)}...
      <Tooltip>
        <ProofDetails hash={hash} status={status} />
      </Tooltip>
    </Badge>
  );
}

// components/RebalanceHistory.tsx
export function RebalanceHistory({ rebalances }: { rebalances: Rebalance[] }) {
  return (
    <Card>
      <h3>Rebalance History (On-Chain)</h3>
      <Table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Allocation</th>
            <th>Proof</th>
            <th>Transaction</th>
          </tr>
        </thead>
        <tbody>
          {rebalances.map((r) => (
            <tr key={r.tx_hash}>
              <td>{formatDate(r.timestamp)}</td>
              <td>
                Jedi {r.jediswap_pct/100}% / Ekubo {r.ekubo_pct/100}%
              </td>
              <td>
                <ProofBadge hash={r.proof_hash} status={r.proof_status} />
              </td>
              <td>
                <Link href={`https://sepolia.voyager.online/tx/${r.tx_hash}`}>
                  View TX
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Card>
  );
}
```

#### 3. Add Real Performance Hook

```typescript
// hooks/useRealPerformance.ts
export function useRealPerformance() {
  return useQuery({
    queryKey: ['performance', 'real'],
    queryFn: async () => {
      const res = await fetch('/api/v1/analytics/performance/real');
      return res.json();
    },
    refetchInterval: 30000, // Refresh every 30s
  });
}

// hooks/useCurrentAllocations.ts
export function useCurrentAllocations() {
  const { data } = useContractRead({
    address: STRATEGY_ROUTER_ADDRESS,
    abi: strategyRouterAbi,
    functionName: 'get_current_allocations',
  });
  
  return {
    data: {
      jediswap_pct: data?.jediswap || 0,
      ekubo_pct: data?.ekubo || 0,
    }
  };
}
```

**Deliverable**: Frontend shows only real on-chain data, proofs visible

---

### Week 3: Polish + Production Ready

#### Error Handling

```typescript
// Add error boundaries
export function Dashboard() {
  const { data, error, loading } = useRealPerformance();
  
  if (error) {
    return (
      <ErrorState
        title="Failed to load performance"
        message={error.message}
        retry={() => refetch()}
      />
    );
  }
  
  if (loading) return <LoadingSkeleton />;
  
  return <DashboardContent data={data} />;
}
```

#### Loading States

```typescript
// Skeleton loaders for every component
<Card>
  {loading ? (
    <Skeleton height={200} />
  ) : (
    <PerformanceChart data={data} />
  )}
</Card>
```

#### Mobile Responsive

```typescript
// Use responsive design
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {stats.map(s => <StatCard {...s} />)}
</div>
```

#### Documentation

```markdown
# User Guide

## How to Use Obsqura Yield Optimizer

1. Connect your Starknet wallet
2. View current allocation across Jediswap and Ekubo
3. See real-time APY and performance metrics
4. Review rebalance history with cryptographic proofs
5. All decisions are verifiable on-chain

## Rebalance Process

Every rebalance follows this flow:
1. AI analyzes protocol metrics
2. Generates STARK proof (2-3s)
3. Executes on-chain
4. Submits to SHARP for L1 verification
5. Proof visible in UI

## Verifying Proofs

Each rebalance shows:
- Proof hash (cryptographic commitment)
- Verification status (local → SHARP → L1)
- Transaction hash (on-chain execution)
- Click proof badge to see details
```

**Deliverable**: Production-ready UI, error handling, documentation

---

## V1.3 Success Criteria

**System is production-ready when**:

1. ✅ Backend generates proof for every rebalance
2. ✅ Proofs stored in database with tx hashes
3. ✅ SHARP submission working (background)
4. ✅ Frontend shows ONLY real on-chain data
5. ✅ All proofs visible in UI with status
6. ✅ Performance calculated from real execution
7. ✅ NO demo mode exists
8. ✅ Error handling for all states
9. ✅ Mobile responsive
10. ✅ Documentation complete

**Measurement**:
- Deploy for 1 week
- Execute 5+ rebalances
- All proofs generated and tracked
- All proofs visible in UI
- 0 instances of demo/mock data

---

## V1.4: Privacy Pool + MIST (Next)

**After V1.3 is solid**:

### Architecture Shift

```
Current (V1.3):
User wallet → StrategyRouter → Protocols

Future (V1.4):
User → PrivatePool (MIST) → StrategyRouter → Protocols
       └─ Anonymous deposits/withdrawals
       └─ Transparent optimization (with proofs)
```

### Implementation

1. Deploy PrivatePool contract (MIST integration)
2. Anonymous deposit flow
3. Anonymous withdrawal flow
4. Keep optimization transparent
5. Migrate users from V1.3

**Timeline**: 2 months after V1.3 complete

---

## Current Status Check

### What You Have (90%)

**Contracts**:
- ✅ RiskEngine (deployed, working)
- ✅ StrategyRouterV2 (deployed, working)
- ✅ DAOConstraintManager (deployed)

**Backend**:
- ✅ FastAPI service (production)
- ✅ Orchestration endpoint (working)
- ✅ Proof generation (2-3s)
- ✅ Database tracking (ready)
- ⚠️ Proof integration (partial)

**Frontend**:
- ✅ Wallet connection
- ✅ Basic dashboard
- ⚠️ Demo mode (needs removal)
- ❌ Proof visibility
- ❌ Real performance

### What's Missing (10%)

1. **Proof Integration** (3 days)
   - Connect proof generation to orchestration
   - Store proofs in database
   - Link proofs to transactions

2. **Frontend Cleanup** (5 days)
   - Remove all demo mode
   - Show real data only
   - Add proof components

3. **Polish** (3 days)
   - Error handling
   - Loading states
   - Documentation

**Total**: ~2 weeks

---

## Implementation Checklist

### Week 1: Backend Proof Integration

- [ ] Update orchestrate_allocation to generate proofs
- [ ] Store proofs in database with tx hashes
- [ ] Add background SHARP submission
- [ ] Create /analytics/performance/real endpoint
- [ ] Test proof generation → storage → SHARP flow

### Week 2: Frontend Demo Removal

- [ ] Audit all demo/mock code (grep search)
- [ ] Remove demo mode toggles
- [ ] Create useRealPerformance hook
- [ ] Create ProofBadge component
- [ ] Create RebalanceHistory component
- [ ] Update Dashboard to show real data only
- [ ] Test end-to-end with real contract calls

### Week 3: Production Polish

- [ ] Add error boundaries
- [ ] Add loading skeletons
- [ ] Make mobile responsive
- [ ] Write user documentation
- [ ] End-to-end testing
- [ ] Deploy to production

---

## Quick Wins (This Week)

### 1. Connect Proofs to Orchestration (2 hours)

```python
# Just add this to existing orchestrate_allocation:
proof = await luminair.generate_proof(metrics)
proof_job = ProofJob(proof_hash=proof.proof_hash, ...)
db.add(proof_job)
return {..., "proof_hash": proof.proof_hash}
```

### 2. Show Proofs in UI (2 hours)

```typescript
// Add to Dashboard:
<div>Proof: {response.proof_hash}</div>
```

### 3. Remove One Demo Toggle (1 hour)

```typescript
// Find and delete:
const [demoMode, setDemoMode] = useState(true);
// Use real data instead
```

**These 3 changes make proofs visible immediately.**

---

## Summary

### V1.3 (2-3 weeks)
Complete existing 90% yield optimizer:
- Add proofs to orchestration
- Remove demo mode
- Show real performance
- Polish for production

### V1.4 (2 months after V1.3)
Add privacy pool with MIST:
- PrivatePool contract
- Anonymous deposits/withdrawals
- Keep transparent optimization
- Migrate users

**Current Focus**: Complete V1.3 (finish what you have)

**Next MVP**: V1.4 (privacy pools with MIST)

---

**Ready to start Week 1: Backend proof integration**

