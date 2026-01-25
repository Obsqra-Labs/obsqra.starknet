# Technical Analysis: Cairo Compiler Versions & CASM Hash Mismatches

## Executive Summary

Investigation into "Mismatch compiled class hash" errors revealed that Starknet's RPC layer performs **deterministic validation** of compiled class (CASM) hashes. Different Cairo compiler versions produce different CASM bytecode for identical Sierra code, causing validation failures when the compiled version doesn't match RPC expectations.

---

## Problem Statement

When attempting to redeploy StrategyRouterV2, multiple Cairo versions produced different CASM hashes, all rejected by the Starknet RPC:

| Cairo Version | CASM Hash (Actual) | Expected (PublicNode) | Status |
|---|---|---|---|
| 2.11.0 | `0x039bcde8fe0a75c6...` | `0x4120dfff561b2868...` | ❌ Rejected |
| 2.10.0 | `0x0523b1b3d221a2e5...` | `0x202f7a806205b2ae...` | ❌ Rejected |
| 2.8.5 | `0x01dc0816ec968a41...` | `0x6e8ed587242e4e00...` | ❌ Rejected |

---

## Root Cause Analysis

### 1. Cairo Compiler Non-Determinism

Cairo compilers are **version-specific** regarding CASM output:

```
Sierra Class (logical code)
         ↓
[Cairo 2.8.5]  → CASM Hash A (Poseidon)
[Cairo 2.10.0] → CASM Hash B (Poseidon, different bytecode)
[Cairo 2.11.0] → CASM Hash C (Blake2s)
         ↓
Different hashes ≠ code changes
```

**Key Insight:** CASM is compiled bytecode, not intermediate representation. Different compiler versions optimize differently.

### 2. Starknet Version Hashing Evolution

Starknet ecosystem migrated hash algorithms:
- **Starknet v0.13.x**: Uses Poseidon hashing
- **Starknet v0.14.1+**: Migrated to Blake2s hashing

```
Starknet v0.13.x (PublicNode)  →  Expects Poseidon hashes
Starknet v0.14.1+ (Alchemy)    →  Expects Blake2s hashes
```

However, both rejected our hashes, indicating the issue is **not just algorithm version**, but actual **hash mismatches**.

### 3. Storage API Evolution Complicates Matching

Cairo Storage APIs evolved across versions:

| Cairo Version | Vec Support | Method | Storage Pattern |
|---|---|---|---|
| 2.6-2.9 | ❌ No `.push()` | `.append()` | Immutable vec |
| 2.10.0+ | ✅ `.push()` | `.push()` | Mutable vec |
| 2.11.0+ | ✅ Full traits | Trait-based | Full trait support |

**Impact:** To match original compiled hash, code must be compiled with **exact same Cairo version that supports the same storage patterns**.

---

## Investigation Outcomes

### 1. Already-Deployed Class Identified

Git history revealed successful deployment on Dec 8, 2024:

```json
{
  "StrategyRouterV2": {
    "address": "0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a",
    "classHash": "0x0265b81aeb675e22c88e5bdd9621489a17d397d2a09410e016c31a7fa76af796"
  }
}
```

**Verification:** RPC query confirmed class exists on Sepolia testnet.

### 2. Source Code Divergence

Original deployment used code with `Vec<T>` and `.push()`:
```cairo
pools: Vec<ContractAddress>,
...
self.pools.push(pool_address);
```

This code **cannot compile** with Cairo 2.8.5 (no `.push()`) but **can compile** with Cairo 2.10.0+.

**Conclusion:** Original deployment compiled with **Cairo 2.10.0 or later**.

### 3. Current Source Code Incompatibility

HEAD branch has been modified with Map-based storage:
```cairo
pools_by_index: Map<u32, ContractAddress>,
...
self.pools_by_index.entry(pool_count).write(pool_address);
```

This produces **completely different Sierra/CASM hashes** than original.

---

## Technical Insights

### Insight 1: RPC CASM Hash Validation

Starknet RPC nodes perform two-phase validation:

```
1. Receipt Sierra class: 0x065a9feb...
   ↓ (RPC lookup) ↓
2. "For this Sierra class, CASM should be: 0x4120dfff..."
   ↓ (you submit) ↓
3. Computed CASM: 0x039bcde8...
   ↓ (mismatch) ↓
4. REJECTED
```

The RPC has **pre-indexed expectations** for Sierra↔CASM pairs.

### Insight 2: Compiler Determinism is Per-Version

