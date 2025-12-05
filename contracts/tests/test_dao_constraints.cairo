#[cfg(test)]
mod tests {
    use obsqra_contracts::dao_constraint_manager::{IDAOConstraintManagerDispatcher, IDAOConstraintManagerDispatcherTrait};
    use starknet::ContractAddress;
    use snforge_std::{declare, deploy, start_cheat_caller_address, stop_cheat_caller_address};
    
    fn deploy_contract() -> ContractAddress {
        let declared = declare("DAOConstraintManager").unwrap();
        let (contract_address, _) = deploy(@declared).unwrap();
        contract_address
    }
    
    #[test]
    fn test_get_constraints() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        let (max_single, min_div, max_vol, min_liq) = dispatcher.get_constraints();
        
        assert(max_single == 6000, 'Error');
        assert(min_div == 3, 'Error');
        assert(max_vol == 5000, 'Error');
        assert(min_liq == 1000000, 'Error');
    }
    
    #[test]
    fn test_set_constraints_owner() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        start_cheat_caller_address(manager, owner);
        
        // Update constraints
        dispatcher.set_constraints(5000, 2, 4000, 2000000);
        
        stop_cheat_caller_address(manager);
        
        // Verify update
        let (max_single, min_div, max_vol, min_liq) = dispatcher.get_constraints();
        assert(max_single == 5000, 'Error');
        assert(min_div == 2, 'Error');
        assert(max_vol == 4000, 'Error');
        assert(min_liq == 2000000, 'Error');
    }
    
    #[test]
    #[should_panic(expected: ('Unauthorized',))]
    fn test_set_constraints_unauthorized() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        let unauthorized: ContractAddress = starknet::contract_address_const::<0x999>();
        start_cheat_caller_address(manager, unauthorized);
        
        // Should fail - unauthorized
        dispatcher.set_constraints(5000, 2, 4000, 2000000);
        
        stop_cheat_caller_address(manager);
    }
    
    #[test]
    fn test_validate_allocation_valid() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Valid: well-diversified, within max
        let valid = dispatcher.validate_allocation(4000, 3500, 2500);
        assert(valid == true, 'Error');
    }
    
    #[test]
    fn test_validate_allocation_invalid_max_single() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Invalid: exceeds max single (70% > 60%)
        let invalid = dispatcher.validate_allocation(7000, 2000, 1000);
        assert(invalid == false, 'Error');
    }
    
    #[test]
    fn test_validate_allocation_invalid_diversification() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Invalid: only 2 protocols >10% (need 3)
        let invalid = dispatcher.validate_allocation(8000, 1500, 500);
        assert(invalid == false, 'Error');
    }
    
    #[test]
    fn test_validate_allocation_edge_cases() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Edge case: Exactly at max single
        let valid_at_max = dispatcher.validate_allocation(6000, 2500, 1500);
        assert(valid_at_max == true, 'Error');
        
        // Edge case: Just over max
        let invalid_over_max = dispatcher.validate_allocation(6001, 2500, 1499);
        assert(invalid_over_max == false, 'Error');
        
        // Edge case: Exactly at diversification threshold
        let valid_at_threshold = dispatcher.validate_allocation(4000, 3000, 1000);
        assert(valid_at_threshold == true, 'Error');
        
        // Edge case: Just below threshold
        let invalid_below_threshold = dispatcher.validate_allocation(4000, 3000, 999);
        assert(invalid_below_threshold == false, 'Error');
    }
    
    #[test]
    fn test_validate_allocation_different_constraints() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        start_cheat_caller_address(manager, owner);
        
        // Change constraints to be more lenient
        dispatcher.set_constraints(8000, 2, 5000, 1000000);
        
        stop_cheat_caller_address(manager);
        
        // Now this should pass (only need 2 protocols >10%)
        let valid = dispatcher.validate_allocation(5000, 4000, 1000);
        assert(valid == true, 'Error');
        
        start_cheat_caller_address(manager, owner);
        
        // Change to be more strict
        dispatcher.set_constraints(4000, 3, 5000, 1000000);
        
        stop_cheat_caller_address(manager);
        
        // This should fail (max single is now 40%, we have 50%)
        let invalid = dispatcher.validate_allocation(5000, 3000, 2000);
        assert(invalid == false, 'Error');
    }
}
