#[cfg(test)]
mod tests {
    use super::{IDAOConstraintManagerDispatcher, IDAOConstraintManagerDispatcherTrait};
    use starknet::ContractAddress;
    
    fn deploy_contract() -> ContractAddress {
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        let (contract_address, _) = DAOConstraintManager::DAOConstraintManager::deploy(
            @array![
                owner.into(),
                6000.into(),  // max_single
                3.into(),     // min_diversification
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
    }
    
    #[test]
    fn test_validate_allocation() {
        let manager = deploy_contract();
        let dispatcher = IDAOConstraintManagerDispatcher { contract_address: manager };
        
        // Valid allocation
        let valid = dispatcher.validate_allocation(4000, 3500, 2500);
        assert(valid == true, 'Valid allocation should pass');
        
        // Invalid allocation (exceeds max)
        let invalid = dispatcher.validate_allocation(7000, 2000, 1000);
        assert(invalid == false, 'Invalid allocation should fail');
    }
}

