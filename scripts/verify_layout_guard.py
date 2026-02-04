#!/usr/bin/env python3
"""
Verify that the layout/builtins guard in proof generation pipeline is working correctly.

This ensures the guard prevents regression by checking:
- public_input.layout == 'recursive'
- memory_segments contain only: bitwise, execution, output, pedersen, program, range_check
- No ecdsa segment present
"""
import glob
import json
import logging
import sys
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
            logger.info(f"Found proof at {proof_path}")
            return proof_path
    
    raise FileNotFoundError(
        f"No risk_proof.json found in {proof_dirs[0]}. "
        "Run the canonical pipeline first."
    )


def verify_layout_guard(proof_path: Path) -> bool:
    """Verify layout and builtins guard conditions."""
    logger.info("=" * 80)
    logger.info("VERIFYING LAYOUT & BUILTINS GUARD")
    logger.info("=" * 80)
    
    with open(proof_path, 'r') as f:
        proof_data = json.load(f)
    
    public_input = proof_data.get("public_input", {})
    if not public_input:
        logger.error("❌ Proof missing 'public_input' field")
        return False
    
    # Check layout
    layout = public_input.get("layout")
    expected_layout = "recursive"
    
    logger.info(f"Checking layout: {layout} (expected: {expected_layout})")
    if layout != expected_layout:
        logger.error(f"❌ Layout mismatch: got '{layout}', expected '{expected_layout}'")
        return False
    logger.info("✅ Layout matches: recursive")
    
    # Check memory segments
    memory_segments = public_input.get("memory_segments", {})
    if not isinstance(memory_segments, dict):
        logger.error(f"❌ memory_segments is not a dict: {type(memory_segments)}")
        return False
    
    segment_names = set(memory_segments.keys())
    expected_segments = {"bitwise", "execution", "output", "pedersen", "program", "range_check"}
    
    logger.info(f"Checking memory segments: {sorted(segment_names)}")
    logger.info(f"Expected segments: {sorted(expected_segments)}")
    
    # Check for ecdsa (should NOT be present)
    if "ecdsa" in segment_names:
        logger.error("❌ ECDSA segment found (should not be present in recursive layout)")
        return False
    logger.info("✅ No ECDSA segment (correct for recursive layout)")
    
    # Check all segments are expected
    unexpected = segment_names - expected_segments
    if unexpected:
        logger.error(f"❌ Unexpected segments found: {sorted(unexpected)}")
        return False
    
    missing = expected_segments - segment_names
    if missing:
        logger.warning(f"⚠️  Expected segments missing: {sorted(missing)}")
        # This is a warning, not an error, as some segments might be optional
    
    logger.info("✅ All memory segments are valid")
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ SUCCESS: Layout and builtins guard is working correctly!")
    logger.info("=" * 80)
    logger.info("DECISION: Guard prevents regression - layout and builtins are correct")
    logger.info("Next steps: Continue with other isolation steps")
    
    return True


def main():
    """Main entry point."""
    try:
        proof_path = find_latest_proof()
        success = verify_layout_guard(proof_path)
        sys.exit(0 if success else 1)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
