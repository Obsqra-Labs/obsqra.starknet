# Error Code Reference
## Complete Error Code and Resolution Guide

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Living Document  
**Category**: Developer Resources

---

## Error Categories

1. [Stone Prover Errors](#stone-prover-errors)
2. [Integrity Errors](#integrity-errors)
3. [FRI Parameter Errors](#fri-parameter-errors)
4. [Trace Generation Errors](#trace-generation-errors)
5. [Network and RPC Errors](#network-and-rpc-errors)

---

## Stone Prover Errors

### SIGABRT (Signal 6)

**Error Code**: `SIGABRT` or `Signal 6`

**Error Message**: 
```
Error: Signal 6 (SIGABRT)
Stone prover crashed
```

**Root Cause**: FRI parameter mismatch. Fixed FRI parameters don't match trace size.

**Resolution Steps**:
1. Use dynamic FRI calculation
2. Verify FRI equation holds
3. Check n_steps is power of 2

**Prevention**: Always use dynamic FRI calculation, never fixed parameters.

**Related**: `DYNAMIC_FRI_ALGORITHM_DETAILED.md`

---

### File Not Found

**Error Code**: `FileNotFoundError`

**Error Message**:
```
Error: File not found: trace.bin
```

**Root Cause**: Incorrect file path (relative vs absolute).

**Resolution Steps**:
1. Use absolute paths
2. Verify files exist
3. Check file permissions

**Prevention**: Always use `Path(file).absolute()` for paths.

**Code Example**:
```python
# ❌ WRONG
trace_path = "trace.bin"

# ✅ CORRECT
trace_path = str(Path("trace.bin").absolute())
```

---

### Invalid n_steps

**Error Code**: `ValueError: n_steps must be power of 2`

**Error Message**:
```
Error: n_steps must be power of 2 and >= 512, got 1000
```

**Root Cause**: n_steps not power of 2 or < 512.

**Resolution Steps**:
1. Round to next power of 2
2. Ensure >= 512
3. Validate before use

**Prevention**: Always validate and round n_steps.

**Code Example**:
```python
if n_steps & (n_steps - 1) != 0:
    n_steps_log = math.ceil(math.log2(n_steps))
    n_steps = 2 ** n_steps_log
```

---

### Timeout

**Error Code**: `subprocess.TimeoutExpired`

**Error Message**:
```
Error: Timeout after 300 seconds
```

**Root Cause**: Proof generation taking too long.

**Resolution Steps**:
1. Increase timeout for large proofs
2. Optimize trace size
3. Check system resources

**Prevention**: Set appropriate timeout based on trace size.

**Code Example**:
```python
timeout = 300  # Default
if n_steps > 32768:
    timeout = 600  # 10 minutes for very large proofs
```

---

## Integrity Errors

### VERIFIER_NOT_FOUND

**Error Code**: `VERIFIER_NOT_FOUND`

**Error Message**:
```
Error: VERIFIER_NOT_FOUND
```

**Root Cause**: Verifier not registered in FactRegistry.

**Resolution Steps**:
1. Use public FactRegistry (recommended)
2. Register verifier in custom FactRegistry
3. Check verifier configuration

**Prevention**: Always use public FactRegistry unless you have specific needs.

**Code Example**:
```python
PUBLIC_FACT_REGISTRY = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
```

---

### Invalid OODS

**Error Code**: `Invalid OODS`

**Error Message**:
```
Error: Invalid OODS
```

**Root Cause**: Stone version mismatch with Integrity verifier setting.

**Resolution Steps**:
1. Check Stone version
2. Check Integrity verifier setting
3. Match versions (Stone v3 → stone6)

**Prevention**: Always match Stone version with Integrity verifier.

**Code Example**:
```python
# Stone v3 → stone6
if stone_version.startswith("1414a545"):
    integrity_stone_version = "stone6"
```

**Related**: `STONE_VERSION_COMPATIBILITY_MATRIX.md`

---

### Invalid builtin

**Error Code**: `Invalid builtin`

**Error Message**:
```
Error: Invalid builtin
```

**Root Cause**: Layout/builtin mismatch.

**Resolution Steps**:
1. Use correct layout ("recursive" for most cases)
2. Check builtin configuration
3. Match verifier expectations

**Prevention**: Always use correct layout and builtins.

---

### Invalid final_pc

**Error Code**: `Invalid final_pc`

**Error Message**:
```
Error: Invalid final_pc
```

**Root Cause**: Trace execution issue.

**Resolution Steps**:
1. Check trace generation
2. Verify Cairo execution
3. Validate trace format

**Prevention**: Ensure trace generation is correct.

---

## FRI Parameter Errors

### FRI Equation Mismatch

**Error Code**: `ValueError: FRI equation mismatch`

**Error Message**:
```
Error: FRI equation mismatch: log2(128)=7 + [0,4,4,3]=11 = 18, expected 20
```

**Root Cause**: FRI equation not satisfied.

**Resolution Steps**:
1. Recalculate FRI parameters
2. Verify equation holds
3. Check n_steps and last_layer

**Prevention**: Always use dynamic FRI calculation.

**Code Example**:
```python
fri_steps = calculate_fri_step_list(n_steps, last_layer_degree_bound)

# Verify
last_layer_log2 = math.ceil(math.log2(last_layer_degree_bound))
equation_sum = sum(fri_steps)
target_sum = math.ceil(math.log2(n_steps)) + 4
assert last_layer_log2 + equation_sum == target_sum
```

---

### FRI Equation Impossible

**Error Code**: `ValueError: FRI equation impossible`

**Error Message**:
```
Error: FRI equation impossible: log2(last_layer)=7 > target_sum=12
```

**Root Cause**: n_steps too small for last_layer_degree_bound.

**Resolution Steps**:
1. Increase n_steps
2. Decrease last_layer_degree_bound
3. Check minimum n_steps

**Prevention**: Validate n_steps is large enough.

---

## Trace Generation Errors

### Trace File Not Found

**Error Code**: `FileNotFoundError`

**Error Message**:
```
Error: Trace file not found
```

**Root Cause**: Incorrect trace file path.

**Resolution Steps**:
1. Use absolute paths
2. Verify file exists
3. Check file permissions

**Prevention**: Always use absolute paths, verify files exist.

---

### Invalid Trace Format

**Error Code**: `ValueError: Invalid trace format`

**Error Message**:
```
Error: Invalid trace format
```

**Root Cause**: Trace format incorrect.

**Resolution Steps**:
1. Check trace format
2. Validate trace structure
3. Ensure binary format

**Prevention**: Validate trace format before use.

---

## Network and RPC Errors

### RPC Timeout

**Error Code**: `TimeoutError` or `RPCError`

**Error Message**:
```
Error: RPC timeout
```

**Root Cause**: RPC call taking too long.

**Resolution Steps**:
1. Use faster RPC endpoint
2. Increase timeout
3. Retry with backoff

**Prevention**: Use reliable RPC endpoints, implement retry logic.

---

### RPC Rate Limit

**Error Code**: `RateLimitError`

**Error Message**:
```
Error: Rate limit exceeded
```

**Root Cause**: Too many RPC requests.

**Resolution Steps**:
1. Implement rate limiting
2. Use multiple RPC endpoints
3. Batch operations
4. Cache results

**Prevention**: Implement rate limiting, use multiple endpoints.

---

## Error Handling Best Practices

### 1. Always Validate Inputs

```python
# Validate before calling Stone
assert n_steps & (n_steps - 1) == 0, "n_steps must be power of 2"
assert n_steps >= 512, "n_steps must be >= 512"
assert Path(trace_file).exists(), "Trace file not found"
```

### 2. Use Try-Except Blocks

```python
try:
    result = await stone_service.generate_proof(...)
    if not result.success:
        logger.error(f"Proof generation failed: {result.error}")
        # Handle error
except subprocess.TimeoutExpired:
    logger.error("Proof generation timeout")
    # Handle timeout
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Handle unexpected error
```

### 3. Provide Helpful Error Messages

```python
try:
    result = generate_proof(...)
except ValueError as e:
    if "FRI equation" in str(e):
        logger.error("FRI parameter issue. Use dynamic FRI calculation.")
    elif "n_steps" in str(e):
        logger.error("n_steps issue. Round to power of 2.")
    else:
        logger.error(f"Value error: {e}")
```

### 4. Log All Parameters

```python
logger.info("=" * 80)
logger.info("PROOF GENERATION PARAMETERS")
logger.info("=" * 80)
logger.info(f"n_steps: {n_steps}")
logger.info(f"FRI step_list: {fri_steps}")
logger.info(f"Trace file: {trace_file}")
logger.info("=" * 80)
```

---

## Error Prevention Checklist

**Before Calling Stone Prover**:
- [ ] n_steps is power of 2
- [ ] n_steps >= 512
- [ ] FRI parameters calculated dynamically
- [ ] FRI equation verified
- [ ] Trace file exists (absolute path)
- [ ] Memory file exists (absolute path)
- [ ] Public input valid

**Before Calling Integrity**:
- [ ] Using public FactRegistry
- [ ] Stone version matches verifier setting
- [ ] Proof serialized correctly
- [ ] Calldata constructed correctly
- [ ] RPC endpoint accessible

**Before Production**:
- [ ] Tested with multiple trace sizes
- [ ] Tested with canonical proof
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Monitoring set up

---

## Conclusion

Most errors can be prevented by:

1. **Using dynamic FRI calculation**
2. **Matching Stone version with verifier**
3. **Using public FactRegistry**
4. **Using absolute paths**
5. **Validating all inputs**

**For Additional Help**:
- See `TROUBLESHOOTING_GUIDE.md` for detailed solutions
- See `DEVELOPER_FAQ.md` for common questions
- See support resources for professional help

---

**This reference helps identify and resolve errors quickly.**
