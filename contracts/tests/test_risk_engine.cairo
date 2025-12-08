#[cfg(test)]
mod test_risk_engine {
    use starknet::ContractAddress;
    use starknet::contract_address_const;
    use obsqra_contracts::risk_engine::{IRiskEngineDispatcher, IRiskEngineDispatcherTrait};
    use snforge_std::{declare, ContractClassTrait, start_cheat_caller_address, stop_cheat_caller_address};

    fn deploy_contract() -> IRiskEngineDispatcher {
        let contract = declare("RiskEngine").unwrap();
        let (contract_address, _) = contract.deploy(@ArrayTrait::new()).unwrap();
        IRiskEngineDispatcher { contract_address }
    }

    #[test]
    fn test_calculate_risk_score_low_risk() {
        let dispatcher = deploy_contract();
        
        // Low risk scenario: low utilization, low volatility, high liquidity, high audit score, old protocol
        let utilization = 3000; // 30%
        let volatility = 1000;  // 10%
        let liquidity = 0;      // 0% (actually means high liquidity in our model)
        let audit_score = 95;   // 95/100
        let age_days = 1000;    // ~3 years old
        
        let risk_score = dispatcher.calculate_risk_score(
            utilization,
            volatility,
            liquidity,
            audit_score,
            age_days
        );
        
        // Should be relatively low risk (lower score = lower risk)
        assert(risk_score < 5000, 'Risk should be low');
    }

    #[test]
    fn test_calculate_risk_score_high_risk() {
        let dispatcher = deploy_contract();
        
        // High risk scenario: high utilization, high volatility, low liquidity, low audit, new protocol
        let utilization = 9000; // 90%
        let volatility = 5000;  // 50%
        let liquidity = 8000;   // High liquidity risk
        let audit_score = 60;   // Only 60/100
        let age_days = 30;      // Brand new protocol
        
        let risk_score = dispatcher.calculate_risk_score(
            utilization,
            volatility,
            liquidity,
            audit_score,
            age_days
        );
        
        // Should be high risk
        assert(risk_score > 7000, 'Risk should be high');
    }

    #[test]
    fn test_calculate_risk_score_medium_risk() {
        let dispatcher = deploy_contract();
        
        // Medium risk scenario: balanced parameters
        let utilization = 5000; // 50%
        let volatility = 2000;  // 20%
        let liquidity = 2000;
        let audit_score = 80;   // 80/100
        let age_days = 365;     // 1 year old
        
        let risk_score = dispatcher.calculate_risk_score(
            utilization,
            volatility,
            liquidity,
            audit_score,
            age_days
        );
        
        // Should be medium risk
        assert(risk_score >= 4000 && risk_score <= 7000, 'Risk should be medium');
    }

    #[test]
    fn test_calculate_allocation_balanced() {
        let dispatcher = deploy_contract();
        
        // Medium risk for all protocols
        let nostra_risk = 5000;
        let zklend_risk = 5000;
        let ekubo_risk = 5000;
        
        let (nostra_alloc, zklend_alloc, ekubo_alloc) = dispatcher.calculate_allocation(
            nostra_risk,
            zklend_risk,
            ekubo_risk
        );
        
        // All should get equal allocation since risk is equal
        assert(nostra_alloc > 3000 && nostra_alloc < 3700, 'Nostra should be ~33%');
        assert(zklend_alloc > 3000 && zklend_alloc < 3700, 'zkLend should be ~33%');
        assert(ekubo_alloc > 3000 && ekubo_alloc < 3700, 'Ekubo should be ~33%');
        
        // Total should be 100%
        assert(nostra_alloc + zklend_alloc + ekubo_alloc == 10000, 'Total should be 100%');
    }

