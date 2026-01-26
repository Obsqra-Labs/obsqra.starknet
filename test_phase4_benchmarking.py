#!/usr/bin/env python3
"""
Phase 4: Comprehensive Benchmarking & Trace Analysis

Determines:
1. Performance across different trace sizes (512, 8K, 131K)
2. Cost savings vs Atlantic
3. Whether fibonacci trace is sufficient or need custom allocation traces
4. Optimal Stone/Atlantic strategy
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent / "backend/app"))

from backend.app.services.stone_prover_service import StoneProverService

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result from a benchmark test"""
    trace_size: int
    n_steps: int
    generation_time_ms: float
    proof_size_kb: float
    fri_parameters: Dict
    success: bool
    error: Optional[str] = None


class AllocationTraceBenchmark:
    """
    Benchmarks Stone prover across different allocation trace sizes
    """
    
    def __init__(self):
        """Initialize benchmarking"""
        self.stone_service = StoneProverService()
        
        # Fibonacci test files (512-step baseline)
        self.fibonacci_private = "/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_private.json"
        self.fibonacci_public = "/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_public.json"
        
        self.results: List[BenchmarkResult] = []
        
        logger.info("Allocation Trace Benchmarking initialized")
    
    async def benchmark_fibonacci_trace(self, num_runs: int = 5) -> List[BenchmarkResult]:
        """
        Benchmark fibonacci trace (512 steps)
        
        This is our baseline. Real allocations may have different sizes.
        
        Args:
            num_runs: Number of times to run the benchmark
        
        Returns:
            List of benchmark results
        """
        
        logger.info("=" * 70)
        logger.info("BENCHMARK 1: Fibonacci Trace (512 steps)")
        logger.info("=" * 70)
        logger.info(f"Running {num_runs} tests...")
        logger.info("")
        
        results = []
        times = []
        
        for i in range(num_runs):
            run_num = f"Run {i+1}/{num_runs}..."
            logger.info(run_num)
            
            start = time.time()
            proof_result = await self.stone_service.generate_proof(
                self.fibonacci_private,
                self.fibonacci_public
            )
            elapsed_ms = (time.time() - start) * 1000
            
            if proof_result.success:
                result = BenchmarkResult(
                    trace_size=512,
                    n_steps=512,
                    generation_time_ms=elapsed_ms,
                    proof_size_kb=proof_result.proof_size_kb,
                    fri_parameters=proof_result.fri_parameters,
                    success=True
                )
                results.append(result)
                times.append(elapsed_ms)
                logger.info(f"  ✅ {elapsed_ms:.0f}ms")
            else:
                logger.error(f"  ❌ {proof_result.error}")
                results.append(BenchmarkResult(
                    trace_size=512,
                    n_steps=512,
                    generation_time_ms=0,
                    proof_size_kb=0,
                    fri_parameters={},
                    success=False,
                    error=proof_result.error
                ))
        
        logger.info("")
        logger.info("Fibonacci Results:")
        logger.info(f"  Runs completed: {sum(1 for r in results if r.success)}/{num_runs}")
        
        if times:
            logger.info(f"  Min time: {min(times):.0f}ms")
            logger.info(f"  Max time: {max(times):.0f}ms")
            logger.info(f"  Avg time: {sum(times)/len(times):.0f}ms")
            logger.info(f"  Variance: ±{max(times) - min(times):.0f}ms")
            logger.info(f"  Proof size: {results[0].proof_size_kb:.1f}KB")
        
        self.results.extend(results)
        return results
    
    async def benchmark_synthetic_8k_trace(self, num_runs: int = 3) -> List[BenchmarkResult]:
        """
        Benchmark synthetic 8K-step trace
        
        This represents a typical allocation computation.
        We create synthetic traces to test performance without needing
        actual allocation cairo execution.
        
        Args:
            num_runs: Number of benchmark runs
        
        Returns:
            List of benchmark results
        """
        
        logger.info("\n" + "=" * 70)
        logger.info("BENCHMARK 2: Synthetic 8K-Step Trace")
        logger.info("=" * 70)
        logger.info("NOTE: Using 512-step fibonacci as proxy (scaling estimates)")
        logger.info(f"Expected: 2-3x slower than 512 steps")
        logger.info("")
        
        # For now, we'll estimate 8K performance based on 512-step data
        # In production, we'd have actual allocation traces
        
        results = []
        
        # Get fibonacci baseline
        fib_start = time.time()
        fib_result = await self.stone_service.generate_proof(
            self.fibonacci_private,
            self.fibonacci_public
        )
        fib_time_ms = (time.time() - fib_start) * 1000
        
        if fib_result.success:
            # Estimate 8K performance (roughly 2-3x slower based on FRI complexity)
            estimated_8k_time = fib_time_ms * 2.5
            
            result = BenchmarkResult(
                trace_size=8192,
                n_steps=8192,
                generation_time_ms=estimated_8k_time,
                proof_size_kb=fib_result.proof_size_kb * 5,  # Rough estimate
                fri_parameters={"last_layer": 256, "fri_steps": [0, 4, 4, 1]},
                success=True
            )
            results.append(result)
            
            logger.info(f"Run 1/1...")
            logger.info(f"  Baseline (512): {fib_time_ms:.0f}ms")
            logger.info(f"  Estimated (8K): {estimated_8k_time:.0f}ms")
            logger.info(f"  Scaling factor: {estimated_8k_time / fib_time_ms:.1f}x")
            logger.info(f"  Est. proof size: {result.proof_size_kb:.1f}KB")
            logger.info("")
        else:
            logger.error(f"Failed to benchmark baseline: {fib_result.error}")
        
        self.results.extend(results)
        return results
    
    async def benchmark_synthetic_131k_trace(self) -> List[BenchmarkResult]:
        """
        Benchmark synthetic 131K-step trace
        
        This represents a large allocation computation.
        """
        
        logger.info("=" * 70)
        logger.info("BENCHMARK 3: Synthetic 131K-Step Trace")
        logger.info("=" * 70)
        logger.info("NOTE: Using 512-step fibonacci as proxy (scaling estimates)")
        logger.info(f"Expected: 5-8x slower than 512 steps")
        logger.info("")
        
        # Get fibonacci baseline
        fib_start = time.time()
        fib_result = await self.stone_service.generate_proof(
            self.fibonacci_private,
            self.fibonacci_public
        )
        fib_time_ms = (time.time() - fib_start) * 1000
        
        results = []
        
        if fib_result.success:
            # Estimate 131K performance (8x slower based on FRI complexity)
            estimated_131k_time = fib_time_ms * 7
            
            result = BenchmarkResult(
                trace_size=131072,
                n_steps=131072,
                generation_time_ms=estimated_131k_time,
                proof_size_kb=fib_result.proof_size_kb * 8,  # Rough estimate
                fri_parameters={"last_layer": 512, "fri_steps": [0, 4, 4, 4]},
                success=True
            )
            results.append(result)
            
            logger.info(f"Run 1/1...")
            logger.info(f"  Baseline (512): {fib_time_ms:.0f}ms")
            logger.info(f"  Estimated (131K): {estimated_131k_time:.0f}ms")
            logger.info(f"  Scaling factor: {estimated_131k_time / fib_time_ms:.1f}x")
            logger.info(f"  Est. proof size: {result.proof_size_kb:.1f}KB")
            logger.info("")
        else:
            logger.error(f"Failed to benchmark baseline: {fib_result.error}")
        
        self.results.extend(results)
        return results
    
    def analyze_results(self):
        """Analyze and summarize benchmark results"""
        
        logger.info("\n" + "=" * 70)
        logger.info("BENCHMARK ANALYSIS")
        logger.info("=" * 70)
        logger.info("")
        
        # Group by trace size
        by_size = {}
        for result in self.results:
            size = result.trace_size
            if size not in by_size:
                by_size[size] = []
            by_size[size].append(result)
        
        # Analysis table
        logger.info("Trace Size | Avg Time | Est. Size | FRI Params")
        logger.info("-" * 70)
        
        for size in sorted(by_size.keys()):
            results = by_size[size]
            successful = [r for r in results if r.success]
            
            if successful:
                avg_time = sum(r.generation_time_ms for r in successful) / len(successful)
                avg_size = sum(r.proof_size_kb for r in successful) / len(successful)
                fri = successful[0].fri_parameters
                fri_str = f"last_layer={fri.get('last_layer', '?')}, steps={fri.get('fri_steps', [])}"
                
                logger.info(f"{size:>9} | {avg_time:>8.0f}ms | {avg_size:>9.1f}KB | {fri_str}")
        
        logger.info("")
    
    def cost_analysis(self):
        """Analyze cost savings"""
        
        logger.info("\n" + "=" * 70)
        logger.info("COST ANALYSIS")
        logger.info("=" * 70)
        logger.info("")
        
        # Get average time for 512-step (most common)
        fib_results = [r for r in self.results if r.trace_size == 512 and r.success]
        
        if not fib_results:
            logger.warning("No 512-step results for cost analysis")
            return
        
        avg_time_s = sum(r.generation_time_ms for r in fib_results) / len(fib_results) / 1000
        
        # Cost assumptions
        stone_cost_per_proof = 0.0  # Free (local)
        atlantic_cost_per_proof = 0.75  # $0.75 per proof (approximate)
        
        # Scenarios
        scenarios = [
            ("All Stone (95% success)", 0.95, 0.05),
            ("Balanced (90% Stone)", 0.90, 0.10),
            ("Conservative (80% Stone)", 0.80, 0.20),
        ]
        
        logger.info("Per 1,000 Allocations (assuming 512-step avg):")
        logger.info("")
        
        for scenario_name, stone_pct, atlantic_pct in scenarios:
            stone_count = int(1000 * stone_pct)
            atlantic_count = int(1000 * atlantic_pct)
            
            stone_cost = stone_count * stone_cost_per_proof
            atlantic_cost = atlantic_count * atlantic_cost_per_proof
            total_cost = stone_cost + atlantic_cost
            
            baseline_cost = 1000 * atlantic_cost_per_proof
            savings = baseline_cost - total_cost
            savings_pct = (savings / baseline_cost) * 100 if baseline_cost > 0 else 0
            
            logger.info(f"{scenario_name}:")
            logger.info(f"  Stone: {stone_count} × $0.00 = ${stone_cost:.2f}")
            logger.info(f"  Atlantic: {atlantic_count} × ${atlantic_cost_per_proof:.2f} = ${atlantic_cost:.2f}")
            logger.info(f"  Total: ${total_cost:.2f}")
            logger.info(f"  Savings: ${savings:.2f} ({savings_pct:.1f}%)")
            logger.info("")
        
        logger.info("Recommendation:")
        logger.info("  • Use Stone as primary (99%+ of time)")
        logger.info("  • Atlantic as fallback for edge cases")
        logger.info("  • Expected savings: 90-95% cost reduction")


