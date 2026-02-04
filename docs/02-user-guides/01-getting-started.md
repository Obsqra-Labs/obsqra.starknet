# Getting Started

Welcome to Obsqra! This guide will help you set up your wallet, connect to the system, and execute your first verifiable allocation.

## Prerequisites

Before you begin, ensure you have:

1. **Starknet Wallet**
   - Argent X or Braavos wallet installed
   - Wallet connected to Starknet Sepolia testnet
   - Some testnet STRK tokens (for gas fees)

2. **Browser**
   - Modern browser with wallet extension
   - JavaScript enabled

3. **Network Access**
   - Access to Starknet Sepolia RPC
   - Internet connection

## Setting Up Your Wallet

### Step 1: Install Wallet Extension

**Argent X:**
1. Visit https://www.argent.xyz/
2. Install the browser extension
3. Create a new wallet or import existing

**Braavos:**
1. Visit https://braavos.app/
2. Install the browser extension
3. Create a new wallet or import existing

### Step 2: Connect to Sepolia Testnet

1. Open your wallet extension
2. Go to Settings → Networks
3. Add Sepolia testnet:
   - **Network Name:** Sepolia
   - **RPC URL:** `https://starknet-sepolia-rpc.publicnode.com`
   - **Chain ID:** `SN_SEPOLIA`
   - **Explorer:** `https://sepolia.starkscan.co`

4. Switch to Sepolia network

### Step 3: Get Testnet Tokens

**Option 1: Starknet Faucet**
1. Visit https://starknet-faucet.vercel.app/
2. Connect your wallet
3. Request testnet STRK tokens

**Option 2: Bridge from Ethereum**
1. Use Starknet bridge: https://starkgate.starknet.io/
2. Bridge ETH from Ethereum Sepolia
3. Convert to STRK if needed

**Minimum Required:**
- 0.01 STRK for gas fees (recommended: 0.1 STRK)

## Connecting to the System

### Step 1: Access the Frontend

**Production (if available):**
- Visit: `https://starknet.obsqra.fi`

**Local Development:**
1. Ensure backend is running (port 8001)
2. Start frontend:
   ```bash
   cd /opt/obsqra.starknet/frontend
   npm install
   npm run dev
   ```
3. Visit: `http://localhost:3003`

### Step 2: Connect Your Wallet

1. Click "Connect Wallet" button
2. Select your wallet (Argent X or Braavos)
3. Approve connection request
4. Verify wallet address is displayed

**Troubleshooting:**
- Ensure wallet is on Sepolia network
- Check wallet extension is unlocked
- Refresh page if connection fails

## Understanding the Dashboard

Once connected, you'll see the main dashboard:

### Dashboard Components

1. **Portfolio Overview**
   - Total deposited amount
   - Current allocation percentages
   - Total yield accrued
   - Performance metrics

2. **Allocation Display**
   - Current allocation across protocols
   - JediSwap percentage
   - Ekubo percentage
   - Last update timestamp

3. **Proof Information**
   - Latest proof hash
   - Verification status
   - Model version
   - Fact registry link

4. **Action Buttons**
   - "Orchestrate Allocation" - Generate new allocation
   - "Deposit" - Add funds
   - "Withdraw" - Remove funds
   - "View History" - Allocation history

## First Allocation Execution

### Step 1: Review Current State

Before executing:
1. Check current allocation percentages
2. Review protocol metrics (if displayed)
3. Verify wallet has sufficient balance

### Step 2: Execute Allocation

1. Click "Orchestrate Allocation" button
2. Review the allocation request:
   - Protocol metrics will be fetched automatically
   - Risk scores will be calculated
   - Proof will be generated

3. **What Happens:**
   ```
   User clicks "Orchestrate Allocation"
        ↓
   Backend fetches protocol metrics
        ↓
   Risk scores calculated
        ↓
   STARK proof generated (2-4 seconds)
        ↓
   Proof verified in Fact Registry
        ↓
   Transaction submitted to RiskEngine
        ↓
   Contract verifies proof on-chain
        ↓
   Allocation executed
        ↓
   Result displayed to user
   ```

### Step 3: Monitor Progress

You'll see real-time updates:
- "Generating proof..." (2-4 seconds)
- "Verifying proof..." (1-2 seconds)
- "Submitting transaction..." (5-10 seconds)
- "Transaction confirmed!" (12+ seconds)

### Step 4: View Results

After execution:
1. **Allocation Decision:**
   - New allocation percentages
   - Risk scores for each protocol
   - APY values

2. **Proof Information:**
   - Proof hash (clickable link)
   - Verification status (✅ Verified)
   - Fact registry link

3. **Transaction Details:**
   - Transaction hash (Starkscan link)
   - Block number
   - Timestamp

## Understanding Your First Allocation

### What You Just Did

1. **Triggered Verifiable AI Decision**
   - System calculated optimal allocation
   - Generated cryptographic proof
   - Verified proof on-chain

2. **Executed Trustless Allocation**
   - No trust in backend required
   - Proof verifies correctness
   - On-chain verification gate enforced

3. **Created Audit Trail**
   - Proof hash is permanent
   - Transaction is on-chain
   - Verifiable by anyone

### Key Information to Note

**Proof Hash:**
- Example: `0xa580bd...`
- This is your cryptographic proof
- Can be verified independently
- Permanent record

**Verification Status:**
- ✅ Verified: Proof is valid
- ⏳ Pending: Verification in progress
- ❌ Failed: Proof verification failed

**Transaction Hash:**
- Links to Starkscan explorer
- Shows on-chain execution
- Includes all event logs

## Next Steps

Now that you've executed your first allocation:

1. **[Executing Allocations](02-executing-allocations.md)** - Learn more about the allocation process
2. **[Viewing Transparency](03-viewing-transparency.md)** - Understand proof verification
3. **[Troubleshooting](04-troubleshooting.md)** - Common issues and solutions

## Quick Reference

### Contract Addresses (Sepolia)

- **RiskEngine:** `0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4`
- **StrategyRouter:** `0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b`
- **ModelRegistry:** `0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc`

### Useful Links

- **Starkscan Explorer:** https://sepolia.starkscan.co
- **Starknet Docs:** https://docs.starknet.io
- **Argent X:** https://www.argent.xyz/
- **Braavos:** https://braavos.app/

### Support

If you encounter issues:
- Check [Troubleshooting Guide](04-troubleshooting.md)
- Review [FAQ](../10-troubleshooting/02-faq.md)
- Check backend logs (if running locally)

---

**Congratulations!** You've executed your first verifiable allocation. Every decision is now cryptographically proven and verifiable.
