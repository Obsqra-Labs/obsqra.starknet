# Canonical AIR Regeneration Test Results

**Date**: 2026-01-26  
**Test**: Canonical AIR regeneration with recursive layout + stone5  
**Status**: Proof generation successful, Integrity verification failed

---

## Test Configuration

```python
INTEGRITY_LAYOUT: str = "recursive"  # Canonical
INTEGRITY_STONE_VERSION: str = "stone5"  # Canonical
INTEGRITY_HASHER: str = "keccak_160_lsb"
INTEGRITY_MEMORY_VERIFICATION: str = "strict"
INTEGRITY_CAIRO_TIMEOUT: int = 300  # 5 minutes
```

---

## Test Results

### ✅ Proof Generation: SUCCESS

- **Status**: Proof generated successfully
- **Time Elapsed**: 67.95 seconds (well under 300s timeout)
- **Proof Hash**: `21ab946667c293813cb8f9d73b2fcbf4963844c5ec1be1503c8df1e38203a257`
- **Proof Path**: `/tmp/risk_stone_nttstalm/risk_proof.json`
- **Output Directory**: `/tmp/risk_stone_nttstalm`

**Key Finding**: Recursive layout proof generation completes in ~68 seconds (not the 5+ minutes we feared). This is acceptable for production use.

### ❌ Integrity Verification: FAILED

- **Status**: Integrity contract rejected the proof
- **Error**: `Invalid builtin`
- **Error Code**: Contract error (code 40)
- **Fact Hash**: `None` (not registered)

**Error Details**:
```
RPC error: Contract error. Data: {
  'revert_error': {
    'error': "0x496e76616c6964206275696c74696e ('Invalid builtin')",
    'selector': '0x2a4793ce2d7c09e7a3d79cd8d9d57dbc02ef0b9548cc965d248e0d0c17192a3'
  }
}
```

**Interpretation**: The proof was generated and serialized correctly, but Integrity's verifier rejected it due to a builtin mismatch. This suggests:
1. The proof format doesn't match Integrity's expected builtin configuration
2. The Cairo program's builtins may not match what Integrity's verifier expects
3. This is a deeper AIR mismatch, not just a layout issue

---

## Analysis

### What Worked ✅

1. **Recursive Layout Execution**: Cairo program runs successfully with recursive layout
2. **Proof Generation**: Stone prover generates proof in reasonable time (~68s)
3. **Proof Serialization**: Proof serializes correctly for Integrity
4. **No Timeout**: 300s timeout is sufficient (proof completes in ~68s)

### What Failed ❌

1. **Integrity Verification**: Contract rejects proof with "Invalid builtin" error
2. **Fact Registration**: No fact hash registered (verification failed)

### Root Cause Hypothesis

The "Invalid builtin" error suggests:
- The Cairo program uses builtins that don't match Integrity's verifier expectations
- The proof's builtin configuration doesn't align with Integrity's canonical AIR
- This is a deeper issue than layout/stone version - it's about the AIR itself

**Possible Causes**:
1. **Builtin Mismatch**: Our Cairo program uses builtins (e.g., `output`, `pedersen`, `range_check`, `ecdsa`) that don't match Integrity's verifier's expected builtin set
2. **AIR Configuration**: The AIR configuration in the proof doesn't match Integrity's canonical AIR
3. **Program Hash**: The program hash/class hash doesn't match what Integrity expects

---

## Comparison with Previous Errors

### Previous Error: `Invalid final_pc`
- **Meaning**: Program counter mismatch (execution trace issue)
- **Likely Cause**: Layout/AIR mismatch

### Current Error: `Invalid builtin`
- **Meaning**: Builtin configuration mismatch
- **Likely Cause**: Cairo program's builtins don't match Integrity's verifier expectations

**Progression**: We've moved from a layout/trace issue to a builtin configuration issue. This suggests we're getting closer, but there's still a fundamental mismatch.

---

## Recommendations

### Option 1: Investigate Builtin Configuration
- Check what builtins Integrity's verifier expects
- Compare with our Cairo program's builtins
- Adjust Cairo program to match Integrity's expected builtins

### Option 2: Use Integrity's Example Programs
- Use Integrity's example Cairo programs (e.g., fibonacci)
- Verify those work with Integrity
- Adapt our risk_example.cairo to match their structure

### Option 3: Atlantic Integration
- Use Atlantic to generate Integrity-compatible proofs
- Atlantic handles builtin configuration automatically
- Requires Atlantic API credits

### Option 4: Fallback to Small Layout
- Revert to `small` layout for local verification
- Accept that Integrity FactRegistry verification may not work
- Document this as a known limitation

---

## Next Steps

1. **Investigate Builtin Configuration**
   - Check Integrity's verifier requirements
   - Compare with our Cairo program
   - Document builtin mismatch

2. **Test with Integrity's Example**
   - Try Integrity's fibonacci example
   - Verify it works with canonical settings
   - Use as reference for our program

3. **Consider Atlantic**
   - Evaluate Atlantic integration
   - Check if Atlantic handles builtin configuration
   - Assess cost/benefit

4. **Document Limitation**
   - Update `docs/proving_flows.md`
   - Add "Invalid builtin" error to known issues
   - Document workarounds

---

## Test Output

Full test output saved to: `canonical_air_test_output.log`

**Key Metrics**:
- Proof generation time: 67.95s ✅
- Proof generation success: ✅
- Integrity verification: ❌ (Invalid builtin)
- Fact hash: None ❌

---

**Status**: Proof generation works with canonical settings, but Integrity verification fails due to builtin mismatch. This is a deeper AIR configuration issue, not just layout/version.
