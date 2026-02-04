# Obsqra zkML Test Suite

Comprehensive test suite for the Obsqra zkML system.

## Test Files

### End-to-End Tests

#### `e2e_comprehensive_5_5_zkml.py`
Complete end-to-end test suite covering all 5/5 zkML maturity requirements.

**Tests**:
1. Backend health check
2. Model Registry configuration
3. Proof generation with model hash
4. On-chain verification
5. Model Registry on-chain query
6. Full execution flow
7. UX integration

**Usage**:
```bash
cd /opt/obsqra.starknet
python3 tests/e2e_comprehensive_5_5_zkml.py
```

### Benchmarking

#### `benchmark_prover_performance.py`
Performance benchmarking suite for Stone prover.

**Metrics**:
- Proof generation time
- Proof size
- Verification time
- Success rate

**Usage**:
```bash
cd /opt/obsqra.starknet
python3 tests/benchmark_prover_performance.py
```

**Output**: `benchmark_results.json`

## Running All Tests

```bash
# E2E tests
python3 tests/e2e_comprehensive_5_5_zkml.py

# Benchmarks
python3 tests/benchmark_prover_performance.py
```

## Test Requirements

- Backend running on `http://localhost:8000`
- Contracts deployed to Sepolia
- Model Registry configured
- Stone prover binary available

## Test Results

Results are printed to console and can be saved to files for analysis.
