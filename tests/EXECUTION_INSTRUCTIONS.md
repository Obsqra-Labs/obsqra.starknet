# Test Suite Execution Instructions

## Prerequisites

### 1. Backend Server Running
```bash
cd /opt/obsqra.starknet/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Environment Configuration
- `MODEL_REGISTRY_ADDRESS` set in `backend/.env`
- `RISK_ENGINE_ADDRESS` set in `backend/.env`
- `STRATEGY_ROUTER_ADDRESS` set in `backend/.env`
- `BACKEND_WALLET_ADDRESS` set in `backend/.env`
- `BACKEND_WALLET_PRIVATE_KEY` set in `backend/.env`

### 3. Contracts Deployed
- RiskEngine v4 deployed to Sepolia
- StrategyRouter v3.5 deployed to Sepolia
- ModelRegistry deployed to Sepolia

### 4. Model Registered
- Initial model version registered in ModelRegistry

---

## Running Tests

### E2E Test Suite

```bash
cd /opt/obsqra.starknet
python3 tests/e2e_comprehensive_5_5_zkml.py
```

**Expected Output**:
- Backend health check
- Model Registry configuration
- Proof generation with model hash
- On-chain verification
- Test summary

### Benchmarking Suite

```bash
cd /opt/obsqra.starknet
python3 tests/benchmark_prover_performance.py
```

**Expected Output**:
- Performance metrics
- Statistical analysis
- Results saved to `benchmark_results.json`

---

## Troubleshooting

### Backend Not Running
**Error**: `Connection refused` or `404 Not Found`

**Solution**:
```bash
# Start backend
cd /opt/obsqra.starknet/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints Not Found
**Error**: `404 Not Found` for API endpoints

**Solution**:
- Verify routes are registered in `backend/app/main.py`
- Check API base URL in config
- Verify backend is running on correct port

### RPC Errors
**Error**: `IncompatibleRPCVersionWarning` or RPC errors

**Solution**:
- Tests use RPC fallback utilities
- Warnings are non-fatal
- Tests will retry with different RPCs

---

## Test Results

Results are printed to console and can be saved to files for analysis.

See `tests/TEST_RESULTS.md` for detailed results documentation.
