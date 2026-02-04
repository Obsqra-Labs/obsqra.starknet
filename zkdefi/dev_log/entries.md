# Dev Log Entries

Chronological log of progress and unblocks. Scope: Jan 30, 2026 onward.

---

## 2026-01-30 -- Project scaffolding

Set up zkde.fi repo structure: contracts/, backend/, frontend/, circuits/, docs/.
Cairo contracts scaffolded: ProofGatedYieldAgent, SessionKeyManager, ConfidentialTransfer, SelectiveDisclosure, IntentCommitment, ConstraintReceipt, ComplianceProfile.
Circom circuits for PrivateDeposit and PrivateWithdraw started.

---

## 2026-01-31 -- Backend API and proof pipeline

FastAPI backend wired: session keys, rebalancer, zkML endpoints.
Groth16 prover service using snarkjs for proof generation.
Garaga CLI integration for on-chain proof formatting (--format starkli).
Frontend scaffold with Next.js, Starknet React, agent dashboard.

---

## 2026-02-01 -- Hackathon start, initial deployments

Hackathon officially starts (Starknet Re{define}, Privacy track).
Deployed first contracts to Sepolia using sncast.
Hit RPC version incompatibility: sncast requires v0.10.0, public RPCs are v0.7-v0.8.
Workaround: use starkli instead of sncast for deployments.

Deployed: SessionKeyManager, ConstraintReceipt, SelectiveDisclosure, IntentCommitment.
Garaga verifier deployed at 0x06d0cb7a48b48c5b6ca70f856d249caccea90f506ad7596a6838502fe3aa6d37.

---

## 2026-02-02 -- ConfidentialTransfer deploy, interface mismatch discovery

Deployed ConfidentialTransfer contract.
Private deposit flow wired: frontend -> backend -> proof generation -> contract call.

Issue: "Invalid proof" error on every private_deposit call.
Diagnosis: Proof looked valid, VK matched, all values in range.
Root cause found: Interface type mismatch.
- Contract expected: `fn verify_groth16_proof_bn254(...) -> bool`
- Garaga returns: `fn verify_groth16_proof_bn254(...) -> Result<Span<u256>, felt252>`
Call signature mismatch caused immediate failure before proof was checked.

Fix: Updated IGaragaVerifier interface in confidential_transfer.cairo.
Changed verifier call to use `result.is_ok()` instead of casting to bool.
Rebuilt contract with scarb build.

---

## 2026-02-02 -- Redeploy ConfidentialTransfer, proof verification success

Redeployed ConfidentialTransfer with fixed interface.
New address: 0x04b1265fa18e6873899a4f3ff15cfa0348b7bdf3ccb66bc658d0045ac61dfc0c.

Tested private_deposit: "Invalid proof" error gone.
New error: "u256_sub Overflow" -- proof verification passed, failed at token transfer.
Root cause: Contract had no approval to transfer tokens from user wallet.
Fix: Approved ConfidentialTransfer to spend STRK via sncast invoke approve.
TX: 0x05eea94b4f7c6e9c0d24a91600a0fcdf08e91804a635d97629960d9637ce9cbb.

Private deposit now works end-to-end.

---

## 2026-02-02 -- Nullifier overflow fix

Issue: Withdrawal failing with "Invalid proof" despite correct proof.
Root cause: Nullifier generated as hash % 2**252, could exceed Starknet prime.
Fix: Reduce nullifier modulo STARKNET_PRIME in groth16_prover.py.
Unblocked: Private withdrawal proof generation.

---

## 2026-02-02 -- ProofGatedYieldAgent interface fix

Same interface mismatch bug found in ProofGatedYieldAgent.
Applied same fix: IGaragaVerifier returns Result, call uses result.is_ok().
Redeployed: 0x0700f50fdb177ac690e66040b14fba316bc4ecab6aaccac2b86ffc0969f42fb3.

---

## 2026-02-02 -- Commitment tracking (localStorage)

Issue: After deposit, commitment not visible in withdraw screen.
Root cause: Contract only stores commitment->balance, not user->commitments.
Fix: Track commitments in localStorage (privacy-preserving, no on-chain linkage).
Commitments persist across refresh, update on deposit/withdraw.

---

