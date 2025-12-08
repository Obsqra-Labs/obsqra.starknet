# Next: Week 2 - Proof UI Components

## Completed ✅
- Backend proof generation
- Database storage
- Basic proof display in alert
- Demo mode removed

## Now: Build Proof Components (Week 2)

### 1. ProofBadge Component (1 hour)
**File**: `frontend/src/components/ProofBadge.tsx`

Shows proof status with color-coded badge:
- 🟡 Generated (yellow)
- 🔵 Submitted (blue) 
- 🟠 Verifying (orange)
- 🟢 Verified (green)

**Features**:
- Truncated proof hash (0xa580...b7ec)
- Status indicator
- Tooltip with full details
- Clickable to show proof modal

### 2. RebalanceHistory Component (2 hours)
**File**: `frontend/src/components/RebalanceHistory.tsx`

Table showing all past rebalances with proofs:

| Time | Allocation | Proof | Transaction |
|------|------------|-------|-------------|
| 2 min ago | Jedi 45% / Ekubo 55% | 🟢 0xa580... | View TX |
| 1 hour ago | Jedi 50% / Ekubo 50% | 🟢 0xb123... | View TX |

**Features**:
- Fetch from `/api/v1/analytics/rebalance-history`
- ProofBadge for each row
- Link to Voyager for transactions
- Auto-refresh every 30s

### 3. Real Performance Endpoint (1 hour)
**File**: `backend/app/api/routes/analytics.py`

```python
@router.get("/analytics/rebalance-history")
async def get_rebalance_history(db: Session):
    # Query proof_jobs table
    # Join with on-chain decision data
    # Return list with proofs
    return [
        {
            "timestamp": ...,
            "jediswap_pct": ...,
            "ekubo_pct": ...,
            "proof_hash": ...,
            "proof_status": ...,
            "tx_hash": ...,
        }
    ]
```

### 4. Add to Dashboard (30 min)
**File**: `frontend/src/components/Dashboard.tsx`

Add new section below allocation chart:
```tsx
<Card title="Rebalance History">
  <RebalanceHistory />
</Card>
```

---

## Implementation Order

1. **Backend endpoint** (30 min)
   - Create `/analytics/rebalance-history`
   - Query proof_jobs table
   - Return JSON with proofs

2. **ProofBadge component** (1 hour)
   - Small, reusable component
   - Color-coded status
   - Tooltip

3. **RebalanceHistory component** (1.5 hours)
   - Fetch from API
   - Table with ProofBadges
   - Auto-refresh

4. **Integrate into Dashboard** (30 min)
   - Add to overview tab
   - Test end-to-end

**Total: ~3.5 hours**

---

## Start With: Backend Endpoint

Let's create the analytics endpoint first, then build UI components around it.

**Ready to start?**

