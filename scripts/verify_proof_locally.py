#!/usr/bin/env python3
"""
Run local Stone verifier (cpu_air_verifier) on our generated proof.

This script determines if the OODS issue is in proof generation or serialization.
If local verification passes → serialization/on-chain verifier issue
If local verification fails → proof generation/public input issue
"""
import glob
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def find_latest_proof() -> Path:
    """Find the latest generated proof from canonical_integrity pipeline."""
    # Look for proofs in /tmp/canonical_integrity_*
    tmp_dir = Path("/tmp")
    proof_dirs = sorted(
        glob.glob(str(tmp_dir / "canonical_integrity_*")),
        reverse=True
    )
    
    if not proof_dirs:
        raise FileNotFoundError(
            "No canonical_integrity proof directories found in /tmp. "
            "Run the canonical pipeline first."
        )
    
    # Look for risk_proof.json in the most recent directory
    for proof_dir in proof_dirs:
        proof_path = Path(proof_dir) / "risk_proof.json"
        if proof_path.exists():
            logger.info(f"Found proof at {proof_path}")
            return proof_path
    
    raise FileNotFoundError(
        f"No risk_proof.json found in {proof_dirs[0]}. "
        "Run the canonical pipeline first."
    )


def find_stone_verifier() -> Path:
    """Find the cpu_air_verifier binary."""
    repo_root = Path(__file__).resolve().parent.parent
    
    # Try common locations
    possible_paths = [
        repo_root / "stone-prover" / "build" / "bazelout" / "k8-opt" / "bin" /
        "src" / "starkware" / "main" / "cpu" / "cpu_air_verifier",
        repo_root / "stone-prover" / "cpu_air_verifier",
        Path("/usr/local/bin/cpu_air_verifier"),
        Path("/usr/bin/cpu_air_verifier"),
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_file():
            logger.info(f"Found cpu_air_verifier at {path}")
            return path
    
    raise FileNotFoundError(
        f"cpu_air_verifier not found. Tried: {[str(p) for p in possible_paths]}"
    )


def verify_proof_locally(proof_path: Path, verifier_path: Path) -> bool:
    """Run cpu_air_verifier on the proof."""
    logger.info("=" * 80)
    logger.info("Running local Stone verifier (cpu_air_verifier)")
    logger.info("=" * 80)
    logger.info(f"Proof: {proof_path}")
    logger.info(f"Verifier: {verifier_path}")
    
    try:
        result = subprocess.run(
            [str(verifier_path), "--in_file", str(proof_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
        )
        
        if result.returncode == 0:
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: Local verification passed!")
            logger.info("=" * 80)
            if result.stdout:
                logger.info(f"Verifier output:\n{result.stdout}")
            logger.info("DECISION: Issue is in serialization format or on-chain verifier")
            logger.info("Next steps: Compare calldata format, check serializer version")
            return True
        else:
            logger.error("=" * 80)
            logger.error("❌ FAILURE: Local verification failed")
            logger.error("=" * 80)
            if result.stdout:
                logger.error(f"Verifier stdout:\n{result.stdout}")
            if result.stderr:
                logger.error(f"Verifier stderr:\n{result.stderr}")
            logger.error("DECISION: Issue is in proof generation or public input")
            logger.error("Next steps: Compare proof_parameters, check Stone commit, verify AIR config")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Verifier timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"Exception running verifier: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    try:
        proof_path = find_latest_proof()
        verifier_path = find_stone_verifier()
        
        success = verify_proof_locally(proof_path, verifier_path)
        sys.exit(0 if success else 1)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
