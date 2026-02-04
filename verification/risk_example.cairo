// Simple Cairo1 program that mirrors the integer risk calculation
// used in contracts/src/risk_engine.cairo::calculate_risk_score_internal.
// This is meant to be run with `cairo1-run --proof_mode` to produce
// trace/memory inputs for Stone.

use array::ArrayTrait;
use core::traits::TryInto;

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

fn main(inputs: Array<felt252>) -> Array<felt252> {
    // proof_mode only allows Array<felt252> inputs/outputs
    let jedi_utilization: u128 = (*inputs.at(0)).try_into().unwrap();
    let jedi_volatility: u128 = (*inputs.at(1)).try_into().unwrap();
    let jedi_liquidity: u128 = (*inputs.at(2)).try_into().unwrap();
    let jedi_audit_score: u128 = (*inputs.at(3)).try_into().unwrap();
    let jedi_age_days: u128 = (*inputs.at(4)).try_into().unwrap();
    let ekubo_utilization: u128 = (*inputs.at(5)).try_into().unwrap();
    let ekubo_volatility: u128 = (*inputs.at(6)).try_into().unwrap();
    let ekubo_liquidity: u128 = (*inputs.at(7)).try_into().unwrap();
    let ekubo_audit_score: u128 = (*inputs.at(8)).try_into().unwrap();
    let ekubo_age_days: u128 = (*inputs.at(9)).try_into().unwrap();
    let jedi_risk = calculate_risk_score(
        jedi_utilization,
        jedi_volatility,
        jedi_liquidity,
        jedi_audit_score,
        jedi_age_days,
    );

    let ekubo_risk = calculate_risk_score(
        ekubo_utilization,
        ekubo_volatility,
        ekubo_liquidity,
        ekubo_audit_score,
        ekubo_age_days,
    );

    let mut out = ArrayTrait::new();
    out.append(jedi_risk.into());
    out.append(ekubo_risk.into());
    out
}
