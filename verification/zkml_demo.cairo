// Tiny zkML demo program (Cairo1).
// Mirrors contracts/src/zkml_oracle.cairo and backend/app/services/zkml_service.py.

use array::ArrayTrait;

fn infer_score(
    utilization: u128,
    volatility: u128,
    liquidity: u128,
    audit_score: u128,
    age_days: u128,
) -> (u128, u128) {
    let util_component = utilization * 2;
    let vol_component = volatility * 3;
    let liq_component = liquidity * 500;
    let audit_risk = if audit_score >= 100 { 0 } else { 100 - audit_score };
    let age_risk = if age_days >= 730 { 0 } else { 730 - age_days };
    let audit_component = audit_risk * 200;
    let age_component = age_risk * 5;

    let score = util_component + vol_component + liq_component + audit_component + age_component;
    let decision = if score >= 22000 { 1 } else { 0 };
    (score, decision)
}

fn main() -> Array<felt252> {
    // Example inputs
    let utilization = 6500_u128;
    let volatility = 3500_u128;
    let liquidity = 1_u128;
    let audit_score = 98_u128;
    let age_days = 800_u128;

    let (score, decision) = infer_score(
        utilization,
        volatility,
        liquidity,
        audit_score,
        age_days,
    );

    let mut out = ArrayTrait::new();
    out.append(score.into());
    out.append(decision.into());
    out
}
