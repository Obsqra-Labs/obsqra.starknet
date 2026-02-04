# RiskEngine v4 with On-Chain Agent - Deployment Plan

## Implementation Status: ✅ COMPLETE

All contract changes have been implemented and the contract compiles successfully.

## Summary of Changes

### Contract Changes (`contracts/src/risk_engine.cairo`)

1. **New Struct: `ConstraintSignature`**
   - Added user-signed constraint approval struct with signer, constraints, signature, and timestamp

2. **Updated `AllocationDecision` Struct**
   - Added `model_version: felt252` for provenance
   - Added `jediswap_proof_fact: felt252` for audit trail
   - Added `ekubo_proof_fact: felt252` for audit trail
   - Added `constraint_signature: ConstraintSignature` for user approval

3. **Updated Storage**
   - Added `model_registry: ContractAddress` for ModelRegistry integration
   - Added `approved_model_versions: Map<felt252, bool>` for model approval tracking
   - Added `permissionless_mode: bool` for permissionless execution toggle

4. **Updated Function Signature**
   - `propose_and_execute_allocation` now accepts 9 parameters (was 7):
     - Original 7: `jediswap_metrics`, `ekubo_metrics`, `jediswap_proof_fact`, `ekubo_proof_fact`, `expected_jediswap_score`, `expected_ekubo_score`, `fact_registry_address`
     - New 2: `model_version: felt252`, `constraint_signature: ConstraintSignature`

5. **New Execution Steps**
   - **STEP 0.5**: Model version verification (checks approved_model_versions map)
   - **STEP 0.6**: Constraint signature verification (validates user-signed constraints)

6. **Permissionless Mode**
   - Added permissionless mode check at function entry
   - When enabled, skips owner check (proof verification is the authorization gate)

7. **Enhanced Events**
   - `AllocationExecuted` event now includes:
     - `jediswap_proof_fact: felt252`
     - `ekubo_proof_fact: felt252`
     - `constraint_signer: ContractAddress`

8. **New Management Functions**
   - `approve_model_version(model_hash: felt252)` - Owner-only
   - `revoke_model_version(model_hash: felt252)` - Owner-only
   - `is_model_version_approved(model_hash: felt252) -> bool` - Public view
   - `set_permissionless_mode(enabled: bool)` - Owner-only
   - `get_permissionless_mode() -> bool` - Public view
   - `set_model_registry(model_registry: ContractAddress)` - Owner-only

9. **Updated Constructor**
   - Now requires `model_registry: ContractAddress` parameter
   - Initializes `permissionless_mode` to `false`

## Deployment Steps

### Phase 1: Build and Declare

```bash
cd /opt/obsqra.starknet/contracts
scarb build --release
```

The contract should compile successfully (verified ✅).

### Phase 2: Deploy Contract

**Constructor Parameters:**
- `owner: ContractAddress` - Contract owner address
- `strategy_router: ContractAddress` - StrategyRouter contract address
- `dao_manager: ContractAddress` - DAOConstraintManager contract address
- `model_registry: ContractAddress` - ModelRegistry contract address (can be 0 for now)

**Deployment Script:**
```bash
# Update deploy script with new constructor signature
# Example using starkli:
starkli declare target/dev/obsqra_contracts_RiskEngine.sierra.json \
  --account <account> \
  --network sepolia

starkli deploy <class_hash> \
  --account <account> \
  --network sepolia \
  --constructor-calldata \
    <owner_address> \
    <strategy_router_address> \
    <dao_manager_address> \
    <model_registry_address>
```

### Phase 3: Post-Deployment Configuration

1. **Approve Model Versions**
   ```bash
   starkli invoke <risk_engine_address> \
     approve_model_version \
     --account <account> \
     --network sepolia \
     --calldata <model_hash>
   ```

2. **Set Model Registry** (if using ModelRegistry contract)
   ```bash
   starkli invoke <risk_engine_address> \
     set_model_registry \
     --account <account> \
     --network sepolia \
     --calldata <model_registry_address>
   ```

3. **Enable Permissionless Mode** (optional, when ready)
   ```bash
   starkli invoke <risk_engine_address> \
     set_permissionless_mode \
     --account <account> \
     --network sepolia \
     --calldata 1  # true
   ```

### Phase 4: Update Backend Configuration

