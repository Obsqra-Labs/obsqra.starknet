# Verification API Endpoints

This document details the verification API endpoints for checking proof verification status and fact hash verification.

## Base Path

```
/api/v1/verification
```

## GET /verification-status/{proof_job_id}

Checks the verification status of a proof job.

### Request

**Endpoint:**
```
GET /api/v1/verification/verification-status/{proof_job_id}
```

**Path Parameters:**
- `proof_job_id` (string, required): Proof job identifier

### Response

**Success (200):**
```json
{
  "proof_job_id": "abc123-def456",
  "fact_hash": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64",
  "verified": true,
  "verified_at": "2026-01-26T12:00:00Z",
  "fact_registry_address": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"
}
```

**Not Verified:**
```json
{
  "proof_job_id": "abc123-def456",
  "fact_hash": null,
  "verified": false,
  "verified_at": null,
  "fact_registry_address": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64"
}
```

**Error (404):**
```json
{
  "detail": "Proof job not found",
  "error_code": "PROOF_JOB_NOT_FOUND"
}
```

### Example Request

```bash
curl http://localhost:8001/api/v1/verification/verification-status/abc123-def456
```

## GET /verify-fact-hash/{fact_hash}

Verifies if a fact hash exists in the Fact Registry on-chain.

### Request

**Endpoint:**
```
GET /api/v1/verification/verify-fact-hash/{fact_hash}
```

**Path Parameters:**
- `fact_hash` (string, required): Fact hash (hex string with 0x prefix)

### Response

**Success (200):**
```json
{
  "fact_hash": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64",
  "fact_registry": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64",
  "note": "Use sncast to verify on-chain: sncast call --contract-address <registry> --function get_all_verifications_for_fact_hash --arguments <fact_hash>"
}
```

### Example Request

```bash
curl http://localhost:8001/api/v1/verification/verify-fact-hash/0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64
```

## Verification Status Values

### Status Types

**verified:**
- Proof is valid
- Registered in Fact Registry
- Ready for execution
- On-chain verification passed

**pending:**
- Proof generated
- Verification in progress
- Waiting for Fact Registry
- Not yet executable

**failed:**
- Proof invalid
- Verification rejected
- Cannot execute
- Error details available

## Fact Hash Format

### Format

**Type:** Hex string
**Prefix:** `0x`
**Length:** 64 characters (32 bytes)
**Example:** `0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64`

### Validation

**Valid:**
- Starts with `0x`
- 64 hex characters
- Valid hex digits (0-9, a-f)

**Invalid:**
- Missing `0x` prefix
- Wrong length
- Invalid characters

## Error Codes

### Common Errors

**PROOF_JOB_NOT_FOUND:**
- Proof job ID doesn't exist
- Invalid format
- Deleted or expired

**INVALID_FACT_HASH:**
- Fact hash format error
- Invalid hex string
- Wrong length

**VERIFICATION_FAILED:**
- Proof verification error
- Fact Registry error
- Network issues

## Next Steps

- **[Model Registry Endpoints](04-model-registry-endpoints.md)** - Model management APIs
- **[Risk Engine Endpoints](02-risk-engine-endpoints.md)** - Allocation APIs
- **[API Overview](01-overview.md)** - General API information

---

**Verification API Summary:** Endpoints for checking proof verification status and fact hash verification with comprehensive status tracking.
