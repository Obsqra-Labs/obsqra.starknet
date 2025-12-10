# ZAP Contracts & Getting Testnet Tokens

## What is a ZAP Contract?

A **ZAP contract** is a smart contract that bundles multiple DeFi operations into a single transaction. It simplifies complex operations that would normally require multiple steps.

### The Problem It Solves

**Without ZAP:**
```
1. User has 100 STRK
2. Need to add liquidity to STRK/ETH pool
3. Pool requires 50 STRK + 50 ETH
4. Steps needed:
   - Swap 50 STRK → 50 ETH (Transaction 1)
   - Approve pool to spend STRK (Transaction 2)
   - Approve pool to spend ETH (Transaction 3)
   - Add liquidity (Transaction 4)
   = 4 transactions, 4 gas fees
```

**With ZAP:**
```
1. User has 100 STRK
2. Call ZAP contract with 100 STRK
3. ZAP automatically:
   - Swaps 50 STRK → 50 ETH
   - Approves tokens
   - Adds liquidity
   = 1 transaction, 1 gas fee
```

### How It Works

A ZAP contract typically:
1. **Accepts single token** (e.g., STRK)
2. **Splits it** into the required pair (e.g., 50% STRK, 50% ETH)
3. **Swaps** half to the other token if needed
4. **Adds liquidity** to the pool
5. **Returns** LP tokens/NFT to user

### JediSwap ZAP

