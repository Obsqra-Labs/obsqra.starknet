# zkML Roadmap: Path to Full Verifiable AI

## Current Status: ~60% zkML

### ✅ What Works
- **Proof Infrastructure**: LuminAIR operator generating STARK proofs
- **Risk Calculation Proofs**: Proving deterministic risk formula
- **Local Verification**: <1s verification before execution
- **On-Chain Execution**: Cairo contract executing allocations

### ❌ Major Gaps

#### 1. **No Actual ML Model** (CRITICAL)
**Current**: Deterministic formula
```
risk = (util*35 + vol*30 + liq*5 + audit*20 + age_penalty) / 10000
allocation = (APY * 10000) / (Risk + 1)
```

**Needed**: 
- Neural network or other ML model
- Model weights stored and proven
- Training pipeline
- Model inference in ZK circuit

#### 2. **Incomplete Proof Coverage** (HIGH)
**Current**: Only proving risk calculation
**Missing**:
- Allocation decision proof
- Full end-to-end proof (metrics → allocation)
- Constraint verification proof

#### 3. **No On-Chain Verification** (MEDIUM)
**Current**: Local verification only (requires trust)
**Missing**:
- Verifier contract on Starknet
- Public on-chain verification
- Trustless verification

#### 4. **Limited AI Intelligence** (MEDIUM)
**Current**: Simple risk-adjusted allocation
**Missing**:
- Yield prediction models
- Market analysis
- Historical learning
- Multi-factor optimization

## Roadmap to Full zkML

### Phase 1: Add Real ML Model (4-6 weeks)

#### Option A: Neural Network for Allocation
- **Model**: 2-layer neural network
  - Input: [util, vol, liq, audit, age, apy] × 2 protocols
  - Hidden: 16 neurons, ReLU
  - Output: [jediswap_pct, ekubo_pct]
- **Training**: Historical allocation performance
- **ZK Circuit**: Convert to LuminAIR graph
- **Proof**: Prove model inference

#### Option B: Gradient Boosting (Simpler)
- **Model**: XGBoost or LightGBM
- **Features**: Same as above
- **ZK Circuit**: Tree-based circuits (more complex)
- **Proof**: Prove tree traversal

#### Implementation Steps:
1. Design model architecture
2. Collect training data (historical allocations)
3. Train model (Python)
4. Convert to LuminAIR circuit
5. Generate proofs for inference
6. Replace deterministic formula

### Phase 2: Complete Proof Coverage (2-3 weeks)

**Goal**: Prove entire decision pipeline

1. **Extend Proof to Include Allocation**
   - Current: Prove risk calculation only
   - Target: Prove risk → allocation → constraints
   - Method: Extend LuminAIR operator

2. **End-to-End Proof**
   - Input: Protocol metrics
   - Output: Final allocation percentages
   - Single proof for entire pipeline

3. **Constraint Verification Proof**
   - Prove DAO constraints satisfied
   - Include in main proof

### Phase 3: On-Chain Verification (3-4 weeks)

**Goal**: Trustless verification on Starknet

1. **Deploy Verifier Contract**
   - Starknet contract for LuminAIR proofs
   - Verify proof before execution
   - Public verification endpoint

2. **Update Execution Flow**
   ```
   Generate Proof → Submit to Verifier Contract
                        ↓
                   Verify On-Chain
                        ↓
                   Execute if Verified
   ```

3. **Remove Backend Trust**
   - Frontend can verify independently
   - No need to trust backend

### Phase 4: Advanced AI (6-8 weeks)

1. **Yield Prediction Model**
   - Predict future APY
   - ML model for forecasting
   - Prove predictions

2. **Market Analysis**
   - Multi-factor analysis
   - Market condition models
   - Risk correlation models

3. **Historical Learning**
   - Learn from past allocations
   - Update model weights
   - Performance feedback loop

## Recommended Next Steps

### Immediate (This Sprint)
1. ✅ **Document gaps** (DONE)
2. **Design ML model architecture**
   - Choose: Neural network vs gradient boosting
   - Define inputs/outputs
   - Design training pipeline

### Short Term (Next Month)
1. **Implement ML model**
   - Train on historical data
   - Convert to LuminAIR
   - Generate proofs

2. **Extend proof coverage**
   - Include allocation in proof
   - End-to-end proof

### Medium Term (Next Quarter)
1. **On-chain verifier**
   - Deploy verifier contract
   - Public verification

2. **Advanced models**
   - Yield prediction
   - Market analysis

## Technical Considerations

### Model Size Limits
- LuminAIR has circuit size limits
- Need to balance model complexity vs proof time
- Consider model compression/quantization

### Proof Generation Time
- Current: ~2-3 seconds
- With ML model: May increase to 5-10 seconds
- Need to optimize circuit

### Training Data
- Need historical allocation data
- Performance metrics
- Market conditions

### Model Updates
- How to update model weights?
- On-chain vs off-chain updates
- Versioning strategy

## Success Metrics

### Full zkML Achieved When:
- ✅ Real ML model (not deterministic formula)
- ✅ Complete proof coverage (end-to-end)
- ✅ On-chain verification (trustless)
- ✅ Advanced AI capabilities

### Current: 60% zkML
### Target: 100% zkML

