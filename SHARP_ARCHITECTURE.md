# SHARP Integration Architecture

## Flow with Async SHARP Verification

```
User Request → AI Decision → Generate Proof (2-5s) → Execute TX (instant) → Submit SHARP (async) → Verify (10-60min)
                                                            ↓
                                                    User sees result immediately
                                                            ↓
                                                    Background job tracks SHARP
                                                            ↓
                                                    Frontend shows status updates
```

## Database Schema for Proof Tracking

```sql
CREATE TABLE proof_jobs (
    id UUID PRIMARY KEY,
    tx_hash TEXT NOT NULL,
    proof_hash TEXT NOT NULL,
    sharp_job_id TEXT,
    fact_hash TEXT,
    status TEXT NOT NULL, -- 'generating', 'generated', 'submitted', 'verifying', 'verified', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    submitted_at TIMESTAMP,
    verified_at TIMESTAMP,
    metrics JSONB NOT NULL,
    proof_data BYTEA,
    error TEXT
);

CREATE INDEX idx_proof_jobs_tx_hash ON proof_jobs(tx_hash);
CREATE INDEX idx_proof_jobs_status ON proof_jobs(status);
CREATE INDEX idx_proof_jobs_sharp_job ON proof_jobs(sharp_job_id);
```

## API Endpoints

### 1. Execute with Proof (Async)

```python
@router.post("/orchestrate-allocation")
async def orchestrate_allocation(request: OrchestrationRequest):
    # 1. Generate STARK proof (2-5 seconds)
    proof = await luminair_service.generate_proof(
        jediswap_metrics=request.jediswap_metrics,
        ekubo_metrics=request.ekubo_metrics
    )
    
    # 2. Store proof job
    job = await db.proof_jobs.create({
        "proof_hash": proof.hash,
        "status": "generated",
        "metrics": {
            "jediswap": request.jediswap_metrics.dict(),
            "ekubo": request.ekubo_metrics.dict()
        },
        "proof_data": proof.binary_data
    })
    
    # 3. Execute transaction IMMEDIATELY
    tx = await account.execute_v3(
        calls=[
            propose_and_execute_allocation(
                request.jediswap_metrics,
                request.ekubo_metrics
            )
        ]
    )
    
    # 4. Update job with tx hash
    await db.proof_jobs.update(job.id, {
        "tx_hash": hex(tx.transaction_hash),
        "status": "submitted"
    })
    
    # 5. Submit to SHARP in background (non-blocking)
    asyncio.create_task(
        sharp_submission_task(job.id, proof)
    )
    
    # 6. Return immediately to user
    return {
        "tx_hash": hex(tx.transaction_hash),
        "proof_job_id": str(job.id),
        "proof_hash": proof.hash,
        "status": "executed",
        "sharp_status": "pending",
        "verification_url": f"/api/v1/proofs/{job.id}"
    }
```

### 2. Check Proof Status

```python
@router.get("/proofs/{job_id}")
async def get_proof_status(job_id: UUID):
    job = await db.proof_jobs.get(job_id)
    
    return {
        "job_id": str(job.id),
        "tx_hash": job.tx_hash,
        "proof_hash": job.proof_hash,
        "sharp_job_id": job.sharp_job_id,
        "fact_hash": job.fact_hash,
        "status": job.status,
        "created_at": job.created_at.isoformat(),
        "submitted_at": job.submitted_at.isoformat() if job.submitted_at else None,
        "verified_at": job.verified_at.isoformat() if job.verified_at else None,
        "elapsed_seconds": (datetime.now() - job.submitted_at).seconds if job.submitted_at else None,
        "estimated_completion": estimate_completion_time(job),
        "verification_url": f"https://sepolia.voyager.online/proof/{job.fact_hash}" if job.fact_hash else None
    }
```

### 3. List Recent Proofs

