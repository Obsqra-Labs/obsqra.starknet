# Technical Glossary
## Complete Terminology Reference for Stone Prover and Verifiable AI

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Living Document  
**Category**: Developer Resources

---

## A

### AIR (Algebraic Intermediate Representation)
A mathematical representation of computation as polynomial constraints. STARK proofs prove that AIR constraints are satisfied.

### Atlantic
Herodotus' managed cloud-based proof generation service. Provides API access to SHARP for proof generation. Charges $0.75/proof on mainnet.

---

## B

### Builtin
Cairo's built-in functions (e.g., Pedersen hash, range check, ECDSA). Different layouts support different builtins.

---

## C

### Cairo
StarkWare's programming language for writing STARK-provable programs. Used to write verifiable computation.

### Calldata
Data passed to a smart contract function. For Integrity, calldata includes verifier config + serialized proof.

### Commitment
Cryptographic commitment to a value (e.g., Merkle root commits to all leaves). Used in STARK proofs for efficiency.

---

## D

### Dynamic FRI
FRI parameter calculation that adapts to trace size. Enables variable trace sizes without "Signal 6" crashes.

---

## E

### Execution Trace
Record of Cairo program execution, showing state at each step. Used as input to Stone Prover.

---

## F

### Fact Hash
Hash commitment to a verified computation. Registered in FactRegistry after proof verification.

### FactRegistry
Integrity smart contract that stores verified computation facts. Enables on-chain proof verification.

### FRI (Fast Reed-Solomon Interactive)
Cryptographic protocol used in STARK proofs to prove polynomial has low degree. Requires specific parameter relationship.

### FRI Equation
Critical constraint: `log2(last_layer_degree_bound) + Σ(fri_steps) = log2(n_steps) + 4`. Must be satisfied for proof generation.

### FRI Step List
List of step values for FRI protocol. Must be calculated dynamically based on trace size.

---

## G

### Giza
zkML platform focused on ML model inference. Uses LuminAIR framework with S-two prover.

---

## H

### Herodotus
Company behind Integrity FactRegistry and Atlantic proof service.

---

## I

### Integrity
Herodotus' FactRegistry system for on-chain STARK proof verification on Starknet.

---

## L

### Layout
Cairo execution layout (e.g., "recursive", "dynamic", "small"). Determines which builtins are available.

### LuminAIR
Giza's zkML framework using S-two prover for ML inference proofs.

---

## M

### Merkle Tree
Tree structure for efficient commitment. Used in STARK proofs to commit to large data.

---

## N

### n_steps
Number of execution steps in Cairo program. Must be power of 2, >= 512. Determines trace size.

### n_queries
FRI security parameter. Number of queries in FRI protocol. Higher = more secure, slower verification.

---

## O

### OODS (Out-of-Distribution Sampling)
Cryptographic consistency check in STARK verification. Validates composition polynomial reconstruction.

### Obsqra Labs
Company building verifiable AI infrastructure for Starknet. First production Stone Prover orchestration.

---

## P

### proof_of_work_bits
FRI proof-of-work difficulty. Higher = more PoW work, slower generation, more security.

### proof_serializer
Integrity binary tool that serializes Stone proof JSON to calldata format for on-chain verification.

### Public Input
Inputs to Cairo program that are part of the proof. Includes n_steps, layout, memory segments.

---

## S

### SHARP (SHARed Prover)
StarkWare's shared proof aggregator. Generates unified proofs for multiple Cairo programs. Not directly accessible.

### Signal 6 (SIGABRT)
Crash error from Stone Prover when FRI parameters don't match trace size. Solved by dynamic FRI calculation.

### Stone Prover
StarkWare's open-source STARK prover. CPU AIR prover for generating STARK proofs locally.

### stone5 / stone6
Integrity verifier settings. stone6 includes `n_verifier_friendly_commitment_layers` in public input hash, stone5 does not.

### STARK (Scalable Transparent ARgument of Knowledge)
Zero-knowledge proof system. Enables efficient verification of computation correctness.

---

## T

### Trace
Execution trace from Cairo program. Binary format containing program state at each step.

---

## V

### Verifier
Smart contract that verifies STARK proofs. Registered in FactRegistry with specific configuration.

### Verifiable AI
AI systems that generate cryptographic proofs of computation correctness. Enables trustless AI.

---

## Z

### zkML (Zero-Knowledge Machine Learning)
Machine learning with zero-knowledge proofs. Enables verifiable ML inference.

---

**This glossary is a living document. Submit additions via GitHub Issues.**
