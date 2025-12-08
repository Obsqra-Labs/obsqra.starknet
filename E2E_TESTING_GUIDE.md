# End-to-End Testing Guide - StrategyRouterV2

## Overview

This guide provides step-by-step testing procedures for the ObsQRA DeFi Strategy Router V2 integrated with Ekubo and JediSwap protocols on Starknet Sepolia testnet.

## Prerequisites

- ✅ Frontend running at: https://starknet.obsqra.fi (or http://localhost:3003)
- ✅ Contracts deployed on Sepolia
- ✅ Wallet with Sepolia STRK (from faucet)
- ✅ ArgentX or Braavos wallet installed

## Contract Addresses

| Contract | Address |
|----------|---------|
| **StrategyRouterV2** | `0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1` |
| RiskEngine | `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80` |
| DAOManager | `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` |
| STRK Token | `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1` |
| Ekubo Core | `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384` |
| JediSwap Router | `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21` |

## Test Suite

### 1. Contract Verification Tests

#### 1.1 Verify Contract Deployment
```bash
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 \
  get_total_value_locked \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```
**Expected**: `[0x0, 0x0]` (0 STRK initially)

#### 1.2 Verify Allocation Settings
```bash
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 \
  get_allocation \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```
**Expected**: `[0x1388, 0x1388]` (5000, 5000) = 50% JediSwap, 50% Ekubo

#### 1.3 Verify Protocol Addresses
```bash
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 \
  get_protocol_addresses \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```
**Expected**: 
- JediSwap: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- Ekubo: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`

### 2. Frontend Tests

#### 2.1 Wallet Connection
1. Navigate to https://starknet.obsqra.fi
2. Click "Connect Wallet"
3. Select ArgentX or Braavos
4. Approve connection
5. **Expected**: Wallet address displayed, Dashboard visible

#### 2.2 Demo Mode Toggle
1. Click "Demo Mode" toggle in header
2. **Expected**: 
   - Mock statistics appear
   - Transaction buttons disabled or show "demo" state
   - Demo banner visible
3. Toggle back to Live Mode
4. **Expected**: Real contract data loads

#### 2.3 Dashboard Display
Verify the following sections are visible:
- [ ] Portfolio Overview (Total Value, APY, Risk Score)
- [ ] Deposit/Withdraw interface
- [ ] Analytics Dashboard tab
- [ ] Transaction History tab
- [ ] Protocol allocations display

### 3. Transaction Tests

#### 3.1 Get Test STRK
```bash
# Visit Starknet Faucet (requires GitHub login or mobile hotspot if rate-limited)
# https://starknet-faucet.vercel.app/
```

#### 3.2 Check STRK Balance
```bash
starkli balance <YOUR_WALLET_ADDRESS> \
  --erc20 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1 \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```

#### 3.3 Approve STRK for Router (Required before deposit)
```bash
# Using starkli (replace placeholders)
starkli invoke \
  0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1 \
  approve \
  0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 \
  100000000000000000000 0 \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7 \
  --account <YOUR_WALLET_FILE>
```

Or via Frontend:
1. Enter deposit amount (e.g., 10 STRK)
2. Click "Deposit"
3. Wallet will prompt for approval first
4. **Expected**: Approval transaction sent

#### 3.4 Deposit Test
1. Enter amount (e.g., 10 STRK)
2. Click "Deposit"
3. Approve in wallet
4. **Expected**:
   - Transaction sent
   - "Pending" status in Transaction History
   - After confirmation: "Confirmed" status
   - Total Value Locked increases
   - Event emitted (check Starkscan)

#### 3.5 Verify Deposit On-Chain
```bash
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 \
  get_total_value_locked \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```
**Expected**: Shows deposited amount (in u256 format)

#### 3.6 Check User Balance
```bash
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 \
  get_user_balance \
  <YOUR_WALLET_ADDRESS> \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```
**Expected**: Returns total_deposits (simplified, not per-user yet)

#### 3.7 Withdrawal Test
1. Enter withdrawal amount (≤ deposited amount)
2. Click "Withdraw"
3. Approve in wallet
4. **Expected**:
   - Transaction sent
   - STRK returned to wallet
   - Total Value Locked decreases
   - Event emitted

### 4. Analytics Tests

#### 4.1 Analytics Dashboard
1. Click "Analytics" tab
2. Verify display of:
   - [ ] Portfolio performance chart
   - [ ] Risk metrics
   - [ ] Protocol breakdown
   - [ ] Historical APY

**Note**: In current implementation, this may show mock data until actual protocol integration is complete.

#### 4.2 Transaction History
1. Click "History" tab
2. **Expected**:
   - All deposit/withdrawal transactions listed
   - Status indicators (Pending/Confirmed/Failed)
   - Links to Starkscan for each tx
   - Timestamps

### 5. Protocol Integration Tests (Partial)

⚠️ **Current Status**: Interfaces defined, but actual protocol calls (JediSwap liquidity, Ekubo swaps) are marked as TODO in the contract. These tests will pass basic checks but won't trigger real protocol interactions yet.

#### 5.1 Verify Ekubo Integration
```bash
# Check that Ekubo core address is set correctly
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 \
  get_protocol_addresses \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```

#### 5.2 Verify JediSwap Integration
Same as above - verifies router address is configured.

**Next Phase**: Implement actual `add_liquidity()`, `swap()` calls in deposit/withdraw functions.

### 6. Error Handling Tests

#### 6.1 Insufficient Balance Withdrawal
1. Try to withdraw more than deposited
2. **Expected**: Transaction reverts with "Insufficient balance"

#### 6.2 Zero Amount Operations
1. Try to deposit 0 STRK
2. **Expected**: Should handle gracefully (or revert if validation added)

#### 6.3 Network Errors
1. Disconnect internet briefly
2. Try a transaction
3. **Expected**: Proper error message displayed

#### 6.4 Wallet Rejection
1. Start a transaction
2. Reject in wallet
3. **Expected**: Transaction marked as "Failed" or removed

### 7. Block Explorer Verification

#### 7.1 Check Contract on Starkscan
Visit: https://sepolia.starkscan.co/contract/0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1

Verify:
- [ ] Contract is verified (may take time for indexer)
- [ ] Read/Write functions visible
- [ ] Events tab shows Deposit/Withdrawal events

#### 7.2 Check Recent Transactions
After performing a deposit:
1. Visit transaction on Starkscan
2. Verify:
   - [ ] Transaction succeeded
   - [ ] Events emitted
   - [ ] Correct contract called

## Automated Test Script

```bash
#!/bin/bash
# Quick smoke test script

