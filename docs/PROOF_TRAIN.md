# Obsqura Proof Train (Why the zkML step matters)

## One‑line
Obsqura makes **AI‑driven DeFi execution verifiable** by turning each decision step into something you can prove or audit.

## The end‑to‑end flow (what users should understand)
1. **Market Snapshot (read‑only)**
   - We anchor the decision to a specific Starknet block (hash/number/timestamp).
   - This prevents “moving the goalposts” after the fact.

2. **Derived Metrics (deterministic inputs)**
   - We transform raw market data into normalized inputs (utilization/volatility/liquidity/etc.).
   - These are the exact inputs used by the model/risk logic.

3. **zkML Attestation (model step)**
   - A proof attests: “given inputs X, the model produced output Y.”
   - This is the **AI accountability layer** — the model can’t lie about the outcome.

4. **Risk/Constraints (on‑chain rules)**
   - DAO/user constraints are enforced in Cairo (max exposure, diversification, etc.).
   - The allocation must satisfy these constraints or it won’t execute.

5. **Allocation → Execution**
   - Strategy Router executes on-chain using the verified decision.
   - Final transaction hashes complete the audit trail.

6. **(Optional) Privacy**
   - MIST.cash allows private deposits/withdrawals while keeping the proof trail public.

## Why the zkML demo is not a standalone toy
- It uses the **same verifier path** (Integrity on Starknet) that live proofs will use.
- The only difference today is that the proof is **precomputed**, not generated from live inputs.
- When we replace the demo proof with a live model proof, the rest of the pipeline stays the same.

## What’s real today vs demo
**Real today**
- On‑chain constraints and allocation enforcement
- Read‑only market snapshot + derived metrics
- Integrity verifier call that accepts/denies proofs

**Demo today**
- zkML proof is precomputed (not tied to the current snapshot yet)

## Road to “full” zkML (no hand‑waving)
1. Use LuminAIR/Stwo to generate a proof for the exact model inference.
2. Feed that proof into the same Integrity verifier endpoint.
3. Connect proof hash to the allocation decision on‑chain.

## Cairo0 vs Cairo1 (short)
- **Cairo0** = legacy Cairo compiler/runtime (older Starknet programs).
- **Cairo1** = modern Rust‑based compiler/runtime with safer language features.
- In Obsqura, this just means **two proof formats** that the verifier can accept.

## The user story (what we want them to feel)
“I can delegate execution to an AI, **and** I can verify the AI actually followed my rules.”

That’s the product.
