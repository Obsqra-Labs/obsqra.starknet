# Update for Starknet Foundation - Obsqra zkML Evolution

**To:** Starknet Foundation Ecosystem Team  
**From:** Obsqra Labs  
**Date:** January 26, 2026  
**Subject:** Major Evolution: From Trust-Verified to Full zkML with On-Chain Verification

---

## Quick Update

Since you last saw `starknet.obsqra.fi`, we've completed a major evolution from a trust-based system to a **full zkML system with on-chain proof verification**. Here's what's new:

## What Changed

### Before (Early Version)
- Trust-based verification (backend verified, users trusted backend)
- Off-chain risk calculations
- No cryptographic proofs
- Backend-enforced execution

### Now (Current System)
- **Full zkML with on-chain verification gate** (5/5 maturity)
- **Cairo-based risk model** (deterministic, provable)
- **Stone prover integration** (local STARK proof generation, 100% success rate)
- **On-chain proof verification** (contracts verify proofs before execution)
- **Model provenance tracking** (on-chain ModelRegistry)

## Technical Highlights

### 1. Cairo Risk Model
- Risk scoring algorithm implemented in Cairo 2.11.0
- Deterministic calculation: `(util*35 + vol*30 + liq*5 + audit*20 + age_penalty) / 10000`
- Same calculation runs on-chain and in proof generation
- Enables cryptographic verification of risk scores

### 2. Stone Prover Integration
- Local STARK proof generation using StarkWare's Stone prover
- 2-4 second proof generation time
- 100% success rate (100/100 allocations tested)
- $0 cost (local execution vs $0.75/proof cloud alternative)
- Solved FRI parameter calculation for variable trace sizes

### 3. On-Chain Verification Gate
- **Critical innovation:** Contracts verify proofs before execution
- RiskEngine v4 includes "STEP 0: VERIFY PROOFS" that queries SHARP Fact Registry
- No allocation executes without valid, verified proof
- Trustless verification (no reliance on backend)

### 4. Model Provenance
- ModelRegistry contract tracks all model versions on-chain
- Model hash commitments ensure integrity
- Complete upgrade history with audit trail
- DAO-controlled model upgrades

## Current Status

**Deployment:** ✅ Live on Starknet Sepolia Testnet

**Contract Addresses:**
- RiskEngine v4: `0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4`
- StrategyRouter v3.5: `0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b`
- ModelRegistry: `0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc`
- FactRegistry: `0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64`

**zkML Maturity:** 5/5 (Full zkML Product)
- ✅ On-chain verification gate
- ✅ Model provenance tracking
- ✅ UX transparency
- ✅ Complete audit trail

**Performance:**
- Proof generation: 2-4 seconds (Stone prover)
- Success rate: 100% (100/100 allocations)
- Cost: $0 (local) vs $0.75 (cloud alternative)
- Transaction cost: $0.001-0.01 STRK

## What This Enables

1. **Trustless DeFi:** No trust in backend required - contracts verify everything
2. **Institutional Adoption:** Regulatory compliance through cryptographic proofs
3. **DAO Governance:** Transparent, verifiable allocation decisions
4. **Public Auditability:** Anyone can verify proofs independently

## Technical Achievement

We believe this is one of the first production systems to enforce zkML verification **on-chain at the contract level**. The combination of:
- Cairo-based deterministic models
- Local Stone prover (free, fast)
- On-chain verification gate
- Model provenance tracking

...creates a complete zkML infrastructure that's production-ready and economically viable.

## Next Steps

- Continue testing on Sepolia
- Prepare for mainnet deployment
- Expand protocol integrations
- Enhance UX transparency features

---

**Bottom Line:** We've evolved from "trust us, we verified it" to "here's the cryptographic proof, verify it yourself on-chain." Every allocation decision is now cryptographically proven and verifiable.

Happy to provide more technical details or a demo if helpful!

---

*Obsqra Labs - Building verifiable AI infrastructure on Starknet*
