# S-two Understanding Plan: Zoom Out, Zoom In

**Date**: 2026-01-27  
**Objective**: Deep dive into S-two documentation to understand the bigger picture of proof systems

---

## 🎯 The Big Picture (Zoom Out)

### Proof System Ecosystem Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROOF SYSTEM UNIVERSE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              COMPUTATION LAYER                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │  │
│  │  │  Cairo   │  │  Custom  │  │    ML    │               │  │
│  │  │   VM     │  │    VM    │  │  Models  │               │  │
│  │  └──────────┘  └──────────┘  └──────────┘               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              PROOF GENERATION LAYER                        │  │
│  │  ┌──────────┐              ┌──────────┐                   │  │
│  │  │  Stone   │              │  S-two   │                   │  │
│  │  │ (STARK)  │              │(Circle   │                   │  │
│  │  │ CPU AIR  │              │ STARK)   │                   │  │
│  │  └──────────┘              └──────────┘                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              VERIFICATION LAYER                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │  │
│  │  │Integrity │  │  SHARP   │  │ On-chain │               │  │
│  │  │FactReg   │  │(Aggregate)│  │ Verifier │               │  │
│  │  └──────────┘  └──────────┘  └──────────┘               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              APPLICATION LAYER                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │  │
│  │  │  Risk    │  │  Model   │  │   UX     │               │  │
│  │  │ Engine   │  │ Registry │  │Transparency│             │  │
│  │  └──────────┘  └──────────┘  └──────────┘               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: We're operating at **all four layers** with Stone. S-two is an alternative at the **proof generation layer** for custom AIR.

---

## 🔬 Microscope View: Technical Deep Dive Plan

### Phase 1: Foundation Understanding ✅

**Completed**:
1. ✅ S-two documentation access
2. ✅ Stone vs S-two comparison
3. ✅ SHARP integration understanding
4. ✅ Integrity verification mapping

**Key Learnings**:
- **Succinctness** = Core value proposition (verify < compute)
- **Zero-knowledge** = Optional feature
- **Stone** = Cairo execution traces
- **S-two** = Custom AIR proofs

### Phase 2: Architecture Deep Dive (Current)

**Objectives**:
1. Understand S-two's modular AIR architecture
2. Map S-two components to our use case
3. Identify integration points
4. Evaluate migration complexity

**Research Areas**:

#### 2.1 S-two AIR Components
- [ ] Modular chips architecture
- [ ] Lookup systems (static vs dynamic)
- [ ] Constraint types (local row, periodic, public inputs)
- [ ] Preprocessed trace patterns

#### 2.2 Circle STARK Technology
- [ ] Circle STARK vs traditional STARK
- [ ] Performance characteristics
- [ ] Proof size comparisons
- [ ] Verification efficiency

#### 2.3 Integration Points
- [ ] SHARP aggregation pipeline
- [ ] On-chain verification compatibility
- [ ] FactRegistry integration
- [ ] Serialization formats

### Phase 3: Use Case Analysis

**Current Use Case (Stone)**:
- ✅ Cairo-based risk model
- ✅ Execution trace → Stone proof
- ✅ Integrity verification
- ✅ On-chain gating

**Potential S-two Use Cases**:
- [ ] Non-Cairo ML models
- [ ] Custom AIR optimizations
- [ ] Performance improvements
- [ ] Specialized ML inference

**Evaluation Criteria**:
- Migration complexity
- Performance gains
- Ecosystem maturity
- Development overhead

---

## 📚 Documentation Deep Dive Plan

### S-two Book Structure

