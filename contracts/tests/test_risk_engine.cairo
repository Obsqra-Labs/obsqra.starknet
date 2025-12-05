#[cfg(test)]
mod tests {
    use super::{IRiskEngineDispatcher, IRiskEngineDispatcherTrait};
    use starknet::ContractAddress;
    use starknet::testing::{set_caller_address, set_contract_address};
    
    fn deploy_contract() -> ContractAddress {
        // Deploy contract with test owner
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        let (contract_address, _) = RiskEngine::RiskEngine::deploy(@array![owner.into()], @array![]);
        contract_address
    }
    
    #[test]
    fn test_calculate_risk_score_low() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Test case: Low risk protocol
        let utilization = 5000;  // 50%
        let volatility = 2000;    // 20%
        let liquidity = 0;        // Very High
        let audit_score = 95;
        let age_days = 1000;
        
        let risk = dispatcher.calculate_risk_score(
            utilization, volatility, liquidity, audit_score, age_days
        );
        
        // Expected: ~25 (low risk)
        assert(risk >= 20 && risk <= 30, 'Low risk score');
    }
    
    #[test]
    fn test_calculate_risk_score_high() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Test case: High risk protocol
        let utilization = 9500;  // 95%
        let volatility = 8000;    // 80%
        let liquidity = 3;        // Low
        let audit_score = 50;
        let age_days = 100;
        
        let risk = dispatcher.calculate_risk_score(
            utilization, volatility, liquidity, audit_score, age_days
        );
        
        // Expected: ~70-95 (high risk)
        assert(risk >= 70 && risk <= 95, 'High risk score');
    }
    
    #[test]
    fn test_calculate_allocation() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Test case: Balanced allocation
        let aave_risk = 25;
        let lido_risk = 30;
        let compound_risk = 35;
        let aave_apy = 300;   // 3.00%
        let lido_apy = 400;   // 4.00%
        let compound_apy = 350; // 3.50%
        
        let (aave_pct, lido_pct, compound_pct) = dispatcher.calculate_allocation(
            aave_risk, lido_risk, compound_risk,
            aave_apy, lido_apy, compound_apy
        );
        
        // Verify percentages sum to 10000 (100%)
        assert(aave_pct + lido_pct + compound_pct == 10000, 'Percentages do not sum to 100%');
        
        // Verify Lido has highest allocation (highest APY, similar risk)
        assert(lido_pct > aave_pct, 'Lido should have higher allocation');
        assert(lido_pct > compound_pct, 'Lido should have higher allocation');
    }
    
    #[test]
    fn test_verify_constraints_valid() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Test case: Valid allocation
        let aave_pct = 4000;   // 40%
        let lido_pct = 3500;   // 35%
        let compound_pct = 2500; // 25%
        let max_single = 6000;  // 60%
        let min_diversification = 3; // All 3 protocols >10%
        
        let valid = dispatcher.verify_constraints(
            aave_pct, lido_pct, compound_pct,
            max_single, min_diversification
        );
        
        assert(valid == true, 'Valid allocation should pass constraints');
    }
    
    #[test]
    fn test_verify_constraints_invalid_max() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Test case: Invalid allocation (exceeds max single)
        let aave_pct = 7000;  // 70% (exceeds 60% max)
        let lido_pct = 2000;   // 20%
        let compound_pct = 1000; // 10%
        let max_single = 6000;  // 60%
        let min_diversification = 3;
        
        let valid = dispatcher.verify_constraints(
            aave_pct, lido_pct, compound_pct,
            max_single, min_diversification
        );
        
        assert(valid == false, 'Invalid allocation should fail constraints');
    }
    
    #[test]
    fn test_verify_constraints_invalid_diversification() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Test case: Invalid allocation (insufficient diversification)
        let aave_pct = 8000;  // 80%
        let lido_pct = 1500;   // 15%
        let compound_pct = 500; // 5% (<10%)
        let max_single = 6000;
        let min_diversification = 3; // Need 3 protocols >10%
        
        let valid = dispatcher.verify_constraints(
            aave_pct, lido_pct, compound_pct,
            max_single, min_diversification
        );
        
        assert(valid == false, 'Invalid diversification should fail constraints');
    }
}
