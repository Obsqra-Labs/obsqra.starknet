use starknet::ContractAddress;
use core::array::Span;

// Ekubo Core Interface - ACTUAL interface from Ekubo Protocol GitHub
// Source: https://github.com/EkuboProtocol/starknet-contracts/blob/main/src/interfaces/core.cairo
#[starknet::interface]
pub trait IEkuboCore<TContractState> {
    // Lock the core contract and trigger callback to your contract's locked() function
    // Note: No locker parameter - it uses the caller automatically
    fn lock(ref self: TContractState, data: Span<felt252>) -> Span<felt252>;
    
    // Pay tokens to the core (used within locked callback)
    // Note: Takes full allowance - no amount parameter needed
    fn pay(ref self: TContractState, token_address: ContractAddress);
    
    // Withdraw tokens from the core (used within locked callback)
    fn withdraw(
        ref self: TContractState,
        token_address: ContractAddress,
        recipient: ContractAddress,
        amount: u128
    );
    
    // Update liquidity position (used within locked callback)
    // Note: This requires PoolKey and UpdatePositionParameters structs
    // For now, we'll keep a simplified version and implement the full version later
    // The actual signature is:
    // fn update_position(ref self: TContractState, pool_key: PoolKey, params: UpdatePositionParameters) -> Delta;
    
    // Get user's liquidity position
    // Note: Actual signature uses PoolKey and PositionKey structs
    // fn get_position(self: @TContractState, pool_key: PoolKey, position_key: PositionKey) -> Position;
}

// Ekubo Router Interface - For swaps and complex operations
// Router address (Sepolia): 0x9995855C00494d039aB6792f18e368e530DFf931
// Note: Router uses lock/callback pattern internally, but provides simpler swap interface
#[starknet::interface]
pub trait IEkuboRouter<TContractState> {
    // Single swap against a route node
    fn swap(
        ref self: TContractState,
        node: RouteNode,
        token_amount: TokenAmount
    ) -> Delta;
    
    // Multihop swap
    fn multihop_swap(
        ref self: TContractState,
        route: Array<RouteNode>,
        token_amount: TokenAmount
    ) -> Array<Delta>;
}

// Types needed for Router
#[derive(Copy, Drop, Serde)]
pub struct RouteNode {
    pub pool_key: PoolKey,
    pub sqrt_ratio_limit: u256,
    pub skip_ahead: u128,
}

#[derive(Copy, Drop, Serde)]
pub struct TokenAmount {
    pub token: ContractAddress,
    pub amount: i129,
}

#[derive(Copy, Drop, Serde)]
pub struct PoolKey {
    pub token0: ContractAddress,
    pub token1: ContractAddress,
    pub fee: u128,
    pub tick_spacing: u128,
    pub extension: ContractAddress,
}

#[derive(Copy, Drop, Serde)]
pub struct Delta {
    pub amount0: i129,
    pub amount1: i129,
}

// i129 type - signed 129-bit integer (sign + 128-bit magnitude)
#[derive(Copy, Drop, Serde)]
pub struct i129 {
    pub mag: u128,
    pub sign: bool,
}

// Ekubo Positions Interface - For NFT-based positions
// THIS IS WHAT WE SHOULD USE FOR ADDING LIQUIDITY!
// The Positions contract handles Core's lock pattern internally
#[starknet::interface]
pub trait IEkuboPositions<TContractState> {
    // Mint NFT and deposit liquidity in a single call
    fn mint_and_deposit(
        ref self: TContractState,
        pool_key: PoolKey,
        bounds: Bounds,
        min_liquidity: u128
    ) -> (u64, u128); // Returns (token_id, liquidity)
    
    // Deposit specific amounts into a position
    fn deposit_amounts(
        ref self: TContractState,
        id: u64,
        pool_key: PoolKey,
        bounds: Bounds,
        amount0: u128,
        amount1: u128,
        min_liquidity: u128
    ) -> u128; // Returns liquidity
}

// Types needed for Positions (already defined above for Router)
// Bounds type
#[derive(Copy, Drop, Serde)]
pub struct Bounds {
    pub lower: i129,
    pub upper: i129,
}

