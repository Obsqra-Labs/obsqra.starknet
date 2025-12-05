# Starknet DeFi Protocols Integration Guide

**Date:** December 5, 2025  
**Network:** Starknet (Sepolia Testnet / Mainnet)

This document provides information about the Starknet-native DeFi protocols integrated into Obsqra.starknet.

---

## 🌐 Integrated Protocols

### 1. Nostra Finance (Lending)

**Type:** Money Market / Lending Protocol  
**Website:** https://nostra.finance  
**Docs:** https://docs.nostra.finance

**Description:**  
Nostra is Starknet's leading lending protocol, offering both lending and borrowing of assets. It features competitive APYs and deep liquidity.

**Key Features:**
- Supply & borrow STRK, ETH, USDC, USDT
- Isolated lending pools
- Liquidation protection
- High capital efficiency

**Contract Addresses:**
- **Mainnet:** TBD
- **Sepolia:** TBD (research needed)

**APY Range:** 3-8% for STRK/stablecoins

---

### 2. zkLend (Lending)

**Type:** Money Market / Lending Protocol  
**Website:** https://zklend.com  
**Docs:** https://docs.zklend.com

**Description:**  
zkLend is a ZK-native money market built specifically for Starknet. It offers efficient and secure lending/borrowing with a focus on security and UX.

**Key Features:**
- Zero-knowledge optimized
- Battle-tested security
- Competitive yields
- Multiple asset support

**Contract Addresses:**
- **Mainnet:** TBD
- **Sepolia:** TBD (research needed)

**APY Range:** 4-10% for STRK/stablecoins

---

### 3. Ekubo Protocol (DEX)

**Type:** Decentralized Exchange (Concentrated Liquidity)  
**Website:** https://ekubo.org  
**Docs:** https://docs.ekubo.org

**Description:**  
Ekubo is a concentrated liquidity DEX on Starknet (similar to Uniswap V3). Provides liquidity provision with capital efficiency and flexible fee tiers.

**Key Features:**
- Concentrated liquidity (Uniswap V3 model)
- Multiple fee tiers (0.05%, 0.3%, 1%)
- High capital efficiency
- Range orders support

**Contract Addresses:**
- **Mainnet:** TBD
- **Sepolia:** TBD (research needed)

**APY Range:** 5-15% for STRK/stablecoin pairs (varies with volume)

---

## 💰 STRK Token

**Name:** Starknet Token  
**Symbol:** STRK  
**Decimals:** 18  
**Type:** Native gas & governance token for Starknet

**Use Cases:**
- **Gas Fees:** All transactions on Starknet use STRK for fees
- **Staking:** Stake STRK for network security (coming soon)
- **Governance:** Vote on Starknet improvement proposals
- **DeFi:** Collateral, lending, liquidity provision

**Token Info:**
- **Mainnet:** `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d`
- **Sepolia:** Native token (no specific address needed)

**Why STRK over ETH?**
- Native to Starknet (not bridged)
- Lower gas fees (~$0.001 vs $5-50 on Ethereum)
- Faster finality (~30sec vs ~12min)
- Automatic SHARP proving

---

## 📊 Protocol Comparison

| Protocol | Type | TVL | APY Range | Risk Level | Audit Status |
|----------|------|-----|-----------|------------|--------------|
| **Nostra** | Lending | High | 3-8% | Low | ✅ Audited |
| **zkLend** | Lending | Medium | 4-10% | Low | ✅ Audited |
| **Ekubo** | DEX | Medium | 5-15% | Medium | ✅ Audited |

---

## 🔗 Integration Details

### Smart Contract Integration

Our `StrategyRouter` contract routes capital to these protocols:

```cairo
#[storage]
struct Storage {
    nostra_allocation: felt252,   // % to Nostra
    zklend_allocation: felt252,   // % to zkLend
    ekubo_allocation: felt252,    // % to Ekubo
    nostra_address: ContractAddress,
    zklend_address: ContractAddress,
    ekubo_address: ContractAddress,
    ...
}
```

### Allocation Strategy

The `RiskEngine` calculates optimal allocations based on:
- APY (higher is better)
- Risk score (lower is better)
- Liquidity (higher is better)
- Audit status
- Protocol age/maturity

**Formula:**
```
risk_adjusted_score = (APY * 10000) / (Risk + 1)
allocation = score / total_score * 100%
```

