# Obsqra.starknet API Documentation

**Version:** 1.0  
**Date:** December 2025

## Contract Interfaces

### RiskEngine.cairo

#### calculate_risk_score

Calculate risk score for a protocol based on multiple factors.

```cairo
fn calculate_risk_score(
    utilization: felt252,
    volatility: felt252,
    liquidity: felt252,
    audit_score: felt252,
    age_days: felt252
) -> felt252
```

**Parameters:**
- `utilization`: Protocol utilization (0-10000, basis points)
- `volatility`: Volatility metric (0-10000, basis points)
- `liquidity`: Liquidity level (0-3: Very High=0, High=1, Medium=2, Low=3)
- `audit_score`: Audit score (0-100)
- `age_days`: Days since protocol launch

**Returns:** Risk score (5-95)

#### calculate_allocation

Calculate optimal allocation based on risk-adjusted APY.

```cairo
fn calculate_allocation(
    aave_risk: felt252,
    lido_risk: felt252,
    compound_risk: felt252,
    aave_apy: felt252,
    lido_apy: felt252,
    compound_apy: felt252
) -> (felt252, felt252, felt252)
```

**Returns:** (aave_pct, lido_pct, compound_pct) in basis points

### StrategyRouter.cairo

#### update_allocation

Update protocol allocations.

```cairo
fn update_allocation(
    aave_pct: felt252,
    lido_pct: felt252,
    compound_pct: felt252
)
```

#### get_allocation

Get current allocations.

```cairo
fn get_allocation() -> (felt252, felt252, felt252)
```

### DAOConstraintManager.cairo

#### set_constraints

Set governance constraints.

```cairo
fn set_constraints(
    max_single: felt252,
    min_diversification: felt252,
    max_volatility: felt252,
    min_liquidity: felt252
)
```

#### validate_allocation

Validate allocation against constraints.

```cairo
fn validate_allocation(
    aave_pct: felt252,
    lido_pct: felt252,
    compound_pct: felt252
) -> bool
```

## Frontend API

### useRiskEngine Hook

```typescript
const { riskScore, calculateAllocation } = useRiskEngine(contractAddress);
```

### MIST.cash Service

```typescript
const mistService = new MistCashService(provider, chamberAddress);
await mistService.deposit(amount, recipientAddress, claimingKey);
await mistService.withdraw(secret, recipientAddress, amount);
```

## AI Service API

### Health Check

```bash
GET /health
```

### Trigger Rebalance

```bash
POST /trigger-rebalance
```

### Accrue Yields

```bash
POST /accrue-yields
```