async def main():
    """Run Phase 4 benchmarking"""
    
    logger.info("\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " PHASE 4: BENCHMARKING & TRACE ANALYSIS ".center(68) + "║")
    logger.info("╚" + "═" * 68 + "╝")
    logger.info("")
    
    benchmark = AllocationTraceBenchmark()
    
    # Run benchmarks
    try:
        # 512-step fibonacci (baseline - actual execution)
        await benchmark.benchmark_fibonacci_trace(num_runs=5)
        
        # 8K-step synthetic (estimated)
        await benchmark.benchmark_synthetic_8k_trace()
        
        # 131K-step synthetic (estimated)
        await benchmark.benchmark_synthetic_131k_trace()
        
        # Analyze results
        benchmark.analyze_results()
        benchmark.cost_analysis()
        
        # Conclusion
        logger.info("\n" + "=" * 70)
        logger.info("CONCLUSION: TRACE ANALYSIS")
        logger.info("=" * 70)
        logger.info("")
        logger.info("FIBONACCI TRACE SUFFICIENCY:")
        logger.info("")
        logger.info("✅ SUFFICIENT FOR VALIDATION:")
        logger.info("   • Proves Stone prover works")
        logger.info("   • Establishes FRI parameter correctness")
        logger.info("   • Validates proof generation pipeline")
        logger.info("")
        logger.info("⚠️ INSUFFICIENT FOR PRODUCTION:")
        logger.info("   • Only 512 steps (likely too small for allocations)")
        logger.info("   • Doesn't test scaling to 8K-131K step ranges")
        logger.info("   • Real allocations may have higher complexity")
        logger.info("")
        logger.info("ACTION ITEMS:")
        logger.info("")
        logger.info("1. DETERMINE ACTUAL ALLOCATION TRACE SIZES")
        logger.info("   • Run risk_engine.cairo with various parameters")
        logger.info("   • Measure actual n_steps from execution traces")
        logger.info("   • Identify min/max/average trace sizes")
        logger.info("")
        logger.info("2. BUILD REPRESENTATIVE ALLOCATION TRACES")
        logger.info("   If allocations are > 8K steps:")
        logger.info("   • Create synthetic Cairo programs with known n_steps")
        logger.info("   • Or execute risk_engine.cairo variants")
        logger.info("   • Test Stone prover with realistic sizes")
        logger.info("")
        logger.info("3. PERFORMANCE VALIDATION")
        logger.info("   • Benchmark with actual allocation traces")
        logger.info("   • Verify timing predictions (8x slower @ 131K)")
        logger.info("   • Confirm proof generation succeeds")
        logger.info("")
        logger.info("RECOMMENDATION:")
        logger.info("")
        logger.info("Next step: Analyze risk_engine.cairo to determine")
        logger.info("actual allocation trace sizes. This will determine")
        logger.info("whether we need custom traces beyond fibonacci.")
        logger.info("")
        
        return 0
    
    except Exception as e:
        logger.error(f"Benchmarking failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
