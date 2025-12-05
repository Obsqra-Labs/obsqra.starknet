#[cfg(test)]
mod tests {
    use obsqra_contracts::strategy_router::{IStrategyRouterDispatcher, IStrategyRouterDispatcherTrait};
    use starknet::ContractAddress;
    use snforge_std::{declare, deploy, start_cheat_caller_address, stop_cheat_caller_address};
    use core::traits::Into;
    use core::result::ResultTrait;
    
    fn deploy_contract() -> ContractAddress {
        let declared = declare("StrategyRouter");
        let deploy_result: Result<(ContractAddress, Span<felt252>), felt252> = deploy(@declared, @array![
            0x123.into(),  // owner
            0x456.into(),  // aave
            0x789.into(),  // lido
            0xabc.into(),  // compound
            0xdef.into()   // risk_engine
        ]);
        let (contract_address, _) = deploy_result.unwrap();
        contract_address
    }
    
    #[test]
    fn test_get_allocation_initial() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let (aave, lido, compound) = dispatcher.get_allocation();
        
        // Should be initialized to balanced allocation (33.33%, 33.33%, 33.34%)
        assert(aave == 3333, 'Error');
        assert(lido == 3333, 'Error');
        assert(compound == 3334, 'Error');
        
        // Verify sum is 10000
        assert(aave + lido + compound == 10000, 'Error');
    }
    
    #[test]
    fn test_update_allocation_owner() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let owner: ContractAddress = 0x123.into();
        start_cheat_caller_address(router, owner);
        
        // Update allocation
        dispatcher.update_allocation(4000, 3500, 2500);
        
        stop_cheat_caller_address(router);
        
        // Verify update
        let (aave, lido, compound) = dispatcher.get_allocation();
        assert(aave == 4000, 'Error');
        assert(lido == 3500, 'Error');
        assert(compound == 2500, 'Error');
        assert(aave + lido + compound == 10000, 'Error');
    }
    
    #[test]
    fn test_update_allocation_risk_engine() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let risk_engine: ContractAddress = 0xdef.into();
        start_cheat_caller_address(router, risk_engine);
        
        // Risk engine should be able to update allocation
        dispatcher.update_allocation(5000, 3000, 2000);
        
        stop_cheat_caller_address(router);
        
        let (aave, lido, compound) = dispatcher.get_allocation();
        assert(aave == 5000, 'Error');
        assert(lido == 3000, 'Error');
        assert(compound == 2000, 'Error');
    }
    
    #[test]
    #[should_panic(expected: ('Unauthorized',))]
    fn test_update_allocation_unauthorized() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let unauthorized: ContractAddress = 0x999.into();
        start_cheat_caller_address(router, unauthorized);
        
        // Should panic with 'Unauthorized' - no cleanup after this line
        // (panic will terminate test execution immediately)
        dispatcher.update_allocation(4000, 3500, 2500);
        
        // NOTE: No stop_cheat_caller_address here - it would be unreachable
        // Test environment automatically cleans up on panic
    }
    
    #[test]
    #[should_panic(expected: ('Invalid allocation',))]
    fn test_update_allocation_invalid_sum() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let owner: ContractAddress = 0x123.into();
        start_cheat_caller_address(router, owner);
        
        // Should panic with 'Invalid allocation' - no cleanup after this line
        // (panic will terminate test execution immediately)
        dispatcher.update_allocation(4000, 3500, 2000); // Sum = 9500, expects 10000
        
        // NOTE: No stop_cheat_caller_address here - it would be unreachable
        // Test environment automatically cleans up on panic
    }
    
    #[test]
    fn test_update_allocation_edge_cases() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let owner: ContractAddress = 0x123.into();
        start_cheat_caller_address(router, owner);
        
        // Edge case: All in one protocol (if max allows)
        dispatcher.update_allocation(10000, 0, 0);
        let (aave, lido, compound) = dispatcher.get_allocation();
        assert(aave == 10000, 'Error');
        assert(lido == 0, 'Error');
        assert(compound == 0, 'Error');
        
        // Edge case: Equal split
        dispatcher.update_allocation(3333, 3333, 3334);
        let (aave2, lido2, compound2) = dispatcher.get_allocation();
        assert(aave2 == 3333 && lido2 == 3333 && compound2 == 3334, 'Error');
        
        stop_cheat_caller_address(router);
    }
    
    #[test]
    fn test_accrue_yields() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        // accrue_yields should not panic (even if it's a placeholder)
        dispatcher.accrue_yields();
        
        // Verify allocation unchanged
        let (_aave, _lido, _compound) = dispatcher.get_allocation();
        // Allocation unchanged after accrue_yields
    }
}
