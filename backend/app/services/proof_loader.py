"""
Utility helpers for preparing Integrity-friendly calldata from Stone proofs.

This is a thin wrapper around the Integrity `proof_serializer` binary. It lets
us select a Stone proof JSON (e.g., produced by `cpu_air_prover --generate_annotations`)
and turn it into the flattened felt calldata string that the Integrity verifier
examples expect. We keep this isolated so callers can choose which source to use
(local Stone proof vs. Atlantic proof download) without duplicating subprocess
logic.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional


def serialize_stone_proof(
    proof_json_path: Path,
    serializer_bin: Path,
    timeout: int = 30,
) -> List[int]:
    """
    Run the Integrity proof_serializer on a Stone proof JSON and return the felt list.

    Args:
        proof_json_path: Path to Stone/Integrity proof JSON (with annotations).
        serializer_bin: Path to the compiled `proof_serializer` binary.
        timeout: Subprocess timeout in seconds.

    Returns:
        List of felts (ints) suitable for feeding into a Starknet call.

    Raises:
        subprocess.CalledProcessError on serializer failures.
        ValueError if the serializer output cannot be parsed into integers.
    """
    proof_json_path = Path(proof_json_path)
    serializer_bin = Path(serializer_bin)

    if not proof_json_path.exists():
        raise FileNotFoundError(f"Proof JSON not found: {proof_json_path}")
    if not serializer_bin.exists():
        raise FileNotFoundError(f"proof_serializer binary not found: {serializer_bin}")

    proc = subprocess.run(
        [str(serializer_bin)],
        input=proof_json_path.read_bytes(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=True,
    )

    output = proc.stdout.decode().strip()
    try:
        return [int(x) for x in output.split()] if output else []
    except Exception as exc:  # pragma: no cover - defensive parse guard
        raise ValueError(f"Failed to parse serializer output: {output}") from exc


def load_calldata_file(calldata_path: Path) -> List[int]:
    """
    Convenience for loading a whitespace-separated calldata file into ints.
    """
    calldata_path = Path(calldata_path)
    if not calldata_path.exists():
        raise FileNotFoundError(f"Calldata file not found: {calldata_path}")
    text = calldata_path.read_text().strip()
    return [int(x) for x in text.split()] if text else []
