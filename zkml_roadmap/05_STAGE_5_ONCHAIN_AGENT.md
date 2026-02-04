# Stage 5: On-Chain Agent (Hybrid Infrastructure)

**Status**: 2-3 months (accelerated — foundations exist)

---

## What We Already Have

- **STEP 0.6**: `constraint_signature` — user-signed constraints (intent-like).
- **Events**: AllocationExecuted with proof facts, model hash, constraint_signer (receipts).
- **Model version tracking**: Approved model versions and provenance.

---

## What's Missing (Expansion, Not Greenfield)

1. **Intent registry** — Store user intents on-chain (not just constraints in the call).
2. **Agent reputation** — Track execution success rates per agent/caller.
3. **Policy marketplace** — Pre-built policy templates users can select.
4. **Multi-agent coordination** — Agents calling other agents.

---

## Contract Additions (Conceptual)

- `AgentOrchestrator` or extend RiskEngine:
  - `submit_intent(goal, constraints)` → intent_id.
  - `execute_intent_with_proof(intent_id, execution_proof)` — verify proof matches intent, check reputation, execute.
- Reputation storage: `agent_id → (executions, successful, total_value, avg_performance)`.

---

## Value Prop

"Verifiable agent infrastructure — on-chain intents, programmable policies, reputation."

**Timeline**: 2-3 months (accelerated from 6-12 because STEP 0.6 + events already provide foundations).
