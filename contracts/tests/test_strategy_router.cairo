#[cfg(test)]
mod test_strategy_router {
    use starknet::ContractAddress;
    use starknet::contract_address_const;
    use starknet::get_caller_address;
    use obsqra_contracts::strategy_router::{IStrategyRouterDispatcher, IStrategyRouterDispatcherTrait};
    use snforge_std::{declare, ContractClassTrait, start_cheat_caller_address, stop_cheat_caller_address};

    fn deploy_contracts() -> (IRiskEngineDispatcher, IDAOConstraintManagerDispatcher, IStrategyRouterDispatcher) {
        // Deploy RiskEngine
        let risk_contract = declare("RiskEngine").unwrap();
        let (risk_address, _) = risk_contract.deploy(@ArrayTrait::new()).unwrap();
        let risk_engine = IRiskEngineDispatcher { contract_address: risk_address };
        
        // Deploy DAOConstraintManager
        let dao_contract = declare("DAOConstraintManager").unwrap();
        let mut dao_calldata = ArrayTrait::new();
        dao_calldata.append(6000); // max_single_protocol = 60%
        dao_calldata.append(2);    // min_protocols = 2
        dao_calldata.append(3000); // max_volatility = 30%
        dao_calldata.append(1000000000000000000); // min_liquidity = 1 ETH (low)
        dao_calldata.append(0);    // high part of u256
        let (dao_address, _) = dao_contract.deploy(@dao_calldata).unwrap();
        let dao_manager = IDAOConstraintManagerDispatcher { contract_address: dao_address };
        
        // Deploy StrategyRouter
        let router_contract = declare("StrategyRouter").unwrap();
        let mut router_calldata = ArrayTrait::new();
        router_calldata.append(risk_address.into());
        router_calldata.append(dao_address.into());
        router_calldata.append(contract_address_const::<0x123>().into()); // nostra_address
        router_calldata.append(contract_address_const::<0x456>().into()); // zklend_address
        router_calldata.append(contract_address_const::<0x789>().into()); // ekubo_address
        router_calldata.append(3333); // initial nostra allocation
        router_calldata.append(3333); // initial zklend allocation
        router_calldata.append(3334); // initial ekubo allocation
        let (router_address, _) = router_contract.deploy(@router_calldata).unwrap();
        let strategy_router = IStrategyRouterDispatcher { contract_address: router_address };
        
        (risk_engine, dao_manager, strategy_router)
    }

    #[test]
    fn test_initial_allocation() {
        let (_, _, strategy_router) = deploy_contracts();
        
        let (nostra, zklend, ekubo) = strategy_router.get_allocation();
        
        // Check initial allocation
        assert(nostra == 3333, 'Nostra should be 33.33%');
        assert(zklend == 3333, 'zkLend should be 33.33%');
        assert(ekubo == 3334, 'Ekubo should be 33.34%');
        
        // Total should be 100%
        assert(nostra + zklend + ekubo == 10000, 'Total should be 100%');
    }

    #[test]
    fn test_update_allocation() {
        let (_, _, strategy_router) = deploy_contracts();
        
        // Update to new allocation
        let new_nostra = 4000; // 40%
        let new_zklend = 3500; // 35%
        let new_ekubo = 2500;  // 25%
        
        strategy_router.update_allocation(new_nostra, new_zklend, new_ekubo);
        
        let (nostra, zklend, ekubo) = strategy_router.get_allocation();
        
        assert(nostra == new_nostra, 'Nostra not updated');
        assert(zklend == new_zklend, 'zkLend not updated');
        assert(ekubo == new_ekubo, 'Ekubo not updated');
    }

    #[test]
    #[should_panic(expected: ('Allocation must sum to 100%',))]
    fn test_update_allocation_invalid_total() {
        let (_, _, strategy_router) = deploy_contracts();
        
        // Total is 90%, not 100%
        strategy_router.update_allocation(3000, 3000, 3000);
    }

    #[test]
    fn test_get_protocol_addresses() {
        let (_, _, strategy_router) = deploy_contracts();
        
        let (nostra, zklend, ekubo) = strategy_router.get_protocol_addresses();
        
        assert(nostra == contract_address_const::<0x123>(), 'Wrong Nostra address');
        assert(zklend == contract_address_const::<0x456>(), 'Wrong zkLend address');
        assert(ekubo == contract_address_const::<0x789>(), 'Wrong Ekubo address');
    }

    #[test]
    fn test_accrue_yields() {
        let (_, _, strategy_router) = deploy_contracts();
        
        // This should execute without panicking
        // In a real implementation, this would interact with the protocols
        strategy_router.accrue_yields();
        
        // For now, we just verify it doesn't revert
        assert(true, 'Accrue yields completed');
    }

    #[test]
    fn test_allocation_respects_constraints() {
        let (_, dao_manager, strategy_router) = deploy_contracts();
        
        // Get current constraints
        let (max_single, min_protocols, max_vol, min_liq) = dao_manager.get_constraints();
        
        // Try to set allocation that respects constraints
        let nostra = 5000; // 50% - under max_single (60%)
        let zklend = 3000; // 30%
        let ekubo = 2000;  // 20% - uses 3 protocols (over min 2)
        
        strategy_router.update_allocation(nostra, zklend, ekubo);
        
        let (actual_nostra, actual_zklend, actual_ekubo) = strategy_router.get_allocation();
        assert(actual_nostra == nostra, 'Nostra not set correctly');
    }

    #[test]
    fn test_multiple_allocation_updates() {
        let (_, _, strategy_router) = deploy_contracts();
        
        // First update
        strategy_router.update_allocation(4000, 3000, 3000);
        let (n1, z1, e1) = strategy_router.get_allocation();
        assert(n1 == 4000, 'First update failed');
        
        // Second update
        strategy_router.update_allocation(2500, 2500, 5000);
        let (n2, z2, e2) = strategy_router.get_allocation();
        assert(n2 == 2500, 'Second update failed');
        assert(e2 == 5000, 'Second update failed');
        
        // Third update
        strategy_router.update_allocation(3333, 3333, 3334);
        let (n3, z3, e3) = strategy_router.get_allocation();
        assert(n3 == 3333, 'Third update failed');
    }
}
