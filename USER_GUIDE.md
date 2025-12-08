# Obsqura Yield Optimizer - User Guide

## Overview

Obsqura is a verifiable AI-powered yield optimizer on Starknet. Every allocation decision is:
- **Calculated by AI risk engine** - On-chain Cairo smart contracts
- **Cryptographically proven** - STARK proofs for every decision
- **Verified on-chain** - Transparent and auditable
- **Fully traceable** - Complete history with proof status

**Live Application**: https://starknet.obsqra.fi

---

## Getting Started

### 1. Connect Your Wallet

1. Visit **https://starknet.obsqra.fi**
2. Click **"Connect Wallet"**
3. Select your wallet:
   - **Argent X** (Recommended)
   - **Braavos**
4. Approve the connection in your wallet

### 2. View the Dashboard

Once connected, you'll see:

**Current Statistics**:
- **Total Value Locked (TVL)** - Total STRK in the strategy
- **JediSwap Allocation** - Current percentage allocated to JediSwap
- **Ekubo Allocation** - Current percentage allocated to Ekubo

**Rebalance History**:
- Recent allocation decisions
- Cryptographic proofs for each rebalance
- Risk scores and transaction links

---

## Understanding Proofs

Each rebalance generates a **STARK proof** that verifies the AI's decision was calculated correctly.

### Proof Status Indicators

| Status | Icon | Color | Meaning |
|--------|------|-------|---------|
| **Generated** | ⏳ | Yellow | Proof created locally (2-3s) |
| **Submitted** | ✓ | Blue | Sent to SHARP for L1 verification |
| **Verifying** | 🔄 | Orange | SHARP verifying on Ethereum (10-60 min) |
| **Verified** | ✅ | Green | Proof verified on Ethereum L1 |

### Viewing Proof Details

**Hover over any proof badge** to see:
- **Proof Hash** - Cryptographic commitment (e.g., `0xa580bdcca2ad...`)
- **Transaction Hash** - Starknet transaction (click to view on Voyager)
- **Fact Hash** - Ethereum L1 verification hash
- **Submission Timestamp** - When proof was submitted to SHARP

---

## Rebalance History

The **Recent Rebalances** section shows all past allocation decisions:

### Desktop View (Table)
- **Time** - How long ago the rebalance occurred
- **Allocation** - JediSwap and Ekubo percentages
- **Risk Scores** - Calculated risk for each protocol (5-95 scale)
- **Proof** - STARK proof with status badge
- **Transaction** - Link to block explorer

### Mobile View (Cards)
- Compact card design for small screens
- All information available
- Swipe to view more

**Auto-refreshes every 30 seconds** to show latest data.

---

## AI Risk Engine Orchestration

### How It Works

1. **Collect Metrics**
   - Utilization rates
   - Volatility measures  
   - Liquidity tiers
   - Audit scores
   - Protocol age

2. **Calculate Risk**
   - On-chain Cairo smart contract
   - Weighted risk formula
   - Returns risk score (5-95)

3. **Generate Proof**
   - STARK proof (2-3 seconds)
   - Cryptographic commitment
   - Stored in database

4. **Execute On-Chain**
   - Backend signs transaction
   - Updates StrategyRouterV2
   - Records decision

5. **Submit to SHARP**
   - Background process
   - Verifies on Ethereum L1
   - Creates permanent audit trail

### Using the AI Orchestration

_Coming soon in production - Currently in testing_

1. Click **"AI Risk Engine: Orchestrate Allocation"**
2. AI analyzes current protocol metrics
3. Calculates optimal allocation
4. Generates STARK proof
5. Executes allocation on-chain
6. View result in Rebalance History

---

## Technical Architecture

### Smart Contracts

**Network**: Starknet Sepolia (Testnet)

1. **RiskEngine** - On-chain AI risk calculation
   - Address: `0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`
   - Calculates risk scores using Cairo
   - Validates DAO constraints
   - Records allocation decisions

2. **StrategyRouterV2** - Allocation management
   - Routes funds between protocols
   - Enforces allocation constraints
   - Tracks TVL and performance

### Proof System

- **Generator**: LuminAIR (Rust-based STARK prover)
- **Verification**: SHARP (Shared Prover)
- **Settlement**: Ethereum L1
- **Latency**: 
  - Local proof: 2-3 seconds
  - L1 verification: 10-60 minutes