    #[test]
    fn test_calculate_allocation_prefer_low_risk() {
        let dispatcher = deploy_contract();
        
        // Nostra has lowest risk, Ekubo has highest
        let nostra_risk = 3000; // Low risk
        let zklend_risk = 5000; // Medium risk
        let ekubo_risk = 8000;  // High risk
        
        let (nostra_alloc, zklend_alloc, ekubo_alloc) = dispatcher.calculate_allocation(
            nostra_risk,
            zklend_risk,
            ekubo_risk
        );
        
        // Nostra should get most allocation
        assert(nostra_alloc > zklend_alloc, 'Nostra should be largest');
        assert(nostra_alloc > ekubo_alloc, 'Nostra should be largest');
        
        // Ekubo should get least
        assert(ekubo_alloc < zklend_alloc, 'Ekubo should be smallest');
        assert(ekubo_alloc < nostra_alloc, 'Ekubo should be smallest');
        
        // Total should be 100%
        assert(nostra_alloc + zklend_alloc + ekubo_alloc == 10000, 'Total should be 100%');
    }

    #[test]
    fn test_verify_constraints_pass() {
        let dispatcher = deploy_contract();
        
        // Allocation that respects constraints
        let nostra_pct = 4000;  // 40%
        let zklend_pct = 3500;  // 35%
        let ekubo_pct = 2500;   // 25%
        
        // Constraints: max_single=60%, min_protocols=2, max_volatility=30%, min_liquidity=1ETH
        let max_single_protocol = 6000;
        let min_diversification = 2;
        let max_volatility = 3000;
        let min_liquidity = 1000000000000000000;
        
        let result = dispatcher.verify_constraints(
            nostra_pct,
            zklend_pct,
            ekubo_pct,
            max_single_protocol,
            min_diversification,
            max_volatility,
            min_liquidity
        );
        
        assert(result == true, 'Constraints should pass');
    }

    #[test]
    fn test_verify_constraints_fail_max_single() {
        let dispatcher = deploy_contract();
        
        // Nostra gets 70% - exceeds max_single_protocol
        let nostra_pct = 7000;  // 70%
        let zklend_pct = 2000;  // 20%
        let ekubo_pct = 1000;   // 10%
        
        let max_single_protocol = 6000; // 60% max
        let min_diversification = 2;
        let max_volatility = 3000;
        let min_liquidity = 1000000000000000000;
        
        let result = dispatcher.verify_constraints(
            nostra_pct,
            zklend_pct,
            ekubo_pct,
            max_single_protocol,
            min_diversification,
            max_volatility,
            min_liquidity
        );
        
        assert(result == false, 'Should fail max_single constraint');
    }

    #[test]
    fn test_verify_constraints_fail_min_protocols() {
        let dispatcher = deploy_contract();
        
        // Only 1 protocol used (100% to Nostra)
        let nostra_pct = 10000; // 100%
        let zklend_pct = 0;     // 0%
        let ekubo_pct = 0;      // 0%
        
        let max_single_protocol = 10000; // Allow 100%
        let min_diversification = 2;     // But require at least 2 protocols
        let max_volatility = 3000;
        let min_liquidity = 1000000000000000000;
        
        let result = dispatcher.verify_constraints(
            nostra_pct,
            zklend_pct,
            ekubo_pct,
            max_single_protocol,
            min_diversification,
            max_volatility,
            min_liquidity
        );
        
        assert(result == false, 'Should fail min_protocols constraint');
    }

    #[test]
    fn test_age_factor_rewards_maturity() {
        let dispatcher = deploy_contract();
        
        // Old protocol should have lower risk than new one with same other params
        let utilization = 5000;
        let volatility = 2000;
        let liquidity = 2000;
        let audit_score = 80;
        
        let old_protocol_risk = dispatcher.calculate_risk_score(
            utilization, volatility, liquidity, audit_score, 1000 // ~3 years
        );
        
        let new_protocol_risk = dispatcher.calculate_risk_score(
            utilization, volatility, liquidity, audit_score, 30 // 1 month
        );
        
        assert(old_protocol_risk < new_protocol_risk, 'Old protocol should be safer');
    }
}
