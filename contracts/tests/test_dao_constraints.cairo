#[cfg(test)]
mod tests {
    use super::{IDAOConstraintManagerDispatcher, IDAOConstraintManagerDispatcherTrait};
    use starknet::ContractAddress;
    use starknet::testing::{set_caller_address, set_contract_address};
    
    fn deploy_contract() -> ContractAddress {
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        let (contract_address, _) = DAOConstraintManager::DAOConstraintManager::deploy(
            @array![
                owner.into(),
                6000.into(),  // max_single (60%)
                3.into(),     // min_diversification (3 protocols)
                5000.into(),  // max_volatility
                1000000.into() // min_liquidity
            ],
            @array![]
        );
        contract_address
    }
    
    #[test]
    fn test_get_constraints() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        let (max_single, min_div, max_vol, min_liq) = dispatcher.get_constraints();
        
        assert(max_single == 6000, 'Max single should be 60%');
        assert(min_div == 3, 'Min diversification should be 3');
        assert(max_vol == 5000, 'Max volatility should be 5000');
        assert(min_liq == 1000000, 'Min liquidity should be 1000000');
    }
    
    #[test]
    fn test_set_constraints_owner() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        set_caller_address(owner);
        
        // Update constraints
        dispatcher.set_constraints(5000, 2, 4000, 2000000);
        
        // Verify update
        let (max_single, min_div, max_vol, min_liq) = dispatcher.get_constraints();
        assert(max_single == 5000, 'Max single should be updated to 50%');
        assert(min_div == 2, 'Min diversification should be updated to 2');
        assert(max_vol == 4000, 'Max volatility should be updated');
        assert(min_liq == 2000000, 'Min liquidity should be updated');
    }
    
    #[test]
    #[should_panic(expected: ('Unauthorized',))]
    fn test_set_constraints_unauthorized() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        let unauthorized: ContractAddress = starknet::contract_address_const::<0x999>();
        set_caller_address(unauthorized);
        
        // Should fail - unauthorized
        dispatcher.set_constraints(5000, 2, 4000, 2000000);
    }
    
    #[test]
    fn test_validate_allocation_valid() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Valid: well-diversified, within max
        let valid = dispatcher.validate_allocation(4000, 3500, 2500);
        assert(valid == true, 'Valid allocation should pass');
    }
    
    #[test]
    fn test_validate_allocation_invalid_max_single() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Invalid: exceeds max single (70% > 60%)
        let invalid = dispatcher.validate_allocation(7000, 2000, 1000);
        assert(invalid == false, 'Exceeding max single should fail');
    }
    
    #[test]
    fn test_validate_allocation_invalid_diversification() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Invalid: only 2 protocols >10% (need 3)
        let invalid = dispatcher.validate_allocation(8000, 1500, 500);
        assert(invalid == false, 'Insufficient diversification should fail');
    }
    
    #[test]
    fn test_validate_allocation_edge_cases() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Edge case: Exactly at max single
        let valid_at_max = dispatcher.validate_allocation(6000, 2500, 1500);
        assert(valid_at_max == true, 'Exactly at max should be valid');
        
        // Edge case: Just over max
        let invalid_over_max = dispatcher.validate_allocation(6001, 2500, 1499);
        assert(invalid_over_max == false, 'Just over max should fail');
        
        // Edge case: Exactly at diversification threshold
        let valid_at_threshold = dispatcher.validate_allocation(4000, 3000, 1000);
        assert(valid_at_threshold == true, 'Exactly at threshold should be valid');
        
        // Edge case: Just below threshold
        let invalid_below_threshold = dispatcher.validate_allocation(4000, 3000, 999);
        assert(invalid_below_threshold == false, 'Just below threshold should fail');
    }
    
    #[test]
    fn test_validate_allocation_different_constraints() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        set_caller_address(owner);
        
        // Change constraints to be more lenient
        dispatcher.set_constraints(8000, 2, 5000, 1000000);
        
        // Now this should pass (only need 2 protocols >10%)
        let valid = dispatcher.validate_allocation(5000, 4000, 1000);
        assert(valid == true, 'Should pass with relaxed constraints');
        
        // Change to be more strict
        dispatcher.set_constraints(4000, 3, 5000, 1000000);
        
        // This should fail (max single is now 40%, we have 50%)
        let invalid = dispatcher.validate_allocation(5000, 3000, 2000);
        assert(invalid == false, 'Should fail with stricter constraints');
    }
}
