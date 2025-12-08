use starknet::ContractAddress;

// Ekubo Core Interface - Simplified for our use case
#[starknet::interface]
pub trait IEkuboCore<TContractState> {
    // Deposit liquidity to a pool
    fn deposit_liquidity(
        ref self: TContractState,
        token0: ContractAddress,
        token1: ContractAddress,
        amount0: u256,
        amount1: u256,
        fee: u128
    ) -> u256; // Returns liquidity tokens

    // Withdraw liquidity from a pool
    fn withdraw_liquidity(
        ref self: TContractState,
        token0: ContractAddress,
        token1: ContractAddress,
        liquidity: u256,
        fee: u128
    ) -> (u256, u256); // Returns (amount0, amount1)

    // Get user's liquidity position
    fn get_position(
        self: @TContractState,
        owner: ContractAddress,
        token0: ContractAddress,
        token1: ContractAddress,
        fee: u128
    ) -> u256;
}

// Ekubo Router Interface - For swaps and complex operations
#[starknet::interface]
pub trait IEkuboRouter<TContractState> {
    fn swap_exact_input(
        ref self: TContractState,
        token_in: ContractAddress,
        token_out: ContractAddress,
        amount_in: u256,
        min_amount_out: u256
    ) -> u256; // Returns amount_out
}

// Ekubo Positions Interface - For NFT-based positions
#[starknet::interface]
pub trait IEkuboPositions<TContractState> {
    fn get_position_value(
        self: @TContractState,
        position_id: u256
    ) -> u256;
}

