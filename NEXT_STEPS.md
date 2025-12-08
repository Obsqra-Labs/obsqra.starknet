# Next Steps - Complete V1.3 (2-3 weeks)

## What You Have (90%)

✅ RiskEngine + StrategyRouterV2 contracts (deployed, working)  
✅ Backend orchestration (executes rebalances)  
✅ Frontend (wallet connection, dashboard)  
✅ Proof generation service (2-3s)  
✅ Production deployment (starknet.obsqra.fi)

## What's Missing (10%)

❌ Proofs not connected to orchestration  
❌ Demo mode in frontend  
❌ Real performance tracking  
❌ Proof visibility in UI

---

## This Week: Quick Wins (5 hours)

### 1. Connect Proofs to Orchestration (2 hours)

**File**: `backend/app/api/routes/risk_engine.py`

```python
@router.post("/orchestrate-allocation")
async def orchestrate_allocation(request: OrchestrationRequest):
    # EXISTING CODE: Calculate metrics
    
    # ADD THIS: Generate proof
    luminair = get_luminair_service()
    proof = await luminair.generate_proof(
        request.jediswap_metrics.dict(),
        request.ekubo_metrics.dict()
    )
    
    # ADD THIS: Store in database
    proof_job = ProofJob(
        proof_hash=proof.proof_hash,
        status="generated",
        metrics={"jediswap": request.jediswap_metrics.dict(), "ekubo": request.ekubo_metrics.dict()}
    )
    db.add(proof_job)
    db.commit()
    
    # EXISTING CODE: Execute on-chain
    decision = await execute_on_chain(...)
    
    # ADD THIS: Link proof to transaction
    proof_job.tx_hash = decision.tx_hash
    proof_job.status = "executed"
    db.commit()
    
    # EXISTING RETURN + proof info
    return {
        **decision,
        "proof_hash": proof.proof_hash,
        "proof_job_id": str(proof_job.id)
    }
```

**Test**:
```bash
curl -X POST https://starknet.obsqra.fi/api/v1/risk-engine/orchestrate-allocation \
  -d @test_metrics.json

# Should return proof_hash in response
```

### 2. Show Proof in UI (2 hours)

**File**: `frontend/src/components/Dashboard.tsx`

```typescript
// Add after orchestration call:
const { data, isLoading } = useOrchestration();

if (data?.proof_hash) {
  return (
    <div>
      <h3>Latest Rebalance</h3>
      <div>Allocation: Jedi {data.jediswap_pct}% / Ekubo {data.ekubo_pct}%</div>
      <div>
        Proof: <code>{data.proof_hash.slice(0, 16)}...</code>
        <Badge color="green">Verified</Badge>
      </div>
      <Link href={`https://sepolia.voyager.online/tx/${data.tx_hash}`}>
        View Transaction
      </Link>
    </div>
  );
}
```

### 3. Remove One Demo Toggle (1 hour)

**File**: Search for demo mode

```bash
cd frontend
grep -rn "demoMode\|demo_mode" src/
```

**Example fix**:
```typescript
// Before
const [demoMode, setDemoMode] = useState(true);
const data = demoMode ? mockData : realData;

// After
const { data } = useRealData(); // Always real
```

**Result**: Proofs visible in production by end of week

---

## Week 2-3: Complete V1.3

### Backend Tasks

1. **Real Performance Endpoint** (1 day)
   ```python
   @router.get("/analytics/performance/real")
   async def get_real_performance():
       # Query rebalance events from contract
       # Calculate APY from on-chain data
       # Include proof status for each
   ```

2. **SHARP Background Submission** (1 day)
   - Already have sharp_worker.py
   - Just need to trigger it after proof generation

### Frontend Tasks

1. **Find All Demo Code** (2 hours)
   ```bash
   grep -r "mock\|demo\|fake" src/ > demo_audit.txt
   ```

2. **Remove Demo Mode** (2 days)
   - Delete all demo toggles
   - Use real contract calls only
   - Show on-chain data

3. **Add Proof Components** (2 days)
   - ProofBadge (shows status)
   - RebalanceHistory (list with proofs)
   - ProofDetails (expandable)

4. **Real Performance** (1 day)
   - Fetch from /analytics/performance/real
   - Show APY from on-chain execution
   - Chart historical rebalances

### Polish (Week 3)

- Error boundaries
- Loading states
- Mobile responsive
- Documentation

---

## Success Criteria (V1.3 Complete)

1. ✅ Every rebalance generates proof
2. ✅ Proofs stored in database
3. ✅ Proofs visible in UI
4. ✅ Real performance from on-chain
5. ✅ NO demo mode
6. ✅ Production documentation

**Measurement**: 1 week, 5+ rebalances, all proofs visible

---

## Then: V1.4 Privacy Pools (2 months)

After V1.3 solid, pivot to privacy:
- PrivatePool contract
- MIST integration
- Anonymous deposits/withdrawals
- Transparent optimization (proofs still visible)

---

## GitHub Push

**58 commits ready**:

```bash
# Get personal access token: https://github.com/settings/tokens
cd /opt/obsqra.starknet
git push https://YOUR_TOKEN@github.com/Obsqra-Labs/obsqra.starknet.git main
```

Files ready:
- ✅ README.md (professional, dev-focused)
- ✅ ROADMAP_V1.3_CURRENT.md (complete existing system)
- ✅ ROADMAP_PRODUCT.md (privacy pool vision)
- ✅ V1.3_IMPLEMENTATION.md (detailed plan)
- ✅ PRODUCT_VISION.md (for grants)

---

## Immediate Action (Today)

1. **Test current system**:
   ```bash
   curl https://starknet.obsqra.fi/api/v1/risk-engine/orchestrate-allocation \
     -X POST -d @test_metrics.json
   ```

2. **Add proof generation** (2 hours):
   - Edit `backend/app/api/routes/risk_engine.py`
   - Add luminair call + database storage
   - Test locally

3. **Show in UI** (1 hour):
   - Edit `frontend/src/components/Dashboard.tsx`
   - Display proof_hash from response
   - Deploy

**By EOD**: Proofs visible in production

---

**Current Focus**: Complete V1.3 (finish 90% → 100%)  
**Next MVP**: V1.4 privacy pools with MIST  
**Timeline**: V1.3 in 2-3 weeks, V1.4 starts after
