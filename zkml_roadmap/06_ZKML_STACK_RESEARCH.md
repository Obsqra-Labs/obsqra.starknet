# zkML Stack Research (Starknet Integration)

**Not reverse engineering.** EZKL and Giza are documented; we need **Starknet-specific** integration research.

---

## What Stone Required (Context)

- Undocumented FRI parameter equation
- OODS verification debugging (stone5 vs stone6)
- Builtin/layout handling
- Took months to reverse engineer

---

## What EZKL/Giza Provide

- Public docs and SDKs
- Known proof formats
- Example integrations

---

## Research Questions (Starknet-Specific)

### 1. EZKL on Starknet

- Can EZKL verifier deploy to Starknet?
- Verifier contract: Solidity → Cairo or existing Cairo verifier?
- Estimate: 2-4 weeks exploration.

### 2. Giza Integration

- How does Giza's Starknet verifier work?
- SDK integration, proof format, cost model.
- Estimate: 1-2 weeks exploration.

### 3. Orion (Cairo ML)

- Can Orion handle our model complexity?
- Model expressivity, gas costs, limitations.
- If viable: "true on-chain ML" without separate verifier.
- Estimate: 1 week exploration.

---

## Integration Points (Once Stack Chosen)

1. Export risk model to ONNX (or Orion format).
2. Generate zkML proof off-chain.
3. Deploy zkML verifier contract (or use Giza's).
4. Modify RiskEngine to accept proven scores (optional path).
5. Backend: ML inference → zkML proof → Stone proof → execute.

---

## Timeline

- **Research phase**: 4-6 weeks (parallel evaluation).
- **Integration phase**: 6-8 weeks after stack chosen.
- **Total**: 2-4 months (not per stack).
