## Proving flows (Stone / Integrity / Atlantic) — Dec 2025

### Update — Jan 27, 2026 (Stone v3 → stone6) ✅ RESOLVED

**Resolution**: Stone v3 (commit `1414a545...`) produces **stone6** semantics. OODS passes when verifying Stone v3 proofs as `stone6`.

**Production Path (Obsqra)**:
- **Stone Prover**: v3 (`1414a545...`)
- **Integrity Verifier**: `stone6`
- **Configuration**: `layout=recursive`, `hasher=keccak_160_lsb`, `stone_version=stone6`, `memory_verification=strict`
- **Status**: ✅ **Canonical production path**

**Canonical Example Path (Integrity)**:
- **Stone Prover**: Used by Integrity for examples (may be different version)
- **Integrity Verifier**: `stone5`
- **Configuration**: `layout=recursive`, `hasher=keccak_160_lsb`, `stone_version=stone5`, `memory_verification=strict`
- **Use Case**: Only when replaying Integrity's canonical example proofs
- **Status**: Historical/canonical examples only

**Key Difference**:
- `stone6` includes `n_verifier_friendly_commitment_layers` in public input hash
- `stone5` does NOT include it in public input hash
- Stone v3 generates proofs with stone6 semantics → must verify as `stone6`

**Action**: All Obsqra production proofs must use `stone6`. Stone v2 path dropped (no longer needed).

### Local Stone (small trace) end‑to‑end
- Program: `verification/risk_example.cairo` (layout=small, n_steps=8,192).
- Trace/artifacts via `cairo1-run --proof_mode` (see DEV_LOG entry Dec 15).
- Params: `verification/out/risk_small_params.json` (fri_step_list [3,3,3,2], last_layer_degree_bound 64).
- Prover: `cpu_air_prover --generate_annotations ...` → `verification/out/risk_small_proof_annotated.json`.
- Serializer: `integrity/target/release/proof_serializer` → `verification/out/risk_small_calldata.txt`.

### Integrity call test (sepolia)
- **Historical (Dec 2025)**: used `stone5` to mirror Integrity’s canonical example proofs.
- **Current Obsqra production**: use `stone6` for Stone v3 proofs.
- Calldata prefix per Integrity CLI (canonical example path): `layout=recursive`, `hasher=keccak_160_lsb`, `stone_version=stone5`, `memory_verification=strict` (ASCII→felt).
- Final calldata saved to: `verification/out/risk_small_calldata_prefixed.txt`.
- Call (starknet_py FullNodeClient, Sepolia RPC): `verify_proof_full_and_register_fact` on Integrity verifier `0x4ce7…71b8c`.
- Result: **reverted** with `ENTRYPOINT_FAILED` / `invalid final_pc` (proof not accepted by the verifier).
- Interpretation: the small-trace Stone proof shape is now accepted by proof_serializer, but Integrity rejected it; likely due to mismatch between our risk circuit/config and the verifier expectations (proof not generated with the exact Stone/Integrity AIR/layout).

### Takeaways / next steps
- Pipeline is wired: Stone proof → serializer → calldata → Integrity call.
- To get a passing call, we need a proof generated with the exact Stone/Integrity settings for the target AIR.
  - **Canonical example path**: `recursive/keccak_160_lsb/stone5/strict`.
  - **Obsqra production path (Stone v3)**: `recursive/keccak_160_lsb/stone6/strict`.
  - Regenerate proof with Integrity’s canonical AIR/layout (potentially full trace or updated params).
  - Use Atlantic to produce an Integrity-compatible proof for the risk circuit (and re-run serializer + call).
- LuminAIR/stwo proofs remain for zkML/local UX; Integrity still only accepts Stone-format proofs.
- Added `proof_source` tagging (luminair vs stone/atlantic) and surfaced source + error in analytics endpoints (rebalance history, proof summary). Orchestration now marks verifier failures as `FAILED` with `verification_error` captured.

### Attempted full-trace Stone proof (all_cairo, n_steps=131,072)
- Params satisfying degree equation (log2(last_layer_degree_bound)+Σ(fri_steps)=21) were tried:
  - Variant 1: last_layer_degree_bound=64, fri_step_list=[3,3,3,3,3], n_queries=18, pow=24.
  - Variant 2: last_layer_degree_bound=128, fri_step_list=[3,3,3,3,2], n_queries=16, pow=24.
  - Variant 3: last_layer_degree_bound=256, fri_step_list=[3,3,3,2], n_queries=12, pow=24.
- Prover command (with annotations): `cpu_air_prover --generate_annotations ... --parameter_file=<variant> --prover_config_file=e2e_test/Cairo/cpu_air_prover_config.json`
- Result: both variants aborted with `Signal(6)` (no stdout from within sandbox). Suggests either resource limits or AIR/config mismatch for the large trace.
- Tried again with verbose logging and explicit `GLOG_log_dir=/tmp`, `--v=2`, `--logtostderr=1`; still `Signal(6)`, no new logs beyond the small-trace runs (existing /tmp logs show only earlier small-trace executions).
- Another attempt with `GLOG_v=3`, `GLOG_logtostderr=1`, `--n_threads=2` still ended with `Signal(6)` and no additional logs emitted (no new cpu_air_prover log files).
- Recommendation: either (a) continue tuning with richer prover logs (outside sandbox) or (b) pivot to Atlantic to generate the Integrity proof for the risk circuit.
