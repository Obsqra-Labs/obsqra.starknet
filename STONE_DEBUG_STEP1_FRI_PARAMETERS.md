# Phase 1.1: FRI Parameter Analysis

## The Equation

For a STARK proof with `n_steps` execution steps:

```
log2(last_layer_degree_bound) + Σ(fri_step_list) = log2(n_steps) + 4
```

For our full Risk Engine trace: **131,072 steps = 2^17**

```
log2(131072) = 17
Target sum = 17 + 4 = 21
```

---

## Valid Parameter Combinations for Sum = 21

The equation means: `log2(last_layer_degree_bound) + Σ(fri_steps) = 21`

Rearranged: `Σ(fri_steps) = 21 - log2(last_layer_degree_bound)`

### Option 1: last_layer = 32 (log2 = 5)
```
fri_steps must sum to: 21 - 5 = 16
Valid combinations:
  - [4, 4, 4, 4] ✓
  - [3, 4, 4, 5] ✓
  - [4, 4, 3, 5] ✓
  - [2, 4, 5, 5] ✓
  - [3, 3, 5, 5] ✓
```

### Option 2: last_layer = 64 (log2 = 6)
```
fri_steps must sum to: 21 - 6 = 15
Valid combinations:
  - [3, 4, 4, 4] ✓
  - [4, 4, 4, 3] ✓
  - [4, 3, 4, 4] ✓
  - [3, 3, 4, 5] ✓
  - [2, 4, 4, 5] ✓
```

### Option 3: last_layer = 128 (log2 = 7)
```
fri_steps must sum to: 21 - 7 = 14
Valid combinations:
  - [3, 3, 4, 4] ✓
  - [4, 4, 3, 3] ✓
  - [2, 4, 4, 4] ✓
  - [3, 3, 3, 5] ✓
  - [2, 3, 4, 5] ✓
```

### Option 4: last_layer = 256 (log2 = 8)
```
fri_steps must sum to: 21 - 8 = 13
Valid combinations:
  - [3, 3, 3, 4] ✓
  - [4, 3, 3, 3] ✓
  - [2, 3, 4, 4] ✓
  - [3, 3, 3, 2, 2] ✓ (5 FRI layers)
  - [2, 2, 3, 3, 3] ✓ (5 FRI layers)
```

### Option 5: last_layer = 512 (log2 = 9)
```
fri_steps must sum to: 21 - 9 = 12
Valid combinations:
  - [3, 3, 3, 3] ✓
  - [4, 3, 3, 2] ✓
  - [2, 2, 4, 4] ✓
  - [2, 3, 3, 4] ✓
  - [2, 2, 2, 3, 3] ✓ (5 FRI layers)
```

### Option 6: last_layer = 1024 (log2 = 10)
```
fri_steps must sum to: 21 - 10 = 11
Valid combinations:
  - [3, 3, 3, 2] ✓
  - [2, 3, 3, 3] ✓
  - [2, 2, 3, 4] ✓
  - [2, 2, 2, 2, 3] ✓ (5 FRI layers)
```

---

## Trade-offs

### Smaller last_layer (32, 64)
- **Pros:** Lower memory usage during proof generation
- **Cons:** More FRI folding steps (4 or 5 layers), longer computation

### Larger last_layer (256, 512, 1024)
- **Pros:** Fewer FRI layers, faster proof generation
- **Cons:** Higher memory requirements

### Recommended Test Order
1. Start with **last_layer=128, fri=[3,3,4,4]** (balanced)
2. If memory issue → try last_layer=64, fri=[3,4,4,4]
3. If slow → try last_layer=512, fri=[3,3,3,3]
4. If still failing → debug deeper (may not be FRI params)

---

## Implementation Note

When we pass these to cpu_air_prover, the format will be:
```bash
--last_layer_degree_bound <number>
--fri_step_list [<step1>,<step2>,<step3>,<step4>]
```

Example:
```bash
/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover \
  --input_file trace.json \
  --output_file proof.json \
  --parameter_file cpu_air_params.json \
  --last_layer_degree_bound 128 \
  --fri_step_list [3,3,4,4]
```

---

## Next: Test these combinations in Phase 2

