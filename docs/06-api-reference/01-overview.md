# API Overview

This document covers the API base URL, authentication, rate limiting, error handling, and response formats.

## API Base URL

### Production (if available)
```
https://starknet.obsqra.fi/api/v1
```

### Local Development
```
http://localhost:8001/api/v1
```

### Testnet
```
https://api.obsqra.fi/api/v1
```

## Authentication

### Current Status

**No Authentication Required:**
- Public API endpoints
- No API keys needed
- Rate limiting may apply
- Future: API key authentication

### Future Authentication

**Planned:**
- API key authentication
- Rate limit per key
- Usage tracking
- Tiered access

## Rate Limiting

### Current Limits

**Default:**
- No explicit rate limits
- Fair use policy
- May be rate limited if abused

### Future Limits

**Planned:**
- 100 requests/minute (default)
- 1000 requests/minute (authenticated)
- 10000 requests/minute (premium)

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## Error Handling

### HTTP Status Codes

**Success:**
- `200 OK`: Request successful
- `201 Created`: Resource created

**Client Errors:**
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

**Server Errors:**
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format

```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-01-26T12:00:00Z"
}
```

### Common Error Codes

**Validation Errors:**
- `INVALID_METRICS`: Protocol metrics invalid
- `INVALID_PROOF_JOB_ID`: Proof job not found
- `INVALID_FACT_HASH`: Fact hash format error

**Execution Errors:**
- `PROOF_GENERATION_FAILED`: Proof generation error
- `VERIFICATION_FAILED`: Proof verification failed
- `TRANSACTION_REVERTED`: On-chain execution failed

## Response Formats

### JSON Format

**Standard Response:**
```json
{
  "data": {...},
  "status": "success",
  "timestamp": "2026-01-26T12:00:00Z"
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-01-26T12:00:00Z"
}
```

### Data Types

**Numbers:**
- Integers: `123`
- Decimals: `123.45`
- Felt252: Hex string `"0x..."` or integer

**Strings:**
- UTF-8 encoded
- Max length varies by field

**Booleans:**
- `true` or `false`

**Arrays:**
- JSON arrays: `[1, 2, 3]`

**Objects:**
- JSON objects: `{"key": "value"}`

## Request Headers

### Required Headers

**Content-Type:**
```
Content-Type: application/json
```

### Optional Headers

**Accept:**
```
Accept: application/json
```

**User-Agent:**
```
User-Agent: ObsqraClient/1.0
```

## Response Headers

### Standard Headers

**Content-Type:**
```
Content-Type: application/json
```

**Date:**
```
Date: Mon, 26 Jan 2026 12:00:00 GMT
```

### Custom Headers

**X-Request-ID:**
```
X-Request-ID: abc123-def456-ghi789
```

## Pagination

### Paginated Endpoints

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Versioning

### API Version

**Current Version:** `v1`

**Version in URL:**
```
/api/v1/risk-engine/orchestrate-allocation
```

### Versioning Strategy

**Backward Compatible:**
- New fields added (non-breaking)
- Deprecated fields marked
- Migration period provided

**Breaking Changes:**
- New major version (v2)
- Old version maintained
- Migration guide provided

## Next Steps

- **[Risk Engine Endpoints](02-risk-engine-endpoints.md)** - Allocation APIs
- **[Verification Endpoints](03-verification-endpoints.md)** - Proof verification APIs
- **[Model Registry Endpoints](04-model-registry-endpoints.md)** - Model management APIs

---

**API Overview Summary:** RESTful API with JSON responses, standard HTTP status codes, and comprehensive error handling.