According to [JediSwap documentation](https://docs.jediswap.xyz/how-to-use-jediswap/how-to-zap), JediSwap has ZAP functionality that allows:
- Adding liquidity with a single token
- Automatically handling the swap and liquidity provision

**Check if JediSwap has a ZAP contract address** - it might be in their contract addresses list.

---

## Getting Testnet Tokens (Starknet Sepolia)

### Important: Starknet Uses STRK, Not ETH

On Starknet Sepolia testnet, you need:
- **STRK** (Starknet's native token) - for gas fees
- **ETH** (bridged from Ethereum) - for DeFi operations

### Option 1: Starknet Faucet (For STRK)

**Starknet Sepolia Faucet:**
- **URL**: https://faucet.starknet.io/
- **What you get**: STRK tokens for gas
- **Requirements**: 
  - Starknet wallet address
  - Sometimes requires social verification (Twitter/Discord)

**Steps:**
1. Go to https://faucet.starknet.io/
2. Connect your Starknet wallet (ArgentX, Braavos, etc.)
3. Select "Sepolia" testnet
4. Request STRK tokens
5. Wait a few minutes for tokens to arrive

### Option 2: Get Sepolia ETH and Bridge to Starknet

**Step 1: Get Sepolia ETH**

**Chainstack Faucet** (Recommended - No Twitter auth):
- **URL**: https://chainstack.com/faucets/
- **Steps**:
  1. Go to https://chainstack.com/faucets/
  2. Click "Sepolia testnet faucet"
  3. Connect your Ethereum wallet (MetaMask, etc.)
  4. Make sure wallet is on Sepolia network
  5. Click "Claim test tokens"
  6. Wait for ETH to arrive (usually instant)

**Alchemy Sepolia Faucet** (Alternative):
- **URL**: https://sepoliafaucet.com/ or https://www.alchemy.com/faucets/ethereum-sepolia
- **Steps**:
  1. Sign up for free Alchemy account
  2. Go to their Sepolia faucet
  3. Enter your Ethereum address
  4. Request testnet ETH (up to 0.5 ETH per day)

**Step 2: Bridge Sepolia ETH to Starknet Sepolia**

You have **3 options** for bridging:

#### Option A: Rhino.fi Bridge (Easiest)
- **URL**: https://app.rhino.fi/bridge?token=ETH&chainOut=STARKNET
- **Steps**:
  1. Visit https://app.rhino.fi/bridge
  2. Connect your **Ethereum wallet** (MetaMask) - make sure it's on Sepolia network
  3. Connect your **Starknet wallet** (ArgentX or Braavos) - make sure it's on Sepolia
  4. Select:
     - **From**: Sepolia (Ethereum)
     - **To**: Starknet Sepolia
     - **Token**: ETH
  5. Enter amount to bridge
  6. Click "Bridge"
  7. Approve transactions in both wallets
  8. Wait for bridge to complete (usually 5-15 minutes)

#### Option B: StarkGate Bridge (Official)
- **URL**: https://starkgate.starknet.io/ (check if they support Sepolia testnet)
- **Steps**:
  1. Visit StarkGate bridge
  2. Connect both wallets (Ethereum + Starknet)
  3. Select Sepolia → Starknet Sepolia
  4. Enter amount and bridge

#### Option C: Orbiter Finance
- **URL**: https://www.orbiter.finance/ (check if they support Sepolia)
- Similar process to Rhino.fi

**Note**: Not all bridges support testnet. **Rhino.fi is confirmed to work for Sepolia → Starknet Sepolia**.

### Option 3: Chainstack Faucet

**Chainstack Multi-Chain Faucet:**
- **URL**: https://chainstack.com/faucets/
- **What you get**: Testnet tokens for multiple chains
- **Supports**: Sepolia, Starknet, etc.

### Option 4: QuickNode Faucet

**QuickNode Ethereum Faucet:**
- **URL**: https://faucet.quicknode.com/ethereum
- **What you get**: Sepolia ETH
- **Requirements**: QuickNode account (free tier available)

---

## For Your Specific Use Case

### What You Need:

1. **STRK** (for gas fees on Starknet)
   - Get from: https://faucet.starknet.io/
   - Amount: Usually 0.1-1 STRK is enough for testing

2. **ETH** (for DeFi operations - STRK/ETH pool)
   - Get from: Alchemy/Chainstack/QuickNode Sepolia faucets
   - Bridge to Starknet if needed
   - Or swap STRK → ETH on JediSwap testnet

### Recommended Approach:

1. **Get STRK first** (from Starknet faucet)
2. **Swap some STRK to ETH** on JediSwap testnet
   - Use JediSwap Swap Router: `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21`
   - Or use a bridge if available

3. **Now you have both tokens** for liquidity provision

---

## Alternative: Use ZAP If Available

If JediSwap has a ZAP contract on testnet:

1. **Find ZAP contract address** (check JediSwap docs/contract addresses)
2. **Update StrategyRouter** to use ZAP instead of direct liquidity
3. **Call ZAP with STRK only** - it handles the rest

**Example:**
```cairo
// Instead of:
manager.mint(mint_params);  // Requires both tokens

// Use ZAP:
zap.add_liquidity_single_token(
    token: STRK,
    amount: jediswap_amount,
    pool: STRK_ETH_POOL,
    min_liquidity: min_liquidity
);
```

---

## Quick Reference: Token Addresses (Sepolia)

From your `protocol_addresses_sepolia.json`:

- **STRK**: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`
- **ETH**: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`

---

## Testing Strategy

### Option A: Manual Two-Step (No ZAP)
1. Get STRK from faucet
2. Swap half STRK → ETH on JediSwap
3. Now you have both tokens
4. Add liquidity with both tokens

### Option B: Use ZAP (If Available)
1. Get STRK from faucet
2. Call ZAP contract with STRK
3. ZAP handles swap + liquidity in one step

### Option C: Test with Mock Tokens
1. Deploy mock STRK and ETH tokens
2. Mint yourself test amounts
3. Test liquidity provision
4. No faucet needed!

---

## Links

- **Starknet Sepolia Faucet**: https://faucet.starknet.io/
- **Alchemy Sepolia Faucet**: https://www.alchemy.com/faucets/ethereum-sepolia
- **Chainstack Faucet**: https://chainstack.com/faucets/
- **QuickNode Faucet**: https://faucet.quicknode.com/ethereum
- **JediSwap Docs**: https://docs.jediswap.xyz/
- **JediSwap ZAP Guide**: https://docs.jediswap.xyz/how-to-use-jediswap/how-to-zap

---

## Next Steps for Your Implementation

1. **Check if JediSwap has ZAP contract**:
   - Look in their contract addresses
   - Check their documentation
   - If yes, use it! Much simpler.

2. **If no ZAP, implement swap first**:
   - Before adding liquidity, swap half STRK to ETH
   - Then add liquidity with both tokens

3. **For testing**:
   - Get STRK from faucet
   - Swap to ETH on testnet
   - Test your deposit() function

