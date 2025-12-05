use snforge_std::{declare, ContractClassTrait, DeclareResultTrait, deploy, start_cheat_caller_address, stop_cheat_caller_address};
use starknet::ContractAddress;
use core::traits::Into;
use obsqra_contracts::risk_engine::IRiskEngineDispatcher;

// Helper for comparisons using u256
fn felt252_ge(lhs: felt252, rhs: felt252) -> bool {
    let lhs_u256: u256 = lhs.into();
    let rhs_u256: u256 = rhs.into();
    lhs_u256 >= rhs_u256
}

fn felt252_le(lhs: felt252, rhs: felt252) -> bool {
    let lhs_u256: u256 = lhs.into();
    let rhs_u256: u256 = rhs.into();
    lhs_u256 <= rhs_u256
}

fn felt252_gt(lhs: felt252, rhs: felt252) -> bool {
    let lhs_u256: u256 = lhs.into();
    let rhs_u256: u256 = rhs.into();
    lhs_u256 > rhs_u256
}

#[test]
fn test_calculate_risk_score_low_risk() {
    let declared = declare("RiskEngine").unwrap();
    let (contract_address, _) = deploy(@declared).unwrap();
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
    let utilization = 3000;
    let volatility = 1000;
    let liquidity = 0;
    let audit_score = 95;
    let age_days = 1000;
    
    let risk = dispatcher.calculate_risk_score(
        utilization, volatility, liquidity, audit_score, age_days
    );
    
    assert(felt252_ge(risk, 5) && felt252_le(risk, 30), 'Error');
}

#[test]
fn test_calculate_risk_score_high_risk() {
    let declared = declare("RiskEngine").unwrap();
    let (contract_address, _) = deploy(@declared).unwrap();
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
    let utilization = 9500;
    let volatility = 8000;
    let liquidity = 3;
    let audit_score = 50;
    let age_days = 100;
    
    let risk = dispatcher.calculate_risk_score(
        utilization, volatility, liquidity, audit_score, age_days
    );
    
    assert(felt252_ge(risk, 70) && felt252_le(risk, 95), 'Error');
}

#[test]
fn test_calculate_allocation_balanced() {
    let declared = declare("RiskEngine").unwrap();
    let (contract_address, _) = deploy(@declared).unwrap();
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
    let aave_risk = 25;
    let lido_risk = 30;
    let compound_risk = 35;
    let aave_apy = 300;
    let lido_apy = 400;
    let compound_apy = 350;
    
    let (aave_pct, lido_pct, compound_pct) = dispatcher.calculate_allocation(
        aave_risk, lido_risk, compound_risk,
        aave_apy, lido_apy, compound_apy
    );
    
    assert(aave_pct + lido_pct + compound_pct == 10000, 'Error');
    assert(felt252_gt(lido_pct, aave_pct), 'Error');
    assert(felt252_gt(lido_pct, compound_pct), 'Error');
}

#[test]
fn test_verify_constraints_valid() {
    let declared = declare("RiskEngine").unwrap();
    let (contract_address, _) = deploy(@declared).unwrap();
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
    let aave_pct = 4000;
    let lido_pct = 3500;
    let compound_pct = 2500;
    let max_single = 6000;
    let min_diversification = 3;
    
    let valid = dispatcher.verify_constraints(
        aave_pct, lido_pct, compound_pct,
        max_single, min_diversification
    );
    
    assert(valid == true, 'Error');
}

#[test]
fn test_verify_constraints_invalid_max_single() {
    let declared = declare("RiskEngine").unwrap();
    let (contract_address, _) = deploy(@declared).unwrap();
    let dispatcher = IRiskEngineDispatcher { contract_address };
    
    let aave_pct = 7000;
    let lido_pct = 2000;
    let compound_pct = 1000;
    let max_single = 6000;
    let min_diversification = 3;
    
    let valid = dispatcher.verify_constraints(
        aave_pct, lido_pct, compound_pct,
        max_single, min_diversification
    );
    
    assert(valid == false, 'Error');
}
