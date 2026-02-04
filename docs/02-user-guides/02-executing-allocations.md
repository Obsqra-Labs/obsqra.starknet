# Executing Allocations

This guide explains how allocation decisions work, the proof generation process, verification status checking, and understanding allocation results.

## How Allocation Decisions Work

### The Allocation Process

Allocation decisions in Obsqra follow a deterministic, verifiable process:

```
1. Protocol Metrics Collection
   ↓
2. Risk Score Calculation
   ↓
3. Allocation Optimization
   ↓
4. Proof Generation
   ↓
5. On-Chain Verification
   ↓
6. Execution
```

### Step 1: Protocol Metrics Collection

The system collects real-time metrics from each protocol:

**JediSwap Metrics:**
- Utilization: Current pool utilization percentage
- Volatility: Price volatility over time period
- Liquidity: Total liquidity in pool
- Audit Score: Security audit rating (0-100)
- Age Days: Days since protocol launch

**Ekubo Metrics:**
- Same metrics as JediSwap
- Protocol-specific calculations

**Metrics Source:**
- On-chain data queries
- Protocol APIs
- Historical analysis

### Step 2: Risk Score Calculation

Risk scores are calculated using a deterministic formula:

```
Risk Score = (
    utilization * 35 +
    volatility * 30 +
    liquidity * 5 +
    audit_score * 20 +
    age_penalty
) / 10000
```

**Risk Score Range:** 5-95
- **Lower = Safer:** Lower risk protocols
- **Higher = Riskier:** Higher risk protocols

**Age Penalty:**
- Newer protocols have higher risk
- Older protocols have lower risk
- Based on days since launch

### Step 3: Allocation Optimization

Allocation is calculated based on:

1. **Risk-Adjusted APY:**
   ```
   Allocation = (APY * 10000) / (Risk + 1)
   ```

2. **Constraint Enforcement:**
   - Maximum single protocol allocation (DAO-defined)
   - Minimum diversification requirement
   - Volatility limits
   - Liquidity requirements

3. **Optimization:**
   - Maximize risk-adjusted returns
   - Respect all constraints
   - Balance across protocols

### Step 4: Proof Generation

**What Gets Proven:**
- Risk score calculations for each protocol
- Allocation calculation
- Constraint verification

**Proof Generation:**
1. Cairo execution trace generation
2. STARK proof creation (Stone Prover)
3. Fact hash calculation
4. Proof serialization

**Proof Properties:**
- **Size:** ~400-500 KB
- **Generation Time:** 2-4 seconds
- **Verification Time:** <1 second

### Step 5: On-Chain Verification

Before execution, the contract verifies:

1. **Proof Exists:**
   - Queries SHARP Fact Registry
   - Verifies fact hash is registered

2. **Scores Match:**
   - On-chain risk calculation
   - Compares with proof scores
   - Must match exactly

3. **Constraints Valid:**
   - Checks DAO constraints
   - Verifies allocation respects limits

### Step 6: Execution

If all verifications pass:
1. Allocation percentages are set
2. StrategyRouter is called
3. Funds are rebalanced
4. Events are emitted
5. Transaction is confirmed

## Proof Generation Process

### Understanding STARK Proofs

**What is a STARK Proof?**
- Cryptographic proof that computation was correct
- Verifiable by anyone
- Cannot be forged
- Permanent record

**What Does It Prove?**
- Risk scores were calculated correctly
- Allocation follows the model
- Constraints were respected
- Inputs match outputs

### Proof Generation Timeline

```
T+0s:   User clicks "Orchestrate Allocation"
T+0.5s: Backend receives request
T+1s:   Protocol metrics fetched
T+2s:   Risk scores calculated
T+3s:   Proof generation starts
T+5s:   Proof generated (2-4s generation)
T+6s:   Proof verified locally
T+7s:   Proof submitted to Fact Registry
T+8s:   Fact hash registered
T+9s:   Transaction prepared
T+10s:  Transaction submitted
T+22s:  Transaction confirmed (12s block time)
```

### Proof Generation Status

**Status Indicators:**
- ⏳ **Generating:** Proof being created (2-4s)
- ✅ **Generated:** Proof created successfully
- ⏳ **Verifying:** Proof being verified
- ✅ **Verified:** Proof verified and registered
- ❌ **Failed:** Proof generation or verification failed

### Proof Artifacts

**Proof Hash:**
- Unique identifier for the proof
- Example: `0xa580bd7c3f4e2a1b9c8d5e6f7a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1`
- Permanent record
- Verifiable independently

**Fact Hash:**
- SHARP fact registry identifier
- Used for on-chain verification
- Links proof to registry

**Proof Size:**
- Typically 400-500 KB
- Includes all verification data
- Downloadable for independent verification

## Verification Status Checking

### How to Check Verification Status