```python
@router.get("/proofs")
async def list_proofs(
    status: Optional[str] = None,
    limit: int = 20
):
    query = db.proof_jobs.query()
    
    if status:
        query = query.filter(status=status)
    
    jobs = await query.order_by("-created_at").limit(limit).all()
    
    return {
        "proofs": [serialize_job(job) for job in jobs],
        "stats": {
            "generating": await db.proof_jobs.count(status="generating"),
            "verifying": await db.proof_jobs.count(status="verifying"),
            "verified": await db.proof_jobs.count(status="verified"),
            "failed": await db.proof_jobs.count(status="failed")
        }
    }
```

## Background Worker

```python
# sharp_worker.py
async def sharp_submission_task(job_id: UUID, proof: ProofResult):
    """
    Background task to submit proof to SHARP and monitor verification
    """
    try:
        # Update status
        await db.proof_jobs.update(job_id, {"status": "submitting_sharp"})
        
        # Submit to SHARP
        sharp_result = await sharp_service.submit_proof(
            proof_data=proof.binary_data,
            proof_hash=proof.hash
        )
        
        # Update with SHARP job ID
        await db.proof_jobs.update(job_id, {
            "sharp_job_id": sharp_result.job_id,
            "status": "verifying",
            "submitted_at": datetime.now()
        })
        
        logger.info(f"Proof {job_id} submitted to SHARP: {sharp_result.job_id}")
        
        # Monitor verification (10-60 minutes)
        await monitor_sharp_verification(job_id, sharp_result.job_id)
        
    except Exception as e:
        logger.error(f"SHARP submission failed for {job_id}: {e}")
        await db.proof_jobs.update(job_id, {
            "status": "failed",
            "error": str(e)
        })


async def monitor_sharp_verification(job_id: UUID, sharp_job_id: str):
    """
    Poll SHARP every 30 seconds until verification complete
    """
    max_wait = 3600  # 1 hour timeout
    poll_interval = 30  # 30 seconds
    elapsed = 0
    
    while elapsed < max_wait:
        try:
            # Check SHARP status
            status = await sharp_service.check_status(sharp_job_id)
            
            if status.state == "VERIFIED":
                # Success!
                await db.proof_jobs.update(job_id, {
                    "status": "verified",
                    "fact_hash": status.fact_hash,
                    "verified_at": datetime.now()
                })
                
                logger.info(f"Proof {job_id} verified! Fact: {status.fact_hash}")
                
                # Trigger webhook/notification
                await notify_verification_complete(job_id)
                return
                
            elif status.state == "FAILED":
                # Failed
                await db.proof_jobs.update(job_id, {
                    "status": "failed",
                    "error": status.error
                })
                logger.error(f"SHARP verification failed for {job_id}: {status.error}")
                return
                
            # Still processing, wait and retry
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
        except Exception as e:
            logger.error(f"Error checking SHARP status for {job_id}: {e}")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
    
    # Timeout
    await db.proof_jobs.update(job_id, {
        "status": "timeout",
        "error": "SHARP verification timeout after 1 hour"
    })
```

## Frontend Integration

### React Hook

```typescript
// useProofStatus.ts
export function useProofStatus(jobId: string) {
  const [status, setStatus] = useState<ProofStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      const response = await fetch(`/api/v1/proofs/${jobId}`);
      const data = await response.json();
      setStatus(data);
      setLoading(false);
    };

    // Poll every 10 seconds if still verifying
    const interval = setInterval(fetchStatus, 10000);
    fetchStatus();

    return () => clearInterval(interval);
  }, [jobId]);

  return { status, loading };
}
```

### Status Display Component

```typescript
// ProofStatusBadge.tsx
export function ProofStatusBadge({ jobId }: { jobId: string }) {
  const { status, loading } = useProofStatus(jobId);

  if (loading) return <Spinner />;

  const statusConfig = {
    generated: { color: 'blue', icon: '🔨', text: 'Proof Generated' },
    submitted: { color: 'yellow', icon: '📤', text: 'Tx Submitted' },
    verifying: { color: 'orange', icon: '⏳', text: 'Verifying on SHARP' },
    verified: { color: 'green', icon: '✓', text: 'Verified on-chain' },
    failed: { color: 'red', icon: '✗', text: 'Verification Failed' }
  };

  const config = statusConfig[status.status];

  return (
    <div className={`badge badge-${config.color}`}>
      <span>{config.icon}</span>
      <span>{config.text}</span>
      {status.status === 'verifying' && (
        <span className="text-sm">
          ({status.elapsed_seconds}s / ~{status.estimated_completion}s)
        </span>
      )}
      {status.fact_hash && (
        <a href={status.verification_url} target="_blank" className="ml-2">
          View Proof →
        </a>
      )}
    </div>
  );
}
```

