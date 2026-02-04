#!/usr/bin/env python3
"""
Compare OODS values between our proof and canonical example.

Extracts and compares:
- OODS evaluation point
- OODS values
- Channel state at OODS point
"""
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def extract_oods_info(proof_path: Path):
    """Extract OODS information from proof JSON."""
    with open(proof_path, 'r') as f:
        proof = json.load(f)
    
    annotations = proof.get("annotations", [])
    
    # Find OODS evaluation point
    oods_point = None
    oods_values = None
    oods_commitment = None
    
    for i, annotation in enumerate(annotations):
        if "Out Of Domain Sampling/OODS values: Evaluation point" in annotation:
            # Extract field element
            if "Field Element(" in annotation:
                oods_point = annotation.split("Field Element(")[1].split(")")[0]
        elif "Out Of Domain Sampling/OODS values:" in annotation and "Field Elements(" in annotation:
            # Extract OODS values
            if "Field Elements(" in annotation:
                values_str = annotation.split("Field Elements(")[1].split(")")[0]
                oods_values = values_str.split(", ")
        elif "Out Of Domain Sampling/Commit on Trace" in annotation:
            # Extract commitment hash
            if "Hash(" in annotation:
                oods_commitment = annotation.split("Hash(")[1].split(")")[0]
    
    # Also check proof_parameters for channel/commitment info
    proof_params = proof.get("proof_parameters", {})
    channel_hash = proof_params.get("channel_hash")
    commitment_hash = proof_params.get("commitment_hash")
    
    return {
        "oods_point": oods_point,
        "oods_values": oods_values,
        "oods_commitment": oods_commitment,
        "channel_hash": channel_hash,
        "commitment_hash": commitment_hash,
        "n_steps": proof.get("public_input", {}).get("n_steps"),
    }


def main():
    """Compare OODS values between proofs."""
    repo_root = Path(__file__).resolve().parent.parent
    
    # Paths
    canonical_proof = repo_root / "integrity" / "examples" / "proofs" / "recursive" / "cairo0_stone5_keccak_160_lsb_example_proof.json"
    
    # Find our latest proof
    our_proof = None
    temp_dirs = list(Path("/tmp").glob("canonical_integrity_*"))
    if temp_dirs:
        latest_dir = max(temp_dirs, key=lambda p: p.stat().st_mtime)
        our_proof = latest_dir / "risk_proof.json"
    
    if not our_proof or not our_proof.exists():
        logger.error("Could not find our generated proof")
        logger.info("Run test_fri_fix_verification.py first to generate a proof")
        sys.exit(1)
    
    logger.info("=" * 80)
    logger.info("OODS VALUES COMPARISON")
    logger.info("=" * 80)
    logger.info("")
    
    # Extract OODS info
    logger.info("Extracting OODS info from canonical proof...")
    canonical_info = extract_oods_info(canonical_proof)
    
    logger.info("Extracting OODS info from our proof...")
    our_info = extract_oods_info(our_proof)
    
    # Compare
    logger.info("")
    logger.info("=" * 80)
    logger.info("COMPARISON RESULTS")
    logger.info("=" * 80)
    logger.info("")
    
    # n_steps
    logger.info(f"n_steps:")
    logger.info(f"  Canonical: {canonical_info['n_steps']}")
    logger.info(f"  Ours:      {our_info['n_steps']}")
    logger.info(f"  Match:     {'✅' if canonical_info['n_steps'] == our_info['n_steps'] else '❌'}")
    logger.info("")
    
    # Channel hash
    logger.info(f"Channel hash:")
    logger.info(f"  Canonical: {canonical_info['channel_hash']}")
    logger.info(f"  Ours:      {our_info['channel_hash']}")
    logger.info(f"  Match:     {'✅' if canonical_info['channel_hash'] == our_info['channel_hash'] else '❌'}")
    logger.info("")
    
    # Commitment hash
    logger.info(f"Commitment hash:")
    logger.info(f"  Canonical: {canonical_info['commitment_hash']}")
    logger.info(f"  Ours:      {our_info['commitment_hash']}")
    logger.info(f"  Match:     {'✅' if canonical_info['commitment_hash'] == our_info['commitment_hash'] else '❌'}")
    logger.info("")
    
    # OODS point
    logger.info(f"OODS evaluation point:")
    logger.info(f"  Canonical: {canonical_info['oods_point']}")
    logger.info(f"  Ours:      {our_info['oods_point']}")
    if canonical_info['oods_point'] and our_info['oods_point']:
        match = canonical_info['oods_point'] == our_info['oods_point']
        logger.info(f"  Match:     {'✅' if match else '❌'}")
        if not match:
            logger.warning("  ⚠️  OODS points differ - this is expected if channel state differs")
    else:
        logger.warning("  ⚠️  Could not extract OODS point from one or both proofs")
    logger.info("")
    
    # OODS commitment
    logger.info(f"OODS commitment hash:")
    logger.info(f"  Canonical: {canonical_info['oods_commitment']}")
    logger.info(f"  Ours:      {our_info['oods_commitment']}")
    if canonical_info['oods_commitment'] and our_info['oods_commitment']:
        match = canonical_info['oods_commitment'] == our_info['oods_commitment']
        logger.info(f"  Match:     {'✅' if match else '❌'}")
        if not match:
            logger.warning("  ⚠️  OODS commitments differ - indicates different trace/constraints")
    else:
        logger.warning("  ⚠️  Could not extract OODS commitment from one or both proofs")
    logger.info("")
    
    # OODS values count
    if canonical_info['oods_values'] and our_info['oods_values']:
        logger.info(f"OODS values count:")
        logger.info(f"  Canonical: {len(canonical_info['oods_values'])} values")
        logger.info(f"  Ours:      {len(our_info['oods_values'])} values")
        logger.info(f"  Match:     {'✅' if len(canonical_info['oods_values']) == len(our_info['oods_values']) else '❌'}")
        logger.info("")
        logger.info("Note: OODS values will differ if trace/constraints differ")
        logger.info("      This is expected - the key is whether they verify")
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("CONCLUSION")
    logger.info("=" * 80)
    logger.info("")
    logger.info("If OODS points/commitments differ:")
    logger.info("  → Different channel state or trace structure")
    logger.info("  → Likely Stone version or AIR config mismatch")
    logger.info("")
    logger.info("If OODS points match but verification fails:")
    logger.info("  → Issue in OODS value calculation or constraint evaluation")
    logger.info("  → Likely Stone version semantics difference")


if __name__ == "__main__":
    main()
