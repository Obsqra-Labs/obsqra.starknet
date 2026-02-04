# Viewing Transparency

This guide explains how to view and verify proof information, model versions, verification status, and navigate the audit trail.

## Proof Hash Verification

### What is a Proof Hash?

A proof hash is a unique cryptographic identifier for a STARK proof. It represents:
- The computation that was proven
- The inputs and outputs
- The verification status
- A permanent audit record

**Example Proof Hash:**
```
0xa580bd7c3f4e2a1b9c8d5e6f7a2b3c4d5e6f7a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1
```

### Where to Find Proof Hashes

**In the UI:**
1. Navigate to allocation history
2. Click on any allocation
3. View "Proof Hash" section
4. Copy or click to explore

**Via API:**
```bash
curl https://api.obsqra.fi/api/v1/proofs/{proof_job_id}
```

**Response:**
```json
{
  "proof_job_id": "abc123",
  "proof_hash": "0xa580bd...",
  "fact_hash": "0x063fee...",
  "status": "verified",
  "generated_at": "2026-01-26T12:00:00Z"
}
```

### Verifying Proof Hashes

**Independent Verification:**
1. Copy the proof hash
2. Use STARK verifier tool
3. Verify against public inputs
4. Confirm proof validity

**On-Chain Verification:**
1. Query Fact Registry contract
2. Check if fact hash exists
3. Verify registration timestamp
4. Confirm proof is valid

## Model Version Information

### Understanding Model Versions

The risk calculation model can be upgraded over time. Each version is:
- Tracked on-chain in ModelRegistry
- Hashed for integrity verification
- Versioned with semantic versioning
- Described with metadata

### Viewing Current Model

**In the UI:**
1. Navigate to "Model Information" section
2. View current model version
3. See model hash
4. Check deployment date

**Via API:**
```bash
curl https://api.obsqra.fi/api/v1/model-registry/current
```

**Response:**
```json
{
  "version": "1.0.0",
  "model_hash": "0x06ab2595...",
  "deployed_at": 1706268000,
  "description": "Initial risk scoring model",
  "is_active": true
}
```

### Model Version History

**Viewing History:**
1. Navigate to "Model History"
2. See all previous versions
3. View upgrade timeline
4. Check model changes

**Via API:**
```bash
curl https://api.obsqra.fi/api/v1/model-registry/history
```

**Response:**
```json
{
  "versions": [
    {
      "version": "1.0.0",
      "model_hash": "0x06ab2595...",
      "deployed_at": 1706268000,
      "description": "Initial risk scoring model"
    }
  ]
}
```

### Model Hash Verification

**What is a Model Hash?**
- SHA-256 hash of model code
- Ensures model integrity
- Prevents tampering
- Verifiable independently

**Verifying Model Hash:**
1. Get model code from contract
2. Calculate SHA-256 hash
3. Compare with registered hash
4. Confirm match

## Verification Status Indicators

### Status Types

**✅ Verified:**
- Proof is valid
- Registered in Fact Registry
- Ready for execution
- On-chain verification passed

**⏳ Pending:**
- Proof generated
- Verification in progress
- Waiting for Fact Registry
- Not yet executable

**❌ Failed:**
- Proof invalid
- Verification rejected
- Cannot execute
- Error details available

### Understanding Status Flow

```
Proof Generated
    ↓
Submitted to Fact Registry
    ↓
⏳ Pending Verification
    ↓
Fact Hash Registered
    ↓
✅ Verified
    ↓
Ready for Execution
```

### Checking Verification Status

**In the UI:**
1. View allocation details
2. Check verification badge
3. See status message
4. View verification timestamp

**Via API:**
```bash
curl https://api.obsqra.fi/api/v1/verification/verification-status/{proof_job_id}
```

**Response:**
```json
{
  "proof_job_id": "abc123",
  "status": "verified",
  "fact_hash": "0x063fee...",
  "verified_at": "2026-01-26T12:00:00Z",
  "fact_registry_address": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"
}
```

## Fact Registry Lookup

### What is the Fact Registry?

The Fact Registry (SHARP) is an on-chain contract that stores verified computation facts. It:
- Registers proof fact hashes
- Enables on-chain verification
- Provides immutable records
- Supports trustless verification

### Fact Registry Address

**Sepolia Testnet:**
```
0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64
```

### Looking Up Facts

**Via Contract Call:**
1. Connect to Fact Registry contract
2. Call `get_all_verifications_for_fact_hash(fact_hash)`
3. Check if array is non-empty
4. Verify fact exists

**Via API:**
```bash
curl https://api.obsqra.fi/api/v1/verification/verify-fact-hash/{fact_hash}
```