### Dashboard Integration

```typescript
// Dashboard.tsx
export function Dashboard() {
  const [proofJobs, setProofJobs] = useState<ProofJob[]>([]);

  return (
    <div>
      <h2>Recent Allocations</h2>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Transaction</th>
            <th>Proof Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {proofJobs.map(job => (
            <tr key={job.id}>
              <td>{formatTime(job.created_at)}</td>
              <td>
                <a href={`https://sepolia.voyager.online/tx/${job.tx_hash}`}>
                  {truncate(job.tx_hash)}
                </a>
              </td>
              <td>
                <ProofStatusBadge jobId={job.id} />
              </td>
              <td>
                <button onClick={() => downloadProof(job.proof_hash)}>
                  Download Proof
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## SHARP Service Implementation

```python
# backend/app/services/sharp_service.py
import httpx
from typing import Optional

class SHARPService:
    def __init__(self):
        self.gateway_url = "https://sharp-gateway.starknet.io"  # Sepolia
        self.api_key = os.getenv("SHARP_API_KEY")  # If required
    
    async def submit_proof(
        self,
        proof_data: bytes,
        proof_hash: str
    ) -> SHARPSubmission:
        """
        Submit STARK proof to SHARP gateway
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.gateway_url}/submit",
                files={"proof": proof_data},
                data={"proof_hash": proof_hash},
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                timeout=30.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            return SHARPSubmission(
                job_id=data["job_id"],
                status="submitted"
            )
    
    async def check_status(
        self,
        job_id: str
    ) -> SHARPStatus:
        """
        Check verification status of SHARP job
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.gateway_url}/status/{job_id}",
                timeout=10.0
            )
            
            response.raise_for_status()
            data = response.json()
            
            return SHARPStatus(
                job_id=job_id,
                state=data["state"],  # PENDING, PROCESSING, VERIFIED, FAILED
                fact_hash=data.get("fact_hash"),
                block_number=data.get("block_number"),
                error=data.get("error")
            )
```

## User Experience Flow

### 1. User Executes Allocation

```
User clicks "Execute AI Allocation"
    ↓ (2-5 seconds)
Frontend shows: "Generating cryptographic proof..."
    ↓ (instant)
Frontend shows: "✓ Transaction executed!"
                "⏳ Submitting proof to SHARP for verification"
                "Your allocation is active. Verification in progress."
    ↓
User can continue using the app
```

### 2. Background Verification

```
(10-60 minutes later, user may or may not be online)

Backend polls SHARP every 30 seconds
    ↓
SHARP returns: "VERIFIED", fact_hash="0x..."
    ↓
Backend updates database: status="verified"
    ↓
Frontend auto-updates (if user still online)
    OR
User receives notification: "Proof verified on-chain!"
```

### 3. Audit Trail

```
Anyone can:
1. Visit obsqra.fi/proofs
2. See all allocations with proof hashes
3. Download proof data
4. Verify locally: `luminair verify proof.bin`
5. Check on Starknet: voyager.online/proof/{fact_hash}
```

## Benefits

1. **Instant Execution**: User doesn't wait 60 minutes
2. **Full Verification**: SHARP verifies on L1
3. **Transparent**: Anyone can verify proofs
4. **Auditable**: Permanent on-chain record
5. **Professional**: Async job tracking system

## Timeline

- **Proof Generation**: 2-5 seconds (blocks user)
- **Transaction Execution**: 10-30 seconds (blocks user)
- **SHARP Submission**: 1-2 seconds (async, doesn't block)
- **SHARP Verification**: 10-60 minutes (async, user notified)

**Total user-facing latency**: ~10-35 seconds

**Full verification**: 10-60 minutes (background)

---

**This is production-grade verifiable AI with L1 settlement.**