**In the UI:**
1. Navigate to allocation history
2. Find your allocation
3. Check verification status badge:
   - ✅ **Verified:** Proof is valid
   - ⏳ **Pending:** Verification in progress
   - ❌ **Failed:** Verification failed

**Via API:**
```bash
curl https://api.obsqra.fi/api/v1/verification/verification-status/{proof_job_id}
```

**Response:**
```json
{
  "proof_job_id": "abc123",
  "status": "verified",
  "fact_hash": "0x...",
  "verified_at": "2026-01-26T12:00:00Z",
  "fact_registry_address": "0x..."
}
```

### Verification States

**1. Pending Verification**
- Proof generated
- Submitted to Fact Registry
- Waiting for registration

**2. Verified**
- Proof registered in Fact Registry
- Fact hash available
- Ready for on-chain execution

**3. Verification Failed**
- Proof invalid or corrupted
- Fact Registry rejection
- Cannot execute

### Independent Verification

You can verify proofs yourself:

**Using Verifier Tool:**
1. Download proof from API
2. Use STARK verifier tool
3. Verify against public inputs
4. Confirm correctness

**On-Chain Verification:**
1. Query Fact Registry contract
2. Check if fact hash exists
3. Verify proof is registered

## Execution Confirmation

### Transaction Confirmation

**What to Expect:**
- Transaction submitted to Starknet
- Block confirmation in ~12 seconds
- On-chain events emitted
- Allocation updated

**Confirmation Indicators:**
- Transaction hash displayed
- Starkscan link provided
- Status changes to "Confirmed"
- Allocation percentages updated

### Transaction Details

**Transaction Hash:**
- Links to Starkscan explorer
- Shows all events
- Includes gas fees

**Block Information:**
- Block number
- Block timestamp
- Confirmation time

**Events Emitted:**
- `AllocationProposed`: Allocation decision
- `AllocationExecuted`: Execution confirmation
- `ConstraintsValidated`: Constraint verification
- `ModelRegistered`: Model version (if applicable)

## Understanding Allocation Results

### Allocation Decision Structure

**Allocation Percentages:**
- JediSwap: X%
- Ekubo: Y%
- Total: 100% (always)

**Risk Scores:**
- JediSwap Risk: 0-95
- Ekubo Risk: 0-95
- Lower = safer

**APY Values:**
- JediSwap APY: Annual percentage yield
- Ekubo APY: Annual percentage yield
- Risk-adjusted returns

**DAO Constraints:**
- Max Single Protocol: Maximum allocation per protocol
- Min Diversification: Minimum spread requirement
- Applied and verified

### Performance Metrics

**Expected Performance:**
- Risk-adjusted APY
- Diversification score
- Constraint compliance

**Historical Performance:**
- Past allocation decisions
- Actual returns
- Performance tracking

### Proof Information

**Proof Hash:**
- Cryptographic proof identifier
- Verifiable independently
- Permanent record

**Verification Status:**
- On-chain verification status
- Fact Registry confirmation
- Trustless verification

**Model Version:**
- Model used for calculation
- Model hash
- Version history

## Common Scenarios

### Scenario 1: Successful Allocation

**What Happens:**
1. Metrics collected ✅
2. Risk scores calculated ✅
3. Proof generated ✅
4. Proof verified ✅
5. On-chain verification ✅
6. Allocation executed ✅

**Result:**
- New allocation percentages
- Proof hash available
- Transaction confirmed
- Funds rebalanced

### Scenario 2: Proof Generation Failure

**What Happens:**
1. Metrics collected ✅
2. Risk scores calculated ✅
3. Proof generation fails ❌

**Result:**
- Error message displayed
- No transaction submitted
- Can retry allocation

**Common Causes:**
- Prover service unavailable
- Trace generation error
- Resource constraints

### Scenario 3: Verification Failure

**What Happens:**
1. Proof generated ✅
2. Verification fails ❌

**Result:**
- Proof not registered
- Transaction cannot execute
- Error message displayed

**Common Causes:**
- Invalid proof format
- Fact Registry error
- Network issues

## Best Practices

1. **Monitor Verification Status**
   - Check status before execution
   - Wait for verification confirmation
   - Verify independently if needed

2. **Understand Allocation Logic**
   - Review risk scores
   - Check constraint compliance
   - Understand APY calculations

3. **Track Proof Hashes**
   - Save proof hashes
   - Verify independently
   - Maintain audit trail

4. **Monitor Performance**
   - Track allocation decisions
   - Review historical performance
   - Adjust strategy if needed

## Next Steps

- **[Viewing Transparency](03-viewing-transparency.md)** - Learn about proof verification
- **[Troubleshooting](04-troubleshooting.md)** - Common issues and solutions
- **[Architecture Deep Dive](../03-architecture/01-system-overview.md)** - Technical details

---

**Key Takeaway:** Every allocation is cryptographically proven, verifiable, and executed only after on-chain verification confirms the proof is valid.
