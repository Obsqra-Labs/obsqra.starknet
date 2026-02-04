# Developer FAQ - Stone Prover Integration
## Frequently Asked Questions for Builders

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Living Document  
**Category**: Developer Resources

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Integration Questions](#integration-questions)
3. [Performance Questions](#performance-questions)
4. [Troubleshooting Questions](#troubleshooting-questions)
5. [Best Practices Questions](#best-practices-questions)
6. [Cost Questions](#cost-questions)

---

## General Questions

### Q: What is Stone Prover?

**A**: Stone Prover is StarkWare's open-source STARK prover that generates cryptographic proofs for Cairo program execution. It enables local proof generation without relying on cloud services.

**Key Points**:
- Open source (Apache 2.0)
- Battle-tested (proved $1 trillion in transactions)
- CPU AIR prover
- Enables zero per-proof cost

### Q: Why use Stone Prover instead of Atlantic?

**A**: Stone Prover offers zero per-proof cost vs Atlantic's $0.75/proof. At scale (1,000+ proofs/day), this results in 99.8%+ cost savings.

**Comparison**:
- Atlantic: $0.75/proof (pay-per-proof)
- Stone: $0/proof (infrastructure only)
- At 10K proofs/day: $225,000/month vs $500/month

### Q: What is the "Signal 6" problem?

**A**: "Signal 6" (SIGABRT) occurs when FRI parameters don't match trace size. Fixed FRI parameters only work for one trace size. Dynamic FRI calculation solves this.

**Solution**: Use dynamic FRI calculation based on trace size. See `DYNAMIC_FRI_ALGORITHM_DETAILED.md`.

---

## Integration Questions

### Q: How do I integrate Stone Prover into my application?

**A**: See `COMPLETE_INTEGRATION_TUTORIAL.md` for step-by-step guide. Basic steps:

1. Build Stone Prover binary
2. Install Integrity proof_serializer
3. Implement dynamic FRI calculation
4. Integrate Stone service
5. Integrate Integrity service
6. Test and deploy

### Q: What are the prerequisites?

**A**:
- Linux/macOS (Windows via WSL2)
- Python 3.11+
- Bazel (for building Stone)
- Rust (for building proof_serializer)
- 8GB+ RAM, 50GB+ disk space

### Q: How long does integration take?

**A**:
- Basic integration: 2-4 hours
- Production integration: 1-2 days
- Full optimization: 1 week

See `QUICK_START_GUIDE.md` for 30-minute setup.

---

## Performance Questions

### Q: How fast is proof generation?

**A**: 2-4 seconds for typical proofs (512-65K steps).

**By Trace Size**:
- 512 steps: 2.0-2.5 seconds
- 16,384 steps: 3.5-4.0 seconds
- 65,536 steps: 4.0-4.5 seconds

See `STONE_PROVER_PERFORMANCE_BENCHMARKS.md` for detailed data.

### Q: What affects proof generation time?

**A**: Primary factor is trace size (n_steps). Larger traces take longer, but scaling is logarithmic (efficient).

**Factors**:
- Trace size: Primary (logarithmic scaling)
- System resources: CPU, RAM
- FRI parameters: Minor impact

### Q: Can I generate proofs in parallel?

**A**: Yes! Stone Prover can generate multiple proofs in parallel. Limit concurrency based on available CPU cores and memory.

**Example**:
```python
# Generate 4 proofs in parallel (4-core CPU)
results = await asyncio.gather(*[
    stone_service.generate_proof(...) for _ in range(4)
])
```

---

## Troubleshooting Questions

### Q: I get "Signal 6" error. What's wrong?

**A**: FRI parameter mismatch. Use dynamic FRI calculation instead of fixed parameters.

**Solution**:
```python
# ❌ WRONG: Fixed parameters
fri_steps = [0, 4, 4, 3]  # Only works for one size

# ✅ CORRECT: Dynamic calculation
fri_steps = calculate_fri_step_list(n_steps, last_layer_degree_bound)
```

See `DYNAMIC_FRI_ALGORITHM_DETAILED.md` for complete algorithm.

### Q: I get "Invalid OODS" error. What's wrong?

**A**: Stone version mismatch with Integrity verifier setting.

**Solution**:
- Stone v3 → Use `stone6` verifier
- Stone v2 → Use `stone5` verifier (hypothesis)

**Check**:
```python
# Get Stone version
stone_version = get_stone_version()  # e.g., "1414a545..."

# Set Integrity verifier accordingly
if stone_version.startswith("1414a545"):  # Stone v3
    integrity_stone_version = "stone6"
```

See `STONE_VERSION_COMPATIBILITY_MATRIX.md` for details.

### Q: I get "VERIFIER_NOT_FOUND" error. What's wrong?

**A**: Verifier not registered in FactRegistry.

**Solution**: Use public FactRegistry (has all verifiers registered):
```python
PUBLIC_FACT_REGISTRY = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
```

See `INTEGRITY_FACTREGISTRY_INTEGRATION_GUIDE.md` for details.

### Q: Proof generation times out. What should I do?

**A**: Increase timeout or optimize trace size.

**Solutions**:
1. Increase timeout for large proofs:
```python
result = subprocess.run(cmd, timeout=600)  # 10 minutes
```

2. Optimize trace size (reduce n_steps)

3. Check system resources (CPU, RAM)

---

## Best Practices Questions

### Q: Should I use fixed or dynamic FRI parameters?

**A**: Always use dynamic FRI calculation. Fixed parameters only work for one trace size and cause "Signal 6" crashes for other sizes.

**Why**: Trace sizes vary in production. Dynamic calculation adapts to any size.

### Q: Should I use public or custom FactRegistry?

**A**: Use public FactRegistry (recommended). Custom FactRegistry requires verifier registration and is only needed for specific use cases.

**Public FactRegistry**: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`

### Q: How do I optimize proof generation performance?

**A**:
1. Minimize trace size (reduce n_steps)
2. Generate proofs in parallel
3. Use faster RPC endpoints
4. Cache results (if deterministic)

See `COST_OPTIMIZATION_GUIDE.md` for detailed strategies.

### Q: Should I verify proofs before or after execution?

**A**: Verify before execution (pre-execution gate). This ensures no execution without valid proof.

**Implementation**:
```cairo
// In contract
let proofs_valid = verify_proofs(...);
assert(proofs_valid, 0);  // Revert if not verified
// Only then execute
```

---

## Cost Questions

### Q: How much does Stone Prover cost?

**A**: $0 per-proof (runs locally). Only infrastructure cost.

**Infrastructure Cost**:
- Server: $50-100/month
- At 1,000 proofs/day: $0.003/proof
- At 10,000 proofs/day: $0.0003/proof

**vs Atlantic**: 99.8%+ cost savings

### Q: What's the break-even point vs Atlantic?

**A**: Immediate. Even at 100 proofs/month, Stone is cheaper.

**Example**:
- Atlantic: 100 proofs × $0.75 = $75/month
- Stone: Infrastructure $100/month
- **Break-even: ~133 proofs/month**

At 1,000+ proofs/month, Stone is significantly cheaper.

### Q: How do I estimate infrastructure costs?

**A**: 
- Base infrastructure: $100/month
- Per customer (shared): $10-50/month
- Scales sub-linearly with customers

**At Scale**:
- 10 customers: $200/month total
- 20 customers: $380/month total
- 50 customers: $580/month total

See `REVENUE_MODEL_AND_PRICING.md` for detailed cost analysis.

---

## Additional Resources

**Documentation**:
- `QUICK_START_GUIDE.md` - 30-minute setup
- `COMPLETE_INTEGRATION_TUTORIAL.md` - Full integration
- `TROUBLESHOOTING_GUIDE.md` - Comprehensive troubleshooting

**Technical**:
- `STONE_PROVER_INTEGRATION_DEEP_DIVE.md` - Complete technical guide
- `DYNAMIC_FRI_ALGORITHM_DETAILED.md` - FRI algorithm details
- `INTEGRITY_FACTREGISTRY_INTEGRATION_GUIDE.md` - Integrity guide

**Performance**:
- `STONE_PROVER_PERFORMANCE_BENCHMARKS.md` - Performance data
- `END_TO_END_LATENCY_ANALYSIS.md` - Latency breakdown

**Support**:
- GitHub Issues: [Your repo]
- Discord: [Your community]
- Email: [Your support email]

---

**This FAQ is a living document. Submit questions via GitHub Issues.**
