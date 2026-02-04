# On-Chain AI Options: Viability, Feasibility, Sustainability & What We Can Do With Being First

**Question**: Are these options viable, feasible, sustainable? Being first is cool – but what can we actually *do* with it?

---

## 1. Option-by-Option Assessment

### Option A: Parameterize the Formula On-Chain (Upgradeable “Model”)

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| **Viable** | ✅ Yes | Same Stone flow; contract change is bounded and well-understood. |
| **Feasible** | ✅ Yes | 1–2 weeks: add `ModelParams` struct, storage map, read params in `calculate_risk_score_internal`, owner `set_model_params`. Backend trace already uses same formula; ensure params match on-chain. |
| **Sustainable** | ✅ Yes | No new proof stack; no per-call cost increase. Upgrades = governance tx. Maintenance = occasional param updates. |
| **Risk** | Low | Main risk: param governance (who can set, timelock, rollback). |

**What we can do with it**:
- Upgrade risk weights without redeploying (DAO or owner).
- Transparent parameter history on-chain.
- “Upgradeable on-chain model” narrative without operational complexity.
- Other protocols can fork the pattern (open, replicable).

**Bottom line**: **Do this first.** It’s the only option that is clearly viable, feasible, and sustainable with your current stack, and it gives you a real “on-chain model” story.

---

### Option B: zkML – Prove ML Inference Off-Chain, Verify On-Chain

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| **Viable** | ✅ Yes | EZKL, Giza, LuminAIR etc. exist; verifiers can be deployed on Starknet. |
| **Feasible** | ⚠️ Medium | New stack: export model (ONNX), integrate prover, deploy verifier, change RiskEngine to accept “proven score” path. 2–4 months + ongoing prover/verifier maintenance. |
| **Sustainable** | ⚠️ Depends | Proof cost and latency per allocation; prover infra (self-host vs vendor); verifier upgrades when proof format changes. |
| **Risk** | Medium | Vendor/format lock-in; proof cost at scale; ops burden. |

**What we can do with it**:
- Use real ML (NN, trees) to drive scores; “true AI” narrative.
- Differentiate from “formula only” protocols.
- But: only sustainable if proof cost is acceptable and we have capacity to maintain the pipeline.

**Bottom line**: **Viable long-term, not a first step.** Pursue after Option A is live and only if (a) we need richer ML for product reasons, and (b) we can afford proof cost and ops.

---

### Option C: Tiny Model Implemented in Cairo

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| **Viable** | ✅ Yes | For a very small NN or tree (e.g. 1–2 layers, few neurons). |
| **Feasible** | ⚠️ Medium | Hand-code forward pass in Cairo (fixed-point); gas cost non-trivial; model expressivity limited. |
| **Sustainable** | ✅ Yes | No external prover; single chain. But “AI” value is limited by model size. |
| **Risk** | Low–Medium | Gas cost per call; model may be too simple to matter for narrative. |

**What we can do with it**:
- Literal “model runs on-chain” – good for demos and “first” story.
- Not enough for “real AI” narrative; more of a technical showcase.

**Bottom line**: **Feasible as a demo or research artifact.** Only invest if we want a clear “model in Cairo” reference implementation; not core to sustainability.

---

### Option D: Hybrid (Formula + Optional zkML Override)

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| **Viable** | ✅ Yes | Same as B for the zkML path; formula fallback is Option A. |
| **Feasible** | ⚠️ Medium | Option A + Option B; two code paths and two proof systems. |
| **Sustainable** | ⚠️ Depends | Same sustainability issues as B for the zkML path; formula path is sustainable. |
| **Risk** | Medium | Complexity of maintaining two paths; clear UX (when each path is used). |

**What we can do with it**:
- Gradual migration to ML without breaking existing users.
- “Best of both”: upgradeable formula + optional “proven ML” path.

**Bottom line**: **Reasonable once we have both A and B.** Not a starting point.

---

## 2. Summary: What’s Actually Viable, Feasible, Sustainable

| Option | Viable | Feasible | Sustainable | Recommendation |
|--------|--------|----------|-------------|----------------|
| **A. Parameterize formula** | ✅ | ✅ (1–2 weeks) | ✅ | **Do first.** |
| **B. zkML proof of ML** | ✅ | ⚠️ (2–4 months) | ⚠️ (cost, ops) | Do later if product needs it. |
| **C. Tiny model in Cairo** | ✅ | ⚠️ (weeks) | ✅ | Optional demo/research. |
| **D. Hybrid** | ✅ | ⚠️ (A + B) | ⚠️ (same as B) | After A and B. |

**Only Option A is clearly viable, feasible, and sustainable with current resources.** B and D depend on proof economics and ops capacity; C is sustainable but limited in impact.

---

## 3. Being First – What Can We Actually Do With It?

“First on-chain AI” is valuable only if we turn it into **product, distribution, and sustainability**. Below is a concrete map.

### 3.1 Product: What Users Get

| Outcome | How |
|---------|-----|
| **Transparent model** | Anyone can read the contract and see how risk is computed (today: formula; with A: formula + params). |
| **Upgradeable model** | With A: DAO/owner can change weights without redeploying; users see “model v2” etc. |
| **Auditable history** | All param changes and (with events) model version per decision are on-chain. |
| **No black box** | “The model is the contract” is a real product claim: no hidden backend model. |

**What we can do**: Ship Option A, then position the app as “DeFi with an on-chain, upgradeable risk model.” Use it in UX (e.g. “Model version”, “Parameters”, “Upgrade history”).

### 3.2 Business: How It Supports Revenue

From your revenue model (consulting, enterprise service, grants):

