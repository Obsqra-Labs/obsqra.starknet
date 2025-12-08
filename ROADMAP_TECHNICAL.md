# Technical Roadmap - V1.3 and Beyond

## Current Status (V1.2 - Production)

**What Works**:
- Risk scoring algorithm (5 components)
- STARK proof generation (Python MVP, 2-3s)
- Local verification (<1s)
- Database tracking (PostgreSQL)
- REST API (FastAPI, production)
- Background worker infrastructure (ready)
- Production deployment (starknet.obsqra.fi)

**What's Ready**:
- LuminAIR RiskScoring operator (75% - Rust AIR + trace)
- SHARP service (mock, ready for gateway)
- Background polling worker (implemented)
- Database schema (migrations complete)

---

## Decision Point: Next Phase

### Question 1: Rust Binary vs Full SHARP?

**Answer**: Do both in parallel, they're complementary.

#### Why Rust Binary First (V1.3a - 1-2 weeks)

**Current**: Python MVP generates proofs in 2-3 seconds
**Target**: Rust binary generates proofs in <500ms (5x faster)

**Path**:
```
1. Complete witness generation (witness.rs)
   - Implement trace row generation
   - Port Python calculation logic to Rust
   - Add test vectors

2. Build luminair_prover binary
   - CLI interface: prove, verify
   - JSON input/output
   - Integrate with LuminAIR prover

3. Update luminair_service.py
   - Replace Python calculation with subprocess call
   - Parse Rust binary output
   - Keep same API interface

4. Deploy and test
   - Verify <500ms proof generation
   - Ensure output matches Python MVP
   - Update production
```

**Why This Matters**:
- 5x faster = better UX
- Real STARK proofs (not mock structure)
- Validates LuminAIR operator works
- Foundation for full SHARP integration

**Effort**: ~1 week (Rust development + integration)

#### Why Full SHARP Next (V1.3b - Concurrent with Rust)

**Current**: Background worker ready, SHARP service has mock implementation
**Target**: Real L1 verification via SHARP gateway

**Path**:
```
1. SHARP Gateway Integration
   - Get SHARP API credentials
   - Implement real submit_proof()
   - Handle job ID tracking

2. Update sharp_service.py
   - Replace mock with real HTTP calls
   - Add retry logic
   - Parse SHARP responses

3. Background Worker Enhancement
   - Poll SHARP for verification status
   - Update database on completion
   - Store fact hash from L1

4. Contract Integration (Optional)
   - Add SHARP verifier contract
   - Query fact registry on-chain
   - Verify proofs in Cairo
```

**Why This Matters**:
- L1 settlement = permanent audit trail
- SHARP = Ethereum security
- Verifiable AI thesis complete
- Grant/investor story

**Effort**: ~1 week (API integration + testing)

**Verdict**: **Do Both**. Rust improves proof generation speed. SHARP adds L1 verification. They don't conflict.

---

### Question 2: When Does Full zkML Come In?

**Answer**: V1.4 (1-2 months), after proving the system works with real SHARP.

#### Current Architecture (V1.2-V1.3)

```
Risk Metrics → Python/Rust Calculation → STARK Proof → SHARP → L1
```

**Calculation**: Off-chain (Python or Rust)
**Proof**: Of correct execution
**Verification**: On-chain (SHARP)

**Limitation**: Risk model logic not on-chain, just proof of execution.

#### Full zkML Architecture (V1.4+)

```
Risk Metrics → Cairo ML Model (on-chain) → Execution Proof → SHARP → L1
```

**Calculation**: On-chain (Cairo contract)
**Proof**: Of correct inference
**Verification**: On-chain (SHARP + Cairo)

**Advantage**: Entire model on-chain, fully auditable.

#### Why Not Now?

1. **Cairo ML is Complex**
   - Need Cairo tensor operations
   - Matrix multiplication in fixed-point
   - Activation functions (sigmoid, tanh)
   - Model serialization

2. **Prove Python/Rust Works First**
   - Validate system with simpler model
   - Get real users, real data
   - Understand performance needs

3. **Cairo ML is Expensive**
   - Higher gas costs
   - Slower execution
   - More complex debugging

4. **Incremental Value**
   - Current system already verifiable
   - SHARP proves correct execution
   - Cairo ML is optimization, not requirement

#### Path to Full zkML (V1.4)

**Phase 1: Cairo Math Foundation** (Done)
- Fixed-point arithmetic (lib/fixed_point.cairo)
- Statistical functions (lib/stats.cairo)
- Risk model in Cairo (ml/risk_model.cairo)

**Phase 2: Cairo Model Deployment** (V1.4 - Month 1)
```
1. Deploy Cairo risk model
2. Update RiskEngine to use Cairo inference
3. Benchmark gas costs
4. Compare accuracy with Python
```