RPC_URL="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
ROUTER="0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1"

echo "=== StrategyRouterV2 Smoke Test ==="
echo ""

echo "1. Checking Total Value Locked..."
starkli call $ROUTER get_total_value_locked --rpc $RPC_URL
echo ""

echo "2. Checking Allocation..."
starkli call $ROUTER get_allocation --rpc $RPC_URL
echo ""

echo "3. Checking Protocol Addresses..."
starkli call $ROUTER get_protocol_addresses --rpc $RPC_URL
echo ""

echo "=== Test Complete ==="
```

Save as `test_router_v2.sh` and run:
```bash
chmod +x test_router_v2.sh
./test_router_v2.sh
```

## Known Limitations (Current Version)

1. **Per-User Balance Tracking**: Simplified to total_deposits (Map API complexity)
2. **Protocol Interactions**: Interfaces defined but actual deposit/withdraw to Ekubo/JediSwap not implemented (marked TODO)
3. **Yield Accrual**: Returns 0 (not querying actual yields yet)
4. **Rebalancing**: Manual trigger exists but logic is placeholder

## Success Criteria

- [x] Contracts deployed and callable ✅
- [x] Frontend connects to wallet ✅
- [x] Contract view functions return expected values ✅
- [ ] Deposit transaction succeeds (requires STRK and approval)
- [ ] Withdrawal transaction succeeds
- [ ] Events emitted correctly
- [ ] Transaction history displays correctly
- [ ] Analytics dashboard renders
- [ ] Demo mode works

## Troubleshooting

### Contract Not Found
- Verify you're on Sepolia testnet
- Check RPC URL is correct
- Contract might need a few blocks to be indexed

### Wallet Won't Connect
- Ensure using HTTPS (https://starknet.obsqra.fi)
- Clear browser cache
- Check wallet is on Sepolia network

### Transaction Fails
- Check STRK balance
- Verify approval was given to router
- Check gas settings
- View error in Starkscan

### Frontend Shows Old Contract
- Restart frontend: `pkill -f "next dev" && cd /opt/obsqra.starknet/frontend && npm run dev`
- Clear browser cache
- Verify `.env.local` has correct address

## Next Phase: Full Protocol Integration

To complete the protocol integration:

1. **Implement JediSwap Liquidity**:
   ```cairo
   // In deposit()
   let jedi_amount = (amount * jediswap_allocation) / 10000;
   let jedi_router = IJediSwapRouterDispatcher { contract_address: self.jediswap_router.read() };
   jedi_router.add_liquidity(...);
   ```

2. **Implement Ekubo Swaps**:
   ```cairo
   // In deposit()
   let ekubo_amount = (amount * ekubo_allocation) / 10000;
   let ekubo_core = IEkuboCoreDispatcher { contract_address: self.ekubo_core.read() };
   ekubo_core.deposit_liquidity(...);
   ```

3. **Yield Queries**:
   ```cairo
   fn accrue_yields() -> u256 {
       let jedi_yield = query_jediswap_yield();
       let ekubo_yield = query_ekubo_yield();
       jedi_yield + ekubo_yield
   }
   ```

4. **Proportional Withdrawals**:
   ```cairo
   fn withdraw(amount: u256) {
       let jedi_withdraw = (amount * jediswap_tvl) / total_tvl;
       let ekubo_withdraw = (amount * ekubo_tvl) / total_tvl;
       // Withdraw from each
   }
   ```

## Resources

- **Starknet Sepolia RPC**: https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
- **Starkscan**: https://sepolia.starkscan.co
- **Voyager**: https://sepolia.voyager.online
- **Faucet**: https://starknet-faucet.vercel.app/
- **Frontend**: https://starknet.obsqra.fi

---

**Last Updated**: December 5, 2025  
**Version**: StrategyRouterV2 (Sepolia)