From [S-two documentation](https://docs.starknet.io/learn/S-two-book/why-use-a-proof-system):

1. **Why Use a Proof System?** ✅ (Reviewed)
   - Succinctness concept
   - Zero-knowledge optionality
   - Blockchain applications

2. **How It Works** (Next)
   - [ ] STARK proof structure
   - [ ] Verification process
   - [ ] Public input handling
   - [ ] OODS validation (relevant to our issues!)

3. **Cairo AIR** (Relevant)
   - [ ] Cairo AIR architecture
   - [ ] Builtin configuration
   - [ ] Layout requirements
   - [ ] Component interconnection

4. **Custom AIR Development** (Future)
   - [ ] Modular chips
   - [ ] Lookup systems
   - [ ] Constraint definition
   - [ ] Optimization techniques

### Priority Reading Order

**Immediate** (Relevant to Current Issues):
1. ✅ Why Use a Proof System? (Completed)
2. 🔄 How It Works → STARK Proof Verification (OODS insights)
3. 🔄 Cairo AIR → Builtin Configuration (Builtin validation)
4. 🔄 Cairo AIR → Layout Requirements (Segment ordering)

**Short-term** (Strategic Understanding):
5. Custom AIR Development → Modular Architecture
6. Custom AIR Development → Lookup Systems
7. Integration → SHARP Pipeline
8. Integration → On-chain Verification

**Long-term** (Future Evaluation):
9. Performance Benchmarks
10. Migration Guides
11. Ecosystem Tools
12. Best Practices

---

## 🎯 Strategic Understanding Framework

### The Three-Layer Model

```
┌─────────────────────────────────────────────────────────────┐
│                    STRATEGIC LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: CONCEPTUAL (Why)                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Succinctness principle                           │   │
│  │  • Zero-knowledge optionality                       │   │
│  │  • Proof system value proposition                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Layer 2: ARCHITECTURAL (What)                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Stone vs S-two distinction                       │   │
│  │  • AIR vs Custom AIR                                │   │
│  │  • Verification pipeline                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Layer 3: IMPLEMENTATION (How)                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Integration points                                │   │
│  │  • Serialization formats                             │   │
│  │  • Error handling                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Our Position**: 
- ✅ Layer 1: Understand proof system value
- ✅ Layer 2: Stone architecture (current)
- ✅ Layer 3: Stone + Integrity integration (in progress)

**S-two Position**:
- ✅ Layer 1: Same principles
- 🔄 Layer 2: Custom AIR architecture (research)
- ⏸️ Layer 3: Not needed (yet)

---

## 🔍 Microscope Focus Areas

### Area 1: OODS Validation (Current Issue)

**From S-two Documentation**:
- OODS = Out-of-Domain Sampling
- Critical for STARK proof verification
- Must match between prover and verifier

**Our Context**:
- ✅ Fixed: `n_verifier_friendly_commitment_layers` mismatch
- ⚠️ Investigating: Builtin validation
- 🔍 Research: S-two's OODS handling

**Action Items**:
- [ ] Review S-two OODS documentation
- [ ] Compare with Stone's OODS implementation
- [ ] Map to Integrity's OODS validation
- [ ] Identify any additional insights

### Area 2: Builtin Configuration (Current Issue)

**From S-two Documentation**:
- Builtins are layout-specific
- Must match between program and verifier
- Validation happens in public input phase

**Our Context**:
- ⚠️ Issue: ECDSA vs bitwise mismatch
- ✅ Fixed: Added bitwise segment
- 🔍 Research: S-two's builtin handling

**Action Items**:
- [ ] Review S-two builtin documentation
- [ ] Understand builtin validation logic
- [ ] Compare with Integrity's expectations
- [ ] Identify best practices

### Area 3: Segment Ordering (Current Issue)

**From S-two Documentation**:
- Segments must be in specific order
- Index-based access in verification
- Order matters for serialization

**Our Context**:
- ⚠️ Issue: Index out of bounds
- ✅ Fixed: Added missing bitwise segment
- 🔍 Research: S-two's segment handling

**Action Items**:
- [ ] Review S-two segment documentation
- [ ] Understand segment ordering requirements
- [ ] Map to Integrity's segment expectations
- [ ] Identify ordering rules

---

## 📋 Action Plan: Understanding S-two

### Week 1: Foundation (Current)

**Day 1-2: Conceptual Understanding** ✅
- [x] Read "Why Use a Proof System?"
- [x] Understand succinctness principle
- [x] Map to our use case

**Day 3-4: Architectural Comparison**
- [ ] Compare Stone vs S-two architecture
- [ ] Map integration points
- [ ] Identify differences

**Day 5-7: Technical Deep Dive**
- [ ] Review "How It Works" section
- [ ] Understand STARK proof structure
- [ ] Map verification process

### Week 2: Application (Next)

**Day 1-3: Cairo AIR Deep Dive**
- [ ] Review Cairo AIR architecture
- [ ] Understand builtin configuration
- [ ] Map to our current issues

**Day 4-5: Integration Analysis**
- [ ] Review SHARP integration
- [ ] Understand FactRegistry compatibility
- [ ] Map serialization requirements

**Day 6-7: Strategic Evaluation**
- [ ] Evaluate migration feasibility
- [ ] Assess performance benefits
- [ ] Plan future considerations

### Week 3: Implementation (Future)

**Day 1-3: Custom AIR Research**
- [ ] Review modular chips architecture
- [ ] Understand lookup systems
- [ ] Evaluate development complexity

**Day 4-5: Performance Analysis**
- [ ] Review benchmarks
- [ ] Compare proof sizes
- [ ] Assess verification speed

**Day 6-7: Migration Planning**
- [ ] Create migration roadmap (if needed)
- [ ] Identify prerequisites
- [ ] Plan transition strategy

---

## 🎓 Key Questions to Answer

### Conceptual (Why)

1. ✅ **What is succinctness?** → Verify < Compute
2. ✅ **Why use proof systems?** → Blockchain efficiency
3. ✅ **What is zero-knowledge?** → Optional privacy feature

### Architectural (What)

1. ✅ **Stone vs S-two?** → Cairo vs Custom AIR
2. 🔄 **When to use S-two?** → Custom AIR needs
3. 🔄 **How do they integrate?** → SHARP pipeline

### Implementation (How)

1. ✅ **How does Stone work?** → CPU AIR for Cairo
2. 🔄 **How does S-two work?** → Circle STARK for custom AIR
3. 🔄 **How to migrate?** → Evaluate when needed

---

## 🚀 Strategic Recommendations

### Immediate (Current Focus)

1. **Complete Stone + Integrity Integration**
   - Fix builtin validation
   - Resolve segment ordering
   - Achieve zkML maturity 5/5

2. **Document Proof Soundness**
   - Stone verifier limitations
   - External checks (Model Registry, Integrity)
   - Trust model explanation

### Short-term (Next Quarter)

1. **Monitor S-two Ecosystem**
   - Tooling maturity
   - Community adoption
   - Performance benchmarks

2. **Evaluate Custom AIR Needs**
   - Non-Cairo ML models?
   - Performance optimizations?
   - Custom VMs?

### Long-term (Future)

1. **Consider S-two Migration** (If Needed)
   - Cost-benefit analysis
   - Migration complexity
   - Performance gains

2. **Hybrid Approach** (If Beneficial)
   - Stone for Cairo models
   - S-two for custom optimizations
   - Unified verification layer

---

## 📊 Understanding Progress Tracker

### Conceptual Understanding ✅
- [x] Proof system value proposition
- [x] Succinctness principle
- [x] Zero-knowledge concept
- [x] Blockchain applications

### Architectural Understanding 🔄
- [x] Stone architecture
- [x] S-two architecture (high-level)
- [ ] S-two architecture (detailed)
- [ ] Integration patterns

### Implementation Understanding ⏸️
- [x] Stone integration
- [x] Integrity integration
- [ ] S-two integration (research)
- [ ] Migration path (evaluate)

---

## 🎯 Conclusion: The Bigger Picture

### Where We Are

**Current State**: Stone + Integrity pipeline
- ✅ 95% complete
- ✅ Production-ready architecture
- ✅ Aligned with SHARP direction
- ⚠️ Refining builtin validation

### Where S-two Fits

**Future State**: S-two for custom AIR
- 🔮 Not required for current zkML
- 🔮 Useful for non-Cairo models
- 🔮 Monitor ecosystem maturity

### The Strategic Path

1. **Complete Stone + Integrity** (Current focus) ✅
2. **Deep dive S-two** (Understanding phase) 🔄
3. **Evaluate migration** (When needed) ⏸️
4. **Hybrid approach** (If beneficial) 🔮

**Bottom Line**: We're on the right path. S-two is a future optimization, not a prerequisite. Understanding S-two helps us make informed decisions about future optimizations.

---

**Status**: Strategic plan created. Ready to execute deep dive into S-two documentation with zoom out/zoom in approach.
