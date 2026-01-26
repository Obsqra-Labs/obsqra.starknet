#!/usr/bin/env python3
"""
Stone Prover FRI Parameter Testing Harness - Auto-adapting version

Automatically determines correct FRI parameters based on trace size,
then systematically tests valid combinations.
"""

import subprocess
import json
import time
import sys
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TestResult:
    last_layer: int
    fri_steps: List[int]
    exit_code: int
    elapsed_seconds: float
    success: bool
    stderr: str
    proof_size_mb: Optional[float] = None
    note: str = ""

class StoneFRITester:
    def __init__(self, private_input_file: str, params_file: str, prover_bin: str):
        self.private_input_file = Path(private_input_file)
        self.params_file = Path(params_file)
        self.prover_bin = Path(prover_bin)
        self.tmp_dir = Path("/tmp/stone_fri_tests")
        self.tmp_dir.mkdir(exist_ok=True)
        
        # For fibonacci example, we have a public input file
        self.public_input_file = Path("/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_public.json")
        self.prover_config_file = Path("/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_prover_config.json")
        
        # Validate inputs
        if not self.private_input_file.exists():
            raise FileNotFoundError(f"Private input file not found: {private_input_file}")
        if not self.params_file.exists():
            raise FileNotFoundError(f"Params file not found: {params_file}")
        if not self.prover_bin.exists():
            raise FileNotFoundError(f"Prover binary not found: {prover_bin}")
        if not self.public_input_file.exists():
            raise FileNotFoundError(f"Public input file not found: {self.public_input_file}")
        if not self.prover_config_file.exists():
            raise FileNotFoundError(f"Prover config file not found: {self.prover_config_file}")
        
        print(f"✓ Private input file: {self.private_input_file.name} ({self.private_input_file.stat().st_size / 1024:.1f} KB)")
        print(f"✓ Public input file: {self.public_input_file.name}")
        print(f"✓ Params file: {self.params_file.name}")
        print(f"✓ Prover config file: {self.prover_config_file.name}")
        print(f"✓ Prover binary: {self.prover_bin.name}")
        print(f"✓ Temp directory: {self.tmp_dir}")
        
        # Read n_steps from public input
        with open(self.public_input_file) as f:
            public_input = json.load(f)
        self.n_steps = public_input.get("n_steps")
        if not self.n_steps:
            raise ValueError(f"Could not find 'n_steps' in {self.public_input_file}")
        
        # Calculate target sum for FRI equation
        self.log_n_steps = (self.n_steps).bit_length() - 1
        if self.n_steps != (1 << self.log_n_steps):
            raise ValueError(f"n_steps must be a power of 2, got {self.n_steps}")
        
        self.target_sum = self.log_n_steps + 4
        print(f"\n📊 Trace Analysis:")
        print(f"   n_steps: {self.n_steps} = 2^{self.log_n_steps}")
        print(f"   FRI equation target: log2(last_layer) + Σ(fri_steps) = {self.target_sum}")
    
    def generate_test_cases(self) -> List[tuple]:
        """Generate valid FRI parameter combinations for this trace size."""
        test_cases = []
        
        # For 512 steps (log2=9, target=13), we need last_layer_log2 + fri_sum = 13
        # Valid combinations:
        if self.target_sum == 13:
            test_cases = [
                # last_layer=32 (log2=5, fri_sum=8)
                (32, [0, 4, 4], "baseline with leading 0"),
                (32, [2, 3, 3], "balanced"),
                (32, [1, 3, 4], "variant 1"),
                (32, [4, 2, 2], "variant 2"),
                
                # last_layer=64 (log2=6, fri_sum=7)
                (64, [0, 4, 3], "baseline"),
                (64, [1, 3, 3], "balanced"),
                (64, [2, 2, 3], "variant 1"),
                (64, [3, 2, 2], "variant 2"),
                
                # last_layer=128 (log2=7, fri_sum=6)
                (128, [0, 3, 3], "baseline"),
                (128, [1, 2, 3], "balanced"),
                (128, [2, 2, 2], "uniform"),
                
                # last_layer=256 (log2=8, fri_sum=5)
                (256, [0, 2, 3], "baseline"),
                (256, [1, 2, 2], "balanced"),
                
                # last_layer=512 (log2=9, fri_sum=4)
                (512, [0, 2, 2], "baseline"),
                (512, [1, 1, 2], "variant"),
                
                # last_layer=1024 (log2=10, fri_sum=3)
                (1024, [0, 1, 2], "baseline"),
                (1024, [1, 1, 1], "uniform"),
            ]
        else:
            # For other trace sizes, generate combinations programmatically
            print(f"⚠️  Target sum={self.target_sum} - generating combinations")
            for last_layer_log2 in range(5, self.target_sum):
                last_layer = 1 << last_layer_log2
                fri_sum = self.target_sum - last_layer_log2
                
                # Generate a few combinations for this last_layer
                if fri_sum <= 8:
                    test_cases.append((last_layer, [0] + [fri_sum // 2] * (fri_sum // 2 > 0) + ([fri_sum % 2] if fri_sum % 2 else []), "auto"))
        
        return test_cases
    
    def test_parameters(self, last_layer: int, fri_steps: List[int], test_num: int) -> TestResult:
        """Test a single FRI parameter combination."""
        
        # Verify equation before testing
        equation_sum = sum(fri_steps)
        last_layer_log2 = (last_layer).bit_length() - 1
        equation_valid = (last_layer_log2 + equation_sum) == self.target_sum
        equation_note = f"(log2({last_layer})={last_layer_log2} + sum({fri_steps})={equation_sum} = {last_layer_log2 + equation_sum}, target={self.target_sum})"
        
        if not equation_valid:
            return TestResult(
                last_layer=last_layer,
                fri_steps=fri_steps,
                exit_code=-1,
                elapsed_seconds=0,
                success=False,
                stderr="EQUATION INVALID",
                note=f"Skipped: {equation_note}"
            )
        
        # Create a modified parameter file with the new FRI parameters
        param_file_copy = self.tmp_dir / f"params_{test_num}.json"
        output_file = self.tmp_dir / f"proof_{test_num}.json"
        log_file = self.tmp_dir / f"test_{test_num}.log"
        
        # Load the base parameters and modify FRI settings
        with open(self.params_file, 'r') as f:
            params = json.load(f)
        
        # Update FRI parameters
        params["stark"]["fri"]["fri_step_list"] = fri_steps
        params["stark"]["fri"]["last_layer_degree_bound"] = last_layer
        
        # Write modified parameters to temp file
        with open(param_file_copy, 'w') as f:
            json.dump(params, f, indent=2)
        
        cmd = [
            str(self.prover_bin),
            "--parameter_file", str(param_file_copy),
            "--private_input_file", str(self.private_input_file),
            "--public_input_file", str(self.public_input_file),
            "--prover_config_file", str(self.prover_config_file),
            "--out_file", str(output_file),
            "--generate_annotations",
        ]
        
        print(f"\n{'='*70}")
        print(f"Test {test_num}: last_layer={last_layer}, fri_steps={fri_steps}")
        print(f"FRI equation: log2({last_layer})={last_layer_log2} + {fri_steps} = {last_layer_log2 + equation_sum} (target={self.target_sum}) ✓")
        print(f"{'='*70}")
        
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start
        
        # Save log
        with open(log_file, 'w') as f:
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"Exit code: {result.returncode}\n")
            f.write(f"Elapsed: {elapsed:.2f}s\n")
            f.write(f"\n--- STDOUT ---\n{result.stdout}\n")
            f.write(f"\n--- STDERR ---\n{result.stderr}\n")
        
        success = result.returncode == 0
        proof_size = None
        
        if success:
            try:
                proof_size = output_file.stat().st_size / (1024*1024)
                print(f"✅ SUCCESS in {elapsed:.1f}s")
                print(f"   Proof size: {proof_size:.1f} MB")
                print(f"   Log saved to: {log_file}")
                return TestResult(
                    last_layer=last_layer,
                    fri_steps=fri_steps,
                    exit_code=result.returncode,
                    elapsed_seconds=elapsed,
                    success=True,
                    stderr="",
                    proof_size_mb=proof_size
                )
            except Exception as e:
                print(f"⚠️  Proof generation succeeded but couldn't read file: {e}")
                return TestResult(
                    last_layer=last_layer,
                    fri_steps=fri_steps,
                    exit_code=result.returncode,
                    elapsed_seconds=elapsed,
                    success=False,
                    stderr=str(e)
                )
        else:
            # Extract relevant error lines
            stderr_lines = result.stderr.split('\n')
            relevant_errors = [line for line in stderr_lines if any(
                keyword in line.lower() for keyword in ['error', 'abort', 'signal', 'assert', 'memory', 'failed', 'exception']
            )]
            
            if not relevant_errors and result.stderr:
                relevant_errors = result.stderr.split('\n')[-5:]  # Last 5 lines
            
            error_msg = ' | '.join(relevant_errors[:3]) if relevant_errors else "Unknown error"
            
            print(f"❌ FAILED (exit code {result.returncode}) in {elapsed:.1f}s")
            print(f"   Error: {error_msg[:80]}")
            print(f"   Log saved to: {log_file}")
            
            return TestResult(
                last_layer=last_layer,
                fri_steps=fri_steps,
                exit_code=result.returncode,
                elapsed_seconds=elapsed,
                success=False,
                stderr=error_msg
            )
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all FRI parameter tests."""
        
        test_cases = self.generate_test_cases()
        
        print(f"\n{'#'*70}")
        print(f"# Running {len(test_cases)} FRI Parameter Tests")
        print(f"# For {self.n_steps}-step trace (target sum = {self.target_sum})")
        print(f"{'#'*70}\n")
        
        results = []
        for i, (last_layer, fri_steps, note) in enumerate(test_cases, 1):
            result = self.test_parameters(last_layer, fri_steps, i)
            result.note = note
            results.append(result)
        
        return results
    
    def print_summary(self, results: List[TestResult]) -> bool:
        """Print test summary and return True if any tests passed."""
        
        print(f"\n\n{'#'*70}")
        print(f"# SUMMARY")
        print(f"{'#'*70}\n")
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print(f"✅ Successful: {len(successful)}/{len(results)}")
        if successful:
            print()
            for r in successful:
                print(f"  ✓ last_layer={r.last_layer:4d}, fri_steps={r.fri_steps}, time={r.elapsed_seconds:.1f}s, size={r.proof_size_mb:.1f}MB - {r.note}")
        
        print(f"\n❌ Failed: {len(failed)}/{len(results)}")
        if failed:
            print()
            for r in failed:
                if r.exit_code == -1:
                    print(f"  ✗ last_layer={r.last_layer:4d}, fri_steps={r.fri_steps} - EQUATION INVALID")
                else:
                    error_short = r.stderr[:60].replace('\n', ' ')
                    print(f"  ✗ last_layer={r.last_layer:4d}, fri_steps={r.fri_steps}, exit={r.exit_code}, error='{error_short}...'")
            print()
        
        if failed:
            print("❌ FAILED PARAMETER SETS:")
            print("-" * 70)
            for r in failed:
                if r.exit_code == -1:
                    print(f"  last_layer={r.last_layer:4d}, fri_steps={r.fri_steps} - EQUATION INVALID")
                else:
                    print(f"  last_layer={r.last_layer:4d}, fri_steps={r.fri_steps}, exit_code={r.exit_code}, error='{r.stderr[:40]}...'")
            print()
        
        if not successful:
            print("🚨 NO WORKING PARAMETERS FOUND")
            print("Next steps:")
            print("  1. Check /tmp/stone_fri_tests/ for detailed logs")
            print("  2. Look for common error patterns")
            print("  3. Consider: memory constraints, layout mismatch, or version issue")
            print()
        
        return len(successful) > 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_stone_fri_auto.py <private_input_file> [params_file] [prover_bin]")
        print()
        print("Example:")
        print("  python3 test_stone_fri_auto.py /opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_private.json")
        print()
        print("Note: Automatically detects trace size and calculates correct FRI parameters")
        print()
        print("Defaults:")
        print("  params_file: /opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json")
        print("  prover_bin: /opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover")
        sys.exit(1)
    
    private_input_file = sys.argv[1]
    params_file = sys.argv[2] if len(sys.argv) > 2 else "/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json"
    prover_bin = sys.argv[3] if len(sys.argv) > 3 else "/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover"
    
    try:
        tester = StoneFRITester(private_input_file, params_file, prover_bin)
        results = tester.run_all_tests()
        success = tester.print_summary(results)
        
        # Save results as JSON for analysis
        results_json = {
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r.success]),
            "n_steps": tester.n_steps,
            "target_fri_sum": tester.target_sum,
            "results": [
                {
                    "last_layer": r.last_layer,
                    "fri_steps": r.fri_steps,
                    "success": r.success,
                    "elapsed_seconds": r.elapsed_seconds,
                    "proof_size_mb": r.proof_size_mb,
                    "exit_code": r.exit_code,
                    "note": r.note,
                }
                for r in results
            ]
        }
        
        results_file = Path("/tmp/stone_fri_tests/results.json")
        results_file.write_text(json.dumps(results_json, indent=2))
        print(f"📊 Results saved to: {results_file}\n")
        
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
