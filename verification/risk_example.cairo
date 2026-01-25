// Simple Cairo1 program that mirrors the integer risk calculation
// used in contracts/src/risk_engine.cairo::calculate_risk_score_internal.
// This is meant to be run with `cairo1-run --proof_mode` to produce
// trace/memory inputs for Stone.

use array::ArrayTrait;

fn calculate_risk_score(
    utilization: u128,
    volatility: u128,
    liquidity: u128,
    audit_score: u128,
    age_days: u128,
) -> u128 {
    // Utilization risk: utilization * 25 / 10000
    let utilization_risk = utilization * 25 / 10000;

    // Volatility risk: volatility * 40 / 10000
    let volatility_risk = volatility * 40 / 10000;

    // Liquidity risk: categorical mapping (0=High, 1=Medium, 2=Low, 3=VeryLow)
    let liquidity_risk = if liquidity == 0 {
        0
    } else if liquidity == 1 {
        5
    } else if liquidity == 2 {
        15
    } else {
        30
    };

    // Audit risk: (100 - audit_score) * 3 / 10
    let audit_diff = 100 - audit_score;
    let audit_risk = audit_diff * 3 / 10;

    // Age risk: max(0, (730 - age_days) * 10 / 730)
    let age_risk = if age_days >= 730 {
        0
    } else {
        (730 - age_days) * 10 / 730
    };

    let total = utilization_risk + volatility_risk + liquidity_risk + audit_risk + age_risk;

    // Clip to [5, 95]
    if total < 5 {
        5
    } else if total > 95 {
        95
    } else {
        total
    }
}

fn main() -> Array<felt252> {
    // Sample metrics (mirrors the Rust/LuminAIR defaults)
    let utilization = 5000_u128;  // basis points
    let volatility = 4000_u128;   // basis points
    let liquidity = 1_u128;       // 0-3 scale
    let audit_score = 95_u128;    // out of 100
    let age_days = 700_u128;      // days since launch

    let risk = calculate_risk_score(utilization, volatility, liquidity, audit_score, age_days);

    // proof_mode only allows Array<felt252> inputs/outputs
    let mut out = ArrayTrait::new();
    out.append(risk.into());
    out
}
