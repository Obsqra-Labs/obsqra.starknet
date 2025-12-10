use starknet::ContractAddress;
use starknet::get_contract_address;
use starknet::get_caller_address;

use super::interfaces::erc20::IERC20Dispatcher;
use super::interfaces::ekubo::{
    IEkuboCoreDispatcher,
    IEkuboCoreDispatcherTrait
};

#[starknet::contract]
mod TestEkubo {
    use starknet::ContractAddress;
    use starknet::get_contract_address;
    use starknet::get_caller_address;
    
    use super::super::interfaces::erc20::IERC20Dispatcher;
    use super::super::interfaces::ekubo::{
        IEkuboCoreDispatcher,
        IEkuboCoreDispatcherTrait
    };
    
    #[storage]
    struct Storage {
        ekubo_core: ContractAddress,
        strk_token: ContractAddress,
        eth_token: ContractAddress,
        owner: ContractAddress,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        LiquidityDeposited: LiquidityDeposited,
    }
    
    #[derive(Drop, starknet::Event)]
    struct LiquidityDeposited {
        liquidity_tokens: u256,
        amount0: u256,
        amount1: u256,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        ekubo_core: ContractAddress,
        strk_token: ContractAddress,
        eth_token: ContractAddress,
        owner: ContractAddress,
    ) {
        self.ekubo_core.write(ekubo_core);
        self.strk_token.write(strk_token);
        self.eth_token.write(eth_token);
        self.owner.write(owner);
    }
    
    // Test function: Deposit liquidity to Ekubo
    // This is a simple test - just deposits STRK/ETH liquidity
    #[external(v0)]
    fn test_deposit_liquidity(
        ref self: ContractState,
        strk_amount: u256,
        eth_amount: u256,
    ) -> u256 {
        let caller = get_caller_address();
        let owner = self.owner.read();
        assert(caller == owner, 'Only owner can test');
        
        let contract_addr = get_contract_address();
        let ekubo_core = self.ekubo_core.read();
        let strk_token = self.strk_token.read();
        let eth_token = self.eth_token.read();
        
        // Approve Ekubo Core for both tokens
        let strk_erc20 = IERC20Dispatcher { contract_address: strk_token };
        strk_erc20.approve(ekubo_core, strk_amount);
        
        let eth_erc20 = IERC20Dispatcher { contract_address: eth_token };
        eth_erc20.approve(ekubo_core, eth_amount);
        
        // Deposit liquidity to Ekubo
        let ekubo = IEkuboCoreDispatcher { contract_address: ekubo_core };
        let fee: u128 = 3000; // 0.3% fee tier
        let liquidity_tokens = ekubo.deposit_liquidity(
            strk_token,
            eth_token,
            strk_amount,
            eth_amount,
            fee
        );
        
        self.emit(LiquidityDeposited {
            liquidity_tokens,
            amount0: strk_amount,
            amount1: eth_amount,
        });
        
        liquidity_tokens
    }
}

