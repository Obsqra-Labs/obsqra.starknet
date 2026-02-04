"""
Groth16 proof generation for private deposits/withdrawals.
Uses snarkjs to generate proofs from Circom circuits.
Uses Docker + garaga CLI (Python 3.10) to format proofs for Garaga verifier.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

# Circuit paths - go from services/ -> app/ -> backend/ -> zkdefi (project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CIRCUITS_DIR = PROJECT_ROOT / "circuits" / "build"
PRIVATE_DEPOSIT_WASM = CIRCUITS_DIR / "PrivateDeposit_js" / "PrivateDeposit.wasm"
PRIVATE_DEPOSIT_ZKEY = CIRCUITS_DIR / "PrivateDeposit_final.zkey"
PRIVATE_DEPOSIT_VK = CIRCUITS_DIR / "verification_key.json"
PRIVATE_WITHDRAW_WASM = CIRCUITS_DIR / "PrivateWithdraw_js" / "PrivateWithdraw.wasm"
PRIVATE_WITHDRAW_ZKEY = CIRCUITS_DIR / "PrivateWithdraw_final.zkey"
PRIVATE_WITHDRAW_VK = CIRCUITS_DIR / "PrivateWithdraw_verification_key.json"


class Groth16Prover:
    """Generate Groth16 proofs using snarkjs for private transfers."""

    @staticmethod
    def _run_snarkjs_command(cmd: list[str], cwd: str | None = None) -> dict[str, Any]:
        """Run snarkjs command and return JSON result."""
        try:
            result = subprocess.run(
                ["npx", "snarkjs"] + cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=120,
            )
            if result.returncode != 0:
                raise Exception(f"snarkjs error: {result.stderr}")
            return json.loads(result.stdout) if result.stdout else {}
        except subprocess.TimeoutExpired:
            raise Exception("snarkjs timeout")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON from snarkjs: {result.stdout}")

    @staticmethod
    def generate_private_deposit_proof(
        amount: int,
        nonce: int,
        balance: int,
    ) -> dict[str, Any]:
        """
        Generate Groth16 proof for private deposit.
        Returns proof_calldata compatible with Garaga verifier.
        """
        if not PRIVATE_DEPOSIT_WASM.exists() or not PRIVATE_DEPOSIT_ZKEY.exists():
            raise Exception(
                f"Circuit files not found. WASM: {PRIVATE_DEPOSIT_WASM.exists()}, ZKEY: {PRIVATE_DEPOSIT_ZKEY.exists()}"
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Prepare input
            input_data = {
                "amount": str(amount),
                "nonce": str(nonce),
                "balance": str(balance),
            }
            input_file = Path(tmpdir) / "input.json"
            with open(input_file, "w") as f:
                json.dump(input_data, f)

            # Generate witness
            witness_file = Path(tmpdir) / "witness.wtns"
            subprocess.run(
                [
                    "node",
                    str(CIRCUITS_DIR / "PrivateDeposit_js" / "generate_witness.js"),
                    str(PRIVATE_DEPOSIT_WASM),
                    str(input_file),
                    str(witness_file),
                ],
                check=True,
                capture_output=True,
            )

            # Generate proof
            proof_file = Path(tmpdir) / "proof.json"
            public_file = Path(tmpdir) / "public.json"
            subprocess.run(
                [
                    "npx",
                    "snarkjs",
                    "groth16",
                    "prove",
                    str(PRIVATE_DEPOSIT_ZKEY),
                    str(witness_file),
                    str(proof_file),
                    str(public_file),
                ],
                check=True,
                capture_output=True,
            )

            # Read proof and public signals
            with open(proof_file) as f:
                proof = json.load(f)
            with open(public_file) as f:
                public = json.load(f)

            # Use garaga CLI via Docker to format proof with MSM hints
            from .garaga_formatter import format_proof_for_garaga
            
            try:
                proof_calldata = format_proof_for_garaga(
                    proof_json=proof,
                    public_json=public,
                    vk_path=PRIVATE_DEPOSIT_VK,
                )
            except Exception as e:
                raise Exception(f"Garaga formatting failed: {str(e)}")

            # Calculate commitment (from circuit public outputs)
            commitment = (amount * 0x10000 + nonce) % (2**252)

            return {
                "commitment": hex(commitment),
                "amount_public": amount,
                "nonce": nonce,
                "proof_calldata": proof_calldata,
            }

    @staticmethod
    def generate_private_withdraw_proof(
        commitment: str,
        amount: int,
        nonce: int,
        balance: int,
        user_secret: int = 0,
    ) -> dict[str, Any]:
        """
        Generate Groth16 proof for private withdrawal.
        Returns proof_calldata compatible with Garaga verifier.
        """
        if not PRIVATE_WITHDRAW_WASM.exists() or not PRIVATE_WITHDRAW_ZKEY.exists():
            raise Exception(
                f"Circuit files not found. WASM: {PRIVATE_WITHDRAW_WASM.exists()}, ZKEY: {PRIVATE_WITHDRAW_ZKEY.exists()}"
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            commitment_int = int(commitment, 16) if isinstance(commitment, str) else commitment

            # Prepare input
            input_data = {
                "amount": str(amount),
                "nonce": str(nonce),
                "balance": str(balance),
                "user_secret": str(user_secret),
                "commitment_public": str(commitment_int),
            }
            input_file = Path(tmpdir) / "input.json"
            with open(input_file, "w") as f:
                json.dump(input_data, f)

            # Generate witness
            witness_file = Path(tmpdir) / "witness.wtns"
            subprocess.run(
                [
                    "node",
                    str(CIRCUITS_DIR / "PrivateWithdraw_js" / "generate_witness.js"),
                    str(PRIVATE_WITHDRAW_WASM),
                    str(input_file),
                    str(witness_file),
                ],
                check=True,
                capture_output=True,
            )

            # Generate proof
            proof_file = Path(tmpdir) / "proof.json"
            public_file = Path(tmpdir) / "public.json"
            subprocess.run(
                [
                    "npx",
                    "snarkjs",
                    "groth16",
                    "prove",
                    str(PRIVATE_WITHDRAW_ZKEY),
                    str(witness_file),
                    str(proof_file),
                    str(public_file),
                ],
                check=True,
                capture_output=True,
            )

            # Read proof and public signals
            with open(proof_file) as f:
                proof = json.load(f)
            with open(public_file) as f:
                public = json.load(f)

            # Use garaga CLI via Docker to format proof with MSM hints
            from .garaga_formatter import format_proof_for_garaga
            
            try:
                proof_calldata = format_proof_for_garaga(
                    proof_json=proof,
                    public_json=public,
                    vk_path=PRIVATE_WITHDRAW_VK,
                )
            except Exception as e:
                raise Exception(f"Garaga formatting failed: {str(e)}")

            # Generate nullifier
            import hashlib

            # Use Starknet prime, not 2^252
            STARKNET_PRIME = 0x800000000000011000000000000000000000000000000000000000000000001
            nullifier_input = f"{commitment_int}:{nonce}:{user_secret}".encode()
            nullifier_hash = hashlib.sha256(nullifier_input).hexdigest()
            nullifier = int(nullifier_hash, 16) % STARKNET_PRIME

            return {
                "nullifier": hex(nullifier),
                "commitment": hex(commitment_int),
                "amount_public": amount,
                "nonce": nonce,
                "proof_calldata": proof_calldata,
            }
