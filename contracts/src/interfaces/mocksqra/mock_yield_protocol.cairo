use starknet::ContractAddress;
use starknet::get_caller_address;
use starknet::get_contract_address;
use starknet::get_block_timestamp;
use super::mocksqra_token::IMocksqraTokenDispatcher;
use super::mocksqra_token::IMocksqraTokenDispatcherTrait;

#[starknet::interface]
pub trait IMockYieldProtocol<TContractState> {
    // Deposit tokens
    fn deposit(ref self: TContractState, amount: u256);
    
    // Withdraw tokens + yield
    fn withdraw(ref self: TContractState, amount: u256) -> u256;
    
    // Get user balance (deposit + accrued yield)
    fn get_balance(self: @TContractState, user: ContractAddress) -> u256;
    
    // Get total deposits (not including yield)
    fn get_total_deposits(self: @TContractState) -> u256;
    
    // Get treasury balance (tokens available for yield)
    fn get_treasury_balance(self: @TContractState) -> u256;
    
    // Admin: Fund treasury with tokens
    fn fund_treasury(ref self: TContractState, amount: u256);
    
    // Admin: Set yield rate per second (basis points per second, e.g., 1 = 0.01% per second)
    // For testing: 1 bps/second = ~315% APY (very high for testing)
    fn set_yield_rate_per_second(ref self: TContractState, rate_bps_per_second: u256);
    
    // Get yield rate per second
    fn get_yield_rate_per_second(self: @TContractState) -> u256;
    
    // Calculate yield for a user (virtual - doesn't transfer tokens)
    fn calculate_yield(self: @TContractState, user: ContractAddress) -> u256;
    
    // Accrue and collect yield (transfers yield tokens from treasury)
    fn accrue_yield(ref self: TContractState) -> u256;
    
    // Admin: Set time multiplier for testing (e.g., 3600 = 1 second = 1 hour of yield)
    fn set_time_multiplier(ref self: TContractState, multiplier: u256);
    
    // Get time multiplier
    fn get_time_multiplier(self: @TContractState) -> u256;
}

#[starknet::contract]
mod MockYieldProtocol {
    use starknet::{
        ContractAddress, get_caller_address, get_contract_address, get_block_timestamp,
        storage::Map
    };
    use core::num::traits::Zero;

    #[storage]
    struct Storage {
        token: ContractAddress,
        admin: ContractAddress,
        treasury_balance: u256,
        balances: Map<ContractAddress, u256>,  // User deposits
        deposit_timestamps: Map<ContractAddress, u64>,  // When user deposited
        yield_rate_bps_per_second: u256,  // Yield rate in basis points per second
        time_multiplier: u256,  // Multiplier for testing (makes time pass faster)
        total_deposits: u256,
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        token: ContractAddress,
        yield_rate_bps_per_second: u256
    ) {
        self.token.write(token);
        self.admin.write(get_caller_address());
        self.treasury_balance.write(0);
        // Default: 1 bps per second = ~315% APY (very high for testing)
        // This means 0.01% yield per second
        self.yield_rate_bps_per_second.write(yield_rate_bps_per_second);
        self.time_multiplier.write(1);  // Default: no multiplier
        self.total_deposits.write(0);
    }

    #[abi(embed_v0)]
    impl IMockYieldProtocolImpl of super::IMockYieldProtocol<ContractState> {
        fn deposit(ref self: ContractState, amount: u256) {
            let caller = get_caller_address();
            let token = IMocksqraTokenDispatcher { contract_address: self.token.read() };
            
            // Transfer tokens from user to protocol
            let success = token.transfer_from(caller, get_contract_address(), amount);
            assert(success, 'Transfer failed');
            
            // Update balance and timestamp
            let current_balance = self.balances.read(caller);
            self.balances.write(caller, current_balance + amount);
            self.deposit_timestamps.write(caller, get_block_timestamp());
            
            // Update total deposits
            self.total_deposits.write(self.total_deposits.read() + amount);
        }

