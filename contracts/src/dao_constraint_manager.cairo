#[starknet::interface]
trait IDAOConstraintManager<TContractState> {
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
    
    #[view]
    fn validate_allocation(
        ref self: ContractState,
        aave_pct: felt252,
        lido_pct: felt252,
        compound_pct: felt252
    ) -> bool {
        let max_single = self.max_single_protocol.read();
        let min_diversification = self.min_diversification.read();
        
        // Check max single protocol
        let max_alloc = if aave_pct > lido_pct {
            if aave_pct > compound_pct {
                aave_pct
            } else {
                compound_pct
            }
        } else {
            if lido_pct > compound_pct {
                lido_pct
            } else {
                compound_pct
            }
        };
        
        if max_alloc > max_single {
            return false;
        };
        
        // Check diversification
        let diversification_count = 0;
        if aave_pct >= 1000 {
            diversification_count += 1;
        };
        if lido_pct >= 1000 {
            diversification_count += 1;
        };
        if compound_pct >= 1000 {
            diversification_count += 1;
        };
        
        if diversification_count < min_diversification {
            return false;
        };
        
        return true;
    }
    
    #[view]
    fn get_constraints(ref self: ContractState) -> (felt252, felt252, felt252, felt252) {
        return (
            self.max_single_protocol.read(),
            self.min_diversification.read(),
            self.max_volatility.read(),
            self.min_liquidity.read()
        );
    }
}

