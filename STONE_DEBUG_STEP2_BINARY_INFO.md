# Phase 1.2: Stone Binary & Git History Analysis

## Binary Information

**Path:** `/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover`

**Details:**
- Type: ELF 64-bit LSB executable, x86-64
- Size: 20 MB
- Built: Dec 12, 2025 at 20:10
- Status: Not stripped (symbols included, good for debugging)
- Dynamic linking: Yes (depends on libc and system libs)

**Binary is ready to use.**

---

## Git Repository Status

**Repository:** `/opt/obsqra.starknet/stone-prover`

**Current State:**
- HEAD: commit `1414a54` ("Stone v3.")
- Branch: main
- Remote: up-to-date with origin/main

**Latest Commits:**
```
1414a54 Stone v3.
ba85f37 Update README.md
b26d07a Merge pull request #27 from Lawliet-Chan/fix_fib
4b1585b Update README.md
238431f Merge pull request #28 from FilipLaurentiu/filip/remove_file_extension
9f5505a Merge pull request #18 from xiaoxianBoy/fix-typos
```

**Version Tags:**
- No semantic version tags (v1.0, v2.0, etc.)
- Commits reference "Stone v3." but no git tags found
- This is a development repository

---

## Signal 6 & FRI Issue Investigation

**Searched for:**
- FRI-related commits: None found with "FRI" in commit message
- Signal-related commits: None found with "Signal" or "abort"
- Parameter-related commits: None found with "parameter"

**Interpretation:**
The Signal 6 issue you hit in December is likely NOT documented in this repository. This could mean:
1. It's a known issue with specific parameter combinations (not yet fixed)
2. It's an edge case for 131K+ step traces (rare)
3. It's related to your specific Cairo program (risk_engine.cairo)

---

## Fixes Since Your Build (Dec 12)

**Commits since Dec 12:** None (repository was at `1414a54` before and after)

**Implication:**
- No new fixes have been pushed since your build
- Your binary is up-to-date with latest main branch
- No newer version to upgrade to

---

## Possible Root Causes

### 1. **FRI Parameter Mismatch** (Most likely)
Signal 6 typically indicates an assertion failure in the prover. When you supply invalid FRI parameters (that don't satisfy the equation), cpu_air_prover asserts and aborts.

**Solution:** Test all valid parameter combinations systematically (Phase 2).

### 2. **Memory Constraints**
Larger last_layer_degree_bound + large trace = more RAM needed.

**Quick test:**
```bash
free -h  # Check available RAM
du -h /path/to/execution_trace.json  # Check trace size
```

### 3. **Layout Mismatch**
If trace was generated with one layout (e.g., "small") but prover expects different layout (e.g., "recursive").

**Check:** Both cairo-run and cpu_air_prover need same layout.

### 4. **Missing --generate_annotations Flag**
As documented, Stone proofs MUST be generated with `--generate_annotations` for serialization to work.

**Check:** Ensure this flag is used.

---

## Next Steps (Phase 1.3)

1. Create test harness with all valid FRI combinations
2. Run cpu_air_prover with full execution trace and capture stderr
3. Identify which parameter sets work vs which cause Signal 6
4. If Signal 6 persists across all valid parameters, investigate deeper

