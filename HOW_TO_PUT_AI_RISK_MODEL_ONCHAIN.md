# How to Put Our AI Risk Model On-Chain

**Current state**: Your **risk score formula is already on-chain** in `risk_engine.cairo` (`calculate_risk_score_internal`). It’s a deterministic formula (weights 25, 40, categorical liquidity, audit, age), not a learned ML model. The Stone proof proves that this **same formula** was executed with given inputs and produced the claimed scores. Your **ML** risk model (`RiskPredictionModel` in `backend/app/ml/models.py`) and the zkML demo linear classifier (`ZkmlService`) run **off-chain** and are not what the contract computes or verifies today.

So “putting the AI risk model on-chain” can mean different things. Below are the main options and how you’d get there.

---

## 1. Current State (Formula On-Chain, ML Off-Chain)

| What | Where | Role |
|------|--------|------|
| **Risk score formula** | `risk_engine.cairo` (`calculate_risk_score_internal`) | On-chain: contract computes it; Stone proves execution with given inputs. |
| **Python mirror** | `backend/app/services/risk_model.py` | Off-chain: same math for display/consistency. |
| **ML model** | `backend/app/ml/models.py` (`RiskPredictionModel`) | Off-chain: sklearn-style models; not used in proof/execution path. |
| **zkML demo** | `backend/app/services/zkml_service.py` | Off-chain: tiny linear classifier for demo; not the contract formula. |

So today: **the “model” that is on-chain is the fixed formula**. To put **your AI/ML risk model** on-chain you have to choose one of the approaches below.

---

## 2. Option A: Parameterize the Formula On-Chain (Upgradeable “Model”)

**Idea**: Keep a **single formula** on-chain but make its **parameters** (weights, thresholds) read from storage, keyed e.g. by `model_version`. Upgrading the “model” = updating parameters (via governance), not redeploying the contract.

**What goes on-chain**:
- Weights: e.g. `w_util`, `w_vol`, `w_liq_0..3`, `w_audit`, `w_age`, and constants like 730, 5, 95.
- Contract: `calculate_risk_score_internal(metrics, model_version)` reads params for `model_version` and computes `util*w_util/10000 + vol*w_vol/10000 + ...`, then clamps to [5, 95].
- Model registry / storage: e.g. `model_params: Map<felt252, ModelParams>` where owner (or governance) sets params for each `model_version`. Your v4 `approved_model_versions` can still gate which `model_version` is allowed for execution.

**Pros**: Simple, no new proof system; same Stone flow (prove execution of Cairo that now uses params); upgrade = parameter update.  
**Cons**: Still a **linear/categorical formula**, not a general ML model (no neural net, no tree).

**Steps**:
1. Define a `ModelParams` struct in Cairo (e.g. weights + clamp bounds).
2. Add storage `model_params: Map<felt252, ModelParams>` and optionally `current_model_version: felt252`.
3. Replace literals (25, 40, 5, 15, 30, 3, 10, 730, 5, 95) in `calculate_risk_score_internal` with reads from `model_params.get(model_version)` (or current version).
4. Add admin: `set_model_params(model_version, params)` (owner-only).
5. In `propose_and_execute_allocation`, pass `model_version` (you already do); contract uses `model_params.read(model_version)` for the risk formula.
6. Backend: no change to proof flow; ensure trace uses the same params you set on-chain.

---

## 3. Option B: zkML – Prove ML Inference Off-Chain, Verify On-Chain

**Idea**: Run your **real AI risk model** (e.g. neural net, gradient boosting) **off-chain**. Produce a **ZK proof** that “model(input_metrics) = risk_score”. The **contract** only verifies that proof and uses the **proven score**; it does not run the model.

**What goes on-chain**:
- A **verifier** for the proof system you use (e.g. EZKL, Giza, or a LuminAIR/Atlantic-style verifier).
- Contract logic: “If risk_score is provided via zkML proof, verify the proof and use proven score; else fall back to on-chain formula (Option A or current).”

**Pros**: You can use **arbitrary** ML (bigger nets, trees, etc.); only the proof is verified on-chain.  
**Cons**: Different proof stack (e.g. EZKL for NN); integration work; proof size/cost.

