# Stage 4: Trustless AI (Governance Layer)

**Status**: 3-6 months after Stage 3A/3B

---

## What Changes

- **DAO governance** for model approval (propose model version → vote → execute approval).
- **Public artifacts**: Model code, weights, training script on IPFS/Arweave.
- **Reproducibility**: Documentation for training data provenance and reproducible training.

---

## Contract Additions (Conceptual)

- `propose_model_version(model_hash, training_data_hash, artifact_ipfs_cid)` → proposal_id.
- `vote_on_model_proposal(proposal_id, for_or_against)`.
- `execute_model_approval(proposal_id)` — if passed, set `approved_model_versions.write(model_hash, true)`.

---

## Off-Chain

- IPFS/Arweave: Publish model artifacts.
- GitHub: Open source model repos.
- Docs: Training reproducibility guide.

---

## Value Prop

"Fully trustless AI — DAO governance, public artifacts, reproducible training."

**Proof system**: Same as Stage 3A or 3B.
