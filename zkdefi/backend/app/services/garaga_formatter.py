"""
Garaga proof formatter using Docker with Python 3.10.
Generates full_proof_with_hints format required by Garaga verifier.
"""
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CIRCUITS_DIR = PROJECT_ROOT / "circuits" / "build"


def format_proof_for_garaga(
    proof_json: dict,
    public_json: list,
    vk_path: Path,
) -> list[str]:
    """
    Use garaga CLI in Docker (Python 3.10) to format proof with MSM hints.
    
    Args:
        proof_json: snarkjs proof.json content
        public_json: snarkjs public.json content
        vk_path: Path to verification_key.json
    
    Returns:
        List of felt252 hex strings ready for Garaga verification
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Write proof and public inputs
        proof_file = tmp_path / "proof.json"
        public_file = tmp_path / "public.json"
        
        with open(proof_file, 'w') as f:
            json.dump(proof_json, f)
        with open(public_file, 'w') as f:
            json.dump(public_json, f)
        
        # Run garaga CLI in Docker container with Python 3.10
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{tmp_path}:/work",
            "-v", f"{vk_path.parent}:/circuits",
            "-w", "/work",
            "python:3.10-slim",
            "bash", "-c",
            f"""
            pip install -q garaga && \
            garaga calldata \
                --system groth16 \
                --vk /circuits/{vk_path.name} \
                --proof proof.json \
                --public-inputs public.json \
                --format starkli \
                > garaga_calldata.txt
            """
        ]
        
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=180,
        )
        
        if result.returncode != 0:
            raise Exception(f"Garaga Docker formatting failed: {result.stderr}")
        
        # Read the formatted calldata
        calldata_file = tmp_path / "garaga_calldata.txt"
        if not calldata_file.exists():
            raise Exception("Garaga did not generate calldata file")
        
        with open(calldata_file) as f:
            content = f.read().strip()
        
        # Garaga --format starkli returns: length followed by space-separated decimal values
        # Example: "1949 13319788039342200419402383041 13831044747143748575809708628 ..."
        try:
            values = content.split()
            if not values:
                raise ValueError("Empty calldata")
            
            # First value is the length, rest are the actual calldata as decimals
            length = int(values[0])
            decimals = [int(v) for v in values[1:]]
            
            if len(decimals) != length:
                raise ValueError(f"Length mismatch: expected {length}, got {len(decimals)}")
            
            # Convert to hex
            calldata_hex = [hex(v) for v in decimals]
            return calldata_hex
        except Exception as e:
            raise Exception(f"Failed to parse garaga starkli output: {e}\nContent: {content[:200]}")
