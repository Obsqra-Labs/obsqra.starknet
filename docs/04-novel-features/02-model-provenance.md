# Model Provenance

This document explains model version tracking, on-chain model registry, model hash commitment, upgradeability with audit trail, and version history.

## Model Version Tracking

### Overview

Model provenance ensures that every risk calculation can be traced back to the exact model version used. This provides:

- **Transparency:** Know which model was used for each decision
- **Auditability:** Complete history of model changes
- **Integrity:** Model hash verification prevents tampering
- **Accountability:** Clear upgrade path with governance

### Version Management

**Semantic Versioning:**
- Format: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`)
- Stored as felt252: `(major << 16) + (minor << 8) + patch`
- Current version: `1.0.0` (0x010000)

**Version Storage:**
- On-chain in ModelRegistry contract
- Immutable once registered
- Chronological history
- Active version tracking

## On-Chain Model Registry

### ModelRegistry Contract

**Address:** `0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc`

**Purpose:** Track all model versions on-chain with complete provenance.

### Key Functions

**1. `register_model_version(version, model_hash, description) -> ModelVersion`**
- Owner-only function
- Registers new model version
- Updates current version
- Emits `ModelRegistered` event

**2. `get_current_model() -> ModelVersion`**
- Returns active model version
- Includes version, hash, deployment date
- Public query function

**3. `get_model_version(version) -> Option<ModelVersion>`**
- Queries specific version
- Returns full model details
- Historical lookup

**4. `get_model_history() -> Span<felt252>`**
- Returns all version numbers
- Chronological order
- Complete upgrade history

### ModelVersion Structure

```cairo
struct ModelVersion {
    version: felt252,        // Semantic version as felt252
    model_hash: felt252,      // SHA-256 hash of model code
    deployed_at: u64,        // Block timestamp
    description: ByteArray,   // Human-readable description
    is_active: bool,         // Current active version
}
```

## Model Hash Commitment

### What is a Model Hash?

A model hash is a SHA-256 hash of the model code, ensuring:
- **Integrity:** Model cannot be modified without hash change
- **Verification:** Anyone can verify model matches hash
- **Provenance:** Links decisions to specific model versions

### Hash Calculation

**Process:**
1. Read model code (risk_engine.cairo)
2. Calculate SHA-256 hash
3. Convert to felt252 (modulo 2^251 - 1)
4. Store in ModelRegistry

**Backend Service:**
```python
def calculate_model_hash(model_code: str) -> str:
    hash_obj = hashlib.sha256(model_code.encode('utf-8'))
    return hash_obj.hexdigest()
```

### Hash Verification

**On-Chain:**
- ModelRegistry stores hash
- RiskEngine reads current hash
- Emits hash in events
- Verifiable by anyone

**Off-Chain:**
- Calculate hash from model code
- Compare with registered hash
- Verify match
- Confirm integrity

## Upgradeability with Audit Trail

### Upgrade Process

**1. Model Development:**
- Modify risk calculation logic
- Test new model
- Calculate new model hash

**2. Registration:**
- Owner calls `register_model_version()`
- New version stored on-chain
- Current version updated
- Event emitted

**3. Activation:**
- New version becomes active
- Future allocations use new model
- Old allocations remain valid
- Complete audit trail

### Audit Trail

**What's Tracked:**
- Version number
- Model hash
- Deployment timestamp
- Description
- Upgrade transaction hash

**Benefits:**
- Complete history
- Immutable records
- Transparent upgrades
- Governance accountability

## Version History

### Accessing History

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

**Via Contract:**
```cairo
let history = model_registry.get_model_history();
// Returns: Span<felt252> of version numbers
```

### Version Query

**Get Specific Version:**
```bash
curl https://api.obsqra.fi/api/v1/model-registry/version/1.0.0
```

**Get Current Version:**
```bash
curl https://api.obsqra.fi/api/v1/model-registry/current
```

## Governance Integration

### DAO Control

**Upgrade Authority:**
- ModelRegistry owner controls upgrades
- Can be transferred to DAO
- Governance-controlled upgrades
- Transparent process

### Upgrade Proposal

**Process:**
1. DAO proposes new model
2. Community reviews
3. Governance vote
4. Owner executes registration
5. New version activated

### Transparency

**Public Information:**
- All versions public
- All hashes verifiable
- All upgrades auditable
- Complete history

## Use Cases

### 1. Audit Requirements

**Need:** Verify which model was used for specific decisions

**Solution:**
- Query decision timestamp
- Look up active model at that time
- Verify model hash
- Confirm integrity

### 2. Model Improvements

**Need:** Upgrade model with better performance

**Solution:**
- Develop new model
- Register new version
- Activate new version
- Track performance differences

### 3. Regulatory Compliance

**Need:** Prove model integrity and version control

**Solution:**
- On-chain model registry
- Immutable version history
- Hash verification
- Complete audit trail

## Security Considerations

### Hash Integrity

**Protection:**
- SHA-256 cryptographic hash
- Cannot be forged
- Verifiable independently
- Immutable once registered

### Upgrade Security

**Controls:**
- Owner-only registration
- Can be DAO-controlled
- Transparent process
- Audit trail

### Version Verification

**Process:**
- Calculate expected hash
- Compare with registered hash
- Verify match
- Confirm integrity

## Next Steps

- **[Transparency Dashboard](03-transparency-dashboard.md)** - UX display
- **[DAO Governance Integration](05-dao-governance-integration.md)** - Governance features
- **[Contract Reference: ModelRegistry](../07-contract-reference/03-model-registry.md)** - Detailed interface

---

**Model Provenance Summary:** On-chain ModelRegistry tracks all model versions with hash commitments, providing complete upgrade history and integrity verification.
