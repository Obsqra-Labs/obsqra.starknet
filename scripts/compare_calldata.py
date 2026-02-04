#!/usr/bin/env python3
"""
Compare serialized calldata format between our proof and canonical example.

This identifies serialization format differences that could cause OODS failures.
"""
import glob
import json
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def find_latest_proof() -> Path:
    """Find the latest generated proof from canonical_integrity pipeline."""
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
    
    for proof_dir in proof_dirs:
        proof_path = Path(proof_dir) / "risk_proof.json"
        if proof_path.exists():
            logger.info(f"Found our proof at {proof_path}")
            return proof_path
    
    raise FileNotFoundError(
        f"No risk_proof.json found in {proof_dirs[0]}. "
        "Run the canonical pipeline first."
    )


def find_serializer() -> Path:
    """Find the proof_serializer binary."""
    repo_root = Path(__file__).resolve().parent.parent
    
    possible_paths = [
        repo_root / "integrity" / "target" / "release" / "proof_serializer",
        repo_root / "integrity" / "target" / "dev" / "proof_serializer",
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found proof_serializer at {path}")
            return path
    
    raise FileNotFoundError(
        f"proof_serializer not found. Tried: {[str(p) for p in possible_paths]}\n"
        "Build it with: cd integrity && cargo build --release --bin proof_serializer"
    )


def serialize_proof(proof_path: Path, serializer_path: Path) -> list[int]:
    """Serialize a proof using proof_serializer."""
    try:
        proc = subprocess.run(
            [str(serializer_path)],
            input=proof_path.read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=True,
        )
        
        output = proc.stdout.decode().strip()
        if not output:
            raise ValueError("Serializer returned empty output")
        
        return [int(x) for x in output.split()]
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Serializer failed: {e}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr.decode()}")
        raise
    except ValueError as e:
        logger.error(f"Failed to parse serializer output: {e}")
        raise


def compare_calldata(canonical_calldata: list[int], our_calldata: list[int]):
    """Compare two calldata arrays and identify differences."""
    logger.info("=" * 80)
    logger.info("CALLDATA COMPARISON")
    logger.info("=" * 80)
    
    logger.info(f"Canonical calldata length: {len(canonical_calldata)} felts")
    logger.info(f"Our calldata length: {len(our_calldata)} felts")
    
    if len(canonical_calldata) != len(our_calldata):
        logger.error(f"❌ Length mismatch: {len(canonical_calldata)} vs {len(our_calldata)}")
        min_len = min(len(canonical_calldata), len(our_calldata))
        logger.info(f"Comparing first {min_len} felts...")
    else:
        logger.info("✅ Lengths match")
    
    min_len = min(len(canonical_calldata), len(our_calldata))
    mismatches = []
    
    # Compare first 100 felts in detail
    detail_limit = min(100, min_len)
    for i in range(detail_limit):
        if canonical_calldata[i] != our_calldata[i]:
            mismatches.append((i, canonical_calldata[i], our_calldata[i]))
    
    # Check remaining felts for any mismatches
    for i in range(detail_limit, min_len):
        if canonical_calldata[i] != our_calldata[i]:
            mismatches.append((i, canonical_calldata[i], our_calldata[i]))
            if len(mismatches) >= 20:  # Limit output
                break
    
    if mismatches:
        logger.error(f"❌ Found {len(mismatches)} mismatches (showing first 20):")
        for idx, (i, canon_val, our_val) in enumerate(mismatches[:20]):
            logger.error(f"  Position {i}: canonical={canon_val}, ours={our_val}")
        
        if len(mismatches) > 20:
            logger.error(f"  ... and {len(mismatches) - 20} more mismatches")
        
        # Check if mismatches are in OODS section (typically around positions 96-4416)
        oods_mismatches = [m for m in mismatches if 96 <= m[0] < 4416]
        if oods_mismatches:
            logger.error(f"⚠️  {len(oods_mismatches)} mismatches in OODS section (positions 96-4416)")
        
        return False
    else:
        logger.info("✅ All compared felts match!")
        return True


def main():
    """Main entry point."""
    try:
        repo_root = Path(__file__).resolve().parent.parent
        
        # Load canonical proof
        canonical_proof_path = (
            repo_root / "integrity" / "examples" / "proofs" / "recursive" /
            "cairo0_stone5_keccak_160_lsb_example_proof.json"
        )
        
        if not canonical_proof_path.exists():
            logger.error(f"Canonical proof not found at {canonical_proof_path}")
            sys.exit(1)
        
        # Find our proof
        our_proof_path = find_latest_proof()
        
        # Find serializer
        serializer_path = find_serializer()
        
        # Serialize both proofs
        logger.info("Serializing canonical proof...")
        canonical_calldata = serialize_proof(canonical_proof_path, serializer_path)
        
        logger.info("Serializing our proof...")
        our_calldata = serialize_proof(our_proof_path, serializer_path)
        
        # Compare
        match = compare_calldata(canonical_calldata, our_calldata)
        
        if match:
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: Calldata formats match!")
            logger.info("=" * 80)
            logger.info("DECISION: Serialization format is correct")
            logger.info("Next steps: Check Stone commit or on-chain verifier")
        else:
            logger.error("=" * 80)
            logger.error("❌ FAILURE: Calldata formats differ!")
            logger.error("=" * 80)
            logger.error("DECISION: Serialization format mismatch")
            logger.error("Next steps: Check serializer version, proof structure, or OODS section")
        
        sys.exit(0 if match else 1)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
