use starknet::ContractAddress;

#[starknet::interface]
pub trait IPool<TContractState> {
    // Pool info
    fn get_name(self: @TContractState) -> ByteArray;
    fn get_pool_id(self: @TContractState) -> felt252;
    fn get_cap(self: @TContractState) -> u256;
    fn get_total_deposits(self: @TContractState) -> u256;
    fn get_allocation(self: @TContractState) -> (felt252, felt252);
    
    // User operations
    fn deposit(ref self: TContractState, amount: u256);
    fn withdraw(ref self: TContractState, amount: u256) -> u256;
    fn get_user_balance(self: @TContractState, user: ContractAddress) -> u256;
    
    // Pool management (Obsqra/Risk Engine only)
    fn rebalance(ref self: TContractState, new_jediswap_pct: felt252, new_ekubo_pct: felt252);
    fn update_cap(ref self: TContractState, new_cap: u256);
    fn pause(ref self: TContractState);
    fn unpause(ref self: TContractState);
    fn is_paused(self: @TContractState) -> bool;
}

#[starknet::contract]
mod Pool {
    use starknet::{
        ContractAddress, get_caller_address, get_contract_address, get_block_timestamp,
        storage::{
            Map, StoragePointerReadAccess, StoragePointerWriteAccess,
            StoragePathEntry
        }
    };
    use super::super::interfaces::erc20::{IERC20Dispatcher, IERC20DispatcherTrait};
    
    #[storage]
    struct Storage {
        // Pool metadata
        pool_id: felt252,
        name: ByteArray,
        cap: u256,  // Maximum deposits (e.g., $100K in STRK)
        total_deposits: u256,
        
        // Allocation percentages (basis points, 10000 = 100%)
        jediswap_allocation: felt252,
        ekubo_allocation: felt252,
        
        // User balances
        user_balances: Map<ContractAddress, u256>,
        
        // Protocol addresses
        jediswap_router: ContractAddress,
        ekubo_core: ContractAddress,
        
        // Asset token (STRK)
        asset_token: ContractAddress,
        
