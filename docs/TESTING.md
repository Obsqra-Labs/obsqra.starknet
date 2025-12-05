# Testing Guide

## Current Status

- ✅ **28 unit tests** written across 3 test files
- ✅ **Contracts compile** successfully
- ⏳ **snforge** needs to be installed to run tests

## Test Files

1. `tests/test_risk_engine.cairo` - 15 tests
2. `tests/test_strategy_router.cairo` - 7 tests
3. `tests/test_dao_constraints.cairo` - 9 tests

## Installing snforge

### Option 1: Using snfoundryup (Recommended)

```bash
# Install snfoundryup (if not already installed)
curl -L https://raw.githubusercontent.com/foundry-rs/starknet-foundry/master/scripts/install.sh | bash

# Source bashrc
source ~/.bashrc

# Install Starknet Foundry
snfoundryup

# Verify installation
snforge --version
```

### Option 2: Build from Source

```bash
cd /tmp
git clone https://github.com/foundry-rs/starknet-foundry.git
cd starknet-foundry
git checkout v0.20.0
cargo build --release --bin snforge
cp target/release/snforge ~/.local/bin/
```

## Running Tests

Once snforge is installed:

```bash
cd /opt/obsqra.starknet/contracts
snforge test
```

### Run Specific Test File

```bash
snforge test test_risk_engine
```

### Run with Verbose Output

```bash
snforge test --verbose
```

### Run with Gas Reporting

```bash
snforge test --gas-report
```

## Test Coverage

### RiskEngine Tests (15)
- Risk score calculation (low/high risk, edge cases)
- Allocation calculation (balanced, extreme APY, high risk penalty)
- Constraint verification (valid/invalid, edge cases, diversification)

### StrategyRouter Tests (7)
- Allocation management (initial, update, access control)
- Error handling (unauthorized, invalid sums)
- Edge cases (100% single, equal split)

### DAOConstraintManager Tests (9)
- Constraint management (get/set, access control)
- Allocation validation (valid/invalid, edge cases, different configs)

## Expected Results

All 28 tests should pass. The tests cover:
- Normal operation paths
- Edge cases and boundaries
- Error conditions
- Access control
- Mathematical correctness

## Troubleshooting

### snforge not found
- Ensure PATH includes `~/.foundry/bin` or `~/.local/bin`
- Run `source ~/.bashrc` after installation
- Check installation with `snforge --version`

### Test compilation errors
- Ensure contracts compile: `scarb build`
- Check test syntax matches snforge patterns
- Verify Scarb.toml has correct dependencies

### Test failures
- Review test output for specific errors
- Check contract logic matches test expectations
- Verify test data and assertions

## Next Steps

1. Install snforge
2. Run full test suite
3. Fix any test syntax issues (if needed)
4. Verify all tests pass
5. Add integration tests
6. Gas profiling