| Lever | How “first on-chain AI” helps |
|-------|-------------------------------|
| **Consulting** | “We built the first on-chain AI risk model; we can help you do the same.” Integration support, workshops, architecture. |
| **Enterprise** | “Our stack includes an on-chain, upgradeable model – transparent and auditable.” Differentiator for regulated or institutional clients. |
| **Grants** | “We’re first with on-chain AI for DeFi; we’re extending the ecosystem.” Stronger grant narrative (Starknet Foundation, etc.). |

**What we can do**: Use “first on-chain AI” in proposals, sales, and grant applications; tie it to consulting and enterprise offerings. Without that, “first” doesn’t pay the bills.

### 3.3 Ecosystem: Attract and Retain

| Outcome | How |
|---------|-----|
| **Reference implementation** | Open-source “on-chain parameterized model” others can fork. Docs, tutorials, minimal example repo. |
| **Talks and content** | “How we put the risk model on-chain” – conferences, podcasts, blog. |
| **Partnerships** | Protocols/DAOs that want “verifiable, upgradeable AI” – we have the only live example. |
| **Hiring and community** | “We ship on-chain AI” attracts contributors and talent. |

**What we can do**: Document the design (and, with A, the param layout and upgrade flow); publish one “reference” repo or post; use it in every ecosystem conversation.

### 3.4 Sustainability: What Makes “First” Last

| Requirement | Reality |
|-------------|---------|
| **Revenue or funding** | “First” doesn’t fund itself. Need consulting, enterprise, or grants (as in your revenue model). |
| **Maintenance** | Option A is low maintenance (param updates, governance). B/C/D add prover or Cairo maintenance. |
| **Clarity of value** | Users/partners must understand *why* on-chain model matters (transparency, upgradeability, audit). |
| **Execution** | Ship Option A, then iterate (governance, UX, docs). “First” erodes if we don’t ship or don’t explain. |

**What we can do**: Treat “first” as a **launchpad**, not the product. Tie it to one repeatable revenue stream (e.g. consulting or enterprise) and one ecosystem outcome (e.g. one partnership or one grant).

---

## 4. Honest Constraints and Risks

### 4.1 What “First” Does Not Guarantee

- **Adoption** – First mover can also mean “first to educate the market.” We have to explain why on-chain AI matters.
- **Revenue** – Narrative alone doesn’t pay; we need to convert it into consulting, enterprise, or grants.
- **Moat** – Others can copy Option A (parameterized formula). Moat comes from execution, ecosystem, and brand, not from the idea alone.
- **Sustainability** – Only Option A is low-friction sustainable today. B/D need proof economics and ops.

### 4.2 What We Must Do to Make It Sustainable

1. **Ship Option A** – Parameterize the formula on-chain; make “upgradeable on-chain model” real.
2. **Tie “first” to one revenue stream** – e.g. “On-chain AI consulting” or “Enterprise verifiable AI” using this stack.
3. **Tie “first” to one ecosystem outcome** – e.g. one grant, one partnership, or one adopted fork.
4. **Document and speak** – So others can replicate and we become the obvious reference.
5. **Defer B (and D) until** – We have product need for richer ML and capacity to run proof pipeline sustainably.

### 4.3 Risk: Overreaching

- Pursuing B or C before A: we burn time and complexity before proving the sustainable path.
- Pursuing “first” without a clear revenue or ecosystem hook: we get narrative without sustainability.
- Building “on-chain AI” without user-facing value (transparency, upgrades, audit): we get tech without impact.

---

## 5. Recommended Path

### Phase 1: Viable, Feasible, Sustainable (Now)

1. **Implement Option A** (parameterize formula on-chain).
2. **Ship** “upgradeable on-chain risk model” in product and docs.
3. **Use “first on-chain AI”** in one grant application and one partnership or enterprise conversation.
4. **Publish** one reference piece (e.g. “How we put the risk model on-chain”) and link it to repo/docs.

**Outcome**: “First” is real, shippable, and low-maintenance; we have something to sell and to show.

### Phase 2: If Product Demands It (Later)

1. **Evaluate** whether real ML (NN/trees) would materially improve risk or allocation.
2. **If yes**: prototype Option B (zkML proof of ML); validate proof cost and latency; then consider Hybrid (D).
3. **If no**: stay with Option A; invest in governance, UX, and ecosystem instead.

### Phase 3: Optional Showcase

1. **Option C** (tiny Cairo model) only if we want a “model in Cairo” reference for talks or research.
2. Do not rely on C for core sustainability.

---

## 6. Bottom Line

| Question | Answer |
|----------|--------|
| **Are the options viable?** | A: yes. B, C, D: yes in principle, with B/D more conditional. |
| **Are they feasible?** | A: yes (1–2 weeks). B: 2–4 months. C: weeks. D: after A+B. |
| **Are they sustainable?** | A: yes (low ops, no new proof stack). B/D: only with acceptable proof cost and ops. C: yes but limited value. |
| **What can we do with being first?** | Product: transparent, upgradeable model. Business: consulting, enterprise, grants. Ecosystem: reference impl, talks, partnerships. Sustainability: only if we ship A and tie “first” to revenue or funding. |
| **What should we do?** | **Ship Option A.** Use “first on-chain AI” to drive one revenue stream and one ecosystem outcome. Treat B/C/D as later or optional. |

Being first is useful **only if we convert it into something that lasts**: a shipped feature (Option A), a revenue hook (consulting/enterprise/grants), and an ecosystem asset (reference, content, partnerships). Option A is the only option that is clearly viable, feasible, and sustainable today; the rest are conditional or optional.
