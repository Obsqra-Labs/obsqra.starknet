"""
Cairo Trace Generator v2

Generates execution traces from Cairo programs and allocation data.
This bridges allocation computation to STARK proof generation.
"""

import asyncio
import json
import logging
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class TraceGenerationResult:
    """Result of trace generation"""
    success: bool
    n_steps: Optional[int] = None
    trace_file: Optional[str] = None
    memory_file: Optional[str] = None
    public_input_file: Optional[str] = None
    private_input_file: Optional[str] = None
    generation_time_ms: Optional[float] = None
    error: Optional[str] = None


class CairoTraceGenerator:
    """
    Generates execution traces from Cairo programs
    
    Process:
    1. Execute Cairo program with inputs via cairo-run
    2. Extract execution trace from output
    3. Generate public/private input JSON for Stone prover
    """
    
    def __init__(self):
        """Initialize Cairo Trace Generator"""
        self.cairo_runner = "cairo-run"
        logger.info("Cairo Trace Generator initialized")
    
    async def generate_trace(
        self,
        cairo_program: str,
        inputs: Dict,
        output_dir: Optional[str] = None
    ) -> TraceGenerationResult:
        """
        Generate execution trace from Cairo program
        
        Args:
            cairo_program: Path to Cairo program
            inputs: Input data for program
            output_dir: Directory for trace output (temp if None)
        
        Returns:
            TraceGenerationResult with trace files and metadata
        """
        logger.info(f"Generating trace for {cairo_program}")
        
        start_time = time.time()
        
        try:
            # Validate program exists
            if not Path(cairo_program).exists():
                return TraceGenerationResult(
                    success=False,
                    error=f"Cairo program not found: {cairo_program}"
                )
            
            # Create output directory
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="cairo_trace_")
            else:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            output_path = Path(output_dir)
            trace_file = output_path / "trace.json"
            memory_file = output_path / "memory.json"
            
            # Create input JSON file
            input_file = output_path / "input.json"
            with open(input_file, "w") as f:
                json.dump(inputs, f)
            
            # Build cairo-run command
            # cairo-run generates execution trace
            cmd = [
                "cairo-run",
                "--single_file",
                cairo_program,
                "--trace_file", str(trace_file),
                "--memory_file", str(memory_file),
                "--layout=small"
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            # Execute cairo-run
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                logger.error(f"cairo-run failed: {error_msg}")
                return TraceGenerationResult(
                    success=False,
                    error=f"cairo-run failed: {error_msg}"
                )
            
            # Parse trace to extract n_steps
            if not trace_file.exists():
                return TraceGenerationResult(
                    success=False,
                    error=f"Trace file not created: {trace_file}"
                )
            
            with open(trace_file, "r") as f:
                trace_data = json.load(f)
            
            # n_steps = number of trace entries
            # Each entry represents one execution step
            n_steps = len(trace_data) if isinstance(trace_data, list) else 1
            
            # Ensure n_steps is a power of 2
            import math
            if n_steps > 0:
                # Round up to next power of 2
                n_steps_log = math.ceil(math.log2(n_steps))
                n_steps_rounded = 2 ** n_steps_log
            else:
                n_steps_rounded = 512
            
            # Create public_input JSON for Stone prover
            public_input = {
                "n_steps": n_steps_rounded,
                "layout": "small",
                "memory_segments": [
                    {"begin_addr": 0, "size": 0}
                ]
            }
            
            public_input_file = output_path / "public_input.json"
            with open(public_input_file, "w") as f:
                json.dump(public_input, f)
            
            # Create private_input JSON (points to trace files)
            private_input = {
                "trace_file": str(trace_file),
                "memory_file": str(memory_file)
            }
            
            private_input_file = output_path / "private_input.json"
            with open(private_input_file, "w") as f:
                json.dump(private_input, f)
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            logger.info(f"✅ Trace generated successfully")
            logger.info(f"   Steps: {n_steps} (rounded to {n_steps_rounded})")
            logger.info(f"   Time: {elapsed_ms:.0f}ms")
            
            return TraceGenerationResult(
                success=True,
                n_steps=n_steps_rounded,
                trace_file=str(trace_file),
                memory_file=str(memory_file),
                public_input_file=str(public_input_file),
                private_input_file=str(private_input_file),
                generation_time_ms=elapsed_ms
            )
        
        except subprocess.TimeoutExpired:
            return TraceGenerationResult(
                success=False,
                error="cairo-run timeout (>60 seconds)"
            )
        except Exception as e:
            logger.error(f"Trace generation error: {str(e)}", exc_info=True)
            return TraceGenerationResult(
                success=False,
                error=str(e)
            )


class AllocationToTraceAdapter:
    """
    Converts allocation computation to Cairo execution
    
    Process:
    1. Convert allocation parameters to Cairo inputs
    2. Execute risk_engine.cairo with inputs
    3. Generate proof inputs from execution trace
    """
    
    def __init__(self, trace_generator: Optional[CairoTraceGenerator] = None):
        """Initialize adapter"""
        self.trace_generator = trace_generator or CairoTraceGenerator()
        self.risk_engine_file = Path("/opt/obsqra.starknet/contracts/src/risk_engine.cairo")
        logger.info("AllocationToTraceAdapter initialized")
    
    async def allocation_to_trace(
        self,
        allocation_id: str,
        jediswap_risk: int,
        ekubo_risk: int,
        jediswap_apy: int,
        ekubo_apy: int,
        jediswap_pct: int,
        ekubo_pct: int
    ) -> TraceGenerationResult:
        """
        Convert allocation to execution trace
        
        Args:
            allocation_id: Unique allocation identifier
            jediswap_risk: Risk score (0-100)
            ekubo_risk: Risk score (0-100)
            jediswap_apy: APY in basis points
            ekubo_apy: APY in basis points
            jediswap_pct: Allocation percentage (0-100)
            ekubo_pct: Allocation percentage (0-100)
        
        Returns:
            TraceGenerationResult with proof input files
        """
        
        logger.info(f"Converting allocation {allocation_id} to trace")
        logger.info(f"  Allocation: {jediswap_pct}% Jediswap / {ekubo_pct}% Ekubo")
        
        # Prepare Cairo inputs from allocation parameters
        inputs = {
            "jediswap_risk": jediswap_risk,
            "ekubo_risk": ekubo_risk,
            "jediswap_apy": jediswap_apy,
            "ekubo_apy": ekubo_apy,
            "jediswap_pct": jediswap_pct,
            "ekubo_pct": ekubo_pct
        }
        
        # Verify risk_engine exists
        if not self.risk_engine_file.exists():
            logger.error(f"risk_engine.cairo not found: {self.risk_engine_file}")
            return TraceGenerationResult(
                success=False,
                error=f"risk_engine.cairo not found"
            )
        
        # Generate trace from risk_engine.cairo
        result = await self.trace_generator.generate_trace(
            str(self.risk_engine_file),
            inputs
        )
        
        return result
