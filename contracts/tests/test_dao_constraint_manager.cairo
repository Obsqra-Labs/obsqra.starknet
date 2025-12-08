#[cfg(test)]
mod test_dao_constraint_manager {
    use starknet::ContractAddress;
    use starknet::contract_address_const;
    use obsqra_contracts::dao_constraint_manager::{IDAOConstraintManagerDispatcher, IDAOConstraintManagerDispatcherTrait};
    use snforge_std::{declare, ContractClassTrait, start_cheat_caller_address, stop_cheat_caller_address};

    fn deploy_contract() -> IDAOConstraintManagerDispatcher {
        let contract = declare("DAOConstraintManager").unwrap().contract_class();
        
        let mut calldata = ArrayTrait::new();
        calldata.append(6000); // max_single_protocol = 60%
        calldata.append(2);    // min_protocols = 2
        calldata.append(3000); // max_volatility = 30%
        calldata.append(1000000000000000000); // min_liquidity = 1 ETH (low)
        calldata.append(0);    // high part of u256
        
        let (contract_address, _) = contract.deploy(@calldata).unwrap();
        IDAOConstraintManagerDispatcher { contract_address }
    }

    #[test]
    fn test_initial_constraints() {
        let dispatcher = deploy_contract();
        
        let (max_single, min_protocols, max_vol, min_liq) = dispatcher.get_constraints();
        
        assert(max_single == 6000, 'Max single should be 60%');
        assert(min_protocols == 2, 'Min protocols should be 2');
        assert(max_vol == 3000, 'Max volatility should be 30%');
        assert(min_liq == 1000000000000000000, 'Min liquidity wrong');
    }

    #[test]
    fn test_set_constraints() {
        let (dispatcher, owner) = deploy_contract();
        
        // Set new constraints
        let new_max_single = 5000; // 50%
        let new_min_protocols = 3; // Require 3 protocols
        let new_max_vol = 2000;    // 20%
        let new_min_liq = 5000000000000000000; // 5 ETH
        
        start_cheat_caller_address(dispatcher.contract_address, owner);
        dispatcher.set_constraints(
            new_max_single,
            new_min_protocols,
            new_max_vol,
            new_min_liq
        );
        stop_cheat_caller_address(dispatcher.contract_address);
        
        let (max_single, min_protocols, max_vol, min_liq) = dispatcher.get_constraints();
        
        assert(max_single == new_max_single, 'Max single not updated');
        assert(min_protocols == new_min_protocols, 'Min protocols not updated');
        assert(max_vol == new_max_vol, 'Max volatility not updated');
        assert(min_liq == new_min_liq, 'Min liquidity not updated');
    }

    #[test]
    fn test_validate_allocation_pass() {
        let (dispatcher, _) = deploy_contract();
        
        // Valid allocation: 40%, 35%, 25% (respects 60% max, uses 3 protocols)
        let result = dispatcher.validate_allocation(4000, 3500, 2500);
        assert(result == true, 'Should pass validation');
    }

    #[test]
    fn test_validate_allocation_fail_max_single() {
        let (dispatcher, _) = deploy_contract();
        
        // Invalid: 70%, 20%, 10% (exceeds 60% max)
        let result = dispatcher.validate_allocation(7000, 2000, 1000);
        assert(result == false, 'Should fail: exceeds max');
    }

    #[test]
    fn test_validate_allocation_fail_min_protocols() {
        let (dispatcher, _) = deploy_contract();
        
        // Invalid: 100%, 0%, 0% (only 1 protocol, need 2 minimum)
        let result = dispatcher.validate_allocation(10000, 0, 0);
        assert(result == false, 'Should fail: not enough protocols');
    }

    #[test]
    fn test_validate_allocation_exactly_two_protocols() {
        let (dispatcher, _) = deploy_contract();
        
        // Valid: 60%, 40%, 0% (uses exactly 2 protocols, meets minimum)
        let result = dispatcher.validate_allocation(6000, 4000, 0);
        assert(result == true, 'Should pass with 2 protocols');
    }

    #[test]
    fn test_validate_allocation_all_equal() {
        let (dispatcher, _) = deploy_contract();
        
        // Valid: 33.33%, 33.33%, 33.34% (balanced, uses 3 protocols)
        let result = dispatcher.validate_allocation(3333, 3333, 3334);
        assert(result == true, 'Should pass balanced allocation');
    }

    #[test]
    fn test_multiple_constraint_updates() {
        let (dispatcher, owner) = deploy_contract();
        
        start_cheat_caller_address(dispatcher.contract_address, owner);
        
        // First update
        dispatcher.set_constraints(5000, 2, 2500, 2000000000000000000);
        let (max1, _, _, _) = dispatcher.get_constraints();
        assert(max1 == 5000, 'First update failed');
        
        // Second update
        dispatcher.set_constraints(7000, 3, 4000, 1000000000000000000);
        let (max2, min2, _, _) = dispatcher.get_constraints();
        assert(max2 == 7000, 'Second update failed');
        assert(min2 == 3, 'Second update failed');
        
        stop_cheat_caller_address(dispatcher.contract_address);
    }

    #[test]
    fn test_validate_with_updated_constraints() {
        let (dispatcher, owner) = deploy_contract();
        
        // This allocation would fail with default constraints
        let nostra = 7000; // 70%
        let zklend = 2000; // 20%
        let ekubo = 1000;  // 10%
        
        // Should fail with default (max 60%)
        let result_before = dispatcher.validate_allocation(nostra, zklend, ekubo);
        assert(result_before == false, 'Should fail before update');
        
        // Update constraints to allow 80% max
        start_cheat_caller_address(dispatcher.contract_address, owner);
        dispatcher.set_constraints(8000, 2, 3000, 1000000000000000000);
        stop_cheat_caller_address(dispatcher.contract_address);
        
        // Should now pass
        let result_after = dispatcher.validate_allocation(nostra, zklend, ekubo);
        assert(result_after == true, 'Should pass after update');
    }

    #[test]
    fn test_edge_case_exactly_at_max() {
        let (dispatcher, _) = deploy_contract();
        
        // Exactly at 60% max
        let result = dispatcher.validate_allocation(6000, 3000, 1000);
        assert(result == true, 'Should pass at exact max');
    }

    #[test]
    fn test_edge_case_just_over_max() {
        let (dispatcher, _) = deploy_contract();
        
        // Just 0.01% over max (60.01%)
        let result = dispatcher.validate_allocation(6001, 2999, 1000);
        assert(result == false, 'Should fail just over max');
    }

    #[test]
    fn test_realistic_conservative_allocation() {
        let (dispatcher, _) = deploy_contract();
        
        // Conservative allocation: 45%, 35%, 20%
        let result = dispatcher.validate_allocation(4500, 3500, 2000);
        assert(result == true, 'Conservative allocation should pass');
    }

    #[test]
    fn test_realistic_aggressive_allocation() {
        let (dispatcher, _) = deploy_contract();
        
        // Aggressive but valid: 55%, 30%, 15%
        let result = dispatcher.validate_allocation(5500, 3000, 1500);
        assert(result == true, 'Aggressive allocation should pass');
    }
}

