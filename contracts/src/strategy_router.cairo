#[starknet::interface]
pub trait IStrategyRouter<TContractState> {
    fn update_allocation(
        ref self: TContractState,
        aave_pct: felt252,
        lido_pct: felt252,
        compound_pct: felt252
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
        aave_allocation: felt252,
        lido_allocation: felt252,
        compound_allocation: felt252,
        aave_address: ContractAddress,
        lido_address: ContractAddress,
        compound_address: ContractAddress,
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
        aave_pct: felt252,
        lido_pct: felt252,
        compound_pct: felt252,
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
        aave_address: ContractAddress,
        lido_address: ContractAddress,
        compound_address: ContractAddress,
        risk_engine: ContractAddress
    ) {
        self.owner.write(owner);
        self.aave_address.write(aave_address);
        self.lido_address.write(lido_address);
        self.compound_address.write(compound_address);
        self.risk_engine.write(risk_engine);
        
        // Initialize with balanced allocation
        self.aave_allocation.write(3333);
        self.lido_allocation.write(3333);
        self.compound_allocation.write(3334);
    }
    
    #[external(v0)]
    fn update_allocation(
        ref self: ContractState,
        aave_pct: felt252,
        lido_pct: felt252,
        compound_pct: felt252
    ) {
        // Verify caller is authorized
        let caller = get_caller_address();
        let owner = self.owner.read();
        let risk_engine = self.risk_engine.read();
        
        assert(caller == owner || caller == risk_engine, 'Unauthorized');
        
        // Verify percentages sum to 10000 (100%)
        assert(aave_pct + lido_pct + compound_pct == 10000, 'Invalid allocation');
        
        // Update allocations
        self.aave_allocation.write(aave_pct);
        self.lido_allocation.write(lido_pct);
        self.compound_allocation.write(compound_pct);
        
        // Emit event
        self.emit(AllocationUpdated {
            aave_pct,
            lido_pct,
            compound_pct,
            timestamp: get_block_timestamp(),
        });
    }
    
    #[external(v0)]
    fn get_allocation(ref self: ContractState) -> (felt252, felt252, felt252) {
        (
            self.aave_allocation.read(),
            self.lido_allocation.read(),
            self.compound_allocation.read()
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

