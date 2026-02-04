"""
Stone Prover Service for local STARK proof generation

Generates STARK proofs locally using the Stone CPU AIR prover.
This provides cost-free, independent proof generation without external dependencies.

Key features:
- Auto-detects trace size and calculates FRI parameters dynamically
- No external service calls needed
- Fast proof generation (~2-3 seconds for 512-step traces)
- Fallback to Atlantic available
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import hashlib
import math
import struct

from starknet_py.cairo.felt import encode_shortstring

logger = logging.getLogger(__name__)


@dataclass
class StoneProofResult:
    """Result of Stone proof generation"""
    success: bool
    proof_hash: str
    proof_data: Optional[bytes] = None
    proof_json: Optional[dict] = None
    trace_size: Optional[int] = None
    fri_parameters: Optional[Dict] = None
    generation_time_ms: Optional[float] = None
    proof_size_kb: Optional[float] = None
    error: Optional[str] = None
    verifier_config: Optional[dict] = None
    stark_proof: Optional[dict] = None


class StoneProverService:
    """
    Service for generating STARK proofs using Stone prover
    
    The Stone prover is a CPU AIR prover that generates STARK proofs
    for execution traces. It requires:
    1. Execution trace (binary format)
    2. Memory trace (binary format)
    3. Public input (JSON with n_steps, layout, memory_segments, etc.)
    4. FRI parameters (calculated based on trace size)
    """
    
    def __init__(self):
        """Initialize Stone Prover Service"""
        # Paths
        backend_dir = Path(__file__).parent.parent.parent
        self.stone_binary = Path(
            "/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover"
        )
        self.base_params_file = Path(
            "/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json"
        )
        self.prover_config_file = Path(
            "/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_prover_config.json"
        )
        
        # Validate binary exists
        if not self.stone_binary.exists():
            logger.error(f"Stone prover binary not found at {self.stone_binary}")
            raise FileNotFoundError(f"Stone prover binary not found")
        
        if not self.base_params_file.exists():
            logger.error(f"Base parameters file not found at {self.base_params_file}")
            raise FileNotFoundError(f"Base parameters file not found")
        
        logger.info(f"Stone Prover Service initialized")
        logger.info(f"  Binary: {self.stone_binary}")
        logger.info(f"  Params: {self.base_params_file}")
    
    def _calculate_fri_step_list(self, n_steps: int, last_layer_degree_bound: int) -> List[int]:
        """
        Calculate FRI step list based on trace size and fixed last_layer_degree_bound.
        
        FRI equation: log2(last_layer_degree_bound) + Σ(fri_steps) = log2(n_steps) + 4
        
        Args:
            n_steps: Number of execution steps
            last_layer_degree_bound: Fixed last layer degree bound from params file
        
        Returns:
            fri_step_list
        
        Raises:
            ValueError: If n_steps is not a power of 2
        """
        # Verify n_steps is a power of 2
        if n_steps & (n_steps - 1) != 0 or n_steps < 512:
            raise ValueError(f"n_steps must be a power of 2 and >= 512, got {n_steps}")
        
        log_n_steps = math.ceil(math.log2(n_steps))
        last_layer_log2 = math.ceil(math.log2(last_layer_degree_bound))
        target_sum = log_n_steps + 4
        sigma = target_sum - last_layer_log2
        if sigma < 0:
            raise ValueError(
                f"FRI equation impossible: log2(last_layer)={last_layer_log2} > target_sum={target_sum}"
            )
        q, r = divmod(sigma, 4)
        fri_steps = [0] + [4] * q + ([r] if r > 0 else [])
        
        # Verify equation
        equation_sum = sum(fri_steps)
        actual_sum = last_layer_log2 + equation_sum
        
        if actual_sum != target_sum:
            raise ValueError(
                f"FRI equation mismatch: log2({last_layer_degree_bound})={last_layer_log2} + {fri_steps}={equation_sum} "
                f"= {actual_sum}, expected {target_sum}"
            )
        
        logger.info(
            "FRI Parameters: last_layer=%s, fri_steps=%s",
            last_layer_degree_bound,
            fri_steps,
        )
        logger.info(
            "  Equation: log2(%s)=%s + %s = %s ✓",
            last_layer_degree_bound,
            last_layer_log2,
            equation_sum,
            actual_sum,
        )
        
        return fri_steps
    
    async def generate_proof(
        self,
        private_input_file: str,
        public_input_file: str,
        proof_output_file: Optional[str] = None,
        timeout_seconds: int = 300
    ) -> StoneProofResult:
        """
        Generate STARK proof using Stone prover
        
        Args:
            private_input_file: Path to private input JSON (trace paths)
            public_input_file: Path to public input JSON (n_steps, layout, etc.)
            proof_output_file: Where to save the proof JSON (optional)
            timeout_seconds: Timeout for proof generation
        
        Returns:
            StoneProofResult with proof data or error
        """
        import time
        start_time = time.time()
        
        try:
            # Validate input files
            private_path = Path(private_input_file)
            public_path = Path(public_input_file)
            
            if not private_path.exists():
                raise FileNotFoundError(f"Private input file not found: {private_input_file}")
            if not public_path.exists():
                raise FileNotFoundError(f"Public input file not found: {public_input_file}")
            
            # Read public input to get n_steps
            with open(public_path) as f:
                public_input = json.load(f)
            
            n_steps = public_input.get("n_steps")
            if not n_steps:
                raise ValueError(f"'n_steps' not found in public input")
            
            logger.info(f"Generating Stone proof for n_steps={n_steps}")
            
            # Load base parameters and modify FRI settings
            with open(self.base_params_file) as f:
                params = json.load(f)
            
            last_layer = params["stark"]["fri"]["last_layer_degree_bound"]
            fri_steps = self._calculate_fri_step_list(n_steps, last_layer)
            params["stark"]["fri"]["fri_step_list"] = fri_steps
            
            # HARD LOG: Dump Stone prover parameters before generation
            logger.info("=" * 80)
            logger.info("🔍 STONE PROVER - PARAMETERS")
            logger.info("=" * 80)
            logger.info(f"Base params file: {self.base_params_file}")
            logger.info(f"n_steps: {n_steps}")
            logger.info(f"FRI last_layer_degree_bound: {last_layer}")
            logger.info(f"FRI step_list: {fri_steps}")
            logger.info(f"FRI n_queries: {params['stark']['fri'].get('n_queries')}")
            logger.info(f"FRI log_n_cosets: {params['stark'].get('log_n_cosets')}")
            logger.info(f"FRI proof_of_work_bits: {params['stark']['fri'].get('proof_of_work_bits')}")
            logger.info(f"Channel hash: {params.get('channel_hash')}")
            logger.info(f"Commitment hash: {params.get('commitment_hash')}")
            logger.info(f"Pow hash: {params.get('pow_hash')}")
            logger.info(f"n_verifier_friendly_commitment_layers: {params.get('n_verifier_friendly_commitment_layers')}")
            logger.info(f"Verifier friendly channel updates: {params.get('verifier_friendly_channel_updates')}")
            logger.info(f"Verifier friendly commitment hash: {params.get('verifier_friendly_commitment_hash')}")
            logger.info("=" * 80)
            
            # Create temporary parameter file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                param_file = f.name
                json.dump(params, f)
            
            # Determine output file
            if proof_output_file is None:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    proof_output_file = f.name
            
            # Build command
            cmd = [
                str(self.stone_binary),
                "--parameter_file", param_file,
                "--private_input_file", str(private_path),
                "--public_input_file", str(public_path),
                "--prover_config_file", str(self.prover_config_file),
                "--out_file", proof_output_file,
                "--generate_annotations",
            ]
            
            logger.info(f"Running Stone prover...")
            logger.debug(f"Command: {' '.join(cmd[-6:])}")
            
            # Run prover
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Check result
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                logger.error(f"Stone prover failed: {error_msg[:200]}")
                return StoneProofResult(
                    success=False,
                    proof_hash="",
                    error=error_msg[:500],
                    generation_time_ms=elapsed_ms,
                    fri_parameters={"last_layer": last_layer, "fri_steps": fri_steps}
                )
            
            # Read generated proof
            with open(proof_output_file, 'rb') as f:
                proof_data = f.read()
            
            # Also read as JSON for analysis
            with open(proof_output_file) as f:
                proof_json = json.load(f)
            
            # Calculate proof hash
            proof_hash = hashlib.sha256(proof_data).hexdigest()
            proof_size_kb = len(proof_data) / 1024
            
            logger.info(f"✅ Stone proof generated successfully")
            logger.info(f"   Hash: {proof_hash[:16]}...")
            logger.info(f"   Size: {proof_size_kb:.1f} KB")
            logger.info(f"   Time: {elapsed_ms:.0f} ms")
            
            # Clean up temp param file
            try:
                Path(param_file).unlink()
            except:
                pass
            
            return StoneProofResult(
                success=True,
                proof_hash=proof_hash,
                proof_data=proof_data,
                proof_json=proof_json,
                trace_size=n_steps,
                fri_parameters={"last_layer": last_layer, "fri_steps": fri_steps},
                generation_time_ms=elapsed_ms,
                proof_size_kb=proof_size_kb
            )
        
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Error in Stone proof generation: {str(e)}", exc_info=True)
            return StoneProofResult(
                success=False,
                proof_hash="",
                error=str(e),
                generation_time_ms=elapsed_ms
            )
    
    async def generate_proof_from_trace_files(
        self,
        trace_file: str,
        memory_file: str,
        public_input_file: str,
        proof_output_file: Optional[str] = None
    ) -> StoneProofResult:
        """
        Generate proof from raw trace and memory files
        
        This is a convenience method that creates the private_input_file
        from the raw trace and memory paths.
        
        Args:
            trace_file: Path to execution trace binary
            memory_file: Path to memory trace binary
            public_input_file: Path to public input JSON
            proof_output_file: Where to save proof (optional)
        
        Returns:
            StoneProofResult
        """
        # Create private input
        private_input = {
            "trace_path": str(Path(trace_file).absolute()),
            "memory_path": str(Path(memory_file).absolute()),
            "pedersen": [],
            "range_check": [],
            "ecdsa": []
        }
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            private_input_file = f.name
            json.dump(private_input, f)
        
        try:
            return await self.generate_proof(
                private_input_file,
                public_input_file,
                proof_output_file
            )
        finally:
            # Clean up temp file
            try:
                Path(private_input_file).unlink()
            except:
                pass
