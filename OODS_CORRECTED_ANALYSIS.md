# OODS Error - Corrected Analysis

**Date**: 2026-01-26  
**Status**: Corrected based on user's research findings

---

## What the Error Actually Means ✅

**OODS mismatch = composition polynomial consistency failure**

- We cleared the builtin gate (`Invalid builtin` → `Invalid OODS`)
- Verifier is now doing the **real cryptographic check**
- It recomputes the composition polynomial at the OODS point
- Compares with claimed value in proof
- **Mismatch = strict AIR/proof/public-input consistency failure**

This is **not** a parsing failure - it's a cryptographic consistency issue.

---

## Corrections to Previous Analysis

### ❌ Wrong: Comparing to dex example
- **Correct**: Should compare to Integrity's **recursive** example
- Integrity has canonical recursive example: `recursive/cairo0_stone5_keccak_160_lsb_example_proof.json`
- The README provides exact verification command for recursive + stone5 + keccak_160_lsb + strict

### ❌ Wrong: "Recursive might not be supported"
- **Correct**: Integrity **explicitly supports** recursive layout
- Ships Cairo0 recursive example proof that verifies on-chain
- Recursive is first-class in Integrity's Cairo0 world

### ✅ Correct: Monolith serialization constraint
- **Monolith proof serialization only supports recursive layout**
- If we want small layout, we must use split serialization
- If we want monolith, we must use recursive
- We're using monolith + recursive ✅ (correct)

---

## Root Cause Analysis (Ranked)

### 1. Public Input Structure Mismatch (Most Likely)
Even tiny differences in:
- `memory_segments` structure
- Segment order
- Layout flags
- `public_memory` format

Will make the verifier reconstruct a different composition polynomial.

### 2. AIR Mismatch vs. Canonical Recursive
If our program/builtin set doesn't match the canonical recursive AIR used in the example proof:
- We'll pass builtin checks ✅
- But still fail OODS ❌

### 3. Serializer Mismatch (Possible)
The proof serializer must output exactly the structure Integrity expects. The README's `proof_serializer` example is the canonical pipeline.

---

## Diagnostic Plan (User's Recommendations)

### Step 1: Verify Canonical Recursive Proof End-to-End ✅
**Goal**: If canonical proof fails, deployment/config is off. If it passes, our proof/public-input is the issue.

**Action**:
1. Use Integrity's recursive example: `recursive/cairo0_stone5_keccak_160_lsb_example_proof.json`
2. Serialize it: `cargo run --release --bin proof_serializer < example_proof.json > calldata`
3. Verify via our flow: `verify_proof_full_and_register_fact` on FactRegistry
4. If this fails → deployment/config issue
5. If this passes → our proof/public-input issue

### Step 2: Diff Our Proof/Public Input vs. Recursive Example ✅
**Goal**: Identify which field(s) are off.

**Compare**:
- `layout` (should be `"recursive"`)
- `n_steps`
- `memory_segments` (structure, order, builtin segments)
- `public_memory` (format, addresses, values)
- Builtin segment presence and order
- Proof config fields

### Step 3: If We Want Small Layout
- Switch to **split serialization** (not monolith)
- Or stay with recursive (recommended)

---

## Current Setup Verification

### ✅ What We're Doing Right
1. **Using monolith serialization** → Correct for recursive
2. **Using recursive layout** → Supported by Integrity
3. **Using canonical public input** → From `cairo-run --air_public_input`
4. **Using stone5 + keccak_160_lsb + strict** → Matches canonical example

### ⚠️ What to Check
1. **Public input structure** → Compare with recursive example field-by-field
2. **AIR configuration** → Ensure matches canonical recursive AIR
3. **Proof structure** → Ensure matches Integrity's expected format

---

## Next Actions

1. **Test canonical recursive proof** → Verify our deployment/config
2. **Compare structures** → Field-by-field diff with recursive example
3. **Identify mismatch** → Public input, AIR, or serializer

---

**Status**: Following user's corrected analysis. Ready to test canonical recursive proof and compare structures.