**Steps**:
1. **Export your model** in a format the zkML stack supports (e.g. ONNX for EZKL).
2. **Generate proofs** off-chain: input = metrics, output = risk score (and optionally allocation); proof = “inference(metrics) = score”.
3. **Deploy a verifier** on Starknet that matches that proof system (e.g. verifier contract from EZKL/Giza).
4. **Change RiskEngine** (or a wrapper): accept an optional “risk_score_proof” + “risk_score”; if present, call the verifier contract; if valid, use proven score instead of computing the formula. You can keep the current formula as fallback when no proof is supplied.
5. **Backend**: Add a pipeline that runs your ML model, generates the zkML proof, and passes proof + score into the existing orchestration path so the contract receives them.

---

## 4. Option C: Tiny Model Implemented in Cairo

**Idea**: Implement a **very small** ML model (e.g. small neural net or decision tree) **directly in Cairo**. The contract runs it; no separate proof of inference.

**What goes on-chain**:
- Cairo code that implements e.g. a few layers of a small NN (fixed weights) or a small tree (comparisons and branches). Input = metrics; output = risk score.

**Pros**: Single chain, no extra verifier; “model is on-chain” in the literal sense.  
**Cons**: Cairo is expensive; only tiny models are feasible; weights are fixed unless you add parameter storage (then similar to Option A).

**Steps**:
1. Train a **tiny** model (e.g. 1–2 hidden layers, few neurons, or a small tree) that approximates your risk.
2. Export weights / structure and **hand-code** the forward pass in Cairo (fixed-point math, no floats).
3. Replace (or branch from) `calculate_risk_score_internal` to call this Cairo “inference” and return the score.
4. Stone proof still proves execution of this new Cairo path.

---

## 5. Option D: Hybrid – Formula + Optional zkML Override

**Idea**: Keep the **current formula** as the default (or Option A parameterized formula). Add an **optional** path: “risk score from zkML proof”. If the caller supplies a valid zkML proof of your ML model’s output, the contract uses that score; otherwise it uses the on-chain formula.

**What goes on-chain**:
- Same as Option B: a verifier for your zkML proof.
- Contract: in `propose_and_execute_allocation`, accept optional `(risk_score_proof, jediswap_proven_score, ekubo_proven_score)`. If present and verifier accepts, use those scores for STEP 1/2 instead of computing from metrics. If absent, keep current behavior (compute from metrics).

**Pros**: Backward compatible; you can migrate gradually to ML; fallback stays simple.  
**Cons**: Two code paths and two proof systems (Stone for trace, zkML for inference).

---

## 6. Recommendation (Short Term vs Long Term)

- **Short term**: **Option A** (parameterize the formula on-chain) gives you an “upgradeable model” without a new proof stack. You can tune weights and thresholds via governance and keep the same Stone flow. That’s the fastest way to “put the model on-chain” in the sense of “model parameters and formula live on-chain.”
- **Long term**: If you want the **actual AI** (e.g. neural net or tree) to drive the score, **Option B or D** (zkML proof of inference, verify on-chain) is the standard approach: model stays off-chain, only the proof is verified on-chain.
- **Option C** is only if you explicitly want a tiny model to **run** on-chain and accept the limits on size and complexity.

---

## 7. Summary

| Option | What’s “on-chain” | Complexity | Best for |
|--------|--------------------|------------|----------|
| **A. Parameterized formula** | Weights/thresholds + same formula | Low | Upgradeable formula, same Stone flow. |
| **B. zkML proof of ML** | Verifier + proven score | High | Real ML (NN, tree) with ZK proof. |
| **C. Tiny model in Cairo** | Full forward pass in Cairo | Medium | Literal “model runs on-chain”, tiny only. |
| **D. Hybrid** | Formula + optional zkML verifier | High | Gradual move to ML with fallback. |

Your **AI risk model** today is off-chain (Python ML + zkML demo). To put it on-chain you either: **(A)** make the current formula parameterized and upgradeable, **(B/D)** prove ML inference off-chain and verify on-chain, or **(C)** implement a tiny model in Cairo. Option A is the smallest step; B/D is the path to “real AI” driving the score with cryptographic assurance.
