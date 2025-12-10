use starknet::ContractAddress;
use starknet::get_contract_address;
use starknet::get_caller_address;
use starknet::get_block_timestamp;

use super::interfaces::erc20::IERC20Dispatcher;
use super::interfaces::jediswap::{
    IJediSwapV2NFTPositionManagerDispatcher,
    IJediSwapV2NFTPositionManagerDispatcherTrait,
    MintParams
};

#[starknet::contract]
mod TestJediSwap {
    use starknet::ContractAddress;
    use starknet::get_contract_address;
    use starknet::get_caller_address;
    use starknet::get_block_timestamp;
    
    use super::super::interfaces::erc20::IERC20Dispatcher;
    use super::super::interfaces::jediswap::{
        IJediSwapV2NFTPositionManagerDispatcher,
        IJediSwapV2NFTPositionManagerDispatcherTrait,
        MintParams
    };
    
    #[storage]
    struct Storage {
        jediswap_nft_manager: ContractAddress,
        strk_token: ContractAddress,
        eth_token: ContractAddress,
        owner: ContractAddress,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        LiquidityAdded: LiquidityAdded,
    }
    
    #[derive(Drop, starknet::Event)]
    struct LiquidityAdded {
        token_id: u256,
        liquidity: u256,
        amount0: u256,
        amount1: u256,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        jediswap_nft_manager: ContractAddress,
        strk_token: ContractAddress,
        eth_token: ContractAddress,
        owner: ContractAddress,
    ) {
        self.jediswap_nft_manager.write(jediswap_nft_manager);
        self.strk_token.write(strk_token);
        self.eth_token.write(eth_token);
        self.owner.write(owner);
    }
    
    // Test function: Add liquidity to JediSwap
    // This is a simple test - just adds STRK/ETH liquidity
    #[external(v0)]
    fn test_add_liquidity(
        ref self: ContractState,
        strk_amount: u256,
        eth_amount: u256,
    ) -> (u256, u256, u256, u256) {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can test');
        
        let contract_addr = get_contract_address();
        let jediswap_nft_manager = self.jediswap_nft_manager.read();
        let strk_token = self.strk_token.read();
        let eth_token = self.eth_token.read();
        
        // Approve NFT Manager for both tokens
        let strk_erc20 = IERC20Dispatcher { contract_address: strk_token };
        strk_erc20.approve(jediswap_nft_manager, strk_amount);
        
        let eth_erc20 = IERC20Dispatcher { contract_address: eth_token };
        eth_erc20.approve(jediswap_nft_manager, eth_amount);
        
        // Add liquidity via NFT Position Manager
        let nft_manager = IJediSwapV2NFTPositionManagerDispatcher { contract_address: jediswap_nft_manager };
        let mint_params = MintParams {
            token0: strk_token,
            token1: eth_token,
            fee: 3000, // 0.3% fee tier
            tick_lower: -887272, // Full range
            tick_upper: 887272,  // Full range
            amount0_desired: strk_amount,
            amount1_desired: eth_amount,
            amount0_min: 0, // No slippage protection for testing
            amount1_min: 0,
            recipient: contract_addr,
            deadline: get_block_timestamp() + 1800, // 30 minutes
        };
        
        let (token_id, liquidity, amount0, amount1) = nft_manager.mint(mint_params);
        
        self.emit(LiquidityAdded {
            token_id,
            liquidity,
            amount0,
            amount1,
        });
        
        (token_id, liquidity, amount0, amount1)
    }
}

