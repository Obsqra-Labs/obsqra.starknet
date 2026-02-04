#!/usr/bin/env python3
"""
Compare proof_parameters fields between our proof and canonical example.

This identifies specific parameter mismatches that could cause OODS failures.
"""
import glob
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

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


def load_canonical_proof() -> Dict[str, Any]:
    """Load Integrity's canonical recursive example proof."""
    repo_root = Path(__file__).resolve().parent.parent
    canonical_path = (
        repo_root / "integrity" / "examples" / "proofs" / "recursive" /
        "cairo0_stone5_keccak_160_lsb_example_proof.json"
    )
    
    if not canonical_path.exists():
        raise FileNotFoundError(f"Canonical proof not found at {canonical_path}")
    
    logger.info(f"Loading canonical proof from {canonical_path}")
    with open(canonical_path, 'r') as f:
        return json.load(f)


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get nested value from dict using dot notation (e.g., 'stark.fri.n_queries')."""
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current


def compare_field(
    canonical: Dict[str, Any],
    our: Dict[str, Any],
    path: str,
    label: str
) -> tuple[bool, Any, Any]:
    """Compare a single field between canonical and our proof."""
    canonical_val = get_nested_value(canonical, path)
    our_val = get_nested_value(our, path)
    
    match = canonical_val == our_val
    return match, canonical_val, our_val


def compare_proof_parameters(canonical: Dict[str, Any], our: Dict[str, Any]) -> Dict[str, tuple[bool, Any, Any]]:
    """Compare all relevant proof_parameters fields."""
    # Extract proof_parameters from both
    canonical_params = canonical.get("proof_parameters", {})
    our_params = our.get("proof_parameters", {})
    
    if not canonical_params:
        logger.warning("Canonical proof missing 'proof_parameters' field")
        canonical_params = {}
    if not our_params:
        logger.warning("Our proof missing 'proof_parameters' field")
        our_params = {}
    
    # Fields to compare
    fields_to_compare = [
        ("channel_hash", "Channel hash"),
        ("commitment_hash", "Commitment hash"),
        ("pow_hash", "Pow hash"),
        ("n_verifier_friendly_commitment_layers", "n_verifier_friendly_commitment_layers"),
        ("stark.fri.fri_step_list", "FRI step_list"),
        ("stark.fri.n_queries", "FRI n_queries"),
        ("stark.fri.last_layer_degree_bound", "FRI last_layer_degree_bound"),
        ("stark.fri.proof_of_work_bits", "FRI proof_of_work_bits"),
        ("stark.log_n_cosets", "FRI log_n_cosets"),
    ]
    
    results = {}
    for path, label in fields_to_compare:
        match, canonical_val, our_val = compare_field(
            canonical_params, our_params, path, label
        )
        results[label] = (match, canonical_val, our_val)
    
    return results


def compare_public_input(canonical: Dict[str, Any], our: Dict[str, Any]) -> Dict[str, tuple[bool, Any, Any]]:
    """Compare public_input fields."""
    canonical_pi = canonical.get("public_input", {})
    our_pi = our.get("public_input", {})
    
    fields_to_compare = [
        ("layout", "Layout"),
        ("n_steps", "n_steps"),
    ]
    
    results = {}
    for path, label in fields_to_compare:
        match, canonical_val, our_val = compare_field(
            canonical_pi, our_pi, path, label
        )
        results[label] = (match, canonical_val, our_val)
    
    # Compare memory segments
    canonical_segments = canonical_pi.get("memory_segments", {})
    our_segments = our_pi.get("memory_segments", {})
    
    canonical_segment_names = set(canonical_segments.keys()) if isinstance(canonical_segments, dict) else set()
    our_segment_names = set(our_segments.keys()) if isinstance(our_segments, dict) else set()
    
    results["Memory segments"] = (
        canonical_segment_names == our_segment_names,
        sorted(canonical_segment_names),
        sorted(our_segment_names)
    )
    
    return results


def format_value(val: Any, max_len: int = 80) -> str:
    """Format a value for display."""
    if val is None:
        return "None"
    if isinstance(val, (list, tuple)):
        if len(val) > 5:
            return f"[{val[0]}, {val[1]}, ..., {val[-1]}] (length: {len(val)})"
        return str(val)
    val_str = str(val)
    if len(val_str) > max_len:
        return val_str[:max_len] + "..."
    return val_str


def print_comparison(results: Dict[str, tuple[bool, Any, Any]], title: str):
    """Print comparison results."""
    logger.info("=" * 80)
    logger.info(title)
    logger.info("=" * 80)
    
    matches = 0
    mismatches = 0
    
    for label, (match, canonical_val, our_val) in results.items():
        if match:
            matches += 1
            status = "✅ MATCH"
        else:
            mismatches += 1
            status = "❌ MISMATCH"
        
        logger.info(f"{status}: {label}")
        logger.info(f"  Canonical: {format_value(canonical_val)}")
        logger.info(f"  Ours:      {format_value(our_val)}")
        logger.info("")
    
    logger.info(f"Summary: {matches} matches, {mismatches} mismatches")
    logger.info("=" * 80)
    
    return matches, mismatches


def main():
    """Main entry point."""
    try:
        # Load proofs
        canonical = load_canonical_proof()
        our_path = find_latest_proof()
        
        logger.info(f"Loading our proof from {our_path}")
        with open(our_path, 'r') as f:
            our = json.load(f)
        
        # Compare proof_parameters
        param_results = compare_proof_parameters(canonical, our)
        param_matches, param_mismatches = print_comparison(
            param_results, "PROOF PARAMETERS COMPARISON"
        )
        
        # Compare public_input
        pi_results = compare_public_input(canonical, our)
        pi_matches, pi_mismatches = print_comparison(
            pi_results, "PUBLIC INPUT COMPARISON"
        )
        
        # Overall summary
        total_matches = param_matches + pi_matches
        total_mismatches = param_mismatches + pi_mismatches
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("OVERALL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total matches: {total_matches}")
        logger.info(f"Total mismatches: {total_mismatches}")
        
        if total_mismatches == 0:
            logger.info("✅ All fields match! Issue is likely in serialization or Stone commit.")
        else:
            logger.info("❌ Mismatches found! These may be causing OODS failures.")
            logger.info("Next steps: Correct mismatched parameters and regenerate proof.")
        
        sys.exit(0 if total_mismatches == 0 else 1)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
