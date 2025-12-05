#[starknet::interface]
pub trait IDAOConstraintManager<TContractState> {
    fn set_constraints(
        ref self: TContractState,
        max_single: felt252,
        min_diversification: felt252,
        max_volatility: felt252,
        min_liquidity: felt252
    );
    
    fn validate_allocation(
        ref self: TContractState,
        aave_pct: felt252,
        lido_pct: felt252,
        compound_pct: felt252
    ) -> bool;
    
    fn get_constraints(ref self: TContractState) -> (felt252, felt252, felt252, felt252);
}

#[starknet::contract]
mod DAOConstraintManager {
    use starknet::ContractAddress;
    use starknet::get_caller_address;
    use starknet::storage::StoragePointerWriteAccess;
    use starknet::storage::StoragePointerReadAccess;
    use core::traits::Into;
    
    #[storage]
    struct Storage {
        max_single_protocol: felt252,
        min_diversification: felt252,
        max_volatility: felt252,
        min_liquidity: felt252,
        owner: ContractAddress,
    }
    
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        ConstraintsUpdated: ConstraintsUpdated,
    }
    
    #[derive(Drop, starknet::Event)]
    struct ConstraintsUpdated {
        max_single: felt252,
        min_diversification: felt252,
        max_volatility: felt252,
        min_liquidity: felt252,
    }
    
    #[constructor]
    fn constructor(
        ref self: ContractState,
        owner: ContractAddress,
        max_single: felt252,
        min_diversification: felt252,
        max_volatility: felt252,
        min_liquidity: felt252
    ) {
        self.owner.write(owner);
        self.max_single_protocol.write(max_single);
        self.min_diversification.write(min_diversification);
        self.max_volatility.write(max_volatility);
        self.min_liquidity.write(min_liquidity);
    }
    
    #[external(v0)]
    fn set_constraints(
        ref self: ContractState,
        max_single: felt252,
        min_diversification: felt252,
        max_volatility: felt252,
        min_liquidity: felt252
    ) {
        let owner = self.owner.read();
        assert(get_caller_address() == owner, 'Unauthorized');
        
        self.max_single_protocol.write(max_single);
        self.min_diversification.write(min_diversification);
        self.max_volatility.write(max_volatility);
        self.min_liquidity.write(min_liquidity);
        
        self.emit(ConstraintsUpdated {
            max_single,
            min_diversification,
            max_volatility,
            min_liquidity,
        });
    }
    
    #[external(v0)]
    fn validate_allocation(
        ref self: ContractState,
        aave_pct: felt252,
        lido_pct: felt252,
        compound_pct: felt252
    ) -> bool {
        let max_single = self.max_single_protocol.read();
        let min_diversification = self.min_diversification.read();
        
        // Check max single protocol using u256 comparisons
        let aave_u256: u256 = aave_pct.into();
        let lido_u256: u256 = lido_pct.into();
        let compound_u256: u256 = compound_pct.into();
        
        let max_alloc = if aave_u256 > lido_u256 {
            if aave_u256 > compound_u256 {
                aave_pct
            } else {
                compound_pct
            }
        } else {
            if lido_u256 > compound_u256 {
                lido_pct
            } else {
                compound_pct
            }
        };
        
        // Compare using u256
        let max_alloc_u256: u256 = max_alloc.into();
        let max_single_u256: u256 = max_single.into();
        if max_alloc_u256 > max_single_u256 {
            return false;
        };
        
        // Check diversification (>= 1000 basis points = 10%)
        let threshold_u256: u256 = 1000_u256;
        let mut diversification_count = 0;
        if aave_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        if lido_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        if compound_u256 >= threshold_u256 {
            diversification_count += 1;
        };
        
        // Compare using u256
        let min_div_u256: u256 = min_diversification.into();
        let count_u256: u256 = diversification_count.into();
        if count_u256 < min_div_u256 {
            return false;
        };
        
        true
    }
    
    #[external(v0)]
    fn get_constraints(ref self: ContractState) -> (felt252, felt252, felt252, felt252) {
        (
            self.max_single_protocol.read(),
            self.min_diversification.read(),
            self.max_volatility.read(),
            self.min_liquidity.read()
        )
    }
}