**Phase 3: SHARP Integration** (V1.4 - Month 2)
```
1. Generate proofs of Cairo execution
2. Submit to SHARP
3. Verify on-chain
4. Full verifiable AI stack
```

**Timeline**: 1-2 months after V1.3 stable

---

### Question 3: UI Plan?

**Answer**: V1.3 - Basic proof display. V1.4 - Full verifiable AI UX.

#### Current UI (V1.2)

**What Exists**:
- Wallet connection (@starknet-react/core)
- Basic dashboard
- Manual rebalancing triggers
- No proof visualization

**What's Missing**:
- Proof generation UI
- Verification status display
- Constraint builder
- Audit trail

#### V1.3 UI (Next - 2 weeks)

**Goal**: Make proofs visible to users

**Components**:

```typescript
// 1. ProofGenerationButton.tsx
<Button onClick={generateProof}>
  Generate Risk Proof
</Button>
{loading && <Spinner text="Generating proof (2-3s)..." />}

// 2. ProofStatusBadge.tsx
{status === 'verified' && (
  <Badge color="green">
    Verified on L1
    <Link href={voyagerUrl}>View Proof</Link>
  </Badge>
)}

// 3. ProofDetails.tsx
<Card>
  <h3>Proof: {proof.hash.slice(0, 10)}...</h3>
  <p>Jediswap Risk: {proof.jediswap_score}</p>
  <p>Ekubo Risk: {proof.ekubo_score}</p>
  <p>Status: {proof.status}</p>
  <p>SHARP Job: {proof.sharp_job_id}</p>
</Card>

// 4. ProofList.tsx
<Table>
  <Row>
    <Cell>{proof.timestamp}</Cell>
    <Cell>{proof.hash.slice(0, 10)}</Cell>
    <Cell><StatusBadge status={proof.status} /></Cell>
    <Cell><Link to={`/proof/${proof.id}`}>Details</Link></Cell>
  </Row>
</Table>
```

**API Integration**:
```typescript
// hooks/useProofGeneration.ts
export function useProofGeneration() {
  const generate = async (metrics) => {
    const res = await fetch('/api/v1/proofs/generate', {
      method: 'POST',
      body: JSON.stringify(metrics)
    });
    return res.json();
  };

  const checkStatus = async (jobId) => {
    const res = await fetch(`/api/v1/proofs/${jobId}`);
    return res.json();
  };

  return { generate, checkStatus };
}

// Real-time updates
useEffect(() => {
  const interval = setInterval(async () => {
    const status = await checkStatus(jobId);
    setProofStatus(status);
    if (status === 'verified') clearInterval(interval);
  }, 10000); // Poll every 10s
}, [jobId]);
```

**Timeline**: 1-2 weeks

#### V1.4 UI (Full zkML UX - 1-2 months)

**Goal**: Complete verifiable AI experience

**New Components**:

```typescript
// 1. ConstraintBuilder.tsx
<ConstraintBuilder>
  <Rule>
    Max allocation per protocol: <Input type="number" />%
  </Rule>
  <Rule>
    Max risk score: <Input type="number" />
  </Rule>
  <Rule>
    Min liquidity tier: <Select options={[1,2,3]} />
  </Rule>
  <Button>Save Constraints</Button>
</ConstraintBuilder>

// 2. AIProposalDisplay.tsx
<AIProposal>
  <h3>AI Proposes:</h3>
  <AllocationChart data={proposal.allocations} />
  <ConstraintCheck>
    {constraints.map(c => (
      <Check passed={c.satisfied}>
        {c.name}: {c.value} {c.satisfied ? '✓' : '✗'}
      </Check>
    ))}
  </ConstraintCheck>
  <Button onClick={generateProof}>Generate Proof & Execute</Button>
</AIProposal>

// 3. VerificationTimeline.tsx
<Timeline>
  <Step completed={true}>
    Risk Calculated (2.3s)
  </Step>
  <Step completed={true}>
    Proof Generated (2.8s)
  </Step>
  <Step active={true}>
    Transaction Executed (15s)
  </Step>
  <Step>
    SHARP Submitted (pending)
  </Step>
  <Step>
    L1 Verified (est. 45min)
  </Step>
</Timeline>

// 4. AuditTrail.tsx
<AuditTrail>
  <Transaction>
    <Timestamp>2025-12-08 14:00:00</Timestamp>
    <Action>Rebalance: 60% Jedi, 40% Ekubo</Action>
    <Proof>0xa580bd... <Badge>Verified</Badge></Proof>
    <Constraints>
      <Check>Max 70% ✓</Check>
      <Check>Risk < 50 ✓</Check>
    </Constraints>
    <Links>
      <Link href={voyager}>Transaction</Link>
      <Link href={sharp}>Proof</Link>
    </Links>
  </Transaction>
</AuditTrail>
```

