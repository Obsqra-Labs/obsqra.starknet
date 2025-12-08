use starknet::ContractAddress;

#[starknet::interface]
pub trait IStrategyRouterV2<TContractState> {
    // Allocation management
    fn update_allocation(
        ref self: TContractState,
        jediswap_pct: felt252,
        ekubo_pct: felt252
    );
    fn get_allocation(self: @TContractState) -> (felt252, felt252);
    
    // User deposits and withdrawals
    fn deposit(ref self: TContractState, amount: u256);
    fn withdraw(ref self: TContractState, amount: u256) -> u256;
    fn get_user_balance(self: @TContractState, user: ContractAddress) -> u256;
    
    // Yield and rebalancing
    fn accrue_yields(ref self: TContractState) -> u256;
    fn rebalance(ref self: TContractState);
    
    // Protocol info
    fn get_protocol_addresses(self: @TContractState) -> (ContractAddress, ContractAddress);
    fn get_total_value_locked(self: @TContractState) -> u256;
}

#[starknet::contract]
mod StrategyRouterV2 {
    use starknet::{
        ContractAddress, get_caller_address, get_contract_address, get_block_timestamp
    };
    use starknet::storage::{StoragePointerWriteAccess, StoragePointerReadAccess};
    use super::super::interfaces::erc20::{IERC20Dispatcher, IERC20DispatcherTrait};
    
    #[storage]
    struct Storage {
        // Allocation percentages (basis points, 10000 = 100%)
        jediswap_allocation: felt252,
        ekubo_allocation: felt252,
        
        // Protocol addresses
        jediswap_router: ContractAddress,
        ekubo_core: ContractAddress,
        
        // Total deposits (simplified - not tracking per-user for now)
        total_deposits: u256,
        
        // Asset token (STRK)
        asset_token: ContractAddress,
        
        // Governance
        owner: ContractAddress,
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        
        // Performance tracking
        last_decision_id: felt252,  // Links to RiskEngine decision
        jediswap_position_value: u256,
        ekubo_position_value: u256,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        AllocationUpdated: AllocationUpdated,
        Deposit: Deposit,
        Withdrawal: Withdrawal,
        YieldsAccrued: YieldsAccrued,
        Rebalanced: Rebalanced,
        PerformanceLinked: PerformanceLinked,
    }
    
    #[derive(Drop, starknet::Event)]
    struct AllocationUpdated {
        jediswap_pct: felt252,
        ekubo_pct: felt252,
        timestamp: u64,
        decision_id: felt252,  // Links to RiskEngine decision
    }
    
