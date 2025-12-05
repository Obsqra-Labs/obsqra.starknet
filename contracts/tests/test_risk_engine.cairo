#[cfg(test)]
mod tests {
    use super::{IRiskEngineDispatcher, IRiskEngineDispatcherTrait};
    use starknet::ContractAddress;
    use starknet::testing::{set_caller_address, set_contract_address};
    use snforge_std::{declare, ContractClassTrait, get_contract_class, deploy};
    
    fn deploy_contract() -> ContractAddress {
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        let (contract_address, _) = RiskEngine::RiskEngine::deploy(@array![owner.into()], @array![]);
        contract_address
    }
    
    // ========== Risk Score Tests ==========
    
    #[test]
    fn test_calculate_risk_score_low_risk() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Low risk: low utilization, low volatility, high liquidity, high audit, old
        let utilization = 3000;  // 30%
        let volatility = 1000;   // 10%
        let liquidity = 0;        // Very High
        let audit_score = 95;
        let age_days = 1000;
        
        let risk = dispatcher.calculate_risk_score(
            utilization, volatility, liquidity, audit_score, age_days
        );
        
        // Should be low risk (5-30 range expected)
        assert(risk >= 5 && risk <= 30, 'Low risk score');
    }
    
    #[test]
    fn test_calculate_risk_score_high_risk() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // High risk: high utilization, high volatility, low liquidity, low audit, new
        let utilization = 9500;  // 95%
        let volatility = 8000;    // 80%
        let liquidity = 3;        // Very Low
        let audit_score = 50;
        let age_days = 100;
        
        let risk = dispatcher.calculate_risk_score(
            utilization, volatility, liquidity, audit_score, age_days
        );
        
        // Should be high risk (70-95 range expected)
        assert(risk >= 70 && risk <= 95, 'High risk score');
    }
    
    #[test]
    fn test_calculate_risk_score_edge_cases() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Edge case: Minimum values
        let risk_min = dispatcher.calculate_risk_score(0, 0, 0, 100, 730);
        assert(risk_min >= 5, 'Minimum risk should be at least 5');
        
        // Edge case: Maximum values
        let risk_max = dispatcher.calculate_risk_score(10000, 10000, 3, 0, 0);
        assert(risk_max <= 95, 'Maximum risk should be at most 95');
        
        // Edge case: Age exactly 730 days (no age risk)
        let risk_730 = dispatcher.calculate_risk_score(5000, 5000, 1, 80, 730);
        assert(risk_730 >= 5 && risk_730 <= 95, 'Risk at 730 days should be valid');
    }
    
    #[test]
    fn test_calculate_risk_score_liquidity_categories() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Test each liquidity category
        let base_util = 5000;
        let base_vol = 5000;
        let base_audit = 80;
        let base_age = 365;
        
        let risk_0 = dispatcher.calculate_risk_score(base_util, base_vol, 0, base_audit, base_age);
        let risk_1 = dispatcher.calculate_risk_score(base_util, base_vol, 1, base_audit, base_age);
        let risk_2 = dispatcher.calculate_risk_score(base_util, base_vol, 2, base_audit, base_age);
        let risk_3 = dispatcher.calculate_risk_score(base_util, base_vol, 3, base_audit, base_age);
        
        // Risk should increase with lower liquidity
        assert(risk_0 < risk_1, 'Very High liquidity should have lower risk');
        assert(risk_1 < risk_2, 'Medium liquidity should have lower risk than Low');
        assert(risk_2 < risk_3, 'Low liquidity should have lower risk than Very Low');
    }
    
    // ========== Allocation Tests ==========
    
    #[test]
    fn test_calculate_allocation_balanced() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Balanced risk and APY
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
        assert(aave_pct + lido_pct + compound_pct == 10000, 'Percentages must sum to 100%');
        
        // Lido should have highest allocation (highest APY, similar risk)
        assert(lido_pct > aave_pct, 'Lido should have higher allocation than Aave');
        assert(lido_pct > compound_pct, 'Lido should have higher allocation than Compound');
    }
    
    #[test]
    fn test_calculate_allocation_extreme_apy() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // One protocol has much higher APY
        let aave_risk = 20;
        let lido_risk = 20;
        let compound_risk = 20;
        let aave_apy = 1000;  // 10% (very high)
        let lido_apy = 100;   // 1%
        let compound_apy = 100; // 1%
        
        let (aave_pct, lido_pct, compound_pct) = dispatcher.calculate_allocation(
            aave_risk, lido_risk, compound_risk,
            aave_apy, lido_apy, compound_apy
        );
        
        assert(aave_pct + lido_pct + compound_pct == 10000, 'Percentages must sum to 100%');
        // Aave should dominate due to much higher APY
        assert(aave_pct > lido_pct * 5, 'Aave should have much higher allocation');
        assert(aave_pct > compound_pct * 5, 'Aave should have much higher allocation');
    }
    
    #[test]
    fn test_calculate_allocation_high_risk_penalty() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // High risk should reduce allocation even with good APY
        let aave_risk = 90;   // Very high risk
        let lido_risk = 20;   // Low risk
        let compound_risk = 20;
        let aave_apy = 500;   // 5% (good APY)
        let lido_apy = 300;   // 3% (lower APY)
        let compound_apy = 300;
        
        let (aave_pct, lido_pct, compound_pct) = dispatcher.calculate_allocation(
            aave_risk, lido_risk, compound_risk,
            aave_apy, lido_apy, compound_apy
        );
        
        assert(aave_pct + lido_pct + compound_pct == 10000, 'Percentages must sum to 100%');
        // Despite higher APY, Aave should have lower allocation due to high risk
        assert(aave_pct < lido_pct, 'High risk should reduce allocation');
        assert(aave_pct < compound_pct, 'High risk should reduce allocation');
    }
    
    #[test]
    fn test_calculate_allocation_edge_cases() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Edge case: All same risk and APY (should be equal)
        let (aave_pct, lido_pct, compound_pct) = dispatcher.calculate_allocation(
            25, 25, 25, 300, 300, 300
        );
        
        assert(aave_pct + lido_pct + compound_pct == 10000, 'Percentages must sum to 100%');
        // Should be roughly equal (within 1% tolerance for rounding)
        let diff1 = if aave_pct > lido_pct { aave_pct - lido_pct } else { lido_pct - aave_pct };
        let diff2 = if lido_pct > compound_pct { lido_pct - compound_pct } else { compound_pct - lido_pct };
        assert(diff1 <= 100, 'Allocations should be roughly equal');
        assert(diff2 <= 100, 'Allocations should be roughly equal');
    }
    
    // ========== Constraint Verification Tests ==========
    
    #[test]
    fn test_verify_constraints_valid() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Valid allocation: well-diversified, within max
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
    fn test_verify_constraints_invalid_max_single() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Invalid: exceeds max single protocol
        let aave_pct = 7000;  // 70% (exceeds 60% max)
        let lido_pct = 2000;   // 20%
        let compound_pct = 1000; // 10%
        let max_single = 6000;  // 60%
        let min_diversification = 3;
        
        let valid = dispatcher.verify_constraints(
            aave_pct, lido_pct, compound_pct,
            max_single, min_diversification
        );
        
        assert(valid == false, 'Exceeding max single should fail');
    }
    
    #[test]
    fn test_verify_constraints_invalid_diversification() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Invalid: insufficient diversification
        let aave_pct = 8000;  // 80%
        let lido_pct = 1500;   // 15%
        let compound_pct = 500; // 5% (<10%)
        let max_single = 6000;
        let min_diversification = 3; // Need 3 protocols >10%
        
        let valid = dispatcher.verify_constraints(
            aave_pct, lido_pct, compound_pct,
            max_single, min_diversification
        );
        
        assert(valid == false, 'Insufficient diversification should fail');
    }
    
    #[test]
    fn test_verify_constraints_edge_cases() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Edge case: Exactly at max single
        let valid_at_max = dispatcher.verify_constraints(
            6000, 2500, 1500, 6000, 3
        );
        assert(valid_at_max == true, 'Exactly at max should be valid');
        
        // Edge case: Exactly at min diversification threshold (1000 = 10%)
        let valid_at_threshold = dispatcher.verify_constraints(
            4000, 3000, 1000, 6000, 3
        );
        assert(valid_at_threshold == true, 'Exactly at threshold should be valid');
        
        // Edge case: Just below threshold
        let invalid_below_threshold = dispatcher.verify_constraints(
            4000, 3000, 999, 6000, 3
        );
        assert(invalid_below_threshold == false, 'Just below threshold should fail');
    }
    
    #[test]
    fn test_verify_constraints_min_diversification_variations() {
        let risk_engine = deploy_contract();
        let dispatcher = IRiskEngineDispatcher { contract_address: risk_engine };
        
        // Test with min_diversification = 2 (need 2 protocols >10%)
        let valid_2 = dispatcher.verify_constraints(
            5000, 4000, 1000, 6000, 2
        );
        assert(valid_2 == true, 'Should pass with 2 protocols >10%');
        
        // Test with min_diversification = 1 (need 1 protocol >10%)
        let valid_1 = dispatcher.verify_constraints(
            9000, 500, 500, 6000, 1
        );
        assert(valid_1 == true, 'Should pass with 1 protocol >10%');
        
        // Test with min_diversification = 3 but only 2 qualify
        let invalid_2_of_3 = dispatcher.verify_constraints(
            5000, 4000, 1000, 6000, 3
        );
        assert(invalid_2_of_3 == false, 'Should fail with only 2 of 3 required');
    }
}