**Timeline**: 1-2 months (with Cairo ML)

---

## Recommended Sequence

### V1.3a: Rust Binary (Week 1-2)

**Goal**: 5x faster proof generation

**Tasks**:
1. Complete witness.rs (trace generation)
2. Build luminair_prover binary
3. Update luminair_service.py
4. Test and deploy

**Deliverable**: <500ms proof generation

### V1.3b: Real SHARP (Week 2-3, parallel)

**Goal**: L1 verification working

**Tasks**:
1. Get SHARP API access
2. Implement real sharp_service.py
3. Test on Sepolia
4. Update background worker

**Deliverable**: Proofs verified on Ethereum L1

### V1.3c: Proof UI (Week 3-4)

**Goal**: Users can see proofs

**Tasks**:
1. ProofGenerationButton
2. ProofStatusBadge  
3. ProofDetails component
4. ProofList table

**Deliverable**: Working proof visualization

### V1.4: Cairo ML + Full UX (Month 2-3)

**Goal**: Full verifiable AI stack

**Tasks**:
1. Deploy Cairo risk model
2. Integrate with RiskEngine
3. Build constraint builder UI
4. Build AI proposal display
5. Build verification timeline
6. Build audit trail

**Deliverable**: Complete verifiable AI experience

---

## Priority Decision

**If You Have 2 Weeks**:

**Option A**: Rust + SHARP (parallel)
- Best technical foundation
- Real SHARP verification
- 5x faster proofs
- No UI changes

**Option B**: Rust + Basic UI
- Faster proofs
- Users can see proofs
- No L1 verification yet
- Better UX

**Option C**: SHARP + Basic UI
- L1 verification working
- Users can see status
- Proofs still slow (2-3s)
- Complete flow

**Recommendation**: **Option A** (Rust + SHARP in parallel)

**Why**:
- UI can come later
- Technical foundation matters more
- SHARP is core to thesis
- Rust enables future optimizations
- Users tolerate 2-3s for now

**Then**: Add UI in V1.3c (week 3-4)

---

## Summary

### Now (V1.2)
- ✓ Python MVP (2-3s proofs)
- ✓ Production deployed
- ✓ Database tracking
- ✓ Background worker ready

### Next (V1.3 - 3-4 weeks)
1. **Rust Binary** (week 1-2): <500ms proofs
2. **Real SHARP** (week 2-3): L1 verification
3. **Proof UI** (week 3-4): User visualization

### Future (V1.4 - 2-3 months)
1. **Cairo ML**: On-chain inference
2. **Full UX**: Constraints, proposals, audit trail
3. **Advanced Features**: Multi-model, batch proofs

### Long Term (V2.0 - 6 months)
1. **Full zkML Stack**: End-to-end verifiable
2. **DAO Governance**: Community constraints
3. **Multi-Protocol**: Expand beyond 2 protocols
4. **Cross-Chain**: Proof verification on other chains

---

## Technical Debt

**Current**:
- Python MVP (works but slow)
- Mock SHARP (structure ready)
- Basic UI (functional but minimal)

**Needs Addressing**:
1. Replace Python with Rust (V1.3a)
2. Integrate real SHARP (V1.3b)
3. Build proof UI (V1.3c)
4. Deploy Cairo model (V1.4)

**Priority**: Rust > SHARP > UI > Cairo ML

**Timeline**: 3-4 weeks to V1.3 complete, 2-3 months to V1.4

---

## Resources Needed

### V1.3 (Rust + SHARP)
- Rust developer (witness generation)
- SHARP API access (credentials)
- Sepolia ETH (testing)
- 2-3 weeks development time

### V1.4 (Cairo ML + Full UX)
- Cairo developer (ML model)
- Frontend developer (UI components)
- Gas optimization (Cairo inference)
- 2-3 months development time

---

## Questions to Answer

1. **Rust Binary**: Start now or wait?
   **Answer**: Start now. 1 week to complete.

2. **SHARP Integration**: Mock or real first?
   **Answer**: Real. It's the thesis. 1 week to integrate.

3. **Cairo ML**: When to deploy?
   **Answer**: V1.4 (1-2 months). Prove Python works first.

4. **UI**: What's minimum viable?
   **Answer**: Proof display, status badges, list. 1 week.

5. **Timeline**: What's realistic?
   **Answer**: 3-4 weeks to V1.3 complete. 2-3 months to V1.4.

---

**Current Status**: V1.2 production, ready for V1.3

**Next Steps**: 
1. Complete Rust binary (week 1-2)
2. Integrate real SHARP (week 2-3)  
3. Build proof UI (week 3-4)

**Goal**: V1.3 complete in 1 month, V1.4 in 3 months

