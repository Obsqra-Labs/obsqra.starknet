#[starknet::interface]
pub trait IStrategyRouter<TContractState> {
    fn update_allocation(
        ref self: TContractState,
        nostra_pct: felt252,
        zklend_pct: felt252,
        ekubo_pct: felt252
    );
    
    fn get_allocation(ref self: TContractState) -> (felt252, felt252, felt252);
    
    fn accrue_yields(ref self: TContractState);
}

#[starknet::contract]
mod StrategyRouter {
    use starknet::{
        ContractAddress, get_caller_address, get_block_timestamp
    };
    use starknet::storage::StoragePointerWriteAccess;
    use starknet::storage::StoragePointerReadAccess;
    
    #[storage]
    struct Storage {
        nostra_allocation: felt252,
        zklend_allocation: felt252,
        ekubo_allocation: felt252,
        nostra_address: ContractAddress,
        zklend_address: ContractAddress,
        ekubo_address: ContractAddress,
        owner: ContractAddress,
        risk_engine: ContractAddress,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        AllocationUpdated: AllocationUpdated,
        YieldsAccrued: YieldsAccrued,
    }
    
    #[derive(Drop, starknet::Event)]
    struct AllocationUpdated {
        nostra_pct: felt252,
        zklend_pct: felt252,
        ekubo_pct: felt252,
        timestamp: u64,
    }
    
    #[derive(Drop, starknet::Event)]
    struct YieldsAccrued {
        total_yield: felt252,
        timestamp: u64,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        nostra_address: ContractAddress,
        zklend_address: ContractAddress,
        ekubo_address: ContractAddress,
        risk_engine: ContractAddress
    ) {
        self.owner.write(owner);
        self.nostra_address.write(nostra_address);
        self.zklend_address.write(zklend_address);
        self.ekubo_address.write(ekubo_address);
        self.risk_engine.write(risk_engine);
        
        // Initialize with balanced allocation
        self.nostra_allocation.write(3333);
        self.zklend_allocation.write(3333);
        self.ekubo_allocation.write(3334);
    }
    
    #[external(v0)]
    fn update_allocation(
        ref self: ContractState,
        nostra_pct: felt252,
        zklend_pct: felt252,
        ekubo_pct: felt252
    ) {
        // Verify caller is authorized
        let caller = get_caller_address();
        let owner = self.owner.read();
        let risk_engine = self.risk_engine.read();
        
        assert(caller == owner || caller == risk_engine, 'Unauthorized');
        
        // Verify percentages sum to 10000 (100%)
        assert(nostra_pct + zklend_pct + ekubo_pct == 10000, 'Invalid allocation');
        
        // Update allocations
        self.nostra_allocation.write(nostra_pct);
        self.zklend_allocation.write(zklend_pct);
        self.ekubo_allocation.write(ekubo_pct);
        
        // Emit event
        self.emit(AllocationUpdated {
            nostra_pct,
            zklend_pct,
            ekubo_pct,
            timestamp: get_block_timestamp(),
        });
    }
    
    #[external(v0)]
    fn get_allocation(ref self: ContractState) -> (felt252, felt252, felt252) {
        (
            self.nostra_allocation.read(),
            self.zklend_allocation.read(),
            self.ekubo_allocation.read()
        )
    }
    
    #[external(v0)]
    fn accrue_yields(ref self: ContractState) {
        // TODO: Implement yield accrual logic
        let total_yield = 0;
        
        self.emit(YieldsAccrued {
            total_yield,
            timestamp: get_block_timestamp(),
        });
    }
}

