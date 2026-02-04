# AIR Configuration Analysis

**Date**: 2026-01-27  
**Status**: Comparing AIR/proof parameters between our proof and Integrity example

---

## Investigation Focus

Since structure matches perfectly but OODS fails, the issue is likely in:
1. **AIR Configuration**: Stone's AIR parameters vs Integrity's expectations
2. **FRI Parameters**: FRI step list, degree bounds, queries
3. **Proof Parameters**: n_queries, security parameters
4. **Cairo Toolchain Version**: Version mismatch can cause AIR differences

---

## Key Parameters to Compare

### FRI Parameters
- `fri_step_list`: Step sizes for FRI layers
- `last_layer_degree_bound`: Degree bound for final FRI layer
- These affect how the composition polynomial is constructed

### STARK Parameters
- `n_queries`: Number of query points
- Security parameters
- These affect OODS point selection and validation

### Prover Config
- Stone version
- Hasher configuration
- Memory verification mode

---

## Status

Comparing proof parameters, FRI configuration, and STARK parameters...
