#[cfg(test)]
mod tests {
    use super::{IStrategyRouterDispatcher, IStrategyRouterDispatcherTrait};
    use starknet::ContractAddress;
    
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
    fn test_get_allocation() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        let (aave, lido, compound) = dispatcher.get_allocation();
        
        // Should be initialized to balanced allocation
        assert(aave == 3333, 'Aave should be ~33%');
        assert(lido == 3333, 'Lido should be ~33%');
        assert(compound == 3334, 'Compound should be ~33%');
    }
    
    #[test]
    fn test_update_allocation() {
        let router = deploy_contract();
        let dispatcher = IStrategyRouterDispatcher { contract_address: router };
        
        // Update allocation
        dispatcher.update_allocation(4000, 3500, 2500);
        
        // Verify update
        let (aave, lido, compound) = dispatcher.get_allocation();
        assert(aave == 4000, 'Aave should be 40%');
        assert(lido == 3500, 'Lido should be 35%');
        assert(compound == 2500, 'Compound should be 25%');
    }
}