### Backend

- **API**: Python (FastAPI)
- **Database**: PostgreSQL
- **Endpoints**:
  - `/api/v1/risk-engine/orchestrate-allocation` - Execute rebalance
  - `/api/v1/analytics/rebalance-history` - Get history with proofs
  - `/api/v1/proofs/{job_id}` - Check proof status

### Frontend

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **Wallet**: @starknet-react/core
- **RPC**: Alchemy (Starknet Sepolia)

---

## Security & Verification

### On-Chain Verification

Every rebalance is:
1. **Executed on-chain** - StrategyRouterV2 contract
2. **Recorded permanently** - Decision stored in RiskEngine
3. **Verifiable by anyone** - View on Voyager block explorer

### Cryptographic Proofs

STARK proofs ensure:
- **Correctness** - AI calculation was done properly
- **Integrity** - No tampering with the decision
- **Transparency** - Anyone can verify the proof
- **Auditability** - Permanent record on Ethereum L1

### DAO Constraints

The RiskEngine enforces:
- **Allocation limits** - Max percentage per protocol
- **Risk thresholds** - Min/max risk scores
- **Rebalance frequency** - Time between decisions
- **Emergency controls** - Circuit breakers

---

## Troubleshooting

### Wallet Connection Issues

**Problem**: Wallet won't connect

**Solutions**:
1. Ensure you're on Starknet Sepolia testnet
2. Update your wallet extension to latest version
3. Try refreshing the page
4. Clear browser cache and try again

### Rebalance History Not Loading

**Problem**: History shows "Loading..." indefinitely

**Solutions**:
1. Check your internet connection
2. Refresh the page
3. Clear browser cache
4. Check if backend is online: https://starknet.obsqra.fi/api/health

### Proof Status Not Updating

**Problem**: Proof stuck in "Generated" status

**Note**: This is expected! Proofs remain "Generated" until:
1. Backend submits to SHARP (automatic)
2. SHARP verifies (10-60 minutes)
3. Ethereum L1 settlement completes

**Check Status**: Hover over proof badge to see submission timestamp.

---

## Performance Metrics

### System Performance

- **Proof Generation**: 2-3 seconds (local)
- **Transaction Confirmation**: 10-30 seconds (Starknet)
- **L1 Verification**: 10-60 minutes (SHARP)
- **History Refresh**: 30 seconds (auto-refresh)

### Gas Efficiency

All transactions are executed on Starknet Layer 2:
- **Lower fees** than Ethereum L1
- **Fast finality** (seconds, not minutes)
- **Scalable** - High throughput

---

## Support & Resources

### Documentation
- **GitHub**: https://github.com/Obsqra-Labs/obsqra.starknet
- **README**: Technical overview and setup
- **Architecture**: System design documents

### Community
- **Issues**: https://github.com/Obsqra-Labs/obsqra.starknet/issues
- **Discussions**: GitHub Discussions (coming soon)

### Reporting Bugs

Found a bug? Please report it:

1. Go to: https://github.com/Obsqra-Labs/obsqra.starknet/issues
2. Click "New Issue"
3. Provide:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Browser and wallet version

---

## Roadmap

### V1.3 (Current) - Verifiable AI Foundation
- ✅ On-chain risk calculation
- ✅ STARK proof generation
- ✅ Rebalance history with proofs
- ✅ Real-time status updates
- ⏳ Production testing

### V1.4 (Q1 2026) - Privacy Pool
- Private deposits/withdrawals (MIST)
- Anonymous participation
- Transparent optimization
- Proof-of-reserves

### V1.5 (Q2 2026) - Advanced Features
- Multi-strategy support
- Custom risk profiles
- Automated rebalancing
- Performance analytics

---

## Glossary

**APY** - Annual Percentage Yield, the rate of return

**DAO** - Decentralized Autonomous Organization

**L1** - Layer 1 (Ethereum mainnet)

**L2** - Layer 2 (Starknet)

**SHARP** - Shared Prover (StarkWare's proving system)

**STARK** - Scalable Transparent ARgument of Knowledge (zero-knowledge proof)

**TVL** - Total Value Locked (total funds in strategy)

**zkML** - Zero-Knowledge Machine Learning (provable AI)

---

**Version**: 1.3  
**Last Updated**: December 2025  
**Network**: Starknet Sepolia (Testnet)

