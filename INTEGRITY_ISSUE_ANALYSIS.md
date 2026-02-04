# Integrity Contract Issue - Complete Analysis

**Date**: 2026-01-26  
**Status**: Root causes identified with Starknet MCP tool

## Issues Identified

### 1. VERIFIER_NOT_FOUND Error
**Root Cause** (from Starknet MCP):
- The verifier for the layout/hasher combination is **not registered** in the FactRegistry
- The contract calls `get_verifier_address(verifier_preset)` which looks up the verifier
- If not found, it returns VERIFIER_NOT_FOUND

**Our Configuration**:
- Layout: `small` (or `recursive` in config)
- Hasher: `keccak_160_lsb`
- Stone Version: `stone5`
- Memory Verification: `strict`

**Solution**:
1. Check if verifier is registered: Call `get_verifier_address` with layout/hasher
2. If not registered: Need to register the verifier or use a different layout/hasher combo
3. Check deployed verifiers: See `integrity/deployed_contracts.md` for available verifiers

### 2. Invalid final_pc Error (Progress!)
**Root Cause** (from Starknet MCP):
- The Cairo program output format doesn't match what the verifier expects
- The final program counter (final_pc) is invalid
- This happens **after** the verifier is found, so we're making progress!

**Possible Causes**:
1. Cairo program output format is wrong
2. Proof serialization issues
3. State mismatch between proof generation and verification
4. Entry point issues

**Solution**:
1. Check Cairo program output format
2. Verify proof serialization matches expected format
3. Ensure entry point is correct
4. Check that proof generation and verification use same parameters

## Contract Structure

From `fact_registry.cairo`:
```cairo
fn verify_proof_full_and_register_fact(
    ref self: ContractState,
    verifier_config: VerifierConfiguration,
    stark_proof: StarkProofWithSerde,
) -> FactRegistered {
    let (verifier_settings, verifier_preset) = split_settings(verifier_config);
    let verifier_address = self.get_verifier_address(verifier_preset);  // ← This can fail
    let result = ICairoVerifierDispatcher { contract_address: verifier_address }
        .verify_proof_full(verifier_settings, stark_proof.into());  // ← This can fail with Invalid final_pc
    // ...
}
```

## Next Steps

### Immediate Actions

1. **Check Verifier Registration**
   ```bash
   # Try to get verifier address for small/keccak_160_lsb
   sncast call \
     --contract-address 0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64 \
     --function get_verifier_address \
     --arguments <layout_felt> <hasher_felt> \
     --network sepolia
   ```

2. **Check Available Verifiers**
   - See `integrity/deployed_contracts.md` for registered verifiers
   - Use a layout/hasher combo that's actually registered

3. **Fix Cairo Program Output**
   - Check `verification/risk_example.cairo` output format
   - Ensure it matches verifier expectations
   - Verify entry point is correct

4. **Verify Proof Serialization**
   - Check `proof_serializer` output format
   - Ensure it matches `StarkProofWithSerde` structure

### Recommended Approach

1. **Use Known Working Configuration**
   - Check `integrity/deployed_contracts.md` for verified combinations
   - Use `recursive/keccak` if available (matches our config)
   - Or use `small/keccak` if that's registered

2. **Test with Simple Proof First**
   - Use a known-working Cairo program
   - Verify proof format is correct
   - Then adapt to our risk_example.cairo

3. **Check Contract Deployment**
   - Verify FactRegistry is deployed correctly
   - Check if verifiers are registered
   - May need to register verifier if using custom deployment

## Files to Check

- `integrity/deployed_contracts.md` - Available verifiers
- `verification/risk_example.cairo` - Cairo program
- `backend/app/services/proof_loader.py` - Proof serialization
- `integrity/src/contracts/fact_registry.cairo` - Contract code

---

**Status**: Root causes identified ✅ | Solutions outlined ⚠️ | Testing needed 🔄
