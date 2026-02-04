#!/usr/bin/env python3
"""
Check Stone binary commit hash and compare with canonical example's prover version.

This verifies if our Stone binary matches the version used to generate the canonical example.
"""
import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_stone_commit() -> tuple[str, str]:
    """Get Stone binary commit hash and short description."""
    repo_root = Path(__file__).resolve().parent.parent
    stone_dir = repo_root / "stone-prover"
    
    if not stone_dir.exists():
        raise FileNotFoundError(f"Stone-prover directory not found at {stone_dir}")
    
    try:
        # Get latest commit
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=stone_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        short_desc = result.stdout.strip()
        
        # Get full commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=stone_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_hash = result.stdout.strip()
        
        return commit_hash, short_desc
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get Stone commit: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        raise
    except FileNotFoundError:
        logger.error("git command not found. Is git installed?")
        raise


def query_starknet_for_canonical_commit() -> Optional[str]:
    """
    Query ask_starknet tool for canonical example's Stone commit.
    
    This is a placeholder - actual implementation would use the MCP tool.
    """
    logger.info("Querying ask_starknet for canonical example's Stone commit...")
    logger.warning("⚠️  ask_starknet integration not yet implemented in this script")
    logger.info("Manual check: Look in integrity/examples/proofs/recursive/README.md or")
    logger.info("  integrity repository documentation for Stone commit information")
    return None


def main():
    """Main entry point."""
    try:
        logger.info("=" * 80)
        logger.info("STONE COMMIT VERSION CHECK")
        logger.info("=" * 80)
        
        # Get our Stone commit
        commit_hash, short_desc = get_stone_commit()
        logger.info(f"Our Stone commit hash: {commit_hash}")
        logger.info(f"Commit description: {short_desc}")
        
        # Try to get canonical commit (placeholder)
        canonical_commit = query_starknet_for_canonical_commit()
        
        if canonical_commit:
            logger.info(f"Canonical example's Stone commit: {canonical_commit}")
            
            if commit_hash == canonical_commit:
                logger.info("=" * 80)
                logger.info("✅ SUCCESS: Stone commits match!")
                logger.info("=" * 80)
                logger.info("DECISION: Stone version is correct")
                logger.info("Next steps: Check prover config or serialization")
                sys.exit(0)
            else:
                logger.error("=" * 80)
                logger.error("❌ MISMATCH: Stone commits differ!")
                logger.error("=" * 80)
                logger.error("DECISION: Stone commit mismatch (even if both are 'stone5')")
                logger.error("Next steps: Rebuild Stone with matching commit OR find matching verifier")
                sys.exit(1)
        else:
            logger.warning("=" * 80)
            logger.warning("⚠️  Could not determine canonical commit")
            logger.warning("=" * 80)
            logger.info("Manual verification needed:")
            logger.info("1. Check integrity/examples/proofs/recursive/README.md")
            logger.info("2. Check integrity repository documentation")
            logger.info("3. Check git history of integrity examples")
            logger.info(f"4. Compare our commit ({commit_hash[:8]}...) with canonical")
            sys.exit(0)
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