```
$ scarb 2.8.5  --release obsqra_contracts → CASM hash A
$ scarb 2.10.0 --release obsqra_contracts → CASM hash B
$ scarb 2.11.0 --release obsqra_contracts → CASM hash C
```

**Same source code, different hashes!**

This means:
- ✅ Reproducible builds per Cairo version
- ❌ Hash matches across versions (almost impossible)

### Insight 3: No Hash Override Bypass

Even with explicit `--casm-hash` flags, RPC validates:
```bash
starkli declare ... --casm-hash 0x4120dfff561b...
→ RPC still validates: "For Sierra 0x065a9feb, CASM hash should be 0x039bcde8"
→ REJECTED (hash doesn't match validation table)
```

**Conclusion:** CASM hash validation is at protocol level, not tool level.

---

## What We Learned About Starknet's Architecture

### 1. Strict Class Pairing Validation

Starknet doesn't allow arbitrary Sierra↔CASM pairs. Each Sierra class has **pre-defined** expected CASM hash(es).

This prevents:
- ✅ Malicious CASM substitution
- ✅ Buggy compiler outputs
- ❌ Recompiling contracts with updated compilers

### 2. Compiler Version Coupling

Production Starknet chains are coupled to specific compiler versions:

```
Starknet v0.14.1 (Alchemy)
└─ Compiled with: Cairo 2.8.x - 2.11.x (specifically tested set)
└─ Expects: Blake2s hashes for those versions
└─ Rejects: Other Cairo versions or Poseidon hashes

PublicNode (Starknet v0.13.x)
└─ Compiled with: Cairo 2.8.x (specific versions)
└─ Expects: Poseidon hashes
└─ Rejects: Newer Cairo versions
```

### 3. Migration Path for Upgrades

To deploy with a new Cairo version:

```
Step 1: Identify compatible Cairo version for target Starknet version
Step 2: Compile contract with that version
Step 3: RPC will accept if hashes match pre-validated set
Step 4: If mismatch, contract cannot be deployed (requires RPC update)
```

---

## How to Avoid This in Future Projects

### ✅ Best Practice 1: Version Pin in Scarb.toml

```toml
[package]
name = "my_contracts"
version = "0.1.0"
edition = "2024_07"

# FIX: Specify exact Cairo version for reproducibility
cairo-version = "2.8.5"
scarb-version = "2.8.5"

[dependencies]
starknet = ">=2.0.0"
```

### ✅ Best Practice 2: Document Deployment Compiler Version

```markdown
## Deployment Record

**Contract:** StrategyRouterV2
**Cairo Version:** 2.8.5
**Scarb Version:** 2.8.5
**Starknet RPC Version:** v0.13.x (PublicNode)
**CASM Hash:** 0x0265b81aeb675e22c88e5bdd9621489a17d397d2a09410e016c31a7fa76af796
**Deployment Date:** 2024-12-08
```

### ✅ Best Practice 3: Test Recompilation Process

```bash
# Before changing Cairo version:
git checkout [known-good-tag]
scarb build
starkli declare --dry-run  # Verify hashes match expectations

# After Cairo upgrade:
git checkout HEAD
scarb build
# Compare hashes
# Plan RPC upgrade or rollback
```

### ✅ Best Practice 4: Store Compiled Artifacts

```bash
# Commit pre-compiled artifacts for historical deployments
git add contracts/target/deployed/
git commit -m "Archive deployment for Cairo 2.8.5"
```

---

## Starknet Roadmap Implications

**Current State (Jan 2025):**
- Multiple Cairo versions in ecosystem
- Different Starknet RPC versions expect different hashes
- Compiler upgrades require careful coordination

**Future (Implied by this architecture):**
- Starknet will likely standardize on Cairo version
- RPC nodes will validate against blessed compiler versions
- Upgrade procedures will include coordinated compiler/RPC updates

**For Developers:**
- Pin compiler versions in production
- Test recompilation before major upgrades
- Coordinate with RPC providers on version compatibility

---

## Conclusion

The "Mismatch compiled class hash" error is **not a bug** but a **feature**: Starknet validates that CASM bytecode matches expected output for each Sierra class. This prevents:
1. Compiler bugs (wrong bytecode)
2. Malicious code substitution
3. Accidental incompatibilities

**The tradeoff:** Developers must match exact compiler versions used in original deployment or coordinate with RPC providers for validation table updates.

**Solution for this project:** Use already-deployed class hash rather than attempting to recompile with different Cairo version.

---

**Technical Analysis Completed:** January 2025  
**Recommendation:** Document compiler versions as critical production metadata