---

## 🛠️ Getting Protocol Addresses

### Mainnet Addresses

Research actual protocol addresses before mainnet deployment:

```bash
# Visit protocol documentation
- Nostra: https://docs.nostra.finance/developers/contracts
- zkLend: https://docs.zklend.com/developers/contracts  
- Ekubo: https://docs.ekubo.org/developers/contracts
```

### Sepolia Testnet Addresses

For testing on Sepolia, get testnet deployments:

```bash
# Check protocol Discord/docs for testnet addresses
# Or deploy test versions if not available
```

---

## 📈 Expected Performance

### Baseline APYs (Estimated)

| Asset | Nostra | zkLend | Ekubo | Blended |
|-------|--------|--------|-------|---------|
| STRK | 5% | 6% | 8% | ~6.3% |
| ETH | 3% | 4% | 10% | ~5.7% |
| USDC | 7% | 8% 12% | ~9% |

*Note: APYs vary based on market conditions*

### Risk-Adjusted Returns

Obsqra optimizes for **risk-adjusted** returns, not just highest APY:

- High APY + High Risk = Lower allocation
- Medium APY + Low Risk = Higher allocation
- Respects DAO constraints (max single protocol, min diversification)

---

## 🧪 Testing Integration

### Local Testing

Use placeholder addresses for local development:

```bash
NOSTRA_ADDR="0x0456"
ZKLEND_ADDR="0x0789"
EKUBO_ADDR="0x0abc"
```

### Sepolia Testing

1. Research real Sepolia addresses
2. Deploy to Sepolia with real addresses
3. Test deposits/withdrawals
4. Verify yield tracking

### Mainnet Deployment

1. Get audited mainnet addresses
2. Start with small allocations
3. Monitor for 1-2 weeks
4. Gradually increase allocation

---

## 🔒 Security Considerations

### Protocol Risks

1. **Smart Contract Risk:** All protocols audited, but bugs possible
2. **Oracle Risk:** Price feed dependencies
3. **Liquidity Risk:** Withdrawal restrictions during stress
4. **Governance Risk:** Protocol changes via governance

### Our Mitigations

- **Diversification:** Never >60% in single protocol
- **Constraints:** DAO-enforced allocation limits
- **Monitoring:** Off-chain service monitors health
- **Circuit Breakers:** Emergency pause functionality

---

## 🔮 Future Protocols (Phase 2)

### Additional Integration Targets

| Protocol | Type | Why Add It |
|----------|------|------------|
| **Nimbora** | Yield Strategies | Automated yield farming |
| **Haiko** | Options | Derivatives exposure |
| **Carmine** | Options AMM | Options market making |
| **JediSwap** | DEX | Alternative DEX option |

---

## 📚 Resources

### Protocol Documentation

- **Nostra Finance:** https://docs.nostra.finance
- **zkLend:** https://docs.zklend.com
- **Ekubo Protocol:** https://docs.ekubo.org

### Starknet Resources

- **Starknet Docs:** https://docs.starknet.io
- **DeFi Spring:** https://www.starknet.io/defi-spring
- **Ecosystem:** https://www.starknet-ecosystem.com

### Developer Tools

- **Starknet.js:** https://www.starknetjs.com
- **Cairo Book:** https://book.cairo-lang.org
- **Starknet Foundry:** https://foundry-rs.github.io/starknet-foundry

---

## ✅ Integration Checklist

### Before Deployment

- [ ] Research protocol addresses (Sepolia)
- [ ] Verify protocol audit reports
- [ ] Check protocol TVL & health
- [ ] Test integration on Sepolia
- [ ] Monitor protocol governance

### After Deployment

- [ ] Start with conservative allocations
- [ ] Monitor yield generation
- [ ] Track gas costs in STRK
- [ ] Adjust allocations based on performance
- [ ] Document actual APYs achieved

---

## 🎯 Summary

Obsqra.starknet integrates with **Starknet-native DeFi protocols**:

✅ **Nostra** - Leading lending protocol  
✅ **zkLend** - ZK-native money market  
✅ **Ekubo** - Concentrated liquidity DEX  
✅ **STRK** - Native token for all operations

**Next Step:** Research actual protocol contract addresses for Sepolia testnet deployment.

