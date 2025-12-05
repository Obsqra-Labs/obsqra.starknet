#[cfg(test)]
mod tests {
    use obsqra_contracts::risk_engine::{IRiskEngineDispatcher, IRiskEngineDispatcherTrait, RiskEngine};
    use starknet::ContractAddress;
    use snforge_std::{declare, ContractClassTrait, DeclareResultTrait, get_contract_class, deploy, start_cheat_caller_address, stop_cheat_caller_address};
    
    #[test]
    fn test_calculate_risk_score_low_risk() {
        let owner: ContractAddress = starknet::contract_address_const::<0x123>();
        let (contract_address, _) = RiskEngine::RiskEngine::deploy(@array![owner.into()], @array![]);
        let dispatcher = IRiskEngineDispatcher { contract_address };
    
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
    assert(risk >= 5 && risk <= 30, 'Error');
}

#[test]
fn test_calculate_risk_score_high_risk() {
    let owner: ContractAddress = starknet::contract_address_const::<0x123>();
    let (contract_address, _) = RiskEngine::RiskEngine::deploy(@array![owner.into()], @array![]);
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
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
    assert(risk >= 70 && risk <= 95, 'Error');
}

#[test]
fn test_calculate_allocation_balanced() {
    let owner: ContractAddress = starknet::contract_address_const::<0x123>();
    let (contract_address, _) = RiskEngine::RiskEngine::deploy(@array![owner.into()], @array![]);
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
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
    assert(aave_pct + lido_pct + compound_pct == 10000, 'Error');
    
    // Lido should have highest allocation (highest APY, similar risk)
    assert(lido_pct > aave_pct, 'Error');
    assert(lido_pct > compound_pct, 'Error');
}

#[test]
fn test_verify_constraints_valid() {
    let owner: ContractAddress = starknet::contract_address_const::<0x123>();
    let (contract_address, _) = RiskEngine::RiskEngine::deploy(@array![owner.into()], @array![]);
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
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
    
    assert(valid == true, 'Error');
}

#[test]
fn test_verify_constraints_invalid_max_single() {
    let owner: ContractAddress = starknet::contract_address_const::<0x123>();
    let (contract_address, _) = RiskEngine::RiskEngine::deploy(@array![owner.into()], @array![]);
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
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
    
    assert(valid == false, 'Error');
    }
}