Update `backend/app/config.py`:
```python
RISK_ENGINE_ADDRESS = "<new_deployed_address>"
```

### Phase 5: Update Backend Code

**File: `backend/app/api/routes/risk_engine.py`**

1. **Update ABI Detection**
   - Change expected inputs from 7 to 9 (2 structs + 5 proof params + 2 new params)
   - Update `expects_proof_args` check: `onchain_inputs >= 9`

2. **Update `orchestrate_allocation` Function**
   - Add `model_version` parameter (get from proof job or model service)
   - Add `constraint_signature` parameter (get from request or use zero signature)
   - Update calldata construction to include new parameters

3. **Update Calldata Format**
   ```python
   calldata = [
       # Protocol metrics (jediswap)
       jediswap_metrics.utilization,
       jediswap_metrics.volatility,
       jediswap_metrics.liquidity,
       jediswap_metrics.audit_score,
       jediswap_metrics.age_days,
       # Protocol metrics (ekubo)
       ekubo_metrics.utilization,
       ekubo_metrics.volatility,
       ekubo_metrics.liquidity,
       ekubo_metrics.audit_score,
       ekubo_metrics.age_days,
       # Proof parameters
       jediswap_proof_fact,
       ekubo_proof_fact,
       expected_jediswap_score,
       expected_ekubo_score,
       fact_registry_address,
       # NEW: On-chain agent parameters
       model_version,  # felt252
       # ConstraintSignature struct (8 fields)
       constraint_signature.signer,  # ContractAddress -> felt252
       constraint_signature.max_single,
       constraint_signature.min_diversification,
       constraint_signature.max_volatility,
       constraint_signature.min_liquidity,
       constraint_signature.signature_r,
       constraint_signature.signature_s,
       constraint_signature.timestamp,
   ]
   ```

### Phase 6: Update Frontend Code

**File: `frontend/src/hooks/useRiskEngineBackendOrchestration.ts`**

1. **Update Request Model**
   - Add `model_version?: string` to request
   - Add `constraint_signature?: ConstraintSignature` to request

2. **Update API Call**
   - Pass `model_version` from proof job or model registry
   - Pass `constraint_signature` from user approval (if available)

**File: `frontend/src/app/demo/page.tsx`**

1. **Update Constraint Approval**
   - Ensure constraint signature is passed to proof generation
   - Display model version in UI

## Testing Checklist

- [ ] Contract compiles successfully ✅
- [ ] Contract deploys successfully
- [ ] Constructor initializes all storage correctly
- [ ] `propose_and_execute_allocation` accepts 9 parameters
- [ ] Model version verification works (reverts on unapproved model)
- [ ] Constraint signature verification works (accepts zero signature)
- [ ] Permissionless mode toggle works
- [ ] Owner functions work (approve_model_version, set_permissionless_mode)
- [ ] Enhanced events emit correctly
- [ ] Backend passes all 9 parameters correctly
- [ ] Frontend displays model version and constraint signature
- [ ] End-to-end flow works with new interface

## Migration Notes

### Backward Compatibility

- **Breaking Change**: The function signature has changed from 7 to 9 parameters
- Old deployments will not work with new backend code
- Must deploy new contract version

### Demo Mode Removal

- The demo mode fallback in `backend/app/api/routes/risk_engine.py` should be removed
- All executions must use proof-gated v4 contract
- If contract doesn't accept proof parameters, raise error (don't fall back)

## Next Steps

1. Deploy contract to Sepolia testnet
2. Update backend configuration
3. Update backend code to pass new parameters
4. Update frontend code to handle new interface
5. Test end-to-end flow
6. Enable permissionless mode (when ready)

## Files Modified

- ✅ `contracts/src/risk_engine.cairo` - Complete implementation
- ⏳ `backend/app/api/routes/risk_engine.py` - Needs update for new parameters
- ⏳ `backend/app/config.py` - Needs new contract address
- ⏳ `frontend/src/hooks/useRiskEngineBackendOrchestration.ts` - Needs update
- ⏳ `frontend/src/app/demo/page.tsx` - May need minor updates

## Success Criteria

- ✅ Contract compiles without errors
- ⏳ Contract deploys successfully
- ⏳ Backend passes all 9 parameters correctly
- ⏳ Frontend displays new data correctly
- ⏳ End-to-end flow works without demo mode
- ⏳ Permissionless execution works (when enabled)