        // Governance
        factory: ContractAddress,  // PoolFactory that created this
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        
        // State
        paused: bool,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        Deposit: Deposit,
        Withdrawal: Withdrawal,
        Rebalanced: Rebalanced,
        CapUpdated: CapUpdated,
        Paused: Paused,
        Unpaused: Unpaused,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Deposit {
        user: ContractAddress,
        amount: u256,
        new_balance: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Withdrawal {
        user: ContractAddress,
        amount: u256,
        new_balance: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Rebalanced {
        jediswap_pct: felt252,
        ekubo_pct: felt252,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct CapUpdated {
        old_cap: u256,
        new_cap: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Paused {
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Unpaused {
        timestamp: u64,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        pool_id: felt252,
        name: ByteArray,
        cap: u256,
        jediswap_pct: felt252,
        ekubo_pct: felt252,
        factory: ContractAddress,
        jediswap_router: ContractAddress,
        ekubo_core: ContractAddress,
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        asset_token: ContractAddress
    ) {
        self.pool_id.write(pool_id);
        self.name.write(name);
        self.cap.write(cap);
        self.jediswap_allocation.write(jediswap_pct);
        self.ekubo_allocation.write(ekubo_pct);
        self.factory.write(factory);
        self.jediswap_router.write(jediswap_router);
        self.ekubo_core.write(ekubo_core);
        self.risk_engine.write(risk_engine);
        self.dao_manager.write(dao_manager);
        self.asset_token.write(asset_token);
        self.total_deposits.write(0);
        self.paused.write(false);
    }
    
    #[abi(embed_v0)]
    impl PoolImpl of super::IPool<ContractState> {
        fn get_name(self: @ContractState) -> ByteArray {
            self.name.read()
        }
        
        fn get_pool_id(self: @ContractState) -> felt252 {
            self.pool_id.read()
        }
        
        fn get_cap(self: @ContractState) -> u256 {
            self.cap.read()
        }
        
        fn get_total_deposits(self: @ContractState) -> u256 {
            self.total_deposits.read()
        }
        
        fn get_allocation(self: @ContractState) -> (felt252, felt252) {
            (
                self.jediswap_allocation.read(),
                self.ekubo_allocation.read()
            )
        }
        
        fn deposit(ref self: ContractState, amount: u256) {
            // Check if paused
            assert(!self.paused.read(), 'Pool is paused');
            
            let caller = get_caller_address();
            let contract_addr = get_contract_address();
            
            // Check cap
            let total = self.total_deposits.read();
            let new_total = total + amount;
            let cap = self.cap.read();
            assert(new_total <= cap, 'Pool cap exceeded');
            
            // Transfer tokens from user to this contract
            let asset_token = self.asset_token.read();
            let token = IERC20Dispatcher { contract_address: asset_token };
            let success = token.transfer_from(caller, contract_addr, amount);
            assert(success, 'Transfer failed');
            
            // Update user balance
            let user_balance = self.user_balances.entry(caller).read();
            self.user_balances.entry(caller).write(user_balance + amount);
            
            // Update total deposits
            self.total_deposits.write(new_total);
            
            self.emit(Deposit {
                user: caller,
                amount,
                new_balance: user_balance + amount,
                timestamp: get_block_timestamp(),
            });
        }
        
        fn withdraw(ref self: ContractState, amount: u256) -> u256 {
            // Check if paused
            assert(!self.paused.read(), 'Pool is paused');
            
            let caller = get_caller_address();
            
            // Check user balance
            let user_balance = self.user_balances.entry(caller).read();
            assert(user_balance >= amount, 'Insufficient balance');
            
            // Transfer tokens to user
            let asset_token = self.asset_token.read();
            let token = IERC20Dispatcher { contract_address: asset_token };
            let success = token.transfer(caller, amount);
            assert(success, 'Transfer failed');
            
            // Update user balance
            self.user_balances.entry(caller).write(user_balance - amount);
            
            // Update total deposits
            let total = self.total_deposits.read();
            self.total_deposits.write(total - amount);
            
            self.emit(Withdrawal {
                user: caller,
                amount,
                new_balance: user_balance - amount,
                timestamp: get_block_timestamp(),
            });
            
            amount
        }
        
        fn get_user_balance(self: @ContractState, user: ContractAddress) -> u256 {
            self.user_balances.entry(user).read()
        }
        
        fn rebalance(
            ref self: ContractState,
            new_jediswap_pct: felt252,
            new_ekubo_pct: felt252
        ) {
            // Only factory or risk engine can rebalance
            let caller = get_caller_address();
            let factory = self.factory.read();
            let risk_engine = self.risk_engine.read();
            
            assert(caller == factory || caller == risk_engine, 'Unauthorized');
            
            // Verify percentages sum to 10000 (100%)
            assert(new_jediswap_pct + new_ekubo_pct == 10000, 'Allocation must sum to 100%');
            
            // Update allocations
            self.jediswap_allocation.write(new_jediswap_pct);
            self.ekubo_allocation.write(new_ekubo_pct);
            
            self.emit(Rebalanced {
                jediswap_pct: new_jediswap_pct,
                ekubo_pct: new_ekubo_pct,
                timestamp: get_block_timestamp(),
            });
        }
        
        fn update_cap(ref self: ContractState, new_cap: u256) {
            // Only factory can update cap
            let caller = get_caller_address();
            let factory = self.factory.read();
            assert(caller == factory, 'Only factory');
            
            let old_cap = self.cap.read();
            self.cap.write(new_cap);
            
            self.emit(CapUpdated {
                old_cap,
                new_cap,
                timestamp: get_block_timestamp(),
            });
        }
        
        fn pause(ref self: ContractState) {
            // Only factory can pause
            let caller = get_caller_address();
            let factory = self.factory.read();
            assert(caller == factory, 'Only factory');
            
            self.paused.write(true);
            
            self.emit(Paused {
                timestamp: get_block_timestamp(),
            });
        }
        
        fn unpause(ref self: ContractState) {
            // Only factory can unpause
            let caller = get_caller_address();
            let factory = self.factory.read();
            assert(caller == factory, 'Only factory');
            
            self.paused.write(false);
            
            self.emit(Unpaused {
                timestamp: get_block_timestamp(),
            });
        }
        
        fn is_paused(self: @ContractState) -> bool {
            self.paused.read()
        }
    }
}

