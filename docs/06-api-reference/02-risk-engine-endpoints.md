# Risk Engine API Endpoints

This document details the Risk Engine API endpoints for allocation orchestration and execution.

## Base Path

```
/api/v1/risk-engine
```

## POST /orchestrate-allocation

Orchestrates a complete allocation workflow: fetches metrics, generates proof, verifies, and executes.

### Request

**Endpoint:**
```
POST /api/v1/risk-engine/orchestrate-allocation
```

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "jediswap_metrics": {
    "utilization": 6500,
    "volatility": 3500,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800
  },
  "ekubo_metrics": {
    "utilization": 5000,
    "volatility": 2500,
    "liquidity": 2,
    "audit_score": 95,
    "age_days": 600
  }
}
```

**Parameters:**
- `jediswap_metrics` (object, required): JediSwap protocol metrics
- `ekubo_metrics` (object, required): Ekubo protocol metrics

### Response

**Success (200):**
```json
{
  "proof_job_id": "abc123-def456",
  "decision_id": 1,
  "jediswap_pct": 60,
  "ekubo_pct": 40,
  "jediswap_risk": 45,
  "ekubo_risk": 38,
  "proof_hash": "0xa580bd7c3f4e2a1b9c8d5e6f7a2b3c4d5e6f7a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1",
  "fact_hash": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64",
  "transaction_hash": "0x0123456789abcdef...",
  "verification_status": "verified",
  "generated_at": "2026-01-26T12:00:00Z"
}
```

**Error (400/500):**
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE"
}
```

### Example Request

```bash
curl -X POST http://localhost:8001/api/v1/risk-engine/orchestrate-allocation \
  -H "Content-Type: application/json" \
  -d '{
    "jediswap_metrics": {
      "utilization": 6500,
      "volatility": 3500,
      "liquidity": 1,
      "audit_score": 98,
      "age_days": 800
    },
    "ekubo_metrics": {
      "utilization": 5000,
      "volatility": 2500,
      "liquidity": 2,
      "audit_score": 95,
      "age_days": 600
    }
  }'
```

## POST /execute-allocation

Executes a previously generated and verified allocation.

### Request

**Endpoint:**
```
POST /api/v1/risk-engine/execute-allocation
```

**Body:**
```json
{
  "proof_job_id": "abc123-def456"
}
```

**Parameters:**
- `proof_job_id` (string, required): Proof job identifier

### Response

**Success (200):**
```json
{
  "decision_id": 1,
  "transaction_hash": "0x0123456789abcdef...",
  "block_number": 12345,
  "status": "executed",
  "executed_at": "2026-01-26T12:00:00Z"
}
```

### Example Request

```bash
curl -X POST http://localhost:8001/api/v1/risk-engine/execute-allocation \
  -H "Content-Type: application/json" \
  -d '{
    "proof_job_id": "abc123-def456"
  }'
```

## GET /decisions

Retrieves allocation decision history.

### Request

**Endpoint:**
```
GET /api/v1/risk-engine/decisions?page=1&limit=20
```

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20, max: 100)

### Response

**Success (200):**
```json
{
  "decisions": [
    {
      "decision_id": 1,
      "timestamp": "2026-01-26T12:00:00Z",
      "jediswap_pct": 60,
      "ekubo_pct": 40,
      "jediswap_risk": 45,
      "ekubo_risk": 38,
      "proof_hash": "0xa580bd...",
      "transaction_hash": "0x012345...",
      "verification_status": "verified"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## GET /decision/{decision_id}

Retrieves a specific allocation decision.

### Request

**Endpoint:**
```
GET /api/v1/risk-engine/decision/1
```

**Path Parameters:**
- `decision_id` (integer, required): Decision identifier

### Response

**Success (200):**
```json
{
  "decision_id": 1,
  "timestamp": "2026-01-26T12:00:00Z",
  "jediswap_pct": 60,
  "ekubo_pct": 40,
  "jediswap_risk": 45,
  "ekubo_risk": 38,
  "jediswap_apy": 1200,
  "ekubo_apy": 1500,
  "proof_hash": "0xa580bd...",
  "fact_hash": "0x063fee...",
  "transaction_hash": "0x012345...",
  "verification_status": "verified",
  "model_version": "1.0.0"
}
```

**Error (404):**
```json
{
  "detail": "Decision not found",
  "error_code": "DECISION_NOT_FOUND"
}
```

## Error Codes

### Common Errors

**INVALID_METRICS:**
- Invalid protocol metrics format
- Out of range values
- Missing required fields

**PROOF_GENERATION_FAILED:**
- Prover service unavailable
- Trace generation error
- Resource constraints

**VERIFICATION_FAILED:**
- Proof verification error
- Fact Registry error
- Network issues

**TRANSACTION_REVERTED:**
- On-chain execution failed
- Proof not verified
- Constraints violated

## Next Steps

- **[Verification Endpoints](03-verification-endpoints.md)** - Proof verification APIs
- **[Model Registry Endpoints](04-model-registry-endpoints.md)** - Model management APIs
- **[API Overview](01-overview.md)** - General API information

---

**Risk Engine API Summary:** Endpoints for allocation orchestration, execution, and decision history with comprehensive error handling.
