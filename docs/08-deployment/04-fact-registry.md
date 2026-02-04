# Fact Registry Deployment Guide

Complete guide for deploying a custom FactRegistry contract, including building, declaring, deploying, and updating configuration.

## Why Deploy Your Own FactRegistry?

### Benefits

**1. Full Control:**
- Independent verification
- Custom verification logic
- No dependency on public registry

**2. Testing:**
- Development and testing
- Custom test scenarios
- Isolated environment

**3. Privacy:**
- Private verification registry
- Custom access control
- Isolated facts

### Trade-offs

**1. Maintenance:**
- You maintain the contract
- Updates are your responsibility
- No automatic upgrades

**2. Standardization:**
- Less standard than public registry
- May not integrate with other tools
- Custom integration required

## Deployment Process

### Step 1: Build FactRegistry

**Navigate to integrity directory:**
```bash
cd integrity
```

**Build contract:**
```bash
scarb build
```

**Verify build:**
```bash
ls target/dev/
# Should see FactRegistry.sierra.json
```

### Step 2: Configure sncast

**Update snfoundry.toml:**
```toml
[sncast.default]
network = "sepolia"
# Remove 'url' if using --network flag
```

**Or use environment:**
```bash
export STARKNET_NETWORK=sepolia
```

### Step 3: Declare Contract

**Using sncast:**
```bash
sncast declare \
  --contract-name FactRegistry \
  --network sepolia \
  --account <account_name>
```

**Wait for propagation:**
```bash
# Wait 30 seconds for class propagation
sleep 30
```

**Save class hash:**
- Copy the class hash from output
- Save for deployment step

### Step 4: Deploy Contract

**Deploy:**
```bash
sncast deploy \
  --class-hash <class_hash_from_step_3> \
  --network sepolia \
  --account <account_name>
```

**Save address:**
- Copy the contract address
- Save for configuration

### Step 5: Verify Deployment

**Check on Starkscan:**
```
https://sepolia.starkscan.co/contract/<address>
```

**Test query:**
```bash
sncast call \
  --contract-address <address> \
  --function get_all_verifications_for_fact_hash \
  --arguments 0x0 \
  --network sepolia
```

## Updating Configuration

### Backend Configuration

**Update .env:**
```bash
# Add or update
FACT_REGISTRY_ADDRESS=0x<your_deployed_address>
```

**Or update config.py:**
```python
FACT_REGISTRY_ADDRESS = "0x<your_deployed_address>"
```

### Contract Configuration

**Update RiskEngine:**
- RiskEngine uses fact_registry_address parameter
- No contract update needed
- Pass address in function calls

**Backend API:**
```python
fact_registry_address = "0x<your_deployed_address>"
# Pass in orchestrate_allocation calldata
```

## Integration Testing

### Test Proof Registration

**1. Generate Proof:**
```bash
curl -X POST http://localhost:8001/api/v1/proofs/generate \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**2. Verify Registration:**
```bash
# Query your FactRegistry
sncast call \
  --contract-address <your_fact_registry> \
  --function get_all_verifications_for_fact_hash \
  --arguments <fact_hash> \
  --network sepolia
```

**3. Test On-Chain Verification:**
```bash
# Execute allocation with your FactRegistry
curl -X POST http://localhost:8001/api/v1/risk-engine/orchestrate-allocation \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## Using Public Registry vs Custom

### Public SHARP Registry

**Address:**
```
0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64
```

**Benefits:**
- No deployment needed
- Standard and tested
- Automatic updates
- Public verification

**Use When:**
- Production deployment
- Standard verification
- Public transparency
- No custom needs

### Custom FactRegistry

**Benefits:**
- Full control
- Custom logic
- Private verification
- Testing flexibility

**Use When:**
- Development/testing
- Custom requirements
- Private verification
- Special use cases

## Troubleshooting

### Declaration Fails

**Issue:** RPC errors
**Solution:**
- Try different RPC endpoint
- Wait and retry
- Check network connectivity

### Deployment Fails

**Issue:** Class not found
**Solution:**
- Wait longer after declaration (30+ seconds)
- Verify class hash
- Check network

### Verification Fails

**Issue:** Facts not registering
**Solution:**
- Check Integrity Service
- Verify proof format
- Check contract address

## Next Steps

- **[Contract Deployment](02-contract-deployment.md)** - Other contracts
- **[Backend Deployment](03-backend-deployment.md)** - Backend setup
- **[Deployment Overview](01-overview.md)** - Architecture

---

**Fact Registry Deployment Summary:** Complete guide for deploying custom FactRegistry with integration testing and configuration updates.
