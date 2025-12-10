# Testing Individual Protocols Before Pool Integration

## Strategy: Test Each Protocol Separately

Before integrating into Strategy Router, test each protocol individually to ensure they work.

## Protocol Addresses (Sepolia)

### JediSwap
- **Swap Router**: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
- **NFT Position Manager**: `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399`
- **Factory**: `0x050d3df81b920d3e608c4f7aeb67945a830413f618a1cf486bdcce66a395109c`

### Ekubo
- **Core**: `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384`
- **Router V3**: `0x0045f933adf0607292468ad1c1dedaa74d5ad166392590e72676a34d01d7b763`

### Tokens
- **STRK**: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d`
- **ETH**: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`

## Current Contract (Has STRK)
- **Address**: `0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a`
- **Balance**: 10 STRK (from your deposit)

## Testing Approach

### Option 1: Direct Contract Calls (Recommended)
Use `starkli` or frontend to call protocols directly from your contract.

### Option 2: Simple Test Contracts
Create minimal contracts that only interact with one protocol at a time.

### Option 3: Manual Testing via Frontend
Create UI buttons to test each protocol individually.

## Test JediSwap First

**Steps:**
1. Approve NFT Position Manager to spend STRK from contract
2. Approve NFT Position Manager to spend ETH (if needed)
3. Call `mint()` on NFT Position Manager with liquidity parameters
4. Verify position NFT was created

**JediSwap mint() parameters:**
- `token0`: STRK or ETH address
- `token1`: ETH or STRK address  
- `fee`: 3000 (0.3% fee tier)
- `tick_lower`: -887272 (full range)
- `tick_upper`: 887272 (full range)
- `amount0_desired`: Amount of token0
- `amount1_desired`: Amount of token1
- `amount0_min`: 0 (slippage)
- `amount1_min`: 0 (slippage)
- `recipient`: Contract address
- `deadline`: Current timestamp + 1800

## Test Ekubo Second

**Steps:**
1. Approve Ekubo Core to spend STRK from contract
2. Approve Ekubo Core to spend ETH (if needed)
3. Call `deposit_liquidity()` on Ekubo Core
4. Verify liquidity tokens received

**Ekubo deposit_liquidity() parameters:**
- `token0`: STRK or ETH address
- `token1`: ETH or STRK address
- `amount0`: Amount of token0
- `amount1`: Amount of token1
- `fee`: 3000 (0.3% fee tier)

## Next Steps

1. ✅ Test JediSwap deposit with small amount (1 STRK)
2. ✅ Test Ekubo deposit with small amount (1 STRK)
3. ✅ Once both work, integrate into Strategy Router's `deploy_to_protocols()`

