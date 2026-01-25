// Tiny zkML oracle (linear classifier) for demo purposes.
// This is intentionally simple to keep proof times low and model transparent.

#[starknet::contract]
mod ZkmlOracle {
    use core::num::traits::Zero;

    // Model weights (must match backend/app/services/zkml_service.py)
    const UTIL_WEIGHT: u256 = 2_u256;
    const VOL_WEIGHT: u256 = 3_u256;
    const LIQ_WEIGHT: u256 = 500_u256;
    const AUDIT_WEIGHT: u256 = 200_u256;
    const AGE_WEIGHT: u256 = 5_u256;
    const THRESHOLD: u256 = 22000_u256;

    #[storage]
    struct Storage {}

    #[external(v0)]
    fn infer(
        self: @ContractState,
        utilization: u256,
        volatility: u256,
        liquidity: u256,
        audit_score: u256,
        age_days: u256,
    ) -> (u256, felt252) {
        let audit_risk = if audit_score > 100_u256 { 0_u256 } else { 100_u256 - audit_score };
        let age_risk = if age_days >= 730_u256 { 0_u256 } else { 730_u256 - age_days };

        let util_component = utilization * UTIL_WEIGHT;
        let vol_component = volatility * VOL_WEIGHT;
        let liq_component = liquidity * LIQ_WEIGHT;
        let audit_component = audit_risk * AUDIT_WEIGHT;
        let age_component = age_risk * AGE_WEIGHT;

        let score = util_component + vol_component + liq_component + audit_component + age_component;
        let decision = if score >= THRESHOLD { 1 } else { 0 };

        (score, decision)
    }

    #[external(v0)]
    fn get_threshold(self: @ContractState) -> u256 {
        THRESHOLD
    }
}