    #[derive(Drop, starknet::Event)]
    struct PerformanceLinked {
        decision_id: felt252,
        total_value: u256,
        jediswap_value: u256,
        ekubo_value: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Deposit {
        user: ContractAddress,
        amount: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Withdrawal {
        user: ContractAddress,
        amount: u256,
        yield_amount: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct YieldsAccrued {
        total_yield: u256,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct Rebalanced {
        jediswap_value: u256,
        ekubo_value: u256,
        timestamp: u64,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        jediswap_router: ContractAddress,
        ekubo_core: ContractAddress,
        risk_engine: ContractAddress,
        dao_manager: ContractAddress,
        asset_token: ContractAddress
    ) {
        self.owner.write(owner);
        self.jediswap_router.write(jediswap_router);
        self.ekubo_core.write(ekubo_core);
        self.risk_engine.write(risk_engine);
        self.dao_manager.write(dao_manager);
        self.asset_token.write(asset_token);
        
        // Initialize with 50/50 allocation
        self.jediswap_allocation.write(5000); // 50%
        self.ekubo_allocation.write(5000);    // 50%
        
        self.total_deposits.write(0);
        self.last_decision_id.write(0);
        self.jediswap_position_value.write(0_u256);
        self.ekubo_position_value.write(0_u256);
    }
    
    #[abi(embed_v0)]
    impl StrategyRouterV2Impl of super::IStrategyRouterV2<ContractState> {
        fn update_allocation(
            ref self: ContractState,
            jediswap_pct: felt252,
            ekubo_pct: felt252
        ) {
            // Verify caller is authorized
            let caller = get_caller_address();
            let owner = self.owner.read();
            let risk_engine = self.risk_engine.read();
            
            assert(caller == owner || caller == risk_engine, 'Unauthorized');
            
            // Verify percentages sum to 10000 (100%)
            assert(jediswap_pct + ekubo_pct == 10000, 'Allocation must sum to 100%');
            
            // Update allocations
            self.jediswap_allocation.write(jediswap_pct);
            self.ekubo_allocation.write(ekubo_pct);
            
            // Note: decision_id will be set by RiskEngine after it creates the decision
            // For now, we'll use 0 as placeholder - RiskEngine will update it
            let decision_id = self.last_decision_id.read();
            
            // Emit event
            self.emit(AllocationUpdated {
                jediswap_pct,
                ekubo_pct,
                timestamp: get_block_timestamp(),
                decision_id,
            });
        }
        
        fn get_allocation(self: @ContractState) -> (felt252, felt252) {
            (
                self.jediswap_allocation.read(),
                self.ekubo_allocation.read()
            )
        }
        
        fn deposit(ref self: ContractState, amount: u256) {
            let caller = get_caller_address();
            let contract_addr = get_contract_address();
            let asset_token = self.asset_token.read();
            
            // Transfer tokens from user to this contract
            let token = IERC20Dispatcher { contract_address: asset_token };
            let success = token.transfer_from(caller, contract_addr, amount);
            assert(success, 'Transfer failed');
            
            // Update total deposits
            let total = self.total_deposits.read();
            self.total_deposits.write(total + amount);
            
            // TODO: Actually deposit to protocols based on allocation
            // This would call JediSwap.add_liquidity() and Ekubo.deposit_liquidity()
            
            self.emit(Deposit {
                user: caller,
                amount,
                timestamp: get_block_timestamp(),
            });
        }
        
        fn withdraw(ref self: ContractState, amount: u256) -> u256 {
            let caller = get_caller_address();
            let total = self.total_deposits.read();
            
            assert(total >= amount, 'Insufficient balance');
            
            // TODO: Withdraw from protocols proportionally
            // This would call protocol withdraw functions
            
            // For now, simple withdrawal without yields
            let asset_token = self.asset_token.read();
            let token = IERC20Dispatcher { contract_address: asset_token };
            let success = token.transfer(caller, amount);
            assert(success, 'Transfer failed');
            
            // Update total deposits
            self.total_deposits.write(total - amount);
            
            self.emit(Withdrawal {
                user: caller,
                amount,
                yield_amount: 0,
                timestamp: get_block_timestamp(),
            });
            
            amount
        }
        
        fn get_user_balance(self: @ContractState, user: ContractAddress) -> u256 {
            // Simplified: returns total deposits (not tracking per-user yet)
            self.total_deposits.read()
        }
        
        fn accrue_yields(ref self: ContractState) -> u256 {
            // TODO: Query actual yields from protocols
            // For now, return 0
            let total_yield = 0_u256;
            
            self.emit(YieldsAccrued {
                total_yield,
                timestamp: get_block_timestamp(),
            });
            
            total_yield
        }
        
        fn rebalance(ref self: ContractState) {
            // TODO: Implement rebalancing logic
            // 1. Calculate current positions in each protocol
            // 2. Calculate target positions based on allocation
            // 3. Move funds as needed
            
            let jediswap_value = 0_u256;
            let ekubo_value = 0_u256;
            
            self.emit(Rebalanced {
                jediswap_value,
                ekubo_value,
                timestamp: get_block_timestamp(),
            });
        }
        
        fn get_protocol_addresses(self: @ContractState) -> (ContractAddress, ContractAddress) {
            (
                self.jediswap_router.read(),
                self.ekubo_core.read()
            )
        }
        
        fn get_total_value_locked(self: @ContractState) -> u256 {
            self.total_deposits.read()
        }
    }
    
    // NEW: Performance tracking functions
    #[external(v0)]
    fn link_decision_id(
        ref self: ContractState,
        decision_id: felt252,
    ) {
        // Only RiskEngine can link decision IDs
        let caller = get_caller_address();
        let risk_engine = self.risk_engine.read();
        assert(caller == risk_engine, 'Unauthorized');
        
        self.last_decision_id.write(decision_id);
    }
    
    #[external(v0)]
    fn get_current_positions(
        ref self: ContractState,
    ) -> (u256, u256) {
        // Returns current position values in each protocol
        // TODO: Query actual positions from JediSwap/Ekubo contracts
        (
            self.jediswap_position_value.read(),
            self.ekubo_position_value.read(),
        )
    }
    
    #[external(v0)]
    fn update_position_values(
        ref self: ContractState,
        jediswap_value: u256,
        ekubo_value: u256,
    ) {
        // Only RiskEngine can update position values
        let caller = get_caller_address();
        let risk_engine = self.risk_engine.read();
        assert(caller == risk_engine, 'Unauthorized');
        
        self.jediswap_position_value.write(jediswap_value);
        self.ekubo_position_value.write(ekubo_value);
        
        // Emit performance linked event
        let decision_id = self.last_decision_id.read();
        let total_value = jediswap_value + ekubo_value;
        
        self.emit(PerformanceLinked {
            decision_id,
            total_value,
            jediswap_value,
            ekubo_value,
            timestamp: get_block_timestamp(),
        });
    }
    
    #[external(v0)]
    fn set_risk_engine(
        ref self: ContractState,
        new_risk_engine: ContractAddress,
    ) {
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        self.risk_engine.write(new_risk_engine);
    }
}

