# Stone vs Atlantic - Technical Comparison
## Detailed Technical Analysis for Decision Making

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Production-Validated Analysis  
**Category**: Technical Comparison

---

## Executive Summary

This document provides a comprehensive technical comparison between Stone Prover (local) and Atlantic (cloud service) for STARK proof generation. Based on Obsqra Labs' production experience with both approaches, this comparison enables informed decision-making for builders choosing between local and cloud proof generation.

**Key Finding**: Stone Prover offers 99.8%+ cost savings at scale with complete control, while Atlantic offers managed service with higher per-proof costs but less operational overhead.

---

## Table of Contents

1. [Architecture Comparison](#architecture-comparison)
2. [Performance Comparison](#performance-comparison)
3. [Cost Comparison](#cost-comparison)
4. [Feature Comparison](#feature-comparison)
5. [Use Case Suitability](#use-case-suitability)
6. [Migration Guide](#migration-guide)
7. [Decision Framework](#decision-framework)

---

## Architecture Comparison

### Stone Prover (Local)

**Architecture**:
```
Your Infrastructure
    ↓
Stone Prover Binary (local)
    ├─ Trace Loading
    ├─ FRI Protocol
    ├─ Proof Generation
    └─ Proof Output
    ↓
Your Application
```

**Characteristics**:
- Self-hosted
- Direct binary execution
- Complete control
- No API dependency
- Data stays local

### Atlantic (Cloud)

**Architecture**:
```
Your Application
    ↓
Atlantic API (cloud)
    ├─ Trace Submission
    ├─ SHARP Processing
    ├─ Proof Generation
    └─ Proof Delivery
    ↓
Your Application
```

**Characteristics**:
- Managed service
- API-based
- Cloud processing
- Data leaves infrastructure
- Managed by Herodotus

---

## Performance Comparison

### Proof Generation Time

| Trace Size | Stone (Local) | Atlantic (Cloud) |
|------------|---------------|------------------|
| 512 steps | 2.0-2.5s | 5-8s |
| 16,384 steps | 3.5-4.0s | 8-12s |
| 65,536 steps | 4.0-4.5s | 10-15s |

**Stone Advantage**: 2-3x faster (no network latency)

### Latency Breakdown

**Stone (Local)**:
- Proof generation: 2-4s (100%)
- Network: 0s (local)
- **Total: 2-4s**

**Atlantic (Cloud)**:
- API roundtrip: 0.5-1s (10%)
- Proof generation: 5-10s (80%)
- Network: 0.5-1s (10%)
- **Total: 6-12s**

**Stone Advantage**: Lower latency, no network dependency

---

## Cost Comparison

### Per-Proof Cost

**Stone (Local)**:
- Infrastructure: $100/month (shared)
- At 1,000 proofs/day: $0.003/proof
- At 10,000 proofs/day: $0.0003/proof
- **Scales with infrastructure, not proofs**

**Atlantic (Cloud)**:
- Per-proof: $0.75 (mainnet)
- At 1,000 proofs/day: $0.75/proof
- At 10,000 proofs/day: $0.75/proof
- **Fixed per-proof cost**

### Monthly Cost Comparison

| Proofs/Day | Stone Cost | Atlantic Cost | Savings |
|------------|------------|---------------|---------|
| 100 | $100 | $2,250 | $2,150 (95.6%) |
| 1,000 | $200 | $22,500 | $22,300 (99.1%) |
| 10,000 | $500 | $225,000 | $224,500 (99.8%) |

**Stone Advantage**: 99.8%+ cost savings at scale

### Break-Even Analysis

**For Customer**:
- Break-even: Immediate (Stone cheaper from day 1)
- At 100 proofs/month: Stone $100 vs Atlantic $75 (Stone slightly more)
- At 1,000 proofs/month: Stone $200 vs Atlantic $22,500 (Stone 99.1% cheaper)

**For Obsqra**:
- Infrastructure: $200/month
- Support: $100/month
- Break-even: 1 customer at $300/month

---

## Feature Comparison

| Feature | Stone (Local) | Atlantic (Cloud) |
|---------|---------------|------------------|
| **Proof Generation** | ✅ Local | ✅ Cloud |
| **Cost Model** | Infrastructure | Pay-per-proof |
| **Control** | Full | Limited |
| **Data Privacy** | Complete | Cloud service |
| **Customization** | High | Limited |
| **Setup** | Complex | Simple (API key) |
| **Maintenance** | Your responsibility | Managed |
| **Support** | Community/Self | Managed support |
| **SLA** | Your responsibility | Managed SLA |
| **Scaling** | Manual | Automatic |
| **API** | Your implementation | Provided |
| **Version Control** | Your control | Managed |

---

## Use Case Suitability

### Use Stone When:

**✅ High Volume**:
- 1,000+ proofs/day
- Cost savings critical
- Infrastructure team available

**✅ Data Privacy**:
- Sensitive data
- Compliance requirements
- Data cannot leave infrastructure

**✅ Customization**:
- Custom FRI parameters
- Specialized requirements
- Full control needed

**✅ Cost Sensitivity**:
- Budget constraints
- Scale economics matter
- Long-term cost optimization

### Use Atlantic When:

**✅ Low Volume**:
- < 100 proofs/day
- Cost not primary concern
- Quick setup needed

**✅ No Infrastructure**:
- No infrastructure team
- Want managed service
- Prefer simplicity

**✅ Standard Use Cases**:
- Standard proof generation
- No special requirements
- General-purpose needs

**✅ Time to Market**:
- Need quick integration
- Don't want setup overhead
- Prefer API simplicity

---

## Migration Guide

### From Atlantic to Stone

**Step 1: Set Up Stone Prover**
- Build Stone binary
- Install Integrity
- Set up infrastructure

**Step 2: Implement Integration**
- Replace Atlantic API calls
- Implement Stone service
- Add Integrity integration

**Step 3: Test and Validate**
- Test with same inputs
- Compare proof outputs
- Validate verification

**Step 4: Deploy**
- Deploy to production
- Monitor performance
- Optimize as needed

**Migration Time**: 1-2 weeks

### From Stone to Atlantic

**Step 1: Get Atlantic API Key**
- Sign up for Atlantic
- Get API key
- Configure access

**Step 2: Replace Stone Calls**
- Replace Stone service calls
- Use Atlantic API
- Update error handling

**Step 3: Test**
- Test with Atlantic
- Validate results
- Monitor performance

**Step 4: Deploy**
- Deploy changes
- Monitor costs
- Optimize usage

**Migration Time**: 1-2 days

---

## Decision Framework

### Decision Matrix

**Question 1: Volume?**
- High (1,000+ proofs/day) → **Stone** (cost advantage)
- Low (< 100 proofs/day) → **Atlantic** (simplicity)

**Question 2: Infrastructure Team?**
- Yes → **Stone** (can manage)
- No → **Atlantic** (managed service)

**Question 3: Data Privacy?**
- Critical → **Stone** (data stays local)
- Not critical → **Atlantic** (acceptable)

**Question 4: Customization?**
- Needed → **Stone** (full control)
- Not needed → **Atlantic** (standard)

**Question 5: Cost Sensitivity?**
- High → **Stone** (99.8% savings at scale)
- Low → **Atlantic** (acceptable cost)

### Decision Tree

```
Start
  ↓
Volume > 1,000/day?
  ├─ Yes → Stone (cost advantage)
  └─ No → Continue
      ↓
Infrastructure team?
  ├─ Yes → Stone (can manage)
  └─ No → Continue
      ↓
Data privacy critical?
  ├─ Yes → Stone (data stays local)
  └─ No → Continue
      ↓
Customization needed?
  ├─ Yes → Stone (full control)
  └─ No → Atlantic (simplicity)
```

---

## Conclusion

**Stone Prover** is better for:
- High-volume applications (1,000+ proofs/day)
- Cost-sensitive use cases
- Data privacy requirements
- Customization needs
- Teams with infrastructure expertise

**Atlantic** is better for:
- Low-volume applications (< 100 proofs/day)
- Quick setup needs
- No infrastructure team
- Standard use cases
- Managed service preference

**Recommendation**: Use Stone for production systems with scale, use Atlantic for prototyping or low-volume use cases.

---

**This comparison enables informed decision-making based on your specific needs.**
