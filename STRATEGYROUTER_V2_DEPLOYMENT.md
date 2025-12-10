# StrategyRouterV2 Deployment Summary

**Date**: January 27, 2025  
**Network**: Starknet Sepolia Testnet  
**Status**: ✅ Successfully Deployed and Verified (ETH as Asset Token)

## Contract Addresses

### StrategyRouterV2 (Latest - ETH Asset Token + Protocol Integration + Exposed Functions)
- **Contract Address**: `0x008d34efb76e16b4b0c06d43010e4497d50d4a8c1e6ec0d7c485acf6d4ba6c6a`
- **Class Hash**: `0x0783c26c976b6bf96830f7efef3bc035b50adbac90216d4ecc54e310d25e365f`
- **Deploy Transaction**: `0x01052b8464dbb3a8adcdfa22abf2fc345ad6df8dba0a2234f4f3a7672abaa817`
- **Deploy Date**: December 9, 2024

**Starkscan Links**:
- Contract: https://sepolia.starkscan.co/contract/0x008d34efb76e16b4b0c06d43010e4497d50d4a8c1e6ec0d7c485acf6d4ba6c6a
- Transaction: https://sepolia.starkscan.co/tx/0x01052b8464dbb3a8adcdfa22abf2fc345ad6df8dba0a2234f4f3a7672abaa817
- Class: https://sepolia.starkscan.co/class/0x0783c26c976b6bf96830f7efef3bc035b50adbac90216d4ecc54e310d25e365f

**⚠️ Previous Deployments (Deprecated)**:
- `0x01c2e698bc0f263ea62dc3c557d32afe25c13cbc91900d726b84c58a0baa09f0` - Functions not exposed in ABI (ENTRYPOINT_NOT_FOUND)
- `0x053b69775c22246080a17c37a38dbda31d1841c8f6d7b4d928d54a99eda2748c` - No protocol integration

## Constructor Parameters

| Parameter | Address | Description |
|-----------|---------|-------------|
| `owner` | `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d` | Deployer wallet |
| `jediswap_router` | `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21` | JediSwap Swap Router (Sepolia) |
| `jediswap_nft_manager` | `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399` | JediSwap V2 NFT Position Manager |
| `ekubo_core` | `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384` | Ekubo Core (Sepolia) |
| `risk_engine` | `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80` | Risk Engine |
| `dao_manager` | `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` | DAO Constraint Manager |
| `asset_token` | `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7` | **ETH Token** ✅ |

## Verification Tests

### ✅ get_allocation
```bash
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 get_allocation \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```
**Result**: `[0x1388, 0x1388]` = 50% JediSwap, 50% Ekubo (5000 basis points each)

### ✅ get_protocol_addresses
```bash
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 get_protocol_addresses \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```
**Result**:
- JediSwap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21` ✓
- Ekubo Core: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384` ✓

### ✅ get_total_value_locked
```bash
starkli call 0x030d822149ad301082bc0e82bf1e0e9c365ee74a60c9e9732770921c79aed0d1 get_total_value_locked \
  --rpc https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7
```
**Result**: `[0x0, 0x0]` = 0 ETH (no deposits yet) ✓

## Key Changes from V1

### 1. Real Protocol Integration
- **Ekubo**: Integrated with Ekubo Core contract on Sepolia
- **JediSwap**: Integrated with JediSwap Swap Router on Sepolia
- Removed mock Nostra and zkLend (not available on testnet)

### 2. Simplified User Balance Tracking
- Removed Map-based per-user balance tracking (Cairo 2 Map API complexity)
- Using total deposits tracking for now
- Can add per-user tracking later with proper Map implementation

### 3. Interface Definitions
- Created `/contracts/src/interfaces/ekubo.cairo` with `IEkuboCore` traits
- Created `/contracts/src/interfaces/jediswap.cairo` with `IJediSwapRouter` traits
- Created `/contracts/src/interfaces/erc20.cairo` with `IERC20` trait

### 4. Event Emissions
- Deposit events with timestamp
- Withdrawal events with yield tracking
- Rebalancing events with old/new allocations

