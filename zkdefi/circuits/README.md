# Private Transfer Circuits (Garaga Groth16)

Circuits for confidential deposit/withdraw: prove commitment and amount validity without revealing full balance.

## Layout

- `PrivateDeposit.circom` – Deposit: commitment = hash(amount, nonce), balance >= amount.
- `PrivateWithdraw.circom` – Withdraw: nullifier check, commitment ownership, amount.

## Prerequisites

- Node.js 18+ (for snarkjs)
- Circom 2.x: https://docs.circom.io/
- Garaga CLI: `pip install garaga==1.0.1`
- snarkjs: `npm install -g snarkjs` or use local npx

## Build (Circom + snarkjs)

```bash
# Compile circuit
circom PrivateDeposit.circom --r1cs --wasm --sym -o build

# Powers of tau (reuse or download)
# snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
# snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="First" -v
# snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v

# Groth16 setup
snarkjs groth16 setup build/PrivateDeposit.r1cs pot12_final.ptau build/PrivateDeposit_0000.zkey
snarkjs zkey contribute build/PrivateDeposit_0000.zkey build/PrivateDeposit_final.zkey --name="Contrib" -v
snarkjs zkey export verificationkey build/PrivateDeposit_final.zkey build/verification_key.json

# Prove (example)
node build/PrivateDeposit_js/generate_witness.js build/PrivateDeposit_js/PrivateDeposit.wasm input.json build/witness.wtns
snarkjs groth16 prove build/PrivateDeposit_final.zkey build/witness.wtns build/proof.json build/public.json

# Export solidity calldata (for reference; Garaga uses its own format)
snarkjs zkey export soliditycalldata build/public.json build/proof.json
```

## Garaga: Generate Cairo verifier and deploy to Sepolia

1. **Verification key**  
   Use the same `verification_key.json` (or Garaga’s expected vk format; see Garaga Groth16 docs).

2. **Generate Cairo verifier**  
   ```bash
   garaga gen --system groth16_bn254 --vk build/verification_key.json -o contracts/verifier
   ```  
   (Exact `--system` and output path per Garaga docs.)

3. **Deploy to Starknet Sepolia**  
   ```bash
   sncast --url https://starknet-sepolia.public.blastapi.io --network alpha-sepolia deploy --contract contracts/verifier/Verifier.sierra.json
   ```  
   Set `GARAGA_VERIFIER_ADDRESS` in `.env`.

4. **Calldata for verification**  
   ```bash
   garaga verify-onchain --system groth16 --contract-address <GARAGA_VERIFIER_ADDRESS> --vk build/verification_key.json --proof build/proof.json
   ```  
   Use the emitted calldata when calling the verifier (or `ConfidentialTransfer.private_deposit`).

## Public inputs (contract ABI)

- **Deposit:** `commitment` (felt), `amount_public` (u256). Contract pulls `amount_public` from user and credits `commitment_balance[commitment]`.
- **Withdraw:** `nullifier`, `commitment`, `amount_public`, `recipient`. Contract checks nullifier unspent, debits commitment, transfers to recipient.

## Version compatibility

Use the same Garaga SDK version for generating the verifier and for `verify-onchain`; otherwise calldata may be incompatible.
