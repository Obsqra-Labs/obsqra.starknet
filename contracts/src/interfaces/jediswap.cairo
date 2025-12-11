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
    
    // V2 Factory: Get pool address for token pair and fee tier
    fn get_pool(
        self: @TContractState,
        token0: ContractAddress,
        token1: ContractAddress,
        fee: u32
    ) -> ContractAddress;
}

// JediSwap V2 Swap Router Interface - For swaps
// Based on: https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_swap_router
#[starknet::interface]
pub trait IJediSwapV2SwapRouter<TContractState> {
    // Swap exact amount of input tokens for as many output tokens as possible
    // For a single hop swap
    fn exact_input_single(
        ref self: TContractState,
        params: ExactInputSingleParams
    ) -> u256; // Returns amount_out

    // Swap exact amount of input tokens for as many output tokens as possible
    // For multi-hop swaps
    fn exact_input(
        ref self: TContractState,
        params: ExactInputParams
    ) -> u256; // Returns amount_out

    // Swap as few input tokens as possible for exact amount of output tokens
    // For a single hop swap
    fn exact_output_single(
        ref self: TContractState,
        params: ExactOutputSingleParams
    ) -> u256; // Returns amount_in

    // Swap as few input tokens as possible for exact amount of output tokens
    // For multi-hop swaps
    fn exact_output(
        ref self: TContractState,
        params: ExactOutputParams
    ) -> u256; // Returns amount_in
}

// Parameter structs for V2 Swap Router
// Based on official ABI from Starkscan and JediSwap docs
// Fee is u32 (32-bit), not u128!
// Available fee tiers: 100 (0.01%), 500 (0.05%), 3000 (0.3%), 10000 (1%)
// For STRK/ETH: Only 0.05% (500) and 1% (10000) pools exist on Sepolia
#[derive(Drop, Serde)]
pub struct ExactInputSingleParams {
    pub token_in: ContractAddress,
    pub token_out: ContractAddress,
    pub fee: u32, // Fee tier - MUST be u32, not u128! (e.g., 500 for 0.05%, 10000 for 1%)
    pub recipient: ContractAddress,
    pub deadline: u64,
    pub amount_in: u256,
    pub amount_out_minimum: u256,
    pub sqrt_price_limit_x96: u256, // 0 for no limit (note: capital X in docs)
}

#[derive(Drop, Serde)]
pub struct ExactInputParams {
    pub path: Array<felt252>, // Encoded path (token_in, fee, token_out) as felt252 array
    pub recipient: ContractAddress,
    pub deadline: u64,
    pub amount_in: u256,
    pub amount_out_minimum: u256,
}

#[derive(Drop, Serde)]
pub struct ExactOutputSingleParams {
    pub token_in: ContractAddress,
    pub token_out: ContractAddress,
    pub fee: u128,
    pub recipient: ContractAddress,
    pub deadline: u64,
    pub amount_out: u256,
    pub amount_in_maximum: u256,
    pub sqrt_price_limit_x96: u256,
}

#[derive(Drop, Serde)]
pub struct ExactOutputParams {
    pub path: Array<felt252>, // Encoded path as felt252 array
    pub recipient: ContractAddress,
    pub deadline: u64,
    pub amount_out: u256,
    pub amount_in_maximum: u256,
}

// Legacy V1 Router Interface - ACTUAL interface from JediSwap V1 docs
// Based on: https://docs.jediswap.xyz/for-developers/jediswap-v1/smart-contract-reference/router
// Router addresses:
//   Starknet Alpha Testnet: 0x02bcc885342ebbcbcd170ae6cafa8a4bed22bb993479f49806e72d96af94c965
//   Starknet Alpha Mainnet: 0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023
//   Sepolia: 0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21 (V1 router)
#[starknet::interface]
pub trait IJediSwapRouter<TContractState> {
    // Swap exact amount of input tokens for as many output tokens as possible
    // NOTE: V1 uses path_len: felt and path: felt* (pointer), not Array!
    fn swap_exact_tokens_for_tokens(
        ref self: TContractState,
        amount_in: u256,
        amount_out_min: u256,
        path_len: felt252,
        path: Span<felt252>, // V1 uses Span/pointer, not Array
        to: ContractAddress,
        deadline: u64
    ) -> (felt252, Span<u256>); // Returns (amounts_len, amounts)
    
