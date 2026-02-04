# RiskEngine Contract Reference

Complete reference for the RiskEngine contract, including address, interface, functions, events, storage, and usage examples.

## Contract Address

**Sepolia Testnet:**
```
0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4
```

**Explorer:**
- Starkscan: https://sepolia.starkscan.co/contract/0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4

## Interface Definition

```cairo
#[starknet::interface]
pub trait IRiskEngine<TContractState> {
    fn get_contract_version(self: @TContractState) -> felt252;
    fn get_build_timestamp(self: @TContractState) -> felt252;
    
    fn calculate_risk_score(
        ref self: TContractState,
        utilization: felt252,
        volatility: felt252,
        liquidity: felt252,
        audit_score: felt252,
        age_days: felt252
    ) -> felt252;
    
    fn calculate_allocation(
        ref self: TContractState,
        nostra_risk: felt252,
        zklend_risk: felt252,
        ekubo_risk: felt252,
        nostra_apy: felt252,
        zklend_apy: felt252,
        ekubo_apy: felt252
    ) -> (felt252, felt252, felt252);
    
    fn verify_constraints(
        ref self: TContractState,
        nostra_pct: felt252,
        zklend_pct: felt252,
        ekubo_pct: felt252,
        max_single: felt252,
        min_diversification: felt252
    ) -> bool;
    
    fn propose_and_execute_allocation(
        ref self: TContractState,
        jediswap_metrics: ProtocolMetrics,
        ekubo_metrics: ProtocolMetrics,
        jediswap_proof_fact: felt252,
        ekubo_proof_fact: felt252,
        expected_jediswap_score: felt252,
        expected_ekubo_score: felt252,
        fact_registry_address: ContractAddress,
    ) -> AllocationDecision;
    
    fn get_decision(ref self: TContractState, decision_id: felt252) -> AllocationDecision;
    fn get_decision_count(ref self: TContractState) -> felt252;
}
```

## Key Functions

### calculate_risk_score

Calculates risk score for a protocol based on metrics.

**Parameters:**
- `utilization`: Utilization percentage (0-10000)
- `volatility`: Volatility score (0-10000)
- `liquidity`: Liquidity score (1-5)
- `audit_score`: Audit score (0-100)
- `age_days`: Protocol age in days

**Returns:**
- `felt252`: Risk score (5-95)

**Formula:**
```
risk = (util*35 + vol*30 + liq*5 + audit*20 + age_penalty) / 10000
```

### calculate_allocation

Calculates optimal allocation based on risk scores and APYs.

**Parameters:**
- Risk scores for each protocol
- APY values for each protocol

**Returns:**
- `(felt252, felt252, felt252)`: Allocation percentages

**Formula:**
```
allocation = (APY * 10000) / (Risk + 1)
```

### propose_and_execute_allocation

Full orchestration function with on-chain proof verification.

**Parameters:**
- `jediswap_metrics`: ProtocolMetrics struct
- `ekubo_metrics`: ProtocolMetrics struct
- `jediswap_proof_fact`: SHARP fact hash
- `ekubo_proof_fact`: SHARP fact hash
- `expected_jediswap_score`: Risk score from proof
- `expected_ekubo_score`: Risk score from proof
- `fact_registry_address`: Fact Registry contract address

**Returns:**
- `AllocationDecision`: Complete decision with proof info

**Process:**
1. Verify proofs in Fact Registry
2. Calculate risk scores on-chain
3. Validate scores match proof
4. Calculate allocation
5. Verify DAO constraints
6. Execute via StrategyRouter
7. Emit events

## Events

### AllocationProposed

Emitted when allocation is proposed with proof.

```cairo
event AllocationProposed {
    decision_id: felt252,
    jediswap_pct: felt252,
    ekubo_pct: felt252,
    proof_fact_hash: felt252
}
```

### AllocationExecuted

Emitted when allocation is executed.

```cairo
event AllocationExecuted {
    decision_id: felt252,
    transaction_hash: felt252,
    model_hash: felt252
}
```

### ConstraintsValidated

Emitted when DAO constraints are validated.

```cairo
event ConstraintsValidated {
    decision_id: felt252,
    constraints: DAOConstraints
}
```

## Storage Layout

```cairo
struct Storage {
    owner: ContractAddress,
    strategy_router: ContractAddress,
    dao_manager: ContractAddress,
    decision_count: felt252,
    current_decision: AllocationDecision,
    current_model_hash: felt252,
    // ... performance tracking
}
```

## Usage Examples

### Calculate Risk Score

```python
from starknet_py.contract import Contract

contract = await Contract.from_address(
    address=risk_engine_address,
    provider=provider
)

risk_score = await contract.functions["calculate_risk_score"].call(
    utilization=6500,
    volatility=3500,
    liquidity=1,
    audit_score=98,
    age_days=800
)
```

### Propose and Execute Allocation

```python
result = await contract.functions["propose_and_execute_allocation"].invoke(
    jediswap_metrics={
        "utilization": 6500,
        "volatility": 3500,
        "liquidity": 1,
        "audit_score": 98,
        "age_days": 800
    },
    ekubo_metrics={
        "utilization": 5000,
        "volatility": 2500,
        "liquidity": 2,
        "audit_score": 95,
        "age_days": 600
    },
    jediswap_proof_fact=proof_fact_hash,
    ekubo_proof_fact=proof_fact_hash,
    expected_jediswap_score=45,
    expected_ekubo_score=38,
    fact_registry_address=fact_registry_address,
    max_fee=max_fee
)
```

## Error Codes

**0:** Proofs not verified
**1:** JediSwap risk score mismatch
**2:** Ekubo risk score mismatch
**3:** Constraints violated
**4:** Insufficient balance

## Next Steps

- **[StrategyRouter](02-strategy-router.md)** - Fund management contract
- **[ModelRegistry](03-model-registry.md)** - Model provenance contract
- **[Architecture: Smart Contracts](../03-architecture/02-smart-contracts.md)** - Contract architecture

---

**RiskEngine Summary:** Core risk assessment and allocation engine with on-chain proof verification gate, enforcing trustless verification before execution.
