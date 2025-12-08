"""Models package - imports from both models.py and models/ directory"""

# Import from original models.py (for User, etc.)
import sys
from pathlib import Path

# Add parent directory to path to import from models.py
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import from models.py
try:
    from models import *
except ImportError:
    pass

# Import from models directory
from app.models.proof_job import ProofJob, ProofStatus

__all__ = ["ProofJob", "ProofStatus"]

