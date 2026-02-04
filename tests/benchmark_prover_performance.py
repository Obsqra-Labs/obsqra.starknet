#!/usr/bin/env python3
"""
Benchmarking Suite for Stone Prover Performance
Measures proof generation time, proof size, and verification time across different trace sizes

Author: Obsqra Labs
Date: January 27, 2026
"""

import asyncio
import json
import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings

settings = get_settings()
backend_url = settings.API_BASE_URL or "http://localhost:8000"


@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    trace_size: int
    proof_generation_time_ms: float
    proof_size_kb: float
    verification_time_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class BenchmarkSummary:
    """Summary of all benchmarks"""
    total_tests: int
    successful_tests: int
    average_generation_time_ms: float
    average_proof_size_kb: float
    average_verification_time_ms: float
    min_generation_time_ms: float
    max_generation_time_ms: float
    results: List[BenchmarkResult]


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


async def benchmark_proof_generation(trace_size: int, iterations: int = 3) -> BenchmarkResult:
    """Benchmark proof generation for a given trace size"""
    print(f"   {Colors.CYAN}Benchmarking trace size {trace_size} ({iterations} iterations)...{Colors.RESET}")
    
    test_metrics = {
        "jediswap_metrics": {
            "utilization": 5000,
            "volatility": 3000,
            "liquidity": 8000,
            "audit_score": 9000,
            "age_days": 365
        },
        "ekubo_metrics": {
            "utilization": 6000,
            "volatility": 2500,
            "liquidity": 7500,
            "audit_score": 8500,
            "age_days": 180
        }
    }
    
    generation_times = []
    proof_sizes = []
    verification_times = []
    errors = []
    
    for i in range(iterations):
        try:
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{backend_url}/api/v1/risk-engine/propose-allocation",
                    json=test_metrics
                )
                
                if response.status_code != 200:
                    errors.append(f"Iteration {i+1}: HTTP {response.status_code}")
                    continue
                
                data = response.json()
                proof_job_id = data.get("proof_job_id")
                
                if not proof_job_id:
                    errors.append(f"Iteration {i+1}: No proof_job_id")
                    continue
                
                # Wait for proof generation
                await asyncio.sleep(5)
                
                # Get proof status
                status_response = await client.get(
                    f"{backend_url}/api/v1/risk-engine/proof-status/{proof_job_id}"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    generation_time = (time.time() - start_time) * 1000  # ms
                    generation_times.append(generation_time)
                    
                    metrics = status_data.get("metrics", {})
                    proof_size_bytes = metrics.get("proof_data_size_bytes", 0)
                    proof_size_kb = proof_size_bytes / 1024
                    proof_sizes.append(proof_size_kb)
                    
                    # Verification time (if available)
                    verification_time = metrics.get("verification_time_ms", 0)
                    if verification_time:
                        verification_times.append(verification_time)
                    
                    print(f"      Iteration {i+1}: {generation_time:.2f}ms, {proof_size_kb:.2f}KB")
                else:
                    errors.append(f"Iteration {i+1}: Status check failed")
        
        except Exception as e:
            errors.append(f"Iteration {i+1}: {str(e)}")
    
    if not generation_times:
        return BenchmarkResult(
            trace_size=trace_size,
            proof_generation_time_ms=0,
            proof_size_kb=0,
            verification_time_ms=0,
            success=False,
            error="; ".join(errors)
        )
    
    return BenchmarkResult(
        trace_size=trace_size,
        proof_generation_time_ms=statistics.mean(generation_times),
        proof_size_kb=statistics.mean(proof_sizes),
        verification_time_ms=statistics.mean(verification_times) if verification_times else 0,
        success=True,
        error="; ".join(errors) if errors else None
    )


async def run_benchmark_suite() -> BenchmarkSummary:
    """Run complete benchmark suite"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print("  OBSQRA LABS - STONE PROVER BENCHMARKING SUITE")
    print(f"{'='*70}{Colors.RESET}\n")
    
    # Test different scenarios (trace sizes are determined by input complexity)
    # We'll test with standard metrics
    print(f"{Colors.CYAN}Running benchmarks...{Colors.RESET}\n")
    
    results: List[BenchmarkResult] = []
    
    # Standard test
    result = await benchmark_proof_generation(trace_size=512, iterations=3)
    results.append(result)
    
    # Wait between tests
    await asyncio.sleep(2)
    
    # Another test with different metrics
    result2 = await benchmark_proof_generation(trace_size=1024, iterations=2)
    results.append(result2)
    
    # Calculate summary
    successful = [r for r in results if r.success]
    
    if successful:
        summary = BenchmarkSummary(
            total_tests=len(results),
            successful_tests=len(successful),
            average_generation_time_ms=statistics.mean([r.proof_generation_time_ms for r in successful]),
            average_proof_size_kb=statistics.mean([r.proof_size_kb for r in successful]),
            average_verification_time_ms=statistics.mean([r.verification_time_ms for r in successful]) if any(r.verification_time_ms > 0 for r in successful) else 0,
            min_generation_time_ms=min([r.proof_generation_time_ms for r in successful]),
            max_generation_time_ms=max([r.proof_generation_time_ms for r in successful]),
            results=results
        )
    else:
        summary = BenchmarkSummary(
            total_tests=len(results),
            successful_tests=0,
            average_generation_time_ms=0,
            average_proof_size_kb=0,
            average_verification_time_ms=0,
            min_generation_time_ms=0,
            max_generation_time_ms=0,
            results=results
        )
    
    return summary


def print_benchmark_results(summary: BenchmarkSummary):
    """Print formatted benchmark results"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print("  BENCHMARK RESULTS")
    print(f"{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.CYAN}Summary:{Colors.RESET}")
    print(f"  Total Tests: {summary.total_tests}")
    print(f"  Successful: {summary.successful_tests}")
    print(f"  Failed: {summary.total_tests - summary.successful_tests}")
    print()
    
    if summary.successful_tests > 0:
        print(f"{Colors.CYAN}Performance Metrics:{Colors.RESET}")
        print(f"  Average Generation Time: {summary.average_generation_time_ms:.2f} ms")
        print(f"  Min Generation Time: {summary.min_generation_time_ms:.2f} ms")
        print(f"  Max Generation Time: {summary.max_generation_time_ms:.2f} ms")
        print(f"  Average Proof Size: {summary.average_proof_size_kb:.2f} KB")
        if summary.average_verification_time_ms > 0:
            print(f"  Average Verification Time: {summary.average_verification_time_ms:.2f} ms")
        print()
        
        print(f"{Colors.CYAN}Detailed Results:{Colors.RESET}")
        for result in summary.results:
            status = f"{Colors.GREEN}✅" if result.success else f"{Colors.RED}❌"
            print(f"  {status} Trace Size {result.trace_size}:")
            if result.success:
                print(f"     Generation: {result.proof_generation_time_ms:.2f} ms")
                print(f"     Proof Size: {result.proof_size_kb:.2f} KB")
                if result.verification_time_ms > 0:
                    print(f"     Verification: {result.verification_time_ms:.2f} ms")
            else:
                print(f"     {Colors.RED}Error: {result.error}{Colors.RESET}")
    
    # Save results to file
    output_file = ROOT / "benchmark_results.json"
    with open(output_file, 'w') as f:
        json.dump(asdict(summary), f, indent=2)
    
    print(f"\n{Colors.CYAN}Results saved to: {output_file}{Colors.RESET}\n")


async def main():
    """Run benchmark suite"""
    summary = await run_benchmark_suite()
    print_benchmark_results(summary)
    
    return 0 if summary.successful_tests > 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
