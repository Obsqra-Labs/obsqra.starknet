#[starknet::interface]
pub trait IZkmlOracle<TContractState> {
    fn infer(
        self: @TContractState,
        utilization: u256,
        volatility: u256,
        liquidity: u256,
        audit_score: u256,
        age_days: u256,
    ) -> (u256, felt252);
    fn get_threshold(self: @TContractState) -> u256;
}
