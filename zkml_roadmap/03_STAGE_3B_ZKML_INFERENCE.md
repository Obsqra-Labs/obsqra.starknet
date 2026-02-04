# Stage 3B: zkML Inference (Option B — Real ML)

**Status**: Future (2-4 months after research)

---

## What Changes

- Real ML model (NN/tree) runs **off-chain**.
- zkML proof proves "model(input_metrics) = risk_score".
- Contract verifies zkML proof and uses **proven score** instead of computing formula (or as override).

---

## Critical Note: Not Reverse Engineering

EZKL and Giza have:

- Public documentation
- SDKs and examples
- Community support

We need **Starknet-specific integration research** (see `06_ZKML_STACK_RESEARCH.md`), not reverse engineering like Stone (FRI params, OODS, etc.).

---

## Contract Additions (Conceptual)

- zkML verifier contract (or interface to Giza/EZKL verifier).
- RiskEngine: optional path `(zkml_proof, proven_score)`; if present and verifier accepts, use `proven_score`; else fallback to on-chain formula (Stage 2/3A).

---

## Backend Pipeline

1. Run ML model on metrics → risk scores.
2. Generate zkML proof (EZKL/Giza).
3. Submit proof + scores to contract (or Stone proof of execution that includes zkML verification).
4. Dual proofs: zkML (inference) + Stone (execution trace) as needed.

---

## Value Prop

"True AI with cryptographic guarantees — neural nets + ZK proofs."

**Proof system**: New stack (EZKL/Giza) + Stone for execution.
