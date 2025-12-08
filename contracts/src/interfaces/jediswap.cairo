use starknet::ContractAddress;

// JediSwap Factory Interface
#[starknet::interface]
pub trait IJediSwapFactory<TContractState> {
    fn get_pair(
        self: @TContractState,
        token0: ContractAddress,
        token1: ContractAddress
    ) -> ContractAddress;

    fn create_pair(
        ref self: TContractState,
        token0: ContractAddress,
        token1: ContractAddress
    ) -> ContractAddress;
}

// JediSwap Router Interface - For swaps and liquidity
#[starknet::interface]
pub trait IJediSwapRouter<TContractState> {
    // Swap tokens
    fn swap_exact_tokens_for_tokens(
        ref self: TContractState,
        amount_in: u256,
        amount_out_min: u256,
        path: Array<ContractAddress>,
        to: ContractAddress,
        deadline: u64
    ) -> Array<u256>; // Returns amounts

    // Add liquidity
    fn add_liquidity(
        ref self: TContractState,
        token_a: ContractAddress,
        token_b: ContractAddress,
        amount_a_desired: u256,
        amount_b_desired: u256,
        amount_a_min: u256,
        amount_b_min: u256,
        to: ContractAddress,
        deadline: u64
    ) -> (u256, u256, u256); // Returns (amountA, amountB, liquidity)

    // Remove liquidity
    fn remove_liquidity(
        ref self: TContractState,
        token_a: ContractAddress,
        token_b: ContractAddress,
        liquidity: u256,
        amount_a_min: u256,
        amount_b_min: u256,
        to: ContractAddress,
        deadline: u64
    ) -> (u256, u256); // Returns (amountA, amountB)

    // Quote functions
    fn get_amounts_out(
        self: @TContractState,
        amount_in: u256,
        path: Array<ContractAddress>
    ) -> Array<u256>;
}

// JediSwap Pair Interface - For LP tokens
#[starknet::interface]
pub trait IJediSwapPair<TContractState> {
    fn get_reserves(self: @TContractState) -> (u256, u256, u64); // (reserve0, reserve1, timestamp)
    
    fn total_supply(self: @TContractState) -> u256;
    
    fn balance_of(self: @TContractState, account: ContractAddress) -> u256;
}

