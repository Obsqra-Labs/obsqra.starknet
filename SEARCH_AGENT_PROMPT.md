# Search Agent Prompt - Find Stone5 Commit

## Context

We're debugging an OODS (Out-of-Distribution Sampling) failure in STARK proof verification using Integrity's FactRegistry on Starknet Sepolia.

### Current Situation
- **Our Stone commit**: `1414a545e4fb38a85391289abe91dd4467d268e1` (Stone v3)
- **Our config**: Using stone5, recursive layout, keccak_160_lsb hasher
- **Problem**: Our proofs fail with "Invalid OODS" even though:
  - FRI parameters match canonical example (n_queries: 10, proof_of_work_bits: 30)
  - Canonical stone5 proof verifies successfully on public FactRegistry
  - All other parameters match canonical example

### What We Know
1. **Public FactRegistry**: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c` (Sepolia)
2. **Canonical example**: `integrity/examples/proofs/recursive/cairo0_stone5_keccak_160_lsb_example_proof.json`
3. **Canonical proof verifies**: Successfully verified on-chain using public FactRegistry
4. **Integrity repo**: https://github.com/HerodotusDev/integrity
5. **Canonical example added**: Commit `5702c4f` (Nov 2024) - "example proofs"
6. **Stone Prover repo**: https://github.com/starkware-libs/stone-prover

### Hypothesis
Our Stone binary commit doesn't match the Stone commit used to build the stone5 verifier registered in the public FactRegistry. Even though both are "stone5", different commits can produce incompatible proofs due to:
- Different channel state calculation
- Different OODS point derivation
- Different AIR constraint evaluation semantics

## Search Task

**Find the exact Stone Prover commit hash used to build the stone5 verifier that's registered in Integrity's public FactRegistry on Starknet Sepolia.**

## Search Strategy

### 1. Integrity Repository
- Search for Stone version/commit documentation in:
  - README.md
  - Deployment scripts (`deployment/verifiers/`)
  - CI/CD workflows (`.github/workflows/`)
  - Example proof generation scripts
  - Any documentation about verifier deployment

- Check commit history around:
  - Commit `5702c4f` (when canonical examples were added)
  - Any commits mentioning "stone5" or "verifier deployment"
  - Deployment-related commits

- Look for:
  - `Cargo.toml` or dependency files mentioning stone-prover
  - Build scripts that specify Stone version
  - Documentation about which Stone version to use

### 2. Stone Prover Repository
- Search for:
  - "stone5" tags or releases
  - Commit history around Nov 2024 (when canonical examples were added)
  - Any documentation about stone5 version
  - Release notes or changelog mentioning stone5

### 3. Integrity GitHub Issues/Discussions
- Search for:
  - Issues about Stone version compatibility
  - Discussions about verifier deployment
  - Questions about which Stone version to use
  - Any mentions of Stone commit hashes

### 4. Integrity Documentation
- Check:
  - Deployment guides
  - Verifier setup instructions
  - Any version requirements documentation
  - Contributing guidelines

### 5. Public FactRegistry Deployment Info
- Look for:
  - Deployment transactions on Starknet
  - Any public documentation about FactRegistry deployment
  - Contract verification info that might include build details

## Key Search Terms

1. "Integrity stone5 verifier commit"
2. "HerodotusDev integrity stone prover version"
3. "Integrity FactRegistry stone5 deployment"
4. "stone-prover stone5 commit hash"
5. "Integrity verifier stone version requirements"
6. "stone5 verifier deployment integrity"
7. "starkware stone-prover stone5 tag"
8. "Integrity stone5 verifier build"

## Expected Output Format

If found, provide:
- **Stone commit hash**: `[full commit hash]`
- **Source**: Where you found it (URL, file, commit, etc.)
- **Confidence**: High/Medium/Low
- **Additional context**: Any related information

If not found, provide:
- **What was searched**: List of sources checked
- **Closest matches**: Any related but not exact matches
- **Alternative approaches**: Suggestions for finding the info

## Success Criteria

The search is successful if we can find:
1. The exact Stone Prover commit hash used for stone5 verifier
2. OR a way to determine it (e.g., build script, dependency version)
3. OR documentation stating which Stone version/commit to use

## Additional Context

- **Integrity repo**: https://github.com/HerodotusDev/integrity
- **Stone Prover repo**: https://github.com/starkware-libs/stone-prover
- **Public FactRegistry**: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c` (Sepolia)
- **Our Stone commit**: `1414a545e4fb38a85391289abe91dd4467d268e1` (Stone v3)
- **Canonical example commit**: `5702c4f` (Nov 19, 2024)

## What We've Already Checked (Local Server)

### ✅ Checked Files
- `integrity/README.md` - References Stone Prover docs but no commit
- `integrity/deployment/verifiers/` - Deployment configs but no Stone version info
- `integrity/.github/workflows/proof_verification_tests.yml` - Tests with stone5 but no commit
- `integrity/examples/proofs/generate.py` - Generates proofs but doesn't specify Stone commit
- `integrity/Cargo.toml` - No stone-prover dependency (verifier is Cairo-based)

### ❌ Not Found Locally
- No Stone commit hash in deployment files
- No Stone version in CI workflows (just "stone5" string)
- No dependency on stone-prover (Integrity is a verifier, not a prover)

### 🔍 Key Insight
Integrity is the **verifier** (Cairo-based), not the prover. The Stone commit we need is the one used to:
1. Generate the canonical example proofs (Nov 2024)
2. Build the stone5 verifier that's registered in FactRegistry

The verifier itself doesn't depend on stone-prover - it verifies proofs generated by stone-prover. We need to find which stone-prover commit was used to generate the proofs that the verifier expects.