**Response:**
```json
{
  "fact_hash": "0x063fee...",
  "verified": true,
  "verifications": [
    {
      "verifier": "0x...",
      "timestamp": 1706268000
    }
  ]
}
```

### Understanding Fact Hashes

**Fact Hash vs Proof Hash:**
- **Proof Hash:** Identifier for the proof artifact
- **Fact Hash:** Identifier in Fact Registry
- Both are related but different
- Fact hash is used for on-chain verification

## Audit Trail Navigation

### What is the Audit Trail?

The audit trail is a complete, immutable record of:
- All allocation decisions
- Proof hashes for each decision
- Model versions used
- Verification status
- Transaction hashes
- Performance metrics

### Accessing the Audit Trail

**In the UI:**
1. Navigate to "Allocation History"
2. View chronological list
3. Filter by date, status, or protocol
4. Click for detailed view

**Via API:**
```bash
curl https://api.obsqra.fi/api/v1/risk-engine/decisions
```

**Response:**
```json
{
  "decisions": [
    {
      "decision_id": 1,
      "timestamp": 1706268000,
      "jediswap_pct": 60,
      "ekubo_pct": 40,
      "proof_hash": "0xa580bd...",
      "transaction_hash": "0x012345...",
      "verification_status": "verified"
    }
  ]
}
```

### Audit Trail Components

**For Each Decision:**
1. **Decision ID:** Unique identifier
2. **Timestamp:** When decision was made
3. **Allocation Percentages:** JediSwap and Ekubo
4. **Risk Scores:** For each protocol
5. **APY Values:** Current yields
6. **Proof Hash:** Cryptographic proof
7. **Transaction Hash:** On-chain execution
8. **Verification Status:** Proof validity
9. **Model Version:** Model used
10. **Performance Metrics:** Results

### Filtering and Searching

**Filter Options:**
- Date range
- Verification status
- Protocol allocation
- Model version
- Performance metrics

**Search Options:**
- Proof hash
- Transaction hash
- Decision ID
- Model hash

### Exporting Audit Data

**Export Formats:**
- CSV: Spreadsheet format
- JSON: Structured data
- PDF: Report format

**Export Contents:**
- All decisions in date range
- Proof hashes
- Verification status
- Performance metrics
- Model versions

## Transparency Dashboard

### Dashboard Overview

The transparency dashboard provides:
- Real-time verification status
- Model version information
- Proof hash display
- Fact registry links
- Audit trail access

### Key Sections

**1. Current Status:**
- Latest allocation
- Current verification status
- Active model version
- Recent proof hash

**2. Verification Status:**
- All pending verifications
- Recent verified proofs
- Failed verifications
- Verification timeline

**3. Model Information:**
- Current model version
- Model hash
- Deployment date
- Version history

**4. Proof Information:**
- Latest proof hash
- Fact hash
- Verification status
- Registry links

### Real-Time Updates

**Auto-Refresh:**
- Status updates every 10 seconds
- New allocations appear automatically
- Verification status updates
- Model changes notified

**Manual Refresh:**
- Click refresh button
- Reload page
- Clear cache if needed

## Best Practices

### 1. Regular Verification Checks

- Verify proof hashes periodically
- Check model version changes
- Monitor verification status
- Review audit trail regularly

### 2. Independent Verification

- Download proofs for verification
- Use verifier tools
- Check Fact Registry directly
- Verify model hashes

### 3. Audit Trail Maintenance

- Export audit data regularly
- Archive historical decisions
- Track model upgrades
- Monitor performance trends

### 4. Transparency Monitoring

- Watch for verification failures
- Monitor model upgrades
- Track proof generation success
- Review performance metrics

## Troubleshooting

### Proof Hash Not Found

**Issue:** Proof hash doesn't appear in UI

**Solutions:**
- Check allocation was completed
- Verify backend is running
- Check API connectivity
- Review transaction logs

### Verification Status Stuck

**Issue:** Status remains "Pending"

**Solutions:**
- Wait for Fact Registry confirmation
- Check network connectivity
- Verify Fact Registry is operational
- Review backend logs

### Model Version Mismatch

**Issue:** Model version doesn't match expected

**Solutions:**
- Check for recent upgrades
- Verify model registry
- Review upgrade history
- Contact support if needed

## Next Steps

- **[Troubleshooting](04-troubleshooting.md)** - Common issues and solutions
- **[Architecture Deep Dive](../03-architecture/01-system-overview.md)** - Technical details
- **[Novel Features](../04-novel-features/03-transparency-dashboard.md)** - Transparency features

---

**Key Takeaway:** Complete transparency means every decision is verifiable, every model is tracked, and every proof is auditable.
