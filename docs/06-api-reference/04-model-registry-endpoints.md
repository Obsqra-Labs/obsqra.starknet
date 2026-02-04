# Model Registry API Endpoints

This document details the Model Registry API endpoints for model version management and history.

## Base Path

```
/api/v1/model-registry
```

## GET /current

Retrieves the current active model version.

### Request

**Endpoint:**
```
GET /api/v1/model-registry/current
```

### Response

**Success (200):**
```json
{
  "registry_address": "0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc",
  "version_felt": "0x010000",
  "version": "1.0.0",
  "model_hash_felt": "0x06ab2595...",
  "model_hash": "0x06ab2595...",
  "deployed_at": 1706268000,
  "description": "Initial risk scoring model",
  "is_active": true
}
```

**Error (404):**
```json
{
  "detail": "No model registered",
  "error_code": "NO_MODEL_REGISTERED"
}
```

### Example Request

```bash
curl http://localhost:8001/api/v1/model-registry/current
```

## GET /history

Retrieves the complete model version history.

### Request

**Endpoint:**
```
GET /api/v1/model-registry/history
```

### Response

**Success (200):**
```json
{
  "registry_address": "0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc",
  "versions": [
    {
      "registry_address": "0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc",
      "version_felt": "0x010000",
      "version": "1.0.0",
      "model_hash_felt": "0x06ab2595...",
      "model_hash": "0x06ab2595...",
      "deployed_at": 1706268000,
      "description": "Initial risk scoring model",
      "is_active": true
    }
  ]
}
```

### Example Request

```bash
curl http://localhost:8001/api/v1/model-registry/history
```

## GET /version/{version}

Retrieves a specific model version.

### Request

**Endpoint:**
```
GET /api/v1/model-registry/version/{version}
```

**Path Parameters:**
- `version` (string, required): Version number (e.g., "1.0.0" or "0x010000")

### Response

**Success (200):**
```json
{
  "registry_address": "0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc",
  "version_felt": "0x010000",
  "version": "1.0.0",
  "model_hash_felt": "0x06ab2595...",
  "model_hash": "0x06ab2595...",
  "deployed_at": 1706268000,
  "description": "Initial risk scoring model",
  "is_active": true
}
```

**Error (404):**
```json
{
  "detail": "Model version not found",
  "error_code": "VERSION_NOT_FOUND"
}
```

### Example Request

```bash
curl http://localhost:8001/api/v1/model-registry/version/1.0.0
```

## POST /register

Registers a new model version (admin only).

### Request

**Endpoint:**
```
POST /api/v1/model-registry/register
```

**Headers:**
```
Content-Type: application/json
X-Admin-Key: <admin_key>
```

**Body:**
```json
{
  "version": "1.0.0",
  "model_hash": "0x06ab2595...",
  "description": "Initial risk scoring model"
}
```

**Parameters:**
- `version` (string, optional): Version (semantic or felt252 hex)
- `model_hash` (string, optional): Model hash (hex string)
- `description` (string, optional): Human-readable description

### Response

**Success (200):**
```json
{
  "transaction_hash": "0x0123456789abcdef...",
  "model": {
    "registry_address": "0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc",
    "version_felt": "0x010000",
    "version": "1.0.0",
    "model_hash_felt": "0x06ab2595...",
    "model_hash": "0x06ab2595...",
    "deployed_at": 1706268000,
    "description": "Initial risk scoring model",
    "is_active": true
  }
}
```

**Error (403):**
```json
{
  "detail": "Invalid admin key",
  "error_code": "INVALID_ADMIN_KEY"
}
```

### Example Request

```bash
curl -X POST http://localhost:8001/api/v1/model-registry/register \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: <admin_key>" \
  -d '{
    "version": "1.0.0",
    "model_hash": "0x06ab2595...",
    "description": "Initial risk scoring model"
  }'
```

## Version Format

### Semantic Versioning

**Format:** `MAJOR.MINOR.PATCH`
**Example:** `1.0.0`

**Conversion to felt252:**
```
(major << 16) + (minor << 8) + patch
```

**Example:**
- `1.0.0` → `0x010000`
- `1.1.0` → `0x010100`
- `2.0.0` → `0x020000`

### Felt252 Format

**Format:** Hex string with `0x` prefix
**Example:** `0x010000`

**Accepted in API:**
- Semantic version: `"1.0.0"`
- Felt252 hex: `"0x010000"`
- Integer: `65536`

## Error Codes

### Common Errors

**NO_MODEL_REGISTERED:**
- No model has been registered yet
- Registry is empty

**VERSION_NOT_FOUND:**
- Version doesn't exist
- Invalid version format

**INVALID_ADMIN_KEY:**
- Admin key missing or invalid
- Unauthorized access

**REGISTRATION_FAILED:**
- On-chain registration failed
- Transaction reverted
- Network error

## Next Steps

- **[Risk Engine Endpoints](02-risk-engine-endpoints.md)** - Allocation APIs
- **[Verification Endpoints](03-verification-endpoints.md)** - Proof verification APIs
- **[API Overview](01-overview.md)** - General API information

---

**Model Registry API Summary:** Endpoints for model version management, history tracking, and registration with admin authentication.