## 2026-02-03 -- VK mismatch for withdrawal circuit

Issue: Private withdrawal failing with "Wrong Glv FakeGLV result".
Diagnosis: ConfidentialTransfer uses ONE Garaga verifier for both deposit and withdrawal.
- Deposit VK hash: 5c6c9f4a1b15d51a
- Withdrawal VK hash: 77b70a9516d35eec
Different circuits = different VKs. Withdrawal proof verified against deposit verifier fails.

Solution: Two-verifier architecture.
Updated contract to accept garaga_verifier_deposit and garaga_verifier_withdraw.
private_deposit() uses deposit verifier, private_withdraw() uses withdrawal verifier.

---

## 2026-02-03 -- RPC CASM hash mismatch, starkli --casm-hash fix

Issue: starkli declare failing with "Mismatch compiled class hash".
Root cause: Scarb 2.14.0 compiles CASM with one hash, starkli 0.4.2 recompiles with different hash.
Compiler version mismatch: Scarb 2.14.0 vs starkli built-in 2.11.4.

Solution: Use --casm-hash flag to skip starkli recompilation.
Extract expected CASM hash from error message, pass to starkli declare.
Unblocked: All contract deployments with version mismatches.

---

## 2026-02-03 -- Withdrawal verifier deployed

Generated new Garaga verifier for PrivateWithdraw circuit using garaga CLI.
Declared with --casm-hash override.
Deployed: 0x026521c74423467ed4db4aab9da3fc5da5dba5dc5eeda39f3da61e3e420d3efd.
TX: 0x07de43719da631acd219d976d179a4c3baf0be6df7621b734b3eebc9a89f8a80.

---

## 2026-02-03 -- ConfidentialTransfer v2 with two verifiers deployed

Deployed updated ConfidentialTransfer with two-verifier architecture.
Address: 0x032f230ac10fc3eafb4c3efa88c3e9ab31c23ef042c66466f6be49cf0498d840.
Constructor args:
- garaga_verifier_deposit: 0x06d0cb7a...
- garaga_verifier_withdraw: 0x026521c7...
- token: 0x04718f5a... (STRK)
- admin: 0x05fe8125...

Updated backend and frontend .env with new address.
Restarted services.

Private deposit and private withdrawal both working end-to-end.

---

## 2026-02-03 -- ShieldedPool contract built

Built ShieldedPool: unified private allocation pool with Conservative/Neutral/Aggressive pools.
Integrates relayer for private withdrawals to fresh addresses.
Distinguishes human-signed vs agent (execution proof required).
Ready for manual deployment via Voyager (CLI blocked by RPC version).

---

## 2026-02-03 -- Selective disclosure and compliance profiles expanded

Added compliance profile types: yield, balance, risk, performance, kyc, portfolio.
Each profile can prove a statement (threshold) without revealing full data.
Frontend UI for compliance panel, selective disclosure generation.

---

## 2026-02-03 -- Framework naming: zkDE + GATE

Finalized naming:
- zkDE = Zero-Knowledge Deterministic Engine (the infrastructure)
- GATE = Governed Autonomous Trustless Execution (the agent standard)

Updated docs, landing page, docs-site to reflect new naming.

---

## 2026-02-03 -- Docs and dev log cleanup

Created dev_log/ for chronological progress tracking.
Archived ephemeral root MDs to archive/.
Stripped emojis from internal docs.
Synced docs-site with current content and naming.
Updated FOR_JUDGES.md scope.

---

## Key Unblocks Summary

| Issue | Root Cause | Solution |
|-------|------------|----------|
| "Invalid proof" | Interface type mismatch (bool vs Result) | Update IGaragaVerifier interface |
| "u256_sub Overflow" | No token approval | Approve contract to spend tokens |
| Nullifier overflow | hash % 2**252 > prime | Reduce modulo STARKNET_PRIME |
| "Wrong Glv FakeGLV" | Single verifier for two circuits | Two-verifier architecture |
| CASM hash mismatch | Compiler version difference | starkli --casm-hash override |
| RPC v0.10.0 required | Public RPCs are v0.7-v0.8 | Use starkli instead of sncast |
| Commitment tracking | No user->commitments on-chain | localStorage (privacy-preserving) |
