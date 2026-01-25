# Strategy Router V3 - Deployment & Next Steps

## ✅ Completed

1. **V3 Contract Created** - `strategy_router_v3.cairo`
   - Fixed yield accrual bug (ekubo salt)
   - Added individual yield accrual functions
   - Added slippage protection

2. **Contract Compiled** - ✅ Successfully
   - Class files generated: `obsqra_contracts_StrategyRouterV3.contract_class.json`
   - No compilation errors

3. **Deployment Script Created** - `deploy-v3-strk.sh`
   - Ready to deploy when account is funded

## ⚠️ Current Issue

**Deployment Failed**: Insufficient account balance
```
Error: Resources bounds exceed balance (28224036825909043040)
```

The deployer account needs more STRK to cover declaration and deployment gas fees.

## 📋 Next Steps

### 1. Fund Deployer Account
```bash
# Deployer address: 0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d
# Send STRK to this address on Sepolia testnet
```

### 2. Deploy V3 Contract
```bash
cd /opt/obsqra.starknet
./deploy-v3-strk.sh
```

### 3. Update Frontend Configuration

After successful deployment, update:
- `frontend/.env.local`:
  ```env
  NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=<new_v3_contract_address>
  ```

### 4. Update Integration Tests

Update `frontend/src/components/IntegrationTests.tsx`:
- Add slippage tolerance test functions
- Update contract address references
- Add tests for `update_slippage_tolerance()` and `get_slippage_tolerance()`

### 5. Test V3 Features

#### Slippage Protection
- Test `update_slippage_tolerance()` with owner wallet
- Test swaps with different slippage settings
- Test liquidity provision with slippage protection
- Verify transactions fail if slippage exceeds tolerance

#### Yield Accrual
- Test `accrue_yields()` (both protocols)
- Test `accrue_jediswap_yields()` (JediSwap only)
- Test `accrue_ekubo_yields()` (Ekubo only)
- Verify salt bug is fixed (no "Input too long" error)

### 6. Update Documentation

- Update `V3_CHANGES.md` with deployment address
- Update integration test documentation
- Document slippage protection usage

## 🔧 Deployment Details

**Deployment Script**: `/opt/obsqra.starknet/deploy-v3-strk.sh`

**Configuration**:
- Network: Starknet Sepolia
- Owner: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`
- Default Slippage: 1% swaps, 0.5% liquidity
- Allocation: 50% JediSwap, 50% Ekubo

**Deployment Output**:
- Contract address will be saved to: `deployments/sepolia-v3-strk.json`
- Class hash will be saved to: `deployments/v3_strk_class_hash.txt`

## 📝 Testing Checklist

- [ ] Deploy V3 contract
- [ ] Update frontend `.env.local`
- [ ] Test deposit/withdraw
- [ ] Test deploy_to_protocols with slippage protection
- [ ] Test yield accrual functions
- [ ] Test slippage tolerance updates
- [ ] Verify slippage protection works (transactions fail if exceeded)
- [ ] Update integration tests UI
- [ ] Document deployment in dev_log.md

## 🚀 Production Considerations

1. **Swap Slippage Calculation**: Currently uses conservative 95% estimate. In production:
   - Get quote from router first
   - Apply slippage to actual quote
   - Consider using price oracles for better estimates

2. **Slippage Settings**: Default values (1% swaps, 0.5% liquidity) are conservative. Adjust based on:
   - Market conditions
   - Pool liquidity
   - Risk tolerance

3. **Gas Optimization**: V3 contract is larger than V2. Monitor gas costs and consider optimizations if needed.