        fn withdraw(ref self: ContractState, amount: u256) -> u256 {
            let caller = get_caller_address();
            let balance = self.balances.read(caller);
            assert(amount <= balance, 'Insufficient balance');
            
            // Calculate yield
            let yield_amount = self.calculate_yield(caller);
            let total_to_pay = amount + yield_amount;
            
            // Check treasury has enough
            let treasury = self.treasury_balance.read();
            assert(total_to_pay <= treasury, 'Insufficient treasury');
            
            // Transfer tokens to user
            let token = IMocksqraTokenDispatcher { contract_address: self.token.read() };
            let success = token.transfer(caller, total_to_pay);
            assert(success, 'Transfer failed');
            
            // Update balances
            self.balances.write(caller, balance - amount);
            self.treasury_balance.write(treasury - total_to_pay);
            self.deposit_timestamps.write(caller, get_block_timestamp()); // Reset timestamp
            self.total_deposits.write(self.total_deposits.read() - amount);
            
            total_to_pay
        }

        fn get_balance(self: @ContractState, user: ContractAddress) -> u256 {
            let balance = self.balances.read(user);
            let yield_amount = self.calculate_yield(user);
            balance + yield_amount
        }

        fn get_total_deposits(self: @ContractState) -> u256 {
            self.total_deposits.read()
        }

        fn get_treasury_balance(self: @ContractState) -> u256 {
            self.treasury_balance.read()
        }

        fn fund_treasury(ref self: ContractState, amount: u256) {
            let caller = get_caller_address();
            assert(caller == self.admin.read(), 'Only admin can fund treasury');
            
            let token = IMocksqraTokenDispatcher { contract_address: self.token.read() };
            let success = token.transfer_from(caller, get_contract_address(), amount);
            assert(success, 'Transfer failed');
            
            self.treasury_balance.write(self.treasury_balance.read() + amount);
        }

        fn set_yield_rate_per_second(ref self: ContractState, rate_bps_per_second: u256) {
            let caller = get_caller_address();
            assert(caller == self.admin.read(), 'Only admin can set yield rate');
            // Allow up to 100 bps per second (1% per second = very high for testing)
            assert(rate_bps_per_second <= 10000, 'Rate cannot exceed 100% per second');
            
            self.yield_rate_bps_per_second.write(rate_bps_per_second);
        }

        fn get_yield_rate_per_second(self: @ContractState) -> u256 {
            self.yield_rate_bps_per_second.read()
        }

        fn calculate_yield(self: @ContractState, user: ContractAddress) -> u256 {
            let balance = self.balances.read(user);
            if balance == 0 {
                return 0;
            }
            
            let deposit_time = self.deposit_timestamps.read(user);
            let current_time = get_block_timestamp();
            
            // Handle case where timestamp hasn't been set
            if deposit_time == 0 {
                return 0;
            }
            
            let time_elapsed_seconds = current_time - deposit_time;
            let time_multiplier = self.time_multiplier.read();
            // Apply time multiplier (for testing: make time pass faster)
            let adjusted_time = time_elapsed_seconds * time_multiplier;
            
            let rate_bps_per_second = self.yield_rate_bps_per_second.read();
            
            // Yield = balance * (rate_bps_per_second / 10000) * adjusted_time
            // This gives yield as a percentage of balance per second
            let yield_amount = (balance * rate_bps_per_second * adjusted_time) / 10000;
            
            yield_amount
        }

        fn accrue_yield(ref self: ContractState) -> u256 {
            // This function can be called to "collect" yield
            // In a real protocol, this would collect fees from liquidity pools
            // Here, it just returns the calculated yield (actual payout happens on withdraw)
            let caller = get_caller_address();
            self.calculate_yield(caller)
        }

        fn set_time_multiplier(ref self: ContractState, multiplier: u256) {
            let caller = get_caller_address();
            assert(caller == self.admin.read(), 'Only admin can set time multiplier');
            // Allow up to 1 million multiplier (for extreme testing)
            assert(multiplier > 0 && multiplier <= 1000000, 'Invalid multiplier');
            
            self.time_multiplier.write(multiplier);
        }

        fn get_time_multiplier(self: @ContractState) -> u256 {
            self.time_multiplier.read()
        }
    }
}

