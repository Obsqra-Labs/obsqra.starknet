# Troubleshooting Guide - Stone Prover Integration
## Comprehensive Problem Resolution Guide

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Production-Validated  
**Category**: Troubleshooting Guide

---

## Executive Summary

This guide provides comprehensive troubleshooting for common issues when integrating Stone Prover. Based on Obsqra Labs' production experience with 100+ proofs, this guide covers errors, root causes, solutions, and prevention strategies.

**Coverage**: Signal 6 errors, OODS failures, FRI parameter issues, Integrity verification failures, trace generation problems, performance issues, and more.

---

## Table of Contents

1. [Common Errors and Solutions](#common-errors-and-solutions)
2. [OODS Error Debugging](#oods-error-debugging)
3. [FRI Parameter Issues](#fri-parameter-issues)
4. [Integrity Verification Failures](#integrity-verification-failures)
5. [Trace Generation Problems](#trace-generation-problems)
6. [Performance Issues](#performance-issues)
7. [Network and RPC Issues](#network-and-rpc-issues)
8. [Debugging Tools and Techniques](#debugging-tools-and-techniques)
9. [Log Analysis](#log-analysis)
10. [Support Resources](#support-resources)

---

## Common Errors and Solutions

### Error 1: "Signal 6" (SIGABRT)

**Symptoms**:
```
Error: Signal 6 (SIGABRT)
Stone prover crashed
```

**Root Cause**: FRI parameter mismatch. Fixed FRI parameters only work for one trace size.

**Solution**: Use dynamic FRI calculation:
```python
# ❌ WRONG: Fixed parameters
fri_steps = [0, 4, 4, 3]  # Only works for n_steps=16384

# ✅ CORRECT: Dynamic calculation
fri_steps = calculate_fri_step_list(n_steps, last_layer_degree_bound)
```

**Prevention**: Always use dynamic FRI calculation. Never use fixed parameters.

**See**: `DYNAMIC_FRI_ALGORITHM_DETAILED.md` for complete algorithm.

### Error 2: "Invalid OODS"

**Symptoms**:
```
Error: Invalid OODS
On-chain verification fails
```

**Root Cause**: Stone version mismatch with Integrity verifier setting.

**Solution**: Match Stone version with verifier:
```python
# Stone v3 → stone6
# Stone v2 → stone5 (hypothesis)

if stone_version.startswith("1414a545"):  # Stone v3
    integrity_stone_version = "stone6"
```

**Prevention**: Always check Stone version and set Integrity verifier accordingly.

**See**: `STONE_VERSION_COMPATIBILITY_MATRIX.md` for version mapping.

### Error 3: "VERIFIER_NOT_FOUND"

**Symptoms**:
```
Error: VERIFIER_NOT_FOUND
Integrity verification fails
```

**Root Cause**: Verifier not registered in FactRegistry.

**Solution**: Use public FactRegistry:
```python
PUBLIC_FACT_REGISTRY = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
```

**Prevention**: Always use public FactRegistry unless you have specific needs.

**See**: `INTEGRITY_FACTREGISTRY_INTEGRATION_GUIDE.md` for details.

### Error 4: "File Not Found"

**Symptoms**:
```
Error: File not found: trace.bin
```

**Root Cause**: Incorrect file paths (relative vs absolute).

**Solution**: Use absolute paths:
```python
# ❌ WRONG: Relative path
trace_path = "trace.bin"

# ✅ CORRECT: Absolute path
trace_path = str(Path("trace.bin").absolute())
```

**Prevention**: Always use absolute paths, verify files exist before calling Stone.

### Error 5: "n_steps must be power of 2"

**Symptoms**:
```
Error: n_steps must be power of 2
```

**Root Cause**: n_steps not power of 2.

**Solution**: Round to next power of 2:
```python
if n_steps & (n_steps - 1) != 0:
    n_steps_log = math.ceil(math.log2(n_steps))
    n_steps = 2 ** n_steps_log
```

**Prevention**: Always validate and round n_steps before use.

### Error 6: Timeout

**Symptoms**:
```
Error: Timeout after 300 seconds
```

**Root Cause**: Proof generation taking too long (large traces or system issues).

**Solution**: Increase timeout or optimize trace size:
```python
# Increase timeout for large proofs
timeout = 600  # 10 minutes for very large proofs
result = subprocess.run(cmd, timeout=timeout)
```

**Prevention**: Set appropriate timeout based on trace size, monitor system resources.

---

## OODS Error Debugging

### Understanding OODS

**What is OODS?**
- Out-of-Distribution Sampling
- Cryptographic consistency check
- Validates composition polynomial reconstruction
- Fails if proof parameters don't match verifier expectations

### Common OODS Causes

**1. Stone Version Mismatch**
- Stone v3 proof with stone5 verifier → OODS failure
- Stone v2 proof with stone6 verifier → OODS failure (hypothesis)

**Solution**: Match versions (Stone v3 → stone6)

**2. FRI Parameter Mismatch**
- n_queries mismatch
- proof_of_work_bits mismatch
- fri_step_list mismatch

**Solution**: Use canonical parameters (n_queries: 10, proof_of_work_bits: 30)

**3. Public Input Hash Mismatch**
- stone6 includes n_verifier_friendly in hash
- stone5 does not include it

**Solution**: Use correct stone version setting

### OODS Debugging Steps

**Step 1: Check Stone Version**
```python
stone_version = get_stone_prover_version()
print(f"Stone version: {stone_version}")
```

**Step 2: Check Integrity Setting**
```python
integrity_stone_version = settings.INTEGRITY_STONE_VERSION
print(f"Integrity setting: {integrity_stone_version}")
```

**Step 3: Verify Compatibility**
```python
if stone_version.startswith("1414a545"):  # Stone v3
    assert integrity_stone_version == "stone6", "Version mismatch!"
```

**Step 4: Check FRI Parameters**
```python
# Verify n_queries and proof_of_work_bits match canonical
assert n_queries == 10, "n_queries mismatch"
assert proof_of_work_bits == 30, "proof_of_work_bits mismatch"
```

**Step 5: Test with Canonical Proof**
```python
# Test if canonical proof verifies
# If yes → issue is in our proof generation
# If no → issue is in verifier/registry
```

---

## FRI Parameter Issues

### Issue: FRI Equation Not Satisfied

**Symptoms**: "Signal 6" error or proof generation failure

**Root Cause**: FRI equation not satisfied:
```
log2(last_layer_degree_bound) + Σ(fri_steps) ≠ log2(n_steps) + 4
```

**Solution**: Use dynamic FRI calculation:
```python
fri_steps = calculate_fri_step_list(n_steps, last_layer_degree_bound)

# Verify equation
last_layer_log2 = math.ceil(math.log2(last_layer_degree_bound))
equation_sum = sum(fri_steps)
target_sum = math.ceil(math.log2(n_steps)) + 4
actual_sum = last_layer_log2 + equation_sum

assert actual_sum == target_sum, "FRI equation not satisfied"
```

### Issue: Wrong FRI Parameters

**Symptoms**: Proof generation succeeds but verification fails

**Root Cause**: Using wrong n_queries or proof_of_work_bits

**Solution**: Use canonical parameters:
```json
{
  "n_queries": 10,
  "proof_of_work_bits": 30
}
```

### Issue: Fixed FRI Parameters

**Symptoms**: Works for one trace size, fails for others

**Root Cause**: Using fixed fri_step_list for variable trace sizes

**Solution**: Always calculate dynamically based on n_steps

---

## Integrity Verification Failures

### Issue: VERIFIER_NOT_FOUND

**Symptoms**: "VERIFIER_NOT_FOUND" error

**Root Cause**: Verifier not registered in FactRegistry

**Solutions**:
1. Use public FactRegistry (recommended)
2. Register verifier in custom FactRegistry
3. Check verifier configuration matches

### Issue: Invalid builtin

**Symptoms**: "Invalid builtin" error

**Root Cause**: Layout/builtin mismatch

**Solutions**:
1. Use correct layout ("recursive" for most cases)
2. Check builtin configuration
3. Match verifier expectations

### Issue: Calldata Too Large

**Symptoms**: RPC error or timeout

**Root Cause**: Proof too large for RPC limits

**Solutions**:
1. Check proof size (should be < 500 KB)
2. Use different RPC endpoint
3. Optimize proof size if possible

---

## Trace Generation Problems

### Issue: Trace File Not Found

**Symptoms**: "File not found" error

**Root Cause**: Incorrect file path

**Solution**: Use absolute paths:
```python
trace_path = str(Path(trace_file).absolute())
```

### Issue: Invalid Trace Format

**Symptoms**: Stone Prover rejects trace

**Root Cause**: Trace format incorrect

**Solution**: Ensure trace is binary format, validate before use

### Issue: Trace Size Mismatch

**Symptoms**: n_steps doesn't match trace

**Root Cause**: Trace size calculation incorrect

**Solution**: Calculate n_steps from actual trace:
```python
# Count trace entries
n_steps = len(trace_entries)

# Round to power of 2
n_steps_log = math.ceil(math.log2(n_steps))
n_steps = 2 ** n_steps_log
```

---

## Performance Issues

### Issue: Proof Generation Too Slow

**Symptoms**: Proofs taking > 10 seconds

**Root Causes**:
- Large trace size
- System resource constraints
- Network issues

**Solutions**:
1. Optimize trace size (reduce n_steps)
2. Increase system resources (CPU, RAM)
3. Check system load
4. Use faster hardware

### Issue: High Memory Usage

**Symptoms**: Out of memory errors

**Root Causes**:
- Large traces
- Multiple proofs in parallel
- System limits

**Solutions**:
1. Reduce trace size
2. Limit parallel proofs
3. Increase system RAM
4. Process proofs sequentially

### Issue: CPU Saturation

**Symptoms**: Slow proof generation, high CPU usage

**Root Causes**:
- Too many parallel proofs
- System overload
- Inefficient processing

**Solutions**:
1. Limit concurrency
2. Use more CPU cores
3. Optimize processing
4. Distribute load

---

## Network and RPC Issues

### Issue: RPC Timeout

**Symptoms**: RPC calls timing out

**Root Causes**:
- Slow RPC endpoint
- Network issues
- Large calldata

**Solutions**:
1. Use faster RPC endpoint
2. Increase timeout
3. Optimize calldata size
4. Retry with backoff

### Issue: RPC Rate Limiting

**Symptoms**: Rate limit errors

**Root Causes**:
- Too many requests
- RPC limits

**Solutions**:
1. Implement rate limiting
2. Use multiple RPC endpoints
3. Batch operations
4. Cache results

### Issue: Network Latency

**Symptoms**: Slow verification

**Root Causes**:
- Network distance
- RPC performance
- Network congestion

**Solutions**:
1. Use closer RPC endpoint
2. Optimize network path
3. Consider dedicated connection
4. Use async operations

---

## Debugging Tools and Techniques

### Tool 1: Verbose Logging

**Enable Debug Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Log Key Parameters**:
```python
logger.info("=" * 80)
logger.info("STONE PROVER PARAMETERS")
logger.info("=" * 80)
logger.info(f"n_steps: {n_steps}")
logger.info(f"FRI step_list: {fri_steps}")
logger.info(f"FRI n_queries: {n_queries}")
logger.info("=" * 80)
```

### Tool 2: Parameter Validation

**Validate Before Calling Stone**:
```python
# Validate n_steps
assert n_steps & (n_steps - 1) == 0, "n_steps must be power of 2"
assert n_steps >= 512, "n_steps must be >= 512"

# Validate FRI equation
last_layer_log2 = math.ceil(math.log2(last_layer_degree_bound))
equation_sum = sum(fri_steps)
target_sum = math.ceil(math.log2(n_steps)) + 4
assert last_layer_log2 + equation_sum == target_sum, "FRI equation mismatch"

# Validate files
assert Path(trace_file).exists(), "Trace file not found"
assert Path(memory_file).exists(), "Memory file not found"
```

### Tool 3: Test with Minimal Input

**Start Small, Scale Up**:
```python
# Test with small trace first
for test_n_steps in [512, 1024, 2048]:
    result = generate_proof(test_n_steps)
    if not result.success:
        print(f"Failed at n_steps={test_n_steps}")
        break
```

### Tool 4: Compare with Canonical

**Test Against Known Good Proof**:
```python
# Test canonical proof verifies
canonical_proof = "integrity/examples/proofs/recursive/cairo0_stone6_keccak_160_lsb_example_proof.json"
verified = await verify_proof(canonical_proof)
assert verified, "Canonical proof should verify"
```

---

## Log Analysis

### Key Log Messages

**Success Indicators**:
```
✅ Stone proof generated successfully
✅ Proof verified on-chain
✅ Fact hash: 0x...
```

**Error Indicators**:
```
❌ Stone prover failed: Signal 6
❌ Invalid OODS
❌ VERIFIER_NOT_FOUND
```

### Log Analysis Steps

**1. Check Stone Prover Logs**:
- Look for "Signal 6" → FRI parameter issue
- Look for "File not found" → Path issue
- Look for timeout → System/resource issue

**2. Check Integrity Logs**:
- Look for "VERIFIER_NOT_FOUND" → Registry issue
- Look for "Invalid OODS" → Version mismatch
- Look for "Invalid builtin" → Layout issue

**3. Check Performance Logs**:
- Proof generation time
- Verification time
- Resource usage

---

## Support Resources

### Documentation

**Primary Resources**:
- `TROUBLESHOOTING_GUIDE.md` - This document
- `DEVELOPER_FAQ.md` - FAQ
- `ERROR_CODE_REFERENCE.md` - Error codes
- `STONE_PROVER_INTEGRATION_DEEP_DIVE.md` - Complete guide

### Community Support

**Channels**:
- GitHub Issues: [Your repo]
- Discord: [Your community]
- Stack Overflow: [Tag: obsqra-stone]

### Professional Support

**Enterprise Support**:
- Email: [Your support email]
- Slack: [Enterprise channel]
- Response time: 4-24 hours (depending on tier)

---

## Conclusion

Most issues can be resolved by:

1. **Using dynamic FRI calculation** (solves Signal 6)
2. **Matching Stone version with verifier** (solves OODS)
3. **Using public FactRegistry** (solves VERIFIER_NOT_FOUND)
4. **Using absolute paths** (solves file not found)
5. **Validating inputs** (prevents many errors)

**Next Steps**:
1. Check this guide for your error
2. Follow solution steps
3. Verify fix works
4. Document new issues

**Related Documents**:
- `ERROR_CODE_REFERENCE.md` - Complete error reference
- `DEBUGGING_STONE_PROVER.md` - Stone-specific debugging
- `DEVELOPER_FAQ.md` - Common questions

---

**This guide helps resolve most integration issues. For additional help, see support resources.**