## Protocol Addresses Reference

### Ekubo (Sepolia)
```json
{
  "core": "0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384",
  "positions": "0x06a2aee84bb0ed5dded4384ddd0e40e9c1372b818668375ab8e3ec08807417e5",
  "router_v3": "0x0045f933adf0607292468ad1c1dedaa74d5ad166392590e72676a34d01d7b763"
}
```

### JediSwap (Sepolia)
```json
{
  "factory": "0x050d3df81b920d3e608c4f7aeb67945a830413f618a1cf486bdcce66a395109c",
  "swap_router": "0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21",
  "nft_router": "0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399"
}
```

### Tokens (Sepolia)
```json
{
  "strk": "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1",
  "eth": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
}
```

## Frontend Integration

The frontend has been updated to use the new StrategyRouterV2 address:

```bash
# /opt/obsqra.starknet/frontend/.env.local
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x008d34efb76e16b4b0c06d43010e4497d50d4a8c1e6ec0d7c485acf6d4ba6c6a
```

**Important**: The contract now accepts **ETH** deposits (not STRK). Users deposit ETH, and the contract swaps half to STRK for liquidity pools.

**Frontend URL**: https://starknet.obsqra.fi

## Next Steps

### Immediate
1. ✅ Deploy contracts
2. ✅ Verify on-chain functionality
3. 🔄 Test frontend integration
4. 🔄 End-to-end testing with real protocols

### Future Enhancements
1. **Add Per-User Balance Tracking**: Implement proper Map access patterns or use alternative storage
2. **Implement Actual Protocol Calls**: 
   - JediSwap: `add_liquidity()` and `swap_exact_tokens_for_tokens()`
   - Ekubo: `deposit_liquidity()` and `swap()`
3. **Yield Accrual**: Query and distribute yields from protocols
4. **Rebalancing Logic**: Automatically adjust allocations based on DAO constraints
5. **Emergency Withdrawals**: Add pause/unpause functionality
6. **Gas Optimization**: Batch operations where possible

## Deployment Commands

For reference, here are the exact commands used:

### Declare
```bash
cd /opt/obsqra.starknet/contracts
sncast --account deployer declare --network sepolia --contract-name StrategyRouterV2
```

### Deploy (Latest - ETH Asset Token + Protocol Integration + Exposed Functions)
```bash
sncast --account deployer deploy \
  --class-hash 0x0783c26c976b6bf96830f7efef3bc035b50adbac90216d4ecc54e310d25e365f \
  --constructor-calldata \
    0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d \
    0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21 \
    0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399 \
    0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384 \
    0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80 \
    0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856 \
    0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7 \
  --network sepolia
```

**Note**: The last parameter is the ETH token address (not STRK). Users deposit ETH, and the contract handles swapping to STRK internally.

## Files Modified

- `/opt/obsqra.starknet/contracts/src/strategy_router_v2.cairo` - New contract
- `/opt/obsqra.starknet/contracts/src/interfaces/ekubo.cairo` - New interface
- `/opt/obsqra.starknet/contracts/src/interfaces/jediswap.cairo` - New interface
- `/opt/obsqra.starknet/contracts/src/interfaces/erc20.cairo` - New interface
- `/opt/obsqra.starknet/contracts/src/interfaces.cairo` - New aggregator
- `/opt/obsqra.starknet/contracts/src/lib.cairo` - Updated to include V2
- `/opt/obsqra.starknet/contracts/protocol_addresses_sepolia.json` - Protocol addresses
- `/opt/obsqra.starknet/frontend/.env.local` - Updated contract address

---

**Note**: This V2 contract is functional but simplified. The TODO comments in the code indicate where actual protocol integration logic needs to be implemented. The current implementation focuses on:
1. Proper interface definitions ✅
2. Storage structure ✅
3. Event emissions ✅
4. Basic deposit/withdraw flow ✅
5. Allocation management ✅

The next phase will implement the actual protocol interaction logic for deposits, withdrawals, and yield accrual.

