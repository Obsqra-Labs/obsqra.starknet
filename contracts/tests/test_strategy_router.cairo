#[cfg(test)]
mod tests {
    use super::{IStrategyRouterDispatcher, IStrategyRouterDispatcherTrait};
    use starknet::ContractAddress;
    use starknet::testing::{set_caller_address, set_contract_address};
    
    fn deploy_contract() -> ContractAddress {
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        let aave: ContractAddress = starknet::contract_address_const::<0x456>();
        let lido: ContractAddress = starknet::contract_address_const::<0x789>();
        let compound: ContractAddress = starknet::contract_address_const::<0xabc>();
        let risk_engine: ContractAddress = starknet::contract_address_const::<0xdef>();
        
        let (contract_address, _) = StrategyRouter::StrategyRouter::deploy(
            @array![
                owner.into(),
                aave.into(),
                lido.into(),
                compound.into(),
                risk_engine.into()
            ],
            @array![]
        );
        contract_address
    }
    
    #[test]
    fn test_get_allocation_initial() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let (aave, lido, compound) = dispatcher.get_allocation();
        
        // Should be initialized to balanced allocation (33.33%, 33.33%, 33.34%)
        assert(aave == 3333, 'Aave should be 3333 (33.33%)');
        assert(lido == 3333, 'Lido should be 3333 (33.33%)');
        assert(compound == 3334, 'Compound should be 3334 (33.34%)');
        
        // Verify sum is 10000
        assert(aave + lido + compound == 10000, 'Sum should be 10000');
    }
    
    #[test]
    fn test_update_allocation_owner() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        set_caller_address(owner);
        
        // Update allocation
        dispatcher.update_allocation(4000, 3500, 2500);
        
        // Verify update
        let (aave, lido, compound) = dispatcher.get_allocation();
        assert(aave == 4000, 'Aave should be 40%');
        assert(lido == 3500, 'Lido should be 35%');
        assert(compound == 2500, 'Compound should be 25%');
        assert(aave + lido + compound == 10000, 'Sum should be 10000');
    }
    
    #[test]
    fn test_update_allocation_risk_engine() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let risk_engine: ContractAddress = starknet::contract_address_const::<0xdef>();
        set_caller_address(risk_engine);
        
        // Risk engine should be able to update allocation
        dispatcher.update_allocation(5000, 3000, 2000);
        
        let (aave, lido, compound) = dispatcher.get_allocation();
        assert(aave == 5000, 'Aave should be 50%');
        assert(lido == 3000, 'Lido should be 30%');
        assert(compound == 2000, 'Compound should be 20%');
    }
    
    #[test]
    #[should_panic(expected: ('Unauthorized',))]
    fn test_update_allocation_unauthorized() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let unauthorized: ContractAddress = starknet::contract_address_const::<0x999>();
        set_caller_address(unauthorized);
        
        // Should fail - unauthorized caller
        dispatcher.update_allocation(4000, 3500, 2500);
    }
    
    #[test]
    #[should_panic(expected: ('Invalid allocation',))]
    fn test_update_allocation_invalid_sum() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        set_caller_address(owner);
        
        // Should fail - doesn't sum to 10000
        dispatcher.update_allocation(4000, 3500, 2000); // Sum = 9500
    }
    
    #[test]
    fn test_update_allocation_edge_cases() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        set_caller_address(owner);
        
        // Edge case: All in one protocol (if max allows)
        dispatcher.update_allocation(10000, 0, 0);
        let (aave, lido, compound) = dispatcher.get_allocation();
        assert(aave == 10000, 'Can allocate 100% to one protocol');
        assert(lido == 0, 'Lido should be 0%');
        assert(compound == 0, 'Compound should be 0%');
        
        // Edge case: Equal split
        dispatcher.update_allocation(3333, 3333, 3334);
        let (aave2, lido2, compound2) = dispatcher.get_allocation();
        assert(aave2 == 3333 && lido2 == 3333 && compound2 == 3334, 'Equal split should work');
    }
    
    #[test]
    fn test_accrue_yields() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        // accrue_yields should not panic (even if it's a placeholder)
        dispatcher.accrue_yields();
        
        // Verify allocation unchanged
        let (aave, lido, compound) = dispatcher.get_allocation();
        assert(aave == 3333, 'Allocation should be unchanged');
    }
}