    // Add liquidity to a pool
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
}

// JediSwap Pair Interface - For LP tokens (V1)
#[starknet::interface]
pub trait IJediSwapPair<TContractState> {
    fn get_reserves(self: @TContractState) -> (u256, u256, u64); // (reserve0, reserve1, timestamp)
    
    fn total_supply(self: @TContractState) -> u256;
    
    fn balance_of(self: @TContractState, account: ContractAddress) -> u256;
}

// JediSwap V2 Pool Interface - For concentrated liquidity pools
// Based on: https://docs.jediswap.xyz/for-developers/jediswap-v2/core/jediswap_v2_pool
#[starknet::interface]
pub trait IJediSwapV2Pool<TContractState> {
    fn get_sqrt_price_X96(self: @TContractState) -> u256; // Q64.96-encoded square-root price
    fn get_tick(self: @TContractState) -> i32; // Current tick
    fn get_fee(self: @TContractState) -> u32; // Fee tier (e.g., 10000 for 1%)
}

// JediSwap V2 NFT Position Manager Interface - For concentrated liquidity
// Based on: https://docs.jediswap.xyz/for-developers/jediswap-v2/periphery/jediswap_v2_nft_position_manager
// CRITICAL: tick_lower and tick_upper use custom i32 struct { mag: u32, sign: bool }, NOT i128!

// Custom i32 struct matching JediSwap ABI exactly
#[derive(Copy, Drop, Serde)]
pub struct I32 {
    pub mag: u32,
    pub sign: bool, // true for negative numbers
}

#[starknet::interface]
pub trait IJediSwapV2NFTPositionManager<TContractState> {
    // Add liquidity to a pool (returns NFT token ID)
    fn mint(
        ref self: TContractState,
        params: MintParams
    ) -> (u256, u128, u256, u256); // Returns (token_id, liquidity, amount0, amount1)

    // Decrease liquidity from a position
    fn decrease_liquidity(
        ref self: TContractState,
        params: DecreaseLiquidityParams
    ) -> (u256, u256); // Returns (amount0, amount1)

    // Collect fees from a position
    fn collect(
        ref self: TContractState,
        params: CollectParams
    ) -> (u256, u256); // Returns (amount0, amount1)

    // Burn a position NFT
    fn burn(
        ref self: TContractState,
        token_id: u256
    );

    // Get position details
    fn positions(
        self: @TContractState,
        token_id: u256
    ) -> Position;
}

// Parameter structs for NFT Position Manager
// EXACT match to JediSwap ABI - tick_lower and tick_upper are I32 structs, not i128!
#[derive(Drop, Serde)]
pub struct MintParams {
    pub token0: ContractAddress,
    pub token1: ContractAddress,
    pub fee: u32,
    pub tick_lower: I32, // Custom struct { mag: u32, sign: bool }
    pub tick_upper: I32, // Custom struct { mag: u32, sign: bool }
    pub amount0_desired: u256,
    pub amount1_desired: u256,
    pub amount0_min: u256,
    pub amount1_min: u256,
    pub recipient: ContractAddress,
    pub deadline: u64,
}

#[derive(Drop, Serde)]
pub struct DecreaseLiquidityParams {
    pub token_id: u256,
    pub liquidity: u128,
    pub amount0_min: u256,
    pub amount1_min: u256,
    pub deadline: u64,
}

#[derive(Drop, Serde)]
pub struct CollectParams {
    pub token_id: u256,
    pub recipient: ContractAddress,
    pub amount0_max: u256,
    pub amount1_max: u256,
}

#[derive(Drop, Serde)]
pub struct Position {
    pub nonce: u128,
    pub operator: ContractAddress,
    pub token0: ContractAddress,
    pub token1: ContractAddress,
    pub fee: u32,
    pub tick_lower: I32, // Custom struct { mag: u32, sign: bool }
    pub tick_upper: I32, // Custom struct { mag: u32, sign: bool }
    pub liquidity: u128,
    pub fee_growth_inside0_last_x128: u256,
    pub fee_growth_inside1_last_x128: u256,
    pub tokens_owed0: u256,
    pub tokens_owed1: u256,
}

